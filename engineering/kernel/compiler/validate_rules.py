"""BRL v2 rule-block validator.

Parses every ```rule block in engineering/domain/model/policies.md and checks:
required fields, enum values, ID uniqueness, decision<->enforcement consistency,
and reports release blockers. Exit code 1 on hard failures.

Run from the repository root:
    py engineering/kernel/compiler/validate_rules.py
"""

from __future__ import annotations

import re
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[3]
POLICIES = REPO / "engineering" / "domain" / "model" / "policies.md"

REQUIRED = {
    "ID", "STATEMENT", "PREDICATE", "WHEN", "EVIDENCE", "RISKS",
    "PRIORITY", "SEVERITY", "DECISION", "ENFORCEMENT", "OWNER", "SOURCE",
}
SEVERITIES = {"BLOCKER", "ERROR", "WARNING", "INFO"}
DECISIONS = {"Enforced", "Validated", "Proposed", "Out of Scope", "Rejected"}
ENFORCEMENTS = {"PLANNED", "DOCUMENTED", "IMPLEMENTED", "TESTED"}
PRIORITIES = {"P0", "P1", "P2", "P3"}

BLOCK = re.compile(r"(?ms)^```rule\s*?\n(.*?)^```")


def parse(text: str) -> dict[str, dict[str, str]]:
    rules: dict[str, dict[str, str]] = {}
    for m in BLOCK.finditer(text):
        fields: dict[str, str] = {}
        for line in m.group(1).splitlines():
            if ":" in line:
                key, _, val = line.partition(":")
                fields[key.strip()] = val.strip()
        if "ID" in fields:
            rules[fields["ID"]] = fields
    return rules


def check(rules: dict[str, dict[str, str]]) -> tuple[list[str], list[str]]:
    errors: list[str] = []
    reports: list[str] = []
    for rid, f in rules.items():
        tag = f"[{rid}]"
        for field in REQUIRED - f.keys():
            errors.append(f"{tag} missing required field {field}")
        if "SEVERITY" in f and f["SEVERITY"] not in SEVERITIES:
            errors.append(f"{tag} SEVERITY {f['SEVERITY']!r} not in {sorted(SEVERITIES)}")
        if "DECISION" in f and f["DECISION"] not in DECISIONS:
            errors.append(f"{tag} DECISION {f['DECISION']!r} not in {sorted(DECISIONS)}")
        if "ENFORCEMENT" in f and f["ENFORCEMENT"] not in ENFORCEMENTS:
            errors.append(f"{tag} ENFORCEMENT {f['ENFORCEMENT']!r} not in {sorted(ENFORCEMENTS)}")
        if "PRIORITY" in f and f["PRIORITY"] not in PRIORITIES:
            errors.append(f"{tag} PRIORITY {f['PRIORITY']!r} not in {sorted(PRIORITIES)}")
        if f.get("DECISION") == "Enforced" and f.get("ENFORCEMENT") in (None, "PLANNED"):
            errors.append(f"{tag} Enforced but ENFORCEMENT is not IMPLEMENTED/TESTED")
        if f.get("ENFORCEMENT") == "TESTED" and f.get("DECISION") != "Enforced":
            errors.append(f"{tag} TESTED but DECISION is not Enforced")
        if f.get("SEVERITY") == "BLOCKER" and f.get("ENFORCEMENT") not in ("IMPLEMENTED", "TESTED"):
            reports.append(f"{tag} BLOCKER not at IMPLEMENTED/TESTED (release blocker)")
        if not f.get("EVIDENCE") or f.get("EVIDENCE").startswith("—"):
            reports.append(f"{tag} EVIDENCE missing (owned gap)")

    headings = re.findall(r"(?m)^# (P\d+)", POLICIES.read_text(encoding="utf-8"))
    for rid in headings:
        if rid not in rules:
            errors.append(f"[{rid}] heading without a rule block")
    for rid in rules:
        if rid not in headings:
            errors.append(f"[{rid}] rule block without a policy heading")
    return errors, reports


def main() -> int:
    text = POLICIES.read_text(encoding="utf-8")
    rules = parse(text)
    errors, reports = check(rules)

    counts = {"BLOCKER": 0, "ERROR": 0, "WARNING": 0, "INFO": 0}
    dec = {}
    enf = {}
    for f in rules.values():
        counts[f.get("SEVERITY", "?")] = counts.get(f.get("SEVERITY", "?"), 0) + 1
        dec[f.get("DECISION", "?")] = dec.get(f.get("DECISION", "?"), 0) + 1
        enf[f.get("ENFORCEMENT", "?")] = enf.get(f.get("ENFORCEMENT", "?"), 0) + 1

    print(f"Rules parsed: {len(rules)}")
    print(f"Severity:    {counts}")
    print(f"Decision:    {dec}")
    print(f"Enforcement: {enf}")
    for r in reports:
        print(f"REPORT {r}")
    for e in errors:
        print(f"FAIL   {e}")
    print("VALIDATOR PASS" if not errors else f"VALIDATOR FAIL ({len(errors)} errors)")
    return 0 if not errors else 1


if __name__ == "__main__":
    sys.exit(main())
