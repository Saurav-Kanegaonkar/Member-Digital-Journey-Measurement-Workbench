# Data Dictionary

| Table | Grain | Purpose |
|---|---|---|
| `journeys.csv` | Journey | Business line, owner, baseline traffic, conversion, value, report suite, and domain metadata. |
| `daily_journey_metrics.csv` | Date x journey x device x channel | Web and app performance, conversion, lead generation, self-service activity, value proxy, call deflection, bounce rate, measurement quality, identity match, and beacon loss. |
| `funnel_steps.csv` | Journey x funnel step | Entrants, exits, continuation rate, fallout reason, and instrumentation status for each journey step. |
| `analytics_schema.csv` | Journey x analytics variable | Adobe-style variable requirements, data elements, processing rules, Launch rules, lifecycle status, coverage, and schema status. |
| `validation_scenarios.csv` | QA scenario x journey | Expected payloads, observed validation results, severity, owner, and release gate for pre-production and production-parity checks. |
| `target_experiments.csv` | Experiment | Adobe Target style experiment readouts with metric, lift, confidence, value, and recommendation. |
| `stakeholder_requests.csv` | Request | Recurring stakeholder questions, expected artifact, cadence, and status. |
| `analysis/outputs/journey_priority_queue.csv` | Journey | Ranked queue combining conversion opportunity, value, measurement trust, schema gap rate, identity risk, validation holds, and experiment evidence. |
| `analysis/outputs/schema_governance_queue.csv` | Journey | Schema coverage, QA need, and governance risk by journey. |
| `analysis/outputs/release_validation_queue.csv` | Validation issue | Release-blocking validation issues sorted by severity. |
| `analysis/outputs/experiment_readouts.csv` | Experiment | Copy of generated experiment readouts for front-end consumption. |
| `analysis/outputs/summary.json` | Artifact | Summary counts and weighted quality measures used by the dashboard header. |
