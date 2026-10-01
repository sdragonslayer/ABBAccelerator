const state = { documents: [], citations: [] };

const elements = {
  statusLamp: document.querySelector("#status-lamp"),
  healthStatus: document.querySelector("#health-status"),
  documentCount: document.querySelector("#document-count"),
  chunkCount: document.querySelector("#chunk-count"),
  libraryCount: document.querySelector("#library-count"),
  uploadToggle: document.querySelector("#upload-toggle"),
  uploadForm: document.querySelector("#upload-form"),
  uploadMessage: document.querySelector("#upload-message"),
  documentList: document.querySelector("#document-list"),
  question: document.querySelector("#question-input"),
  equipmentModel: document.querySelector("#equipment-model"),
  manualVersion: document.querySelector("#manual-version"),
  askButton: document.querySelector("#ask-button"),
  askLabel: document.querySelector("#ask-button .ask-label"),
  emptyState: document.querySelector("#empty-state"),
  answerSection: document.querySelector("#answer-section"),
  gateStrip: document.querySelector("#gate-strip"),
  gateLamp: document.querySelector("#gate-lamp"),
  gateVerdict: document.querySelector("#gate-verdict"),
  gateExplanation: document.querySelector("#gate-explanation"),
  confidence: document.querySelector("#confidence-value"),
  supportBar: document.querySelector("#support-bar"),
  coverage: document.querySelector("#coverage-value"),
  coverageBar: document.querySelector("#coverage-bar"),
  identifierList: document.querySelector("#identifier-list"),
  answerTitle: document.querySelector("#answer-title"),
  answerContent: document.querySelector("#answer-content"),
  warningList: document.querySelector("#warning-list"),
  applicabilityList: document.querySelector("#applicability-list"),
  citationCount: document.querySelector("#citation-count"),
  citationList: document.querySelector("#citation-list"),
  dialog: document.querySelector("#evidence-dialog"),
  dialogTitle: document.querySelector("#dialog-title"),
  dialogMeta: document.querySelector("#dialog-meta"),
  dialogQuote: document.querySelector("#dialog-quote"),
  pagePreview: document.querySelector("#page-preview"),
  dialogClose: document.querySelector("#dialog-close"),
  toast: document.querySelector("#toast"),
};

async function api(path, options = {}) {
  const response = await fetch(path, options);
  if (!response.ok) {
    let message = `Request failed (${response.status})`;
    try {
      const body = await response.json();
      message = body.detail || message;
    } catch (_) {
      // Use the status fallback when the response is not JSON.
    }
    throw new Error(message);
  }
  return response.json();
}

function showToast(message) {
  elements.toast.textContent = message;
  elements.toast.classList.add("visible");
  window.setTimeout(() => elements.toast.classList.remove("visible"), 3200);
}

function pad(value) {
  return String(value).padStart(2, "0");
}

function percent(value) {
  return `${Math.round((value || 0) * 100)}%`;
}

function setLamp(lamp, status) {
  lamp.classList.remove("ok", "fault", "warn");
  if (status) lamp.classList.add(status);
}

async function refreshHealth() {
  try {
    const health = await api("/api/health");
    elements.healthStatus.textContent = `Ready · ${health.answer_provider}`;
    setLamp(elements.statusLamp, "ok");
    elements.documentCount.textContent = pad(health.documents);
    elements.chunkCount.textContent = health.chunks;
  } catch (error) {
    elements.healthStatus.textContent = "Unavailable";
    setLamp(elements.statusLamp, "fault");
    showToast(error.message);
  }
}

async function refreshDocuments() {
  state.documents = await api("/api/documents");
  elements.documentList.replaceChildren();
  elements.libraryCount.textContent = `// ${pad(state.documents.length)}`;
  if (!state.documents.length) {
    const empty = document.createElement("p");
    empty.className = "empty-documents";
    empty.textContent = "No manuals indexed yet. Add the synthetic demo corpus or upload a document.";
    elements.documentList.append(empty);
    return;
  }
  for (const item of state.documents) {
    const label = document.createElement("label");
    label.className = "document-item";
    const checkbox = document.createElement("input");
    checkbox.type = "checkbox";
    checkbox.value = item.id;
    checkbox.checked = true;
    const details = document.createElement("div");
    const title = document.createElement("strong");
    title.textContent = item.title;
    title.title = item.title;
    const meta = document.createElement("span");
    const parts = [item.equipment_model || "Model unspecified", item.document_type];
    if (item.version) parts.push(`v${item.version}`);
    parts.push(`${item.page_count} pg`, `${item.chunk_count} blk`);
    meta.textContent = parts.join(" · ");
    details.append(title, meta);
    for (const warningText of item.ingestion_warnings || []) {
      const warning = document.createElement("small");
      warning.className = "document-warning";
      warning.textContent = warningText;
      details.append(warning);
    }
    label.append(checkbox, details);
    elements.documentList.append(label);
  }
}

elements.uploadToggle.addEventListener("click", () => {
  const hidden = elements.uploadForm.classList.toggle("hidden");
  elements.uploadToggle.setAttribute("aria-expanded", String(!hidden));
});

elements.uploadForm.addEventListener("submit", async (event) => {
  event.preventDefault();
  const submit = elements.uploadForm.querySelector("button[type=submit]");
  submit.disabled = true;
  elements.uploadMessage.textContent = "Indexing evidence…";
  try {
    const form = new FormData(elements.uploadForm);
    const result = await api("/api/documents", { method: "POST", body: form });
    elements.uploadMessage.textContent = `Indexed ${result.document.chunk_count} evidence blocks.`;
    elements.uploadForm.reset();
    await Promise.all([refreshDocuments(), refreshHealth()]);
    if (result.warnings.length) showToast(result.warnings.join(" "));
  } catch (error) {
    elements.uploadMessage.textContent = error.message;
  } finally {
    submit.disabled = false;
  }
});

function selectedDocumentIds() {
  return Array.from(elements.documentList.querySelectorAll("input:checked")).map((input) => input.value);
}

function findCitation(index) {
  return state.citations.find((citation) => citation.index === index);
}

function focusCitation(citation) {
  const card = document.querySelector(`#cite-${citation.index}`);
  if (card) {
    card.scrollIntoView({ behavior: "smooth", block: "nearest" });
    card.classList.add("flash");
    window.setTimeout(() => card.classList.remove("flash"), 1200);
  }
  openEvidence(citation);
}

// Only markers that resolve to an application-owned citation become links.
function appendWithCitations(parent, text) {
  const pattern = /\[(\d+)\]/g;
  let cursor = 0;
  for (const match of text.matchAll(pattern)) {
    const citation = findCitation(Number(match[1]));
    if (!citation) continue;
    if (match.index > cursor) parent.append(document.createTextNode(text.slice(cursor, match.index)));
    const ref = document.createElement("button");
    ref.type = "button";
    ref.className = "cite-ref";
    ref.textContent = pad(citation.index);
    ref.setAttribute("aria-label", `Open citation ${citation.index}: ${citation.document_title}, page ${citation.page_number}`);
    ref.addEventListener("click", () => focusCitation(citation));
    parent.append(ref);
    cursor = match.index + match[0].length;
  }
  if (cursor < text.length) parent.append(document.createTextNode(text.slice(cursor)));
}

function renderAnswerText(text) {
  elements.answerContent.replaceChildren();
  const lines = text.split("\n").map((line) => line.trim()).filter(Boolean);
  let block = null;
  let list = null;
  lines.forEach((line, position) => {
    if (line.startsWith("- ")) {
      if (!list) {
        list = document.createElement("ul");
        list.className = "steps unordered";
        (block || elements.answerContent).append(list);
      }
      const item = document.createElement("li");
      appendWithCitations(item, line.slice(2));
      list.append(item);
      return;
    }
    list = null;
    const next = lines[position + 1];
    if (next && next.startsWith("- ")) {
      block = document.createElement("section");
      block.className = "answer-block";
      if (/safety|warning|hazard/i.test(line)) block.classList.add("safety");
      const heading = document.createElement("h3");
      heading.textContent = line;
      block.append(heading);
      elements.answerContent.append(block);
      return;
    }
    block = null;
    const paragraph = document.createElement("p");
    appendWithCitations(paragraph, line);
    elements.answerContent.append(paragraph);
  });
}

function renderWarnings(warnings) {
  elements.warningList.replaceChildren();
  for (const warning of warnings) {
    const item = document.createElement("div");
    item.className = "warning";
    item.textContent = warning;
    elements.warningList.append(item);
  }
}

function renderApplicability(warnings) {
  elements.applicabilityList.replaceChildren();
  for (const message of warnings) {
    const item = document.createElement("div");
    item.className = "warning applicability";
    item.textContent = message;
    elements.applicabilityList.append(item);
  }
}

function renderDecision(decision, abstained, support) {
  const accepted = !abstained && Boolean(decision && decision.accepted);
  elements.gateStrip.classList.toggle("accepted", accepted);
  elements.gateStrip.classList.toggle("abstained", !accepted);
  setLamp(elements.gateLamp, accepted ? "ok" : "fault");
  const reason = decision ? decision.reason.replaceAll("_", " ") : "unknown";
  elements.gateVerdict.textContent = `${accepted ? "Accepted" : "Abstained"} · ${reason}`;
  elements.gateExplanation.textContent = decision ? decision.explanation : "";

  elements.confidence.textContent = percent(support);
  elements.supportBar.style.width = percent(support);
  const coverage = decision ? decision.query_token_coverage : 0;
  elements.coverage.textContent = percent(coverage);
  elements.coverageBar.style.width = percent(coverage);

  elements.identifierList.replaceChildren();
  const matched = (decision && decision.matched_identifiers) || [];
  const missing = (decision && decision.missing_identifiers) || [];
  for (const [values, kind] of [[matched, "matched"], [missing, "missing"]]) {
    for (const value of values) {
      const tag = document.createElement("span");
      tag.className = `tag ${kind}`;
      tag.textContent = value;
      tag.title = kind === "matched" ? "Found in cited evidence" : "Not found in evidence";
      elements.identifierList.append(tag);
    }
  }
  if (!matched.length && !missing.length) {
    const none = document.createElement("span");
    none.className = "tag-empty";
    none.textContent = "None in query";
    elements.identifierList.append(none);
  }
}

function renderCitations(citations) {
  state.citations = citations;
  elements.citationList.replaceChildren();
  elements.citationCount.textContent = `${pad(citations.length)} citation${citations.length === 1 ? "" : "s"}`;
  if (!citations.length) {
    const empty = document.createElement("p");
    empty.className = "no-citations";
    empty.textContent = "No evidence met the gate. Nothing is cited.";
    elements.citationList.append(empty);
    return;
  }
  for (const citation of citations) {
    const button = document.createElement("button");
    button.className = "citation-card";
    button.type = "button";
    button.id = `cite-${citation.index}`;

    const top = document.createElement("span");
    top.className = "citation-top";
    const index = document.createElement("span");
    index.className = "citation-index";
    index.textContent = pad(citation.index);
    const type = document.createElement("span");
    type.className = "source-type";
    type.textContent = citation.source_type;
    const page = document.createElement("span");
    page.className = "citation-page";
    page.textContent = `p.${citation.page_number}${citation.document_version ? ` · v${citation.document_version}` : ""}`;
    top.append(index, type, page);

    const body = document.createElement("span");
    body.className = "citation-body";
    const title = document.createElement("h4");
    title.textContent = citation.document_title;
    const meta = document.createElement("span");
    meta.className = "citation-meta";
    meta.textContent = `${citation.equipment_model || "Model unspecified"} · ${citation.document_type}`;
    const quote = document.createElement("p");
    quote.textContent = citation.quote;

    const score = document.createElement("span");
    score.className = "citation-score";
    const scoreLabel = document.createElement("span");
    scoreLabel.textContent = `Ranking ${citation.score.toFixed(2)}`;
    const meter = document.createElement("span");
    meter.className = "meter";
    const fill = document.createElement("span");
    fill.style.width = percent(citation.score);
    meter.append(fill);
    score.append(scoreLabel, meter);

    body.append(title, meta, quote, score);
    button.append(top, body);
    button.addEventListener("click", () => openEvidence(citation));
    elements.citationList.append(button);
  }
}

async function askQuestion() {
  const question = elements.question.value.trim();
  if (question.length < 3) {
    showToast("Enter a maintenance question first.");
    return;
  }
  elements.askButton.disabled = true;
  elements.askButton.classList.add("is-busy");
  elements.askLabel.textContent = "Checking evidence…";
  try {
    const selected = selectedDocumentIds();
    const body = {
      question,
      document_ids: selected,
      equipment_model: elements.equipmentModel.value.trim() || null,
      manual_version: elements.manualVersion.value.trim() || null,
    };
    const result = await api("/api/ask", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(body),
    });
    elements.emptyState.classList.add("hidden");
    elements.answerSection.classList.remove("hidden");
    elements.answerTitle.textContent = result.abstained
      ? "Insufficient evidence — no answer"
      : "Maintenance guidance";
    elements.answerTitle.classList.toggle("abstained", result.abstained);
    elements.answerContent.classList.toggle("abstained", result.abstained);
    renderDecision(result.evidence_decision, result.abstained, result.evidence_support);
    renderWarnings(result.warnings || []);
    renderApplicability(result.applicability_warnings || []);
    renderCitations(result.citations || []);
    renderAnswerText(result.answer);
    elements.answerSection.scrollIntoView({ behavior: "smooth", block: "start" });
  } catch (error) {
    showToast(error.message);
  } finally {
    elements.askButton.disabled = false;
    elements.askButton.classList.remove("is-busy");
    elements.askLabel.textContent = "Run query";
  }
}

elements.askButton.addEventListener("click", askQuestion);
elements.question.addEventListener("keydown", (event) => {
  if ((event.ctrlKey || event.metaKey) && event.key === "Enter") askQuestion();
});

for (const button of document.querySelectorAll("[data-prompt]")) {
  button.addEventListener("click", () => {
    elements.question.value = button.dataset.prompt;
    elements.question.focus();
  });
}

function renderDialogMeta(fields) {
  elements.dialogMeta.replaceChildren();
  for (const [label, value] of fields) {
    const row = document.createElement("div");
    const term = document.createElement("dt");
    term.textContent = label;
    const detail = document.createElement("dd");
    detail.textContent = value;
    row.append(term, detail);
    elements.dialogMeta.append(row);
  }
}

function openEvidence(citation) {
  elements.dialogTitle.textContent = citation.document_title;
  renderDialogMeta([
    ["Page", String(citation.page_number)],
    ["Version", citation.document_version || "—"],
    ["Source type", citation.source_type],
    ["Model", citation.equipment_model || "Unspecified"],
  ]);
  elements.dialogQuote.textContent = citation.quote;
  elements.pagePreview.replaceChildren();

  const documentRecord = state.documents.find((item) => item.id === citation.document_id);
  if (documentRecord && documentRecord.content_type === "application/pdf") {
    const params = new URLSearchParams();
    if (citation.bbox) {
      ["x0", "y0", "x1", "y1"].forEach((key, index) => params.set(key, citation.bbox[index]));
    }
    const image = document.createElement("img");
    image.alt = `Highlighted source page ${citation.page_number}`;
    image.src = `/api/documents/${citation.document_id}/pages/${citation.page_number}/image?${params}`;
    image.addEventListener("error", () => {
      const note = document.createElement("p");
      note.className = "preview-note";
      note.textContent = "The source preview could not be rendered. Verify the original source document.";
      elements.pagePreview.replaceChildren(note);
    });
    elements.pagePreview.append(image);
  } else {
    const note = document.createElement("p");
    note.className = "preview-note";
    note.textContent = "Visual page preview is available for PDF sources. The indexed excerpt is shown above.";
    elements.pagePreview.append(note);
  }
  if (!elements.dialog.open) elements.dialog.showModal();
}

elements.dialogClose.addEventListener("click", () => elements.dialog.close());
elements.dialog.addEventListener("click", (event) => {
  if (event.target === elements.dialog) elements.dialog.close();
});

Promise.all([refreshHealth(), refreshDocuments()]).catch((error) => showToast(error.message));
