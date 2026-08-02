import { sleep } from 'k6';
import http from 'k6/http';
import { check } from 'k6';
import { Counter } from 'k6/metrics';
import { BASE_URL, baseHeaders, tags, ATTACK } from './common.js';
import { bruteForce, successLogin } from './login-rate-limit.js';
import { authDownload, signedDownload } from './document-download.js';
import { distinctBooking, sameVehicleBooking } from './booking-workflow.js';
import { companyA, companyB } from './tenant-isolation.js';

// Scenario exec functions must be visible as exports of this module, so
// re-export the imported workflows.
export { bruteForce, successLogin, authDownload, signedDownload, distinctBooking, sameVehicleBooking, companyA, companyB };

const healthNonOk = new Counter('health_non_200');

// Concurrency smoke test for the v1.0.0-rc1 gate. Not a benchmark: 1-5 VUs
// per workflow over ~3 minutes, validating correctness under concurrency
// (status codes, download integrity, tenant isolation, audit + health) rather
// than throughput or latency.
//
// Run modes (see docs/load-testing.md):
//   default -> concurrency workflows + health. SIMULATE_CLIENT_IP defaults to
//              on, so each VU presents its own client IP and the app must
//              trust the load generator (TRUSTED_PROXY_IPS) for the test.
//   ATTACK=1 -> also exercises login throttling (attacker IP vs legit IPs).
const scenarios = {
  health: { executor: 'constant-vus', vus: 1, duration: '180s', exec: 'healthProbe' },
  authDownloads: { executor: 'per-vu-iterations', vus: 2, iterations: 12, startTime: '0s', exec: 'authDownload' },
  signedDownloads: {
    executor: 'per-vu-iterations',
    vus: 2,
    // Signed links are anonymous, so these requests share the per-IP
    // download_anon_ip rate limit (10/h by default). Keep iterations low
    // enough that a VU never exceeds the limit during the run; the rate
    // limit itself is covered by unit tests and the ATTACK login scenario.
    iterations: 4,
    startTime: '2s',
    exec: 'signedDownload',
  },
  distinctVehicles: { executor: 'per-vu-iterations', vus: 3, iterations: 10, startTime: '5s', exec: 'distinctBooking' },
  sameVehicle: { executor: 'per-vu-iterations', vus: 5, iterations: 1, startTime: '10s', exec: 'sameVehicleBooking' },
  tenantA: { executor: 'per-vu-iterations', vus: 1, iterations: 8, startTime: '0s', exec: 'companyA' },
  tenantB: { executor: 'per-vu-iterations', vus: 1, iterations: 8, startTime: '0s', exec: 'companyB' },
};
if (ATTACK) {
  scenarios.bruteForce = { executor: 'per-vu-iterations', vus: 1, iterations: 40, startTime: '0s', exec: 'bruteForce' };
  scenarios.successLogin = { executor: 'per-vu-iterations', vus: 3, iterations: 3, startTime: '5s', exec: 'successLogin' };
}

export const options = {
  // k6 resets the cookie jar between iterations by default; the workflows log
  // in once per VU and keep that session across their iterations.
  noCookiesReset: true,
  scenarios: scenarios,
  thresholds: {
    // Error budget
    unexpected_http_5xx: ['count == 0'],
    unexpected_http_4xx: ['count == 0'],
    health_non_200: ['count == 0'],
    booking_http_500: ['count == 0'],
    // Download integrity
    download_body_mismatch: ['count == 0'],
    // Exclusive booking invariant: at most one same-vehicle booking may win.
    same_vehicle_booking_success: ['count == 1'],
    // Tenant isolation
    tenant_isolation_violation: ['count == 0'],
    // Login throttle correctness (only present with ATTACK=1)
    login_429_without_retry_after: ['count == 0'],
    // Sanity latency gate, NOT a benchmark: only catches gross hangs.
    http_req_duration: ['p(95) < 5000'],
  },
};

export function healthProbe() {
  const res = http.get(`${BASE_URL}/health/`, { headers: baseHeaders(), tags: tags('health') });
  let ok = res.status === 200;
  check(res, { 'health: HTTP 200': () => ok });
  if (ok) {
    try {
      const body = JSON.parse(res.body);
      ok = body.status === 'ok';
      check(body, { 'health: status ok': () => ok });
    } catch (e) {
      ok = false;
    }
  }
  if (!ok) {
    healthNonOk.add(1, tags('health'));
  }
  sleep(3);
}
