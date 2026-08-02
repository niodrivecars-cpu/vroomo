# Load Testing — References

The authoritative source for the framework is `docs/load-testing.md` and the
scripts in `tests/performance/`. Secondary references:

- k6 docs: https://grafana.com/docs/k6/
- Thresholds reference: https://grafana.com/docs/k6/latest/using-k6/thresholds/
- Checks reference: https://grafana.com/docs/k6/latest/using-k6/checks/
- Scenarios (ramping-vus): https://grafana.com/docs/k6/latest/using-k6/scenarios/
- TOML vs JavaScript config rationale: chosen JS (`common.js`) for testability
  with `withSqliteRetry`/`isSqliteLockArtifact` helpers.
- JSON output: k6 `--summary-export` used to keep summaries in
  `docs/releases/v1.0.0-rc1/`.
