"use strict";

const MODEL_CONFIG = {
  essential: {
    label: "Essential",
    confidenceCap: 2,
    formula: "0.35T + 0.35pH + 0.30ORP",
    fields: [
      ["temperature", "Índice de temperatura (T)", 35],
      ["ph", "Índice de pH", 35],
      ["orp", "Índice de ORP", 30]
    ]
  },
  insight: {
    label: "Insight",
    confidenceCap: 4,
    formula: "0.20T + 0.20pH + 0.15ORP + 0.40A + 0.05H",
    fields: [
      ["temperature", "Índice de temperatura (T)", 20],
      ["ph", "Índice de pH", 20],
      ["orp", "Índice de ORP", 15],
      ["anaerobic", "Índice de anaerobiosis (A)", 40],
      ["homogeneity", "Índice de homogeneidad (H)", 5]
    ]
  },
  signature: {
    label: "Signature",
    confidenceCap: 5,
    formula: "0.15T + 0.15pH + 0.10ORP + 0.35A + 0.20B + 0.05H",
    fields: [
      ["temperature", "Índice de temperatura (T)", 15],
      ["ph", "Índice de pH", 15],
      ["orp", "Índice de ORP", 10],
      ["anaerobic", "Índice de anaerobiosis (A)", 35],
      ["biology", "Índice biológico (B)", 20],
      ["homogeneity", "Índice de homogeneidad (H)", 5]
    ]
  }
};

const state = { lastResult: null };

const $ = (id) => document.getElementById(id);
const clamp = (value, min = 0, max = 100) => Math.min(max, Math.max(min, Number(value) || 0));
const round = (value, decimals = 1) => Number(value.toFixed(decimals));

function sensoryScore(sca) {
  return clamp(((Number(sca) - 80) / 20) * 100);
}

function renderProcessInputs() {
  const model = MODEL_CONFIG[$("model").value];
  const container = $("process-inputs");
  container.innerHTML = "";

  model.fields.forEach(([id, label, weight]) => {
    const wrapper = document.createElement("label");
    wrapper.innerHTML = `${label}
      <input id="process-${id}" type="number" min="0" max="100" step="0.1" value="85">
      <small>Ponderación: ${weight}% del Process Score</small>`;
    container.appendChild(wrapper);
  });

  $("model-formula").textContent = model.formula;
  $("meta-model").textContent = model.label;
  bindProcessListeners();
  updatePreviews();
}

function bindProcessListeners() {
  document.querySelectorAll("#process-inputs input").forEach((input) => {
    input.addEventListener("input", updatePreviews);
  });
}

function calculateProcessScore() {
  const model = MODEL_CONFIG[$("model").value];
  return model.fields.reduce((total, [id, , weight]) => {
    return total + clamp($("process-" + id).value) * (weight / 100);
  }, 0);
}

function calculateIntegrityScore() {
  const massBalance = clamp($("mass-balance").value);
  const documentation = clamp($("documentation").value);
  return 0.6 * massBalance + 0.4 * documentation;
}

function calculateConfidence() {
  const modelCap = MODEL_CONFIG[$("model").value].confidenceCap;
  const planCap = Number($("origin-plan").value);
  const evidence = Number($("evidence-level").value);
  return Math.min(modelCap, planCap, evidence);
}

function classify(score) {
  if (score >= 85) return ["Sobresaliente", "Resultado integral muy alto. Debe confirmarse la suficiencia de datos y la ausencia de condiciones de descalificación."];
  if (score >= 70) return ["Avanzado", "El microlote combina desempeño fuerte con evidencia relevante; revise las oportunidades de mejora por componente."];
  if (score >= 55) return ["Competente", "El resultado es prometedor, pero uno o más componentes limitan la calificación integral."];
  if (score >= 40) return ["En desarrollo", "Se requiere fortalecer calidad sensorial, control de proceso o integridad antes de una afirmación comercial robusta."];
  return ["Insuficiente", "La evidencia o el desempeño disponible no sustentan todavía una calificación Nebula Score® robusta."];
}

function updatePreviews() {
  $("sensory-preview").textContent = round(sensoryScore($("sca-score").value)).toFixed(1);
  $("process-preview").textContent = round(calculateProcessScore()).toFixed(1);
}

function calculate(event) {
  if (event) event.preventDefault();

  const sca = clamp($("sca-score").value, 0, 100);
  const sensory = sensoryScore(sca);
  const process = calculateProcessScore();
  const integrity = calculateIntegrityScore();
  const penalties = clamp($("penalties").value, 0, 100);
  const score = clamp(0.6 * sensory + 0.3 * process + 0.1 * integrity - penalties);
  const confidence = calculateConfidence();
  const model = MODEL_CONFIG[$("model").value];
  const [classification, interpretation] = classify(score);

  const result = {
    schema: "nebula-score.coffee.v1",
    generatedAt: new Date().toISOString(),
    lot: $("lot-id").value.trim() || null,
    producer: $("producer").value.trim() || null,
    product: "coffee",
    model: model.label,
    scaScore: round(sca, 2),
    components: {
      sensory: round(sensory),
      process: round(process),
      integrity: round(integrity),
      penalties: round(penalties)
    },
    nebulaScore: round(score),
    confidenceLevel: confidence,
    classification,
    methodologyStatus: "technical-model-under-validation"
  };

  state.lastResult = result;
  renderResult(result, interpretation);
}

function renderResult(result, interpretation) {
  $("final-score").textContent = result.nebulaScore.toFixed(1);
  $("score-ring").style.setProperty("--score-angle", `${result.nebulaScore * 3.6}deg`);
  $("classification").textContent = result.classification;
  $("interpretation").textContent = interpretation;
  $("sensory-result").textContent = result.components.sensory.toFixed(1);
  $("process-result").textContent = result.components.process.toFixed(1);
  $("integrity-result").textContent = result.components.integrity.toFixed(1);
  $("penalty-result").textContent = `−${result.components.penalties.toFixed(1)}`;
  $("confidence-result").textContent = `${result.confidenceLevel}/5`;
  $("meta-lot").textContent = result.lot || "No indicado";
  $("meta-producer").textContent = result.producer || "No indicado";
  $("meta-model").textContent = result.model;
  $("result-status").textContent = `Coffee V1 · ${new Date(result.generatedAt).toLocaleString("es")}`;
}

function exportResult() {
  if (!state.lastResult) calculate();
  const content = JSON.stringify(state.lastResult, null, 2);
  const blob = new Blob([content], { type: "application/json" });
  const url = URL.createObjectURL(blob);
  const anchor = document.createElement("a");
  const lot = state.lastResult.lot || "microlote";
  anchor.href = url;
  anchor.download = `nebula-score-${lot}.json`.replace(/[^a-zA-Z0-9._-]/g, "-");
  document.body.appendChild(anchor);
  anchor.click();
  anchor.remove();
  URL.revokeObjectURL(url);
}

function resetForm() {
  $("score-form").reset();
  $("model").value = "insight";
  renderProcessInputs();
  state.lastResult = null;
  $("final-score").textContent = "—";
  $("score-ring").style.setProperty("--score-angle", "0deg");
  $("classification").textContent = "Complete los datos";
  $("interpretation").textContent = "El resultado debe interpretarse junto con sus componentes y el nivel de confianza.";
  ["sensory-result", "process-result", "integrity-result", "penalty-result"].forEach((id) => $(id).textContent = "—");
  $("confidence-result").textContent = "—/5";
  $("result-status").textContent = "Modelo técnico V1";
}

$("model").addEventListener("change", renderProcessInputs);
$("sca-score").addEventListener("input", updatePreviews);
$("score-form").addEventListener("submit", calculate);
$("reset-button").addEventListener("click", resetForm);
$("export-button").addEventListener("click", exportResult);

renderProcessInputs();
calculate();
