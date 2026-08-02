import { sleep } from 'k6';
import http from 'k6/http';
import { check } from 'k6';
import { Counter } from 'k6/metrics';
import { BASE_URL, loadConfig, login, expectStatus, baseHeaders, tags } from './common.js';

const cfg = loadConfig();

const integrityMismatch = new Counter('download_body_mismatch');

export const options = {
  // k6 resets the cookie jar between iterations by default; the VUs log in
  // once and keep that session for all their iterations.
  noCookiesReset: true,
  scenarios: {
    authDownloads: {
      executor: 'per-vu-iterations',
      vus: 2,
      // The user is picked via the global __VU id, which shifts when other
      // scenarios (e.g. ATTACK=1) change VU numbering; worst case both VUs
      // land on the same user. Cap iterations so 2 VUs * N stays under
      // download_per_user (20/h): N=9 gives 18, leaving margin for any
      // session/auth requests that increment the same key.
      iterations: 9,
      startTime: '0s',
      exec: 'authDownload',
    },
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
  },
  thresholds: {
    download_body_mismatch: ['count == 0'],
    unexpected_http_5xx: ['count == 0'],
    unexpected_http_4xx: ['count == 0'],
  },
};

function ownDocs(company) {
  return cfg.documents.filter((d) => d.company === company);
}

function otherCompanyDocs(company) {
  return cfg.documents.filter((d) => d.company !== company);
}

let authed = false;

// Session-authenticated download: success must return the exact seeded file
// bytes (no truncation/corruption), and a cross-tenant document id must 404.
export function authDownload() {
  const user = cfg.users[__VU % cfg.users.length];
  const docs = ownDocs(user.company);
  if (!docs.length) {
    return;
  }
  if (!authed) {
    login(user.username, user.password, 'dl-auth-login');
    authed = true;
  }
  const doc = docs[__ITER % docs.length];
  const res = http.get(`${BASE_URL}/documents/${doc.id}/download/`, {
    headers: baseHeaders(),
    tags: tags('dl-auth'),
  });
  if (res.status === 200) {
    verifyIntegrity(res, doc, 'dl-auth');
  } else {
    expectStatus(res, [200], 'dl-auth');
  }

  const other = otherCompanyDocs(user.company)[0];
  if (other) {
    const cross = http.get(`${BASE_URL}/documents/${other.id}/download/`, {
      headers: baseHeaders(),
      tags: tags('dl-cross-tenant'),
    });
    expectStatus(cross, [404], 'dl-cross-tenant');
  }
  sleep(1);
}

// Signed-URL download (anonymous): valid token streams the full file, expired
// and tampered tokens are both rejected with 403.
export function signedDownload() {
  const docs = cfg.documents;
  const doc = docs[__ITER % docs.length];

  const ok = http.get(`${BASE_URL}${doc.signed_url}`, {
    headers: baseHeaders(),
    tags: tags('dl-signed'),
  });
  if (ok.status === 200) {
    verifyIntegrity(ok, doc, 'dl-signed');
  } else {
    expectStatus(ok, [200], 'dl-signed');
  }

  const expired = http.get(`${BASE_URL}${doc.expired_signed_url}`, {
    headers: baseHeaders(),
    tags: tags('dl-signed-expired'),
  });
  expectStatus(expired, [403], 'dl-signed-expired');

  const tampered = http.get(`${BASE_URL}${doc.tampered_signed_url}`, {
    headers: baseHeaders(),
    tags: tags('dl-signed-tampered'),
  });
  expectStatus(tampered, [403], 'dl-signed-tampered');

  sleep(1);
}

function verifyIntegrity(res, doc, scenario) {
  const sizeOk = res.body.length === doc.size;
  const magicOk = res.body.slice(0, 5) === '%PDF-';
  check(res, {
    [`${scenario}: full body length`]: () => sizeOk,
    [`${scenario}: pdf magic`]: () => magicOk,
  });
  if (!sizeOk || !magicOk) {
    integrityMismatch.add(1, tags(scenario));
  }
}
