# Data Sources

This folder contains deterministic synthetic data for a member-services digital analytics workbench. The data does not represent any real company, customer, member, web property, mobile app, report suite, or analytics implementation.

The generator in `scripts/score_operating_data.py` uses random seed `20260519`. It models a membership-service organization with web, mobile app, roadside, travel, insurance, discounts, retail, automotive, and financial-service journeys. The structure is based on common digital analytics implementation work: journey events, Adobe-style variables, report-suite readiness, Launch rules, validation scenarios, cross-domain identity continuity, funnel steps, and experiment readouts.

## Files

- `journeys.csv`: 12 digital journeys with business line, owner, baseline traffic, conversion, value, report suite, and primary domain metadata.
- `daily_journey_metrics.csv`: 17,280 synthetic journey x day x device x channel rows over 120 days. Metrics include sessions, starts, completions, leads, self-service successes, value proxy, call deflection, bounce rate, measurement quality, identity match rate, and beacon loss.
- `funnel_steps.csv`: Four-step funnel summaries for each journey, including entrants, exits, continuation rate, fallout reason, and instrumentation status.
- `analytics_schema.csv`: Adobe-style schema requirements with variables, data elements, Launch rules, processing rules, lifecycle status, coverage, and schema status.
- `validation_scenarios.csv`: Pre-production and production-parity QA scenarios with expected payloads, observed debugger-style results, severity, owner, and release gate.
- `target_experiments.csv`: Adobe Target style test readouts with lift, confidence, estimated value, and recommendation.
- `stakeholder_requests.csv`: Standing reporting requests from Marketing, Product, IT, Leadership, Travel, and Insurance.

## Synthetic Assumptions

- Baseline traffic varies by journey from 1,500 to 8,900 daily sessions before device and channel allocation.
- Conversion rates are journey-specific, from low-intent lead journeys near 4 percent to urgent self-service journeys above 40 percent.
- Device and channel effects are applied to conversion and volume, with mobile app stronger for roadside service and email/direct stronger for known-member flows.
- Measurement quality is derived from journey trust baseline, beacon loss, channel risk, and random operational variance.
- Identity match rate is lower for cross-domain and partner handoff journeys.
- Schema gaps are more likely on lower-trust journeys and variables in lifecycle review.
- Release validation failures are seeded to create a realistic mix of passed checks, duplicate beacons, stale Launch rules, report-suite mismatches, unset variables, and missing identity bridge events.
