import { sleep } from 'k6';
import http from 'k6/http';
import { check } from 'k6';
import { Counter } from 'k6/metrics';
import { BASE_URL, loadConfig, login, expectStatus, baseHeaders, tags, SIMULATE_CLIENT_IP } from './common.js';

const cfg = loadConfig();

const retryMissing = new Counter('login_429_without_retry_after');

export const options = {
  scenarios: {
    bruteForce: {
      executor: 'per-vu-iterations',
      vus: 1,
      iterations: 40,
      startTime: '0s',
      exec: 'bruteForce',
    },
    successLogin: {
      executor: 'per-vu-iterations',
      vus: 3,
      // Fewer than login_ip (5/m) attempts per VU so a legit client is never
      // throttled by its own traffic — only the attacker's IP must trip.
      iterations: 3,
      startTime: '5s',
      exec: 'successLogin',
    },
  },
  thresholds: {
    login_429_without_retry_after: ['count == 0'],
    unexpected_http_5xx: ['count == 0'],
    unexpected_http_4xx: ['count == 0'],
  },
};

// Hammer the login with distinct usernames so only the per-IP throttle trips.
// The limit is login_ip = 5/m: after a few attempts the middleware returns
// 429 and MUST include Retry-After. Every 429 also writes a RATE_LIMITED
// audit entry (verified post-run, see docs/load-testing.md).
export function bruteForce() {
  const res = login(`attacker${__ITER}`, 'wrong-password', 'login-bruteforce');
  if (res.status === 429) {
    check(res, {
      'login: 429 carries Retry-After': (r) => r.headers['Retry-After'] !== undefined,
    });
    if (res.headers['Retry-After'] === undefined) {
      retryMissing.add(1, tags('login-bruteforce'));
    }
  } else if (res.status !== 200) {
    // 200 = normal failed-login re-render while still under the limit.
    expectStatus(res, [200], 'login-bruteforce');
  }
  sleep(1);
}

// Legitimate clients logging in. Isolation is asserted only when each VU is
// pinned to its own simulated client IP; on a shared source IP (default,
// staging behind nginx) the attacker's throttle legitimately affects every
// client so we only require a sane, non-5xx outcome.
export function successLogin() {
  const user = cfg.users[__VU % cfg.users.length];
  const res = login(user.username, user.password, 'login-success');
  if (SIMULATE_CLIENT_IP) {
    check(res, {
      'login: legit client isolated from attacker throttle': (r) => r.status !== 429,
    });
    expectStatus(res, [302], 'login-success');
  } else {
    expectStatus(res, [302, 200, 429], 'login-success-shared-ip');
  }
  if (res.status === 302) {
    const dash = http.get(`${BASE_URL}/`, { headers: baseHeaders(), redirects: 0, tags: tags('login-dashboard') });
    expectStatus(dash, [200], 'login-dashboard');
  }
  sleep(1);
}
