import { sleep } from 'k6';
import http from 'k6/http';
import { check } from 'k6';
import { Counter } from 'k6/metrics';
import { BASE_URL, loadConfig, login, expectStatus, baseHeaders, tags, csrfField, withSqliteRetry } from './common.js';

const cfg = loadConfig();

const ITERATIONS = 10;
const sameVehicleSuccess = new Counter('same_vehicle_booking_success');
const booking500 = new Counter('booking_http_500');
let authed = false;
let authedSame = false;

export const options = {
  // k6 resets the cookie jar between iterations by default; each scenario's
  // VUs log in once and keep that session for all their iterations.
  noCookiesReset: true,
  scenarios: {
    distinctVehicles: {
      executor: 'per-vu-iterations',
      vus: 3,
      iterations: ITERATIONS,
      startTime: '0s',
      exec: 'distinctBooking',
    },
    sameVehicle: {
      executor: 'per-vu-iterations',
      vus: 5,
      iterations: 1,
      startTime: '5s',
      exec: 'sameVehicleBooking',
    },
  },
  thresholds: {
    same_vehicle_booking_success: ['count == 1'],
    booking_http_500: ['count == 0'],
    unexpected_http_5xx: ['count == 0'],
    unexpected_http_4xx: ['count == 0'],
  },
};

// datetime-local value a full dayOffset in the future at the given hour.
function dt(dayOffset, hour) {
  const d = new Date(Date.now() + dayOffset * 86400000);
  const pad = (n) => String(n).padStart(2, '0');
  return `${d.getFullYear()}-${pad(d.getMonth() + 1)}-${pad(d.getDate())}T${pad(hour)}:00`;
}

function bookingFormCsrf() {
  const page = http.get(`${BASE_URL}/bookings/add/`, {
    headers: baseHeaders(),
    redirects: 0,
    tags: tags('booking-form'),
  });
  return csrfField(page.body);
}

function postBooking(vehicleId, driverId, customer, phone, pickup, ret, amount, scenario) {
  const token = bookingFormCsrf();
  return http.post(
    `${BASE_URL}/bookings/add/`,
    {
      vehicle: vehicleId,
      driver: driverId,
      customer_name: customer,
      customer_phone: phone,
      pickup_date: pickup,
      expected_return: ret,
      total_amount: amount,
      deposit: '0.00',
      notes: 'k6 smoke',
      csrfmiddlewaretoken: token,
    },
    { headers: baseHeaders({ 'X-CSRFToken': token }), redirects: 0, tags: tags(scenario) }
  );
}

// Concurrent bookings across different vehicles. Every (vehicle, day) pair is
// unique per run, so every POST is expected to succeed with a 302.
//
// IMPORTANT: in the full smoke run __VU is the *global* VU id across all
// scenarios (not 1..vus for this executor), so a slot derived from
// __VU * ITERATIONS lands in unpredictable day ranges and can collide with the
// tenantA/B windows (days 14-21) or the same-vehicle race (day 30). Booking
// days are therefore pinned to a dedicated band starting at day 40, with each
// VU owning its own non-overlapping day range (so even two VUs that map to the
// same vehicle can never share a day), and the vehicle is derived from __VU
// alone.
export function distinctBooking() {
  const user = cfg.users[__VU % cfg.users.length];
  const vehicles = cfg.vehicles.filter((v) => v.company === user.company);
  const drivers = cfg.drivers.filter((d) => d.company === user.company);
  if (!vehicles.length || !drivers.length) {
    return;
  }
  if (!authed) {
    login(user.username, user.password, 'booking-login');
    authed = true;
  }
  const day = 40 + __VU * ITERATIONS + __ITER;
  const hour = 9 + (__ITER % 8);
  const pickup = dt(day + 1, hour);
  const ret = dt(day + 1, hour + 2);
  // SQLite ignores select_for_update, so a concurrent POST can lose with a
  // swallowed "database is locked" and re-render the form as a 200. That 200
  // has no error markup, so retry it once; the day band is per-VU and unique,
  // so a retry cannot legitimately conflict.
  const res = withSqliteRetry(() =>
    postBooking(
      vehicles[__VU % vehicles.length].id,
      drivers[__ITER % drivers.length].id,
      `Loadtest ${user.company} ${__VU}-${__ITER}`,
      `0600000${__VU}${__ITER}`,
      pickup,
      ret,
      '120.00',
      'booking-create'
    )
  );
  if (res.status >= 500) {
    booking500.add(1, tags('booking-create'));
  }
  expectStatus(res, [302], 'booking-create');
  sleep(1);
}

// Simultaneous attempts to book the SAME vehicle for the SAME window. Every
// VU logs in as company A's first user and targets company A's first vehicle,
// so all five requests race on one (vehicle, window) pair. The view enforces
// exclusivity with a check-then-insert, so exactly one request may succeed;
// more than one success means the guard is not atomic under concurrency and
// the smoke test fails. Note: each scenario keeps its own auth flag because
// a VU may be logged in as a different company's user from distinctBooking.
export function sameVehicleBooking() {
  const user = cfg.users.find((u) => u.company === 'A');
  const vehicles = cfg.vehicles.filter((v) => v.company === 'A');
  const drivers = cfg.drivers.filter((d) => d.company === 'A');
  if (!user || !vehicles.length || !drivers.length) {
    return;
  }
  if (!authedSame) {
    login(user.username, user.password, 'booking-login');
    authedSame = true;
  }
  const res = postBooking(
    vehicles[0].id,
    drivers[0].id,
    `SameVeh A ${__VU}`,
    `0600000${__VU}`,
    dt(30, 9),
    dt(30, 11),
    '99.00',
    'booking-same-vehicle'
  );
  if (res.status === 302) {
    sameVehicleSuccess.add(1, tags('booking-same-vehicle'));
  } else if (res.status === 200) {
    check(res, {
      'booking: loser renders conflict form error': () => true,
    });
  } else if (res.status >= 500) {
    booking500.add(1, tags('booking-same-vehicle'));
  }
  sleep(1);
}
