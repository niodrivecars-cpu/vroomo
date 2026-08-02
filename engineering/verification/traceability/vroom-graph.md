# Vroom — Policy Graph

The end-to-end proof chain for every policy: **Policy → Rule → Invariant →
Test → Evidence → Release**. A live snapshot of how far each policy is proven,
in graph form. Derived from `domain/model/policies.md` + the traceability
snapshot (`verification/traceability/vroom-rc1.md`).

## Chain

```text
P* ──implements──▶ Invariant ──tested by──▶ Test ──verified by──▶ Evidence ──approved by──▶ RC1
```

## Graph

```mermaid
graph LR
  P1[P1 maintenance blocks booking] -->|implements| I1[new invariant 2B.1]
  P2[P2 active-only] -->|implements| I2[new invariant 2B.1]
  P3[P3 effective reserved] -->|implements| B1[B1 exclusivity]
  P4[P4 license valid at pickup] -->|implements| I4[new invariant 2B.1]
  P5[P5 booking end >= start] -->|implements| B3[B3 window validity]
  P6[P6 mileage monotonic] -->|implements| I6[new invariant 2B.1]
  P7[P7 money Decimal non-negative] -->|implements| B4[B4 money]
  P9[P9 violation total] -->|implements| T9[property test]
  P10[P10 overdue derivation] -->|implements| I10[derived-state invariant]
  P11[P11 tenant scope] -->|implements| F1[F1 tenant scoped]
  P12[P12 documents private + expire] -->|implements| F3[F3 signed URLs]
  P13[P13 revoked links stop] -->|implements| F4[F4 revoked links]
  P14[P14 superseded file removed] -->|implements| F5[F5 file hygiene]
  P15[P15 status consistent with bookings] -->|implements| I15[new invariant 2B.1]
  P17[P17 unique plate/CIN] -->|implements| F6[F6 unique plate/CIN]
  P19[P19 violation auto-link] -->|implements| T19[auto-link test]
  P20[P20 no overlapping bookings] -->|implements| B1[B1 exclusivity]
  P21[P21 derived states computed] -->|implements| B5[B5 state machine]

  B1 -->|tested by| T1[k6 sameVehicleBooking + suite]
  B3 -->|tested by| T3[needed 2D]
  B4 -->|tested by| T4[needed 2D]
  B5 -->|tested by| T5[needed 2D]
  F1 -->|tested by| T11[IDOR tests + k6]
  F3 -->|tested by| T12[signed/expired tests]
  F4 -->|tested by| T13[revoke test]
  F6 -->|tested by| T17[model unique tests]
  T9 -->|verified by| E9[RC1 suite]
  T11 -->|verified by| E11[RC1 suite + k6]
  T12 -->|verified by| E12[RC1 suite + k6 dl-*]
  T13 -->|verified by| E13[RC1 suite]
  T17 -->|verified by| E17[RC1 suite]
  T19 -->|verified by| E19[RC1 suite]
  T1 -->|verified by| E1[RC1 k6]
  E1 -->|approved by| R1[RC1]
  E9 -->|approved by| R1
  E11 -->|approved by| R1
  E12 -->|approved by| R1
  E13 -->|approved by| R1
  E17 -->|approved by| R1
  E19 -->|approved by| R1
```

## Read it as
- **Green chain** (B1/B3/B4/B5/F1/F3/F4/F6 + derived-state tests) → proven to
  RC1.
- **Red dotted edge** (`tested by needed 2D`) → owned gap (G1–G8), not silence.
- **Broken `implements` edge** (`new invariant 2B.1`) → Phase 2A validated policy
  still in prose only — this is the release blocker set (P1, P2, P4, P6, P15).
- **Proposed policies** (P8, P16, P18) have no `implements` edge until the
  Decision Engine answers them.

## Invariants referenced
| Invariant | Policies | Tests | Evidence | Status |
|---|---|---|---|---|
| B1 exclusivity | P3, P20 | k6 `sameVehicleBooking`; adjacent-window unit needed (G5) | RC1 k6 | ⚠️ |
| B2 tenant | P11 | IDOR/cross-tenant tests | RC1 suite + k6 | ✅ |
| B3 window validity | P5 | needed (G1) | — | ⚠️ |
| B4 money | P7 | needed (G2) | RC1 suite (pricing) | ⚠️ |
| B5 state machine | P21 | needed (G3) | — | ⚠️ |
| B6 PROTECT | — | needed (G4) | — | ⚠️ |
| F1 tenant scoped | P11 | model tests | RC1 suite | ✅ |
| F2 cross-tenant | P11 | IDOR + k6 | RC1 suite + k6 | ✅ |
| F3 signed URLs | P12 | signed/expired/tampered tests | RC1 suite + k6 `dl-*` | ✅ |
| F4 revoked links | P13 | revoke test | RC1 suite | ✅ |
| F5 file hygiene | P14 | needed (G6) | — | ⚠️ |
| F6 unique plate/CIN | P17 | model tests | RC1 suite | ✅ |
| maintenance-due derived | P15 | needed (G7) | — | ⚠️ |
| violation derived-state | P10 | needed (G8) | — | ⚠️ |
| auto-link behavior | P19 | auto-link test | RC1 suite | ✅ |

Maintained as part of Phase 2B/2C; regenerated from `policies.md` + test
matrices each stage.
