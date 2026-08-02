# Booking Knowledge

What we know about the booking domain in Vroom — reserving vehicles for drivers
over time windows.

## Core rule
A vehicle cannot be booked for a window that overlaps an existing booking of the
same vehicle. Enforced check-then-insert; proven under load (exactly one success
per same-vehicle window under concurrent VUs).

## Shape
- Booking: vehicle, driver, company, pickup/return window, amount, status.
- Exclusivity window is per vehicle + company scope.
- Violations can be auto-linked to the driver from an active booking.

## Load-testing model
- Day-bands are computed per-VU (`40 + __VU * ITERATIONS + __ITER`) to keep
  conflict space distinct in smoke tests; `sameVehicleBooking` deliberately
  forces contention to prove the exclusivity guard.
