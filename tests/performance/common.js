import http from 'k6/http';
import { check, sleep } from 'k6';
import { Counter } from 'k6/metrics';

// Base URL of the application under test.
export const BASE_URL = (__ENV.BASE_URL || 'http://127.0.0.1:8000').replace(/\/+$/, '');

// When enabled, every VU presents a distinct X-Forwarded-For header so the
// login throttle and tenant workflows are exercised per resolved client IP.
// This is honored only when the load generator's address is in
// TRUSTED_PROXY_IPS (see docs/load-testing.md) — it works directly against a
// dev server (TRUSTED_PROXY_IPS=127.0.0.1) and through nginx when the load
// generator's egress IP is trusted for the test window. Defaults to on
// because authenticated workflows cannot be load-tested from a single source
// IP without tripping the per-IP login throttle.
export const SIMULATE_CLIENT_IP = (__ENV.SIMULATE_CLIENT_IP || '1') === '1';

// Only relevant to smoke.js: run the login brute-force scenarios (off by
// default because on a shared source IP they would throttle every scenario
// that logs in).
export const ATTACK = (__ENV.ATTACK || '0') === '1';

const CONFIG_FILE = __ENV.LOADTEST_CONFIG || 'loadtest_config.json';

export const unexpected5xx = new Counter('unexpected_http_5xx');
export const unexpected4xx = new Counter('unexpected_http_4xx');

export function loadConfig() {
  return JSON.parse(open(CONFIG_FILE));
}

export function tags(scenario) {
  return { scenario: scenario };
}

export function userAgent() {
  return 'k6-vroom-smoke/1.0';
}

export function baseHeaders(extra) {
  const headers = {
    'User-Agent': userAgent(),
    'Accept': 'text/html,application/json;q=0.9,*/*;q=0.8',
  };
  if (SIMULATE_CLIENT_IP) {
    const vu = __VU || 1;
    // Valid 4-octet IPv4, distinct per VU (10.0.0.1..255, 10.0.1.0..255, ...).
    // django-ratelimit parses the resolved IP as an ipaddress.Network, so an
    // abbreviated value would make every ip-keyed limit raise a 500.
    headers['X-Forwarded-For'] = `10.0.${Math.floor(vu / 256)}.${vu % 256}`;
  }
  return Object.assign(headers, extra);
}

// GET the login page and return the CSRF token for this session.
export function csrfToken() {
  const res = http.get(`${BASE_URL}/accounts/login/`, { headers: baseHeaders(), redirects: 0 });
  const token = csrfField(res.body);
  return { token: token, status: res.status };
}

// Perform a login POST. 302 = success, 200 = failed attempt re-render,
// 429 = throttled.
export function login(username, password, scenario) {
  const csrf = csrfToken();
  return http.post(
    `${BASE_URL}/accounts/login/`,
    {
      username: username,
      password: password,
      csrfmiddlewaretoken: csrf.token,
      next: '/',
    },
    { headers: baseHeaders({ 'X-CSRFToken': csrf.token }), redirects: 0, tags: tags(scenario) }
  );
}

// Verify a response's status against an expected set and tally unexpected
// 4xx/5xx responses into the global error-budget counters.
export function expectStatus(res, expected, scenario) {
  const ok = expected.indexOf(res.status) !== -1;
  check(res, {
    [`${scenario}: status ${expected.join('/')}`]: () => ok,
  });
  if (res.status >= 500) {
    unexpected5xx.add(1, tags(scenario));
  } else if (res.status >= 400 && !ok) {
    unexpected4xx.add(1, tags(scenario));
  }
  return ok;
}

// A booking POST that returns 200 with no rendered form error is the
// SQLite/dev signature of the swallowed OperationalError in booking_create:
// SQLite ignores select_for_update, so concurrent attempts serialize on the
// whole database and the loser surfaces as "database is locked", which the
// view swallows and re-renders the (valid) form as a 200. Genuine conflicts
// and validation errors always render the error block (django-bootstrap5
// field_errors.html -> <div class="invalid-feedback d-block">), so its
// absence means the request never reached the save. Postgres never hits this
// path.
export function isSqliteLockArtifact(res) {
  return res.status === 200 && res.body.indexOf('invalid-feedback') === -1;
}

// Re-run a request function when it hit the SQLite lock path. Use only for
// POSTs that are expected to succeed with a 302; never for requests that
// legitimately return a 200 (conflict / cross-tenant checks). SQLite
// serializes writes across the whole database, so a losing request retries
// after a short pause that lets the winner's transaction commit.
export function withSqliteRetry(fn, attempts = 3) {
  let res = fn();
  for (let i = 1; i < attempts && isSqliteLockArtifact(res); i++) {
    sleep(0.25);
    res = fn();
  }
  return res;
}

// Extract a hidden form field value from rendered HTML (attribute-order
// independent, e.g. Django's csrfmiddlewaretoken input).
export function csrfField(html) {
  const tag = html.match(/<input[^>]*name=["']csrfmiddlewaretoken["'][^>]*>/);
  if (!tag) {
    return '';
  }
  const value = tag[0].match(/value=["']([^"']*)["']/);
  return value ? value[1] : '';
}
