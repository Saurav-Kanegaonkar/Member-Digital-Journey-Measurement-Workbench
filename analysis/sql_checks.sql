-- BigQuery-style checks for the synthetic member digital journey workbench.
-- These queries document the analytical tests behind the static CSV outputs.

-- 1. Journey performance and measurement trust by business line.
select
  j.business_line,
  sum(m.sessions) as sessions,
  safe_divide(sum(m.journey_completions), sum(m.journey_starts)) as conversion_rate,
  avg(m.measurement_quality) as avg_measurement_quality,
  avg(m.identity_match_rate) as avg_identity_match_rate,
  avg(m.beacon_loss_rate) as avg_beacon_loss_rate
from daily_journey_metrics m
join journeys j using (journey_id)
group by 1
order by sessions desc;

-- 2. Schema coverage gaps by journey.
select
  j.journey_name,
  countif(s.required_for_journey = 'yes') as required_variables,
  countif(s.required_for_journey = 'yes' and s.schema_status = 'schema gap') as schema_gaps,
  countif(s.required_for_journey = 'yes' and s.schema_status = 'needs QA') as variables_needing_qa,
  avg(if(s.required_for_journey = 'yes', s.coverage_rate, null)) as average_coverage
from analytics_schema s
join journeys j using (journey_id)
group by 1
order by schema_gaps desc, variables_needing_qa desc;

-- 3. Release-blocking validation issues.
select
  journey_id,
  scenario,
  environment,
  expected_payload,
  observed_result,
  severity,
  fix_owner
from validation_scenarios
where release_gate = 'hold'
order by
  case severity
    when 'critical' then 1
    when 'high' then 2
    when 'medium' then 3
    else 4
  end,
  journey_id;

-- 4. Funnel fallout ranked by lost entrants.
select
  j.journey_name,
  f.step_order,
  f.step_name,
  f.entrants,
  f.exits,
  f.continuation_rate,
  f.fallout_reason,
  f.instrumentation_status
from funnel_steps f
join journeys j using (journey_id)
order by f.exits desc
limit 25;

-- 5. Experiment readouts ready for stakeholder decision.
select
  e.experiment_id,
  j.journey_name,
  e.experiment_name,
  e.primary_metric,
  e.observed_lift,
  e.confidence,
  e.estimated_monthly_value,
  e.recommendation
from target_experiments e
join journeys j using (journey_id)
where e.confidence >= 0.80
order by e.estimated_monthly_value desc;
