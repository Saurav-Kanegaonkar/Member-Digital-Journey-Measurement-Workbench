const DATASETS = {
  summary: "analysis/outputs/summary.json",
  priority: "analysis/outputs/journey_priority_queue.csv",
  schema: "analysis/outputs/schema_governance_queue.csv",
  validation: "analysis/outputs/release_validation_queue.csv",
  experiments: "analysis/outputs/experiment_readouts.csv",
  funnel: "data/funnel_steps.csv",
  requests: "data/stakeholder_requests.csv",
};

const numberFormatter = new Intl.NumberFormat("en-US");
const currencyFormatter = new Intl.NumberFormat("en-US", {
  style: "currency",
  currency: "USD",
  maximumFractionDigits: 0,
});

function parseCSV(text) {
  const rows = [];
  const lines = text.trim().split(/\r?\n/);
  const headers = lines.shift().split(",");

  for (const line of lines) {
    const cells = [];
    let value = "";
    let quoted = false;
    for (let index = 0; index < line.length; index += 1) {
      const char = line[index];
      if (char === '"') {
        quoted = !quoted;
      } else if (char === "," && !quoted) {
        cells.push(value);
        value = "";
      } else {
        value += char;
      }
    }
    cells.push(value);
    rows.push(Object.fromEntries(headers.map((header, index) => [header, cells[index] ?? ""])));
  }

  return rows;
}

async function loadData() {
  const [summary, priority, schema, validation, experiments, funnel, requests] = await Promise.all([
    fetch(DATASETS.summary).then((response) => response.json()),
    fetch(DATASETS.priority).then((response) => response.text()).then(parseCSV),
    fetch(DATASETS.schema).then((response) => response.text()).then(parseCSV),
    fetch(DATASETS.validation).then((response) => response.text()).then(parseCSV),
    fetch(DATASETS.experiments).then((response) => response.text()).then(parseCSV),
    fetch(DATASETS.funnel).then((response) => response.text()).then(parseCSV),
    fetch(DATASETS.requests).then((response) => response.text()).then(parseCSV),
  ]);

  return { summary, priority, schema, validation, experiments, funnel, requests };
}

function asPercent(value, digits = 1) {
  return `${(Number(value) * 100).toFixed(digits)}%`;
}

function byNumber(field, direction = "desc") {
  return (a, b) => {
    const diff = Number(a[field]) - Number(b[field]);
    return direction === "desc" ? -diff : diff;
  };
}

function groupBy(rows, field) {
  return rows.reduce((groups, row) => {
    const key = row[field];
    groups[key] = groups[key] || [];
    groups[key].push(row);
    return groups;
  }, {});
}

function el(tag, className, content) {
  const node = document.createElement(tag);
  if (className) node.className = className;
  if (content !== undefined) node.innerHTML = content;
  return node;
}

function renderKpis(data) {
  const top = data.priority[0];
  const kpis = [
    ["Journeys measured", data.summary.journeys, "web, app, and partner handoffs"],
    ["Weighted measurement quality", `${data.summary.weighted_measurement_quality}%`, "across synthetic beacon volume"],
    ["Identity match rate", asPercent(data.summary.weighted_identity_match_rate), "cross-domain visitor continuity"],
    ["Release holds", data.summary.release_holds, "validation scenarios needing repair"],
    ["Top opportunity", currencyFormatter.format(top.estimated_monthly_value), top.journey_name],
  ];

  const container = document.querySelector("#kpis");
  container.replaceChildren(...kpis.map(([label, value, detail]) => {
    const card = el("article", "kpi");
    card.innerHTML = `<span>${label}</span><strong>${value}</strong><em>${detail}</em>`;
    return card;
  }));
}

function renderPriority(data) {
  const tbody = document.querySelector("#priority-table tbody");
  tbody.replaceChildren(...data.priority.slice(0, 7).map((row, index) => {
    const tr = document.createElement("tr");
    tr.innerHTML = `
      <td><b>${index + 1}</b></td>
      <td><strong>${row.journey_name}</strong><span>${row.business_line}</span></td>
      <td>${numberFormatter.format(row.sessions)}</td>
      <td>${asPercent(row.conversion_rate)}</td>
      <td>${row.measurement_quality}%</td>
      <td>${row.release_hold_count}</td>
      <td>${currencyFormatter.format(row.estimated_monthly_value)}</td>
      <td>${row.recommended_next_move}</td>
    `;
    return tr;
  }));

  const opportunity = document.querySelector("#opportunity-bars");
  const maxValue = Math.max(...data.priority.slice(0, 7).map((row) => Number(row.estimated_monthly_value)));
  opportunity.replaceChildren(...data.priority.slice(0, 7).map((row) => {
    const bar = el("div", "bar-row");
    const width = Math.max(8, (Number(row.estimated_monthly_value) / maxValue) * 100);
    bar.innerHTML = `
      <div>
        <span>${row.journey_name}</span>
        <strong>${currencyFormatter.format(row.estimated_monthly_value)}</strong>
      </div>
      <i style="width:${width}%"></i>
    `;
    return bar;
  }));
}

function renderFunnel(data) {
  const topJourney = data.priority[0].journey_id;
  const rows = data.funnel.filter((row) => row.journey_id === topJourney).sort(byNumber("step_order", "asc"));
  const firstEntrants = Number(rows[0].entrants);
  const container = document.querySelector("#funnel");
  container.replaceChildren(...rows.map((row) => {
    const width = Math.max(8, (Number(row.entrants) / firstEntrants) * 100);
    const card = el("article", "funnel-step");
    card.innerHTML = `
      <div>
        <span>Step ${row.step_order}</span>
        <strong>${row.step_name}</strong>
        <em>${row.fallout_reason}</em>
      </div>
      <div class="funnel-track"><i style="width:${width}%"></i></div>
      <small>${numberFormatter.format(row.entrants)} entrants, ${asPercent(row.continuation_rate)} continued</small>
    `;
    return card;
  }));
}

function renderSchema(data) {
  const tbody = document.querySelector("#schema-table tbody");
  tbody.replaceChildren(...data.schema.slice(0, 8).map((row) => {
    const risk = Number(row.governance_risk);
    const level = risk > 0.4 ? "High" : risk > 0.2 ? "Watch" : "Ready";
    const tr = document.createElement("tr");
    tr.innerHTML = `
      <td><strong>${row.journey_name}</strong></td>
      <td>${row.required_variables}</td>
      <td>${row.schema_gaps}</td>
      <td>${row.needs_qa}</td>
      <td>${asPercent(row.average_coverage)}</td>
      <td><span class="status ${level.toLowerCase()}">${level}</span></td>
    `;
    return tr;
  }));

  const health = document.querySelector("#schema-health");
  const buckets = [
    ["Approved or complete", data.schema.filter((row) => Number(row.governance_risk) <= 0.2).length],
    ["Needs QA", data.schema.filter((row) => Number(row.governance_risk) > 0.2 && Number(row.governance_risk) <= 0.4).length],
    ["Schema gap", data.schema.filter((row) => Number(row.governance_risk) > 0.4).length],
  ];
  health.replaceChildren(...buckets.map(([label, value]) => {
    const item = el("article", "mini-metric");
    item.innerHTML = `<span>${label}</span><strong>${value}</strong>`;
    return item;
  }));
}

function renderValidation(data) {
  const tbody = document.querySelector("#validation-table tbody");
  tbody.replaceChildren(...data.validation.slice(0, 9).map((row) => {
    const severity = row.severity.toLowerCase();
    const tr = document.createElement("tr");
    tr.innerHTML = `
      <td><strong>${row.scenario}</strong><span>${row.environment}</span></td>
      <td>${row.expected_payload}</td>
      <td>${row.observed_result}</td>
      <td><span class="status ${severity}">${row.severity}</span></td>
      <td>${row.fix_owner}</td>
    `;
    return tr;
  }));

  const experiments = document.querySelector("#experiments");
  experiments.replaceChildren(...data.experiments.sort(byNumber("estimated_monthly_value")).slice(0, 5).map((row) => {
    const lift = Number(row.observed_lift);
    const card = el("article", "experiment");
    card.innerHTML = `
      <span>${row.experiment_id}</span>
      <strong>${row.experiment_name}</strong>
      <p>${row.variant}</p>
      <div>
        <b>${asPercent(lift, 2)} lift</b>
        <em>${asPercent(row.confidence)} confidence</em>
      </div>
      <small>${currencyFormatter.format(row.estimated_monthly_value)} monthly value, ${row.recommendation}</small>
    `;
    return card;
  }));
}

function renderRequests(data) {
  const requests = document.querySelector("#requests");
  requests.replaceChildren(...data.requests.map((row) => {
    const card = el("article", "request");
    card.innerHTML = `
      <span>${row.requesting_team}</span>
      <strong>${row.business_question}</strong>
      <em>${row.expected_artifact} | ${row.cadence} | ${row.status}</em>
    `;
    return card;
  }));
}

function activateTabs() {
  const buttons = [...document.querySelectorAll("[data-tab-target]")];
  const panels = [...document.querySelectorAll("[data-tab-panel]")];
  buttons.forEach((button) => {
    button.addEventListener("click", () => {
      const target = button.dataset.tabTarget;
      buttons.forEach((item) => item.classList.toggle("active", item === button));
      panels.forEach((panel) => panel.classList.toggle("active", panel.dataset.tabPanel === target));
    });
  });
}

function updateGeneratedLabel() {
  const label = document.querySelector("#generated-label");
  label.textContent = "Synthetic data generated with seed 20260519";
}

async function main() {
  activateTabs();
  updateGeneratedLabel();
  const data = await loadData();
  renderKpis(data);
  renderPriority(data);
  renderFunnel(data);
  renderSchema(data);
  renderValidation(data);
  renderRequests(data);
}

main().catch((error) => {
  document.querySelector("#app-status").textContent = `Unable to load workbench data: ${error.message}`;
});
