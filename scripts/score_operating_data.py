import csv
import json
import math
import random
from collections import defaultdict
from datetime import date, timedelta
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "data"
OUTPUTS = ROOT / "analysis" / "outputs"
RNG = random.Random(20260519)


JOURNEYS = [
    ("JRN001", "Join membership", "Membership", "web", "Growth", 5400, 0.074, 126, 0.74),
    ("JRN002", "Renew membership", "Membership", "web", "Member Services", 7200, 0.192, 98, 0.82),
    ("JRN003", "Upgrade plan", "Membership", "web", "Growth", 3100, 0.114, 74, 0.69),
    ("JRN004", "Request roadside assistance", "Roadside", "app", "Roadside Ops", 8900, 0.438, 38, 0.91),
    ("JRN005", "Manage vehicles", "Roadside", "web", "Member Services", 2400, 0.287, 22, 0.77),
    ("JRN006", "Book hotel", "Travel", "web", "Travel", 4200, 0.061, 182, 0.66),
    ("JRN007", "Request cruise quote", "Travel", "web", "Travel", 1800, 0.047, 460, 0.58),
    ("JRN008", "Insurance quote", "Insurance", "web", "Insurance", 3600, 0.083, 244, 0.63),
    ("JRN009", "Schedule car care", "Automotive", "web", "Car Care", 2100, 0.128, 86, 0.79),
    ("JRN010", "Search discounts", "Discounts", "web", "Partner Marketing", 5000, 0.216, 18, 0.71),
    ("JRN011", "Apply for credit card", "Financial Services", "web", "Financial Services", 1500, 0.039, 310, 0.54),
    ("JRN012", "Shop travel products", "Retail", "web", "Retail", 1950, 0.054, 64, 0.61),
]

DEVICES = [
    ("desktop", 0.38, 1.07),
    ("mobile_web", 0.42, 0.91),
    ("mobile_app", 0.20, 1.16),
]

CHANNELS = [
    ("organic_search", 0.34, 0.98),
    ("paid_search", 0.24, 0.90),
    ("email", 0.18, 1.18),
    ("direct", 0.24, 1.08),
]

FUNNEL_STEPS = {
    "Join membership": ["Plan comparison", "Account setup", "Payment", "Confirmation"],
    "Renew membership": ["Renewal offer", "Member lookup", "Payment", "Confirmation"],
    "Upgrade plan": ["Benefit comparison", "Eligibility check", "Payment", "Confirmation"],
    "Request roadside assistance": ["Identify vehicle", "Confirm location", "Service type", "Dispatch confirmation"],
    "Manage vehicles": ["Sign in", "Vehicle list", "Edit vehicle", "Save profile"],
    "Book hotel": ["Search destination", "Select hotel", "Traveler details", "Booking handoff"],
    "Request cruise quote": ["Browse sailing", "Select itinerary", "Traveler details", "Lead submit"],
    "Insurance quote": ["Quote start", "Coverage details", "Contact details", "Lead submit"],
    "Schedule car care": ["Find location", "Select service", "Choose appointment", "Confirmation"],
    "Search discounts": ["Search offers", "Offer detail", "Partner handoff", "Redemption"],
    "Apply for credit card": ["Offer detail", "Eligibility", "Application handoff", "Submit"],
    "Shop travel products": ["Product detail", "Cart", "Checkout", "Confirmation"],
}

VARIABLES = [
    ("eVar12", "journey_name", "Persistent journey name", "active"),
    ("eVar18", "member_status", "Known member, guest, household associate", "active"),
    ("eVar21", "business_line", "Membership, roadside, travel, insurance, retail", "active"),
    ("eVar32", "auth_state", "Signed in, anonymous, partially matched", "active"),
    ("eVar41", "quote_type", "Lead product type for quote journeys", "review"),
    ("prop9", "page_template", "Template taxonomy for content performance", "active"),
    ("event14", "journey_start", "Journey start counter", "active"),
    ("event22", "journey_complete", "Journey completion counter", "active"),
    ("event31", "lead_submit", "Lead generation completion counter", "active"),
    ("event44", "self_service_success", "Self-service transaction completion", "active"),
    ("event52", "identity_bridge_success", "Cross-domain identity continuity", "review"),
    ("event63", "validation_error", "Release QA validation failure", "active"),
]


def ensure_dirs():
    DATA.mkdir(exist_ok=True)
    OUTPUTS.mkdir(parents=True, exist_ok=True)


def write_csv(path, rows, fieldnames):
    with path.open("w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)


def clamp(value, low, high):
    return max(low, min(high, value))


def build_journeys():
    rows = []
    for journey_id, name, line, surface, owner, base_sessions, conversion, value, trust in JOURNEYS:
        rows.append({
            "journey_id": journey_id,
            "journey_name": name,
            "business_line": line,
            "primary_surface": surface,
            "owner": owner,
            "baseline_daily_sessions": base_sessions,
            "baseline_conversion_rate": round(conversion, 4),
            "value_per_completion": value,
            "measurement_trust_baseline": round(trust, 3),
            "report_suite": f"{line.lower().replace(' ', '_')}_prod",
            "primary_domain": f"{line.lower().replace(' ', '-')}.member-services.example",
        })
    return rows


def build_daily_metrics():
    rows = []
    start = date(2026, 1, 1)
    for day_index in range(120):
        current = start + timedelta(days=day_index)
        weekday_factor = 1.12 if current.weekday() < 5 else 0.84
        seasonal = 1 + math.sin(day_index / 11) * 0.07
        for journey_id, name, line, surface, owner, base_sessions, conversion, value, trust in JOURNEYS:
            for device, device_share, device_conversion in DEVICES:
                if surface == "app" and device != "mobile_app":
                    share = device_share * 0.28
                elif surface != "app" and device == "mobile_app":
                    share = device_share * 0.42
                else:
                    share = device_share
                for channel, channel_share, channel_conversion in CHANNELS:
                    sessions = max(25, int(base_sessions * share * channel_share * weekday_factor * seasonal * RNG.uniform(0.86, 1.16)))
                    start_rate = clamp(0.42 + conversion * 1.6 + RNG.uniform(-0.08, 0.08), 0.24, 0.86)
                    starts = int(sessions * start_rate)
                    conversion_rate = clamp(conversion * device_conversion * channel_conversion * RNG.uniform(0.78, 1.24), 0.008, 0.62)
                    completes = int(starts * conversion_rate)
                    lead_submits = completes if line in {"Travel", "Insurance", "Financial Services"} else int(completes * RNG.uniform(0.04, 0.12))
                    self_service = completes if line in {"Membership", "Roadside", "Automotive", "Discounts", "Retail"} else int(completes * RNG.uniform(0.08, 0.2))
                    revenue_proxy = completes * value
                    calls_deflected = int(self_service * RNG.uniform(0.18, 0.44))
                    bounce_rate = clamp(0.22 + (0.09 if device == "mobile_web" else 0) - conversion * 0.22 + RNG.uniform(-0.04, 0.06), 0.09, 0.58)
                    beacon_loss = clamp((1 - trust) * RNG.uniform(0.035, 0.12) + (0.012 if channel == "paid_search" else 0), 0.002, 0.09)
                    measurement_quality = clamp(trust * 100 - beacon_loss * 100 - RNG.uniform(0, 7), 48, 98)
                    identity_match = clamp(0.91 - (0.13 if "handoff" in " ".join(FUNNEL_STEPS[name]).lower() else 0) - beacon_loss + RNG.uniform(-0.03, 0.04), 0.52, 0.98)
                    rows.append({
                        "date": current.isoformat(),
                        "journey_id": journey_id,
                        "device": device,
                        "marketing_channel": channel,
                        "sessions": sessions,
                        "journey_starts": starts,
                        "journey_completions": completes,
                        "lead_submits": lead_submits,
                        "self_service_successes": self_service,
                        "revenue_proxy": round(revenue_proxy, 2),
                        "calls_deflected": calls_deflected,
                        "bounce_rate": round(bounce_rate, 4),
                        "measurement_quality": round(measurement_quality, 2),
                        "identity_match_rate": round(identity_match, 4),
                        "beacon_loss_rate": round(beacon_loss, 4),
                    })
    return rows


def build_funnel_steps(daily_rows):
    totals = defaultdict(lambda: {"starts": 0, "completes": 0})
    for row in daily_rows:
        totals[row["journey_id"]]["starts"] += int(row["journey_starts"])
        totals[row["journey_id"]]["completes"] += int(row["journey_completions"])

    rows = []
    for journey_id, name, line, surface, owner, base_sessions, conversion, value, trust in JOURNEYS:
        remaining = totals[journey_id]["starts"]
        target = max(totals[journey_id]["completes"], 1)
        steps = FUNNEL_STEPS[name]
        for index, step in enumerate(steps, start=1):
            if index == len(steps):
                exits = max(remaining - target, 0)
                continued = target
            else:
                planned_loss = clamp(0.12 + index * 0.035 + (1 - trust) * 0.12 + RNG.uniform(-0.035, 0.045), 0.04, 0.34)
                exits = int(remaining * planned_loss)
                continued = max(remaining - exits, target)
            rows.append({
                "journey_id": journey_id,
                "step_order": index,
                "step_name": step,
                "entrants": remaining,
                "exits": exits,
                "continuation_rate": round(continued / remaining if remaining else 0, 4),
                "fallout_reason": RNG.choice(["form friction", "identity handoff", "offer clarity", "page performance", "tracking uncertainty"]),
                "instrumentation_status": RNG.choice(["complete", "complete", "needs QA", "schema gap"]),
            })
            remaining = continued
    return rows


def build_schema():
    rows = []
    for journey_id, name, line, surface, owner, base_sessions, conversion, value, trust in JOURNEYS:
        for variable, data_element, purpose, lifecycle in VARIABLES:
            relevance = 1.0
            if variable in {"eVar41", "event31"} and line not in {"Travel", "Insurance", "Financial Services"}:
                relevance = 0.35
            if variable == "event52" and line not in {"Travel", "Insurance", "Financial Services", "Retail"}:
                relevance = 0.5
            required = relevance > 0.45
            coverage = clamp(trust + RNG.uniform(-0.16, 0.12) - (0.12 if lifecycle == "review" else 0), 0.38, 0.99)
            status = "approved"
            if required and coverage < 0.55:
                status = "schema gap"
            elif required and coverage < 0.72:
                status = "needs QA"
            rows.append({
                "journey_id": journey_id,
                "adobe_variable": variable,
                "data_element": data_element,
                "purpose": purpose,
                "required_for_journey": "yes" if required else "no",
                "coverage_rate": round(coverage, 3),
                "lifecycle_status": lifecycle,
                "processing_rule": f"set {variable} from digitalData.{data_element}",
                "launch_rule": f"{name.lower().replace(' ', '_')}_rule",
                "schema_status": status,
            })
    return rows


def build_validation():
    scenarios = [
        ("Join checkout completion", "prod-parity", "event22, eVar12, eVar18", "high"),
        ("Mobile app roadside dispatch", "pre-prod", "event44, eVar32, event52", "critical"),
        ("Travel partner handoff", "pre-prod", "eVar21, event31, event52", "high"),
        ("Insurance lead submission", "pre-prod", "event31, eVar41, eVar18", "high"),
        ("Credit card application handoff", "pre-prod", "event31, event52, eVar32", "high"),
        ("Discount redemption outbound", "prod-parity", "event44, eVar12, prop9", "medium"),
        ("Vehicle profile save", "pre-prod", "event44, eVar18, eVar32", "medium"),
        ("Retail checkout confirmation", "pre-prod", "event22, eVar12, event52", "medium"),
    ]
    rows = []
    for index, (scenario, environment, expected, base_severity) in enumerate(scenarios, start=1):
        for journey_id, name, line, surface, owner, base_sessions, conversion, value, trust in JOURNEYS:
            if any(token.lower() in name.lower() for token in scenario.lower().split()[:2]) or RNG.random() < 0.28:
                observed = RNG.choice([
                    "matches expectation",
                    "missing identity bridge event",
                    "duplicate journey_complete beacon",
                    "stale Launch rule in staging",
                    "report suite mismatch",
                    "required eVar unset on confirmation",
                ])
                severity = "low" if observed == "matches expectation" else base_severity
                rows.append({
                    "scenario_id": f"VAL{index:03d}-{journey_id}",
                    "journey_id": journey_id,
                    "scenario": scenario,
                    "environment": environment,
                    "expected_payload": expected,
                    "observed_result": observed,
                    "severity": severity,
                    "fix_owner": owner if severity != "low" else "Analytics",
                    "release_gate": "pass" if observed == "matches expectation" else "hold",
                })
    return rows


def build_experiments():
    rows = []
    experiment_ideas = [
        ("Plan comparison clarity", "membership pricing table", "self_service_success"),
        ("Roadside location confirmation", "map pin confirmation", "journey_complete"),
        ("Travel search default sorting", "hotel result relevance", "lead_submit"),
        ("Insurance quote field order", "shorter lead form", "lead_submit"),
        ("Discount offer cards", "partner offer hierarchy", "partner_handoff"),
        ("Car care appointment times", "appointment slot grouping", "journey_complete"),
        ("Payment reassurance copy", "checkout trust messaging", "journey_complete"),
    ]
    for idx, (name, variant, metric) in enumerate(experiment_ideas, start=1):
        journey = RNG.choice(JOURNEYS)
        lift = RNG.uniform(-0.018, 0.092)
        confidence = clamp(0.72 + lift * 2.6 + RNG.uniform(-0.08, 0.1), 0.55, 0.99)
        rows.append({
            "experiment_id": f"TGT{idx:03d}",
            "journey_id": journey[0],
            "experiment_name": name,
            "variant": variant,
            "primary_metric": metric,
            "observed_lift": round(lift, 4),
            "confidence": round(confidence, 3),
            "estimated_monthly_value": round(max(lift, 0) * journey[5] * 30 * journey[7], 2),
            "recommendation": "ship" if lift > 0.03 and confidence > 0.82 else "iterate" if lift > 0 else "stop",
        })
    return rows


def build_stakeholder_requests():
    rows = []
    requests = [
        ("Marketing", "Campaign landing performance by journey and channel", "Power BI scorecard"),
        ("Product", "Release QA evidence for Launch changes", "validation packet"),
        ("IT", "Report-suite processing rule exceptions", "defect queue"),
        ("Leadership", "Self-service conversion and call deflection", "monthly readout"),
        ("Travel", "Partner handoff fallout and lead quality", "journey brief"),
        ("Insurance", "Quote-start to lead-submit funnel", "conversion brief"),
    ]
    for idx, (team, question, artifact) in enumerate(requests, start=1):
        rows.append({
            "request_id": f"REQ{idx:03d}",
            "requesting_team": team,
            "business_question": question,
            "expected_artifact": artifact,
            "cadence": RNG.choice(["weekly", "monthly", "release-based"]),
            "status": RNG.choice(["ready", "ready", "needs schema fix", "needs owner decision"]),
        })
    return rows


def analyze(journeys, daily_rows, schema_rows, validation_rows, experiments):
    daily = defaultdict(lambda: defaultdict(float))
    for row in daily_rows:
        key = row["journey_id"]
        daily[key]["sessions"] += int(row["sessions"])
        daily[key]["starts"] += int(row["journey_starts"])
        daily[key]["completes"] += int(row["journey_completions"])
        daily[key]["leads"] += int(row["lead_submits"])
        daily[key]["self_service"] += int(row["self_service_successes"])
        daily[key]["value"] += float(row["revenue_proxy"])
        daily[key]["calls_deflected"] += int(row["calls_deflected"])
        daily[key]["measurement_quality_weighted"] += float(row["measurement_quality"]) * int(row["sessions"])
        daily[key]["identity_weighted"] += float(row["identity_match_rate"]) * int(row["sessions"])
        daily[key]["beacon_loss_weighted"] += float(row["beacon_loss_rate"]) * int(row["sessions"])

    schema = defaultdict(lambda: {"required": 0, "gaps": 0, "qa": 0, "coverage": 0.0})
    for row in schema_rows:
        if row["required_for_journey"] == "yes":
            schema[row["journey_id"]]["required"] += 1
            schema[row["journey_id"]]["coverage"] += float(row["coverage_rate"])
            if row["schema_status"] == "schema gap":
                schema[row["journey_id"]]["gaps"] += 1
            if row["schema_status"] == "needs QA":
                schema[row["journey_id"]]["qa"] += 1

    validation = defaultdict(lambda: {"holds": 0, "critical": 0, "high": 0, "medium": 0, "low": 0})
    for row in validation_rows:
        if row["release_gate"] == "hold":
            validation[row["journey_id"]]["holds"] += 1
            validation[row["journey_id"]][row["severity"]] += 1

    exp_value = defaultdict(float)
    exp_signal = defaultdict(float)
    for row in experiments:
        exp_value[row["journey_id"]] += float(row["estimated_monthly_value"])
        if row["recommendation"] == "ship":
            exp_signal[row["journey_id"]] += 1.0
        elif row["recommendation"] == "iterate":
            exp_signal[row["journey_id"]] += 0.45

    journey_map = {row["journey_id"]: row for row in journeys}
    priority_rows = []
    for journey_id, metrics in daily.items():
        sessions = metrics["sessions"]
        conversion_rate = metrics["completes"] / metrics["starts"] if metrics["starts"] else 0
        measurement_quality = metrics["measurement_quality_weighted"] / sessions
        identity_match = metrics["identity_weighted"] / sessions
        beacon_loss = metrics["beacon_loss_weighted"] / sessions
        schema_required = max(schema[journey_id]["required"], 1)
        schema_gap_rate = (schema[journey_id]["gaps"] + schema[journey_id]["qa"] * 0.55) / schema_required
        validation_risk = validation[journey_id]["holds"] * 6 + validation[journey_id]["critical"] * 8 + validation[journey_id]["high"] * 4
        opportunity = metrics["value"] / 120 + metrics["calls_deflected"] * 9
        trust_penalty = (100 - measurement_quality) * 1.6 + (1 - identity_match) * 70 + schema_gap_rate * 40 + beacon_loss * 110
        experiment_bonus = min(exp_value[journey_id] / 5000, 24) + exp_signal[journey_id] * 3
        priority = opportunity / 1200 + trust_penalty + validation_risk + experiment_bonus
        action = "Fix measurement before scaling dashboard"
        if validation[journey_id]["critical"] > 0:
            action = "Hold release and repair critical beacon issue"
        elif conversion_rate < float(journey_map[journey_id]["baseline_conversion_rate"]) * 0.88:
            action = "Investigate funnel fallout and test experience change"
        elif exp_signal[journey_id] > 0:
            action = "Promote experiment readout into stakeholder decision"
        priority_rows.append({
            "journey_id": journey_id,
            "journey_name": journey_map[journey_id]["journey_name"],
            "business_line": journey_map[journey_id]["business_line"],
            "sessions": int(sessions),
            "conversion_rate": round(conversion_rate, 4),
            "measurement_quality": round(measurement_quality, 2),
            "identity_match_rate": round(identity_match, 4),
            "schema_gap_rate": round(schema_gap_rate, 3),
            "release_hold_count": validation[journey_id]["holds"],
            "estimated_monthly_value": round(opportunity, 2),
            "priority_score": round(priority, 2),
            "recommended_next_move": action,
        })
    priority_rows.sort(key=lambda row: row["priority_score"], reverse=True)

    schema_queue = []
    for journey_id, values in schema.items():
        required = max(values["required"], 1)
        schema_queue.append({
            "journey_id": journey_id,
            "journey_name": journey_map[journey_id]["journey_name"],
            "required_variables": values["required"],
            "schema_gaps": values["gaps"],
            "needs_qa": values["qa"],
            "average_coverage": round(values["coverage"] / required, 3),
            "governance_risk": round((values["gaps"] + values["qa"] * 0.55) / required, 3),
        })
    schema_queue.sort(key=lambda row: row["governance_risk"], reverse=True)

    validation_queue = [row for row in validation_rows if row["release_gate"] == "hold"]
    severity_order = {"critical": 0, "high": 1, "medium": 2, "low": 3}
    validation_queue.sort(key=lambda row: severity_order[row["severity"]])

    summary = {
        "journeys": len(journeys),
        "daily_metric_rows": len(daily_rows),
        "schema_rows": len(schema_rows),
        "validation_scenarios": len(validation_rows),
        "release_holds": len(validation_queue),
        "top_priority_journey": priority_rows[0]["journey_name"],
        "top_priority_score": priority_rows[0]["priority_score"],
        "weighted_measurement_quality": round(sum(float(row["measurement_quality"]) * int(row["sessions"]) for row in daily_rows) / sum(int(row["sessions"]) for row in daily_rows), 2),
        "weighted_identity_match_rate": round(sum(float(row["identity_match_rate"]) * int(row["sessions"]) for row in daily_rows) / sum(int(row["sessions"]) for row in daily_rows), 4),
        "estimated_monthly_value_in_queue": round(sum(row["estimated_monthly_value"] for row in priority_rows[:5]), 2),
    }
    return priority_rows, schema_queue, validation_queue, summary


def main():
    ensure_dirs()
    journeys = build_journeys()
    daily_rows = build_daily_metrics()
    funnel_rows = build_funnel_steps(daily_rows)
    schema_rows = build_schema()
    validation_rows = build_validation()
    experiments = build_experiments()
    stakeholder_requests = build_stakeholder_requests()
    priority_rows, schema_queue, validation_queue, summary = analyze(journeys, daily_rows, schema_rows, validation_rows, experiments)

    write_csv(DATA / "journeys.csv", journeys, list(journeys[0].keys()))
    write_csv(DATA / "daily_journey_metrics.csv", daily_rows, list(daily_rows[0].keys()))
    write_csv(DATA / "funnel_steps.csv", funnel_rows, list(funnel_rows[0].keys()))
    write_csv(DATA / "analytics_schema.csv", schema_rows, list(schema_rows[0].keys()))
    write_csv(DATA / "validation_scenarios.csv", validation_rows, list(validation_rows[0].keys()))
    write_csv(DATA / "target_experiments.csv", experiments, list(experiments[0].keys()))
    write_csv(DATA / "stakeholder_requests.csv", stakeholder_requests, list(stakeholder_requests[0].keys()))

    write_csv(OUTPUTS / "journey_priority_queue.csv", priority_rows, list(priority_rows[0].keys()))
    write_csv(OUTPUTS / "schema_governance_queue.csv", schema_queue, list(schema_queue[0].keys()))
    write_csv(OUTPUTS / "release_validation_queue.csv", validation_queue, list(validation_queue[0].keys()))
    write_csv(OUTPUTS / "experiment_readouts.csv", experiments, list(experiments[0].keys()))
    (OUTPUTS / "summary.json").write_text(json.dumps(summary, indent=2) + "\n")

    print(json.dumps(summary, indent=2))


if __name__ == "__main__":
    main()
