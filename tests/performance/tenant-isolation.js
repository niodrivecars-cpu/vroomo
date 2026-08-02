import { sleep } from 'k6';
import http from 'k6/http';
import { check } from 'k6';
import { Counter } from 'k6/metrics';
import { BASE_URL, loadConfig, login, expectStatus, baseHeaders, tags, csrfField, withSqliteRetry } from './common.js';

const cfg = loadConfig();

const isolationViolation = new Counter('tenant_isolation_violation');
const booking500 = new Counter('booking_http_500');
let authedA = false;
let authedB = false;

export const options = {
  // k6 resets the cookie jar between iterations by default; each scenario's
  // VU logs in once and keeps that session for all its iterations.
  noCookiesReset: true,
  scenarios: {
    companyA: {
      executor: 'per-vu-iterations',
      vus: 1,
      iterations: 8,
      startTime: '0s',
      exec: 'companyA',
    },
    companyB: {
      executor: 'per-vu-iterations',
      vus: 1,
      iterations: 8,
      startTime: '0s',
      exec: 'companyB',
    },
  },
  thresholds: {
    tenant_isolation_violation: ['count == 0'],
    booking_http_500: ['count == 0'],
    unexpected_http_5xx: ['count == 0'],
    unexpected_http_4xx: ['count == 0'],
  },
};

function firstUser(company) {
  return cfg.users.find((u) => u.company === company);
}

function plates(company) {
  return cfg.vehicles.filter((v) => v.company === company).map((v) => v.plate);
}

function docs(company) {
  return cfg.documents.filter((d) => d.company === company);
}

function vehicles(company) {
  return cfg.vehicles.filter((v) => v.company === company);
}

function drivers(company) {
  return cfg.drivers.filter((d) => d.company === company);
}

function bookingPost(company, vehicleId, driverId, customer, scenario) {
  const page = http.get(`${BASE_URL}/bookings/add/`, {
    headers: baseHeaders(),
    redirects: 0,
    tags: tags('booking-form'),
  });
  const token = csrfField(page.body);
  // Unique day per iteration so a VU never re-books the same vehicle on the
  // same window (which would legitimately produce a conflict form error).
  const d = new Date(Date.now() + (14 + __ITER) * 86400000);
  const pad = (n) => String(n).padStart(2, '0');
  const pickup = `${d.getFullYear()}-${pad(d.getMonth() + 1)}-${pad(d.getDate())}T09:00`;
  return http.post(
    `${BASE_URL}/bookings/add/`,
    {
      vehicle: vehicleId,
      driver: driverId,
      customer_name: customer,
      customer_phone: `0600${company.charCodeAt(0)}42`,
      pickup_date: pickup,
      expected_return: pickup.slice(0, 11) + '11:00',
      total_amount: '80.00',
      deposit: '0.00',
      csrfmiddlewaretoken: token,
    },
    { headers: baseHeaders({ 'X-CSRFToken': token }), redirects: 0, tags: tags(scenario) }
  );
}

function uploadDocument(company, vehicleId, scenario) {
  const page = http.get(`${BASE_URL}/vehicles/${vehicleId}/documents/add/`, {
    headers: baseHeaders(),
    redirects: 0,
    tags: tags('upload-form'),
  });
  const token = csrfField(page.body);
  const pdf = `%PDF-1.4\n1 0 obj<< /Type /Catalog /Pages 2 0 R >>endobj\n` +
    `2 0 obj<< /Type /Pages /Kids [] /Count 0 >>endobj\ntrailer<< /Root 2 0 R >>\n%%EOF\n` +
    `%${company}-${__VU}-${__ITER}`.repeat(64);
  return http.post(
    `${BASE_URL}/vehicles/${vehicleId}/documents/add/`,
    {
      doc_type: 'visite_technique',
      doc_number: `LOAD-${company}-${__ITER}`,
      expiry_date: '2027-12-31',
      csrfmiddlewaretoken: token,
      file: http.file(pdf, `loadtest-${company}-${__ITER}.pdf`, 'application/pdf'),
    },
    { headers: baseHeaders({ 'X-CSRFToken': token }), redirects: 0, tags: tags(scenario) }
  );
}

function assertNoLeak(res, foreignPlates, scenario) {
  const leaked = foreignPlates.filter((p) => res.body.indexOf(p) !== -1);
  check(res, {
    [`${scenario}: no foreign license plates`]: () => leaked.length === 0,
  });
  if (leaked.length) {
    isolationViolation.add(1, tags(scenario));
  }
}

export function companyA() {
  const user = firstUser('A');
  const vs = vehicles('A');
  const ds = drivers('A');
  if (!user || !vs.length || !ds.length) {
    return;
  }
  if (!authedA) {
    login(user.username, user.password, 'iso-a-login');
    authedA = true;
  }

  // A creates a booking on its own vehicle.
  // SQLite ignores select_for_update, so a concurrent POST can lose with a
  // swallowed "database is locked" and re-render the form as a 200; retry that
  // once. The sneak (iso-b-cross-book) is NOT retried: it must keep the 200.
  const book = withSqliteRetry(() =>
    bookingPost('A', vs[__ITER % vs.length].id, ds[0].id, `ISO-A-${__ITER}`, 'iso-a-book')
  );
  if (book.status >= 500) {
    booking500.add(1, tags('iso-a-book'));
  }
  expectStatus(book, [302], 'iso-a-book');

  // A downloads its own document.
  const own = docs('A')[0];
  if (own) {
    const dl = http.get(`${BASE_URL}/documents/${own.id}/download/`, {
      headers: baseHeaders(),
      tags: tags('iso-a-download'),
    });
    expectStatus(dl, [200], 'iso-a-download');
  }

  // A must NOT be able to fetch B's document (expect 404, not content).
  const foreignDoc = docs('B')[0];
  if (foreignDoc) {
    const cross = http.get(`${BASE_URL}/documents/${foreignDoc.id}/download/`, {
      headers: baseHeaders(),
      tags: tags('iso-a-cross-download'),
    });
    expectStatus(cross, [404], 'iso-a-cross-download');
  }

  // A's vehicle list and booking list must never contain B's data.
  const list = http.get(`${BASE_URL}/vehicles/`, { headers: baseHeaders(), tags: tags('iso-a-vehicles') });
  expectStatus(list, [200], 'iso-a-vehicles');
  assertNoLeak(list, plates('B'), 'iso-a-vehicles');

  const bks = http.get(`${BASE_URL}/bookings/`, { headers: baseHeaders(), tags: tags('iso-a-bookings') });
  expectStatus(bks, [200], 'iso-a-bookings');
  if (bks.body.indexOf('ISO-B-') !== -1) {
    isolationViolation.add(1, tags('iso-a-bookings'));
  }
  sleep(1);
}

export function companyB() {
  const user = firstUser('B');
  const vs = vehicles('B');
  const ds = drivers('B');
  if (!user || !vs.length || !ds.length) {
    return;
  }
  if (!authedB) {
    login(user.username, user.password, 'iso-b-login');
    authedB = true;
  }

  // B lists vehicles and must not see A's plates.
  const list = http.get(`${BASE_URL}/vehicles/`, { headers: baseHeaders(), tags: tags('iso-b-vehicles') });
  expectStatus(list, [200], 'iso-b-vehicles');
  assertNoLeak(list, plates('A'), 'iso-b-vehicles');

  // B creates a booking and uploads a document on its own vehicle.
  // Retry the SQLite-lock 200 once; the sneak below is NOT retried.
  const book = withSqliteRetry(() =>
    bookingPost('B', vs[__ITER % vs.length].id, ds[0].id, `ISO-B-${__ITER}`, 'iso-b-book')
  );
  if (book.status >= 500) {
    booking500.add(1, tags('iso-b-book'));
  }
  expectStatus(book, [302], 'iso-b-book');

  // Cap uploads well under the 10/m per-user upload rate limit.
  if (__ITER < 4) {
    const up = uploadDocument('B', vs[0].id, 'iso-b-upload');
    expectStatus(up, [302], 'iso-b-upload');
  }

  // Attempting to book A's vehicle must fail validation (no 302, no 5xx).
  const aVehicle = vehicles('A')[0];
  if (aVehicle) {
    const sneak = bookingPost('B', aVehicle.id, ds[0].id, `SNEAK-${__ITER}`, 'iso-b-cross-book');
    if (sneak.status >= 500) {
      booking500.add(1, tags('iso-b-cross-book'));
    }
    expectStatus(sneak, [200], 'iso-b-cross-book');
  }

  // B's booking list must not contain A's plate.
  const bks = http.get(`${BASE_URL}/bookings/`, { headers: baseHeaders(), tags: tags('iso-b-bookings') });
  expectStatus(bks, [200], 'iso-b-bookings');
  assertNoLeak(bks, plates('A'), 'iso-b-bookings');

  sleep(1);
}
