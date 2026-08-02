# Use Cases

The canonical catalog of **end-to-end business scenarios**. Each use case binds a
scenario to its commands, policies, events, and tests — the traceability chain
`Use Case → Commands → Policies → Events → Tests` closes the loop from a business
activity to proof.

Legend (same as README): ✅ implemented + tested · ⚠️ implemented, unverified ·
🔲 aspirational (no code) · 🧾 decision open.

## UC1 — Create Booking

| | |
|---|---|
| Actor | Staff |
| Commands | CreateBooking |
| Events | BookingCreated |
| Policies | P20 (no overlap), P1 (maintenance), P2 (active only), P3 (derived reserve), P5 (window), P7 (money), P8 (deposit), P15 (status consistency) |
| Tests | B1/B2/B3/B4 guards; k6 `sameVehicleBooking`; 2D for B3/B4 |
| Status | ⚠️ B3–B4 unverified |

## UC2 — Cancel Booking

| | |
|---|---|
| Actor | Staff |
| Commands | CancelBooking |
| Events | BookingCancelled |
| Policies | P3 (reserve window ends), P20 (slot freed) |
| Tests | cancel-before-start guard |
| Status | ⚠️ |

## UC3 — Vehicle Pickup (Start Rental)

| | |
|---|---|
| Actor | Staff |
| Commands | StartRental |
| Events | BookingPickedUp |
| Policies | P4 (license valid at pickup), P3, P6 (pickup_km recorded) |
| Tests | pickup guard; P4 blocked |
| Status | ⚠️ P4 missing |

## UC4 — Vehicle Return

| | |
|---|---|
| Actor | Staff |
| Commands | ReturnVehicle |
| Events | BookingReturned |
| Policies | P3, P6 (mileage never decreases) |
| Tests | return guard; P6 monotonic invariant missing |
| Status | ⚠️ P6 missing |

## UC5 — Extend Booking

| | |
|---|---|
| Actor | Staff |
| Commands | ExtendBooking (🔲 — no command today) |
| Events | BookingExtended (🔲) |
| Policies | P20 (still no overlap), P3 |
| Tests | 2D |
| Status | 🔲 — decision: new command or amend expected_return via CreateBooking guards |

## UC6 — Record Maintenance

| | |
|---|---|
| Actor | Staff |
| Commands | CreateMaintenanceRecord |
| Events | MaintenanceStarted / MaintenanceCompleted (🔲) |
| Policies | P1 (blocks booking), P21 (is_due derived) |
| Tests | `Maintenance.is_due` |
| Status | ⚠️ emissions aspirational |

## UC7 — Set Vehicle Status

| | |
|---|---|
| Actor | Staff |
| Commands | SetVehicleStatus |
| Events | VehicleStatusChanged |
| Policies | P15 (cannot contradict active booking), P21 |
| Tests | 2D — P15 missing |
| Status | ⚠️ P15 missing |

## UC8 — Upload Vehicle Document

| | |
|---|---|
| Actor | Staff |
| Commands | UploadDocument |
| Events | DocumentUploaded |
| Policies | P11 (tenant scope), P14 (superseded file cleanup), P21 (is_expired) |
| Tests | file validators; P14 best-effort cleanup unverified |
| Status | ⚠️ |

## UC9 — Download Vehicle Document

| | |
|---|---|
| Actor | Staff / Document Owner |
| Commands | (service-layer; signed URL flow) |
| Events | DocumentDownloaded |
| Policies | P12 (private + expire), P13 (revoked links stop working) |
| Tests | signed / expired / tampered / revoked |
| Status | ✅ |

## UC10 — Revoke Download Links

| | |
|---|---|
| Actor | Staff / Document Owner |
| Commands | RevokeDownloadLinks |
| Events | DocumentLinksRevoked |
| Policies | P13 |
| Tests | revoke test (token bump) |
| Status | ✅ |

## UC11 — Record Violation

| | |
|---|---|
| Actor | Staff |
| Commands | CreateViolation |
| Events | ViolationRecorded |
| Policies | P9 (total = fine + surcharge), P10 (overdue), P19 (auto-link to booking driver), P11 |
| Tests | total_due, is_overdue, auto-link |
| Status | ✅ |

## UC12 — Mark Violation Paid

| | |
|---|---|
| Actor | Staff / Finance |
| Commands | MarkViolationPaid (🔲) |
| Events | ViolationPaid (🔲) |
| Policies | P10 (overdue means past deadline and **unpaid**) |
| Tests | 2D |
| Status | 🔲 — no payment flow (see "Not yet available" in commands.md) |

## Use Case → Policies → Events → Tests matrix

| UC | Key policy | Key event | Test / evidence |
|---|---|---|---|
| UC1 | P20, P1 | BookingCreated | B1–B4, k6 |
| UC2 | P3 | BookingCancelled | cancel guard |
| UC3 | P4 | BookingPickedUp | pickup guard |
| UC4 | P6 | BookingReturned | return guard + monotonic |
| UC5 | P20 | BookingExtended | 2D |
| UC6 | P1, P21 | MaintenanceStarted (🔲) | is_due |
| UC7 | P15 | VehicleStatusChanged | 2D |
| UC8 | P11, P14 | DocumentUploaded | validators |
| UC9 | P12, P13 | DocumentDownloaded | signed/expired/tampered |
| UC10 | P13 | DocumentLinksRevoked | revoke |
| UC11 | P9, P19 | ViolationRecorded | total_due, auto-link |
| UC12 | P10 | ViolationPaid (🔲) | 2D |

## Rules
1. A use case exists here **before** its views/URLs are built.
2. Every use case must be reachable from at least one command in `commands.md`;
   a scenario with no command is marked 🔲 until one exists.
3. When a policy changes, its use cases are re-validated and the status column is
   updated — never silently.
