const state = { documents: [], citations: [] };

const elements = {
  healthStatus: document.querySelector("#health-status"),
  documentCount: document.querySelector("#document-count"),
  chunkCount: document.querySelector("#chunk-count"),
  uploadToggle: document.querySelector("#upload-toggle"),
  uploadForm: document.querySelector("#upload-form"),
  uploadMessage: document.querySelector("#upload-message"),
  documentList: document.querySelector("#document-list"),
  question: document.querySelector("#question-input"),
  equipmentModel: document.querySelector("#equipment-model"),
  manualVersion: document.querySelector("#manual-version"),
  askButton: document.querySelector("#ask-button"),
  emptyState: document.querySelector("#empty-state"),
  answerSection: document.querySelector("#answer-section"),
  answerTitle: document.querySelector("#answer-title"),
  answerContent: document.querySelector("#answer-content"),
  confidence: document.querySelector("#confidence-value"),
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

async function refreshHealth() {
  try {
    const health = await api("/api/health");
    elements.healthStatus.textContent = `Ready · ${health.answer_provider}`;
    elements.documentCount.textContent = health.documents;
    elements.chunkCount.textContent = health.chunks;
  } catch (error) {
    elements.healthStatus.textContent = "Unavailable";
    showToast(error.message);
  }
}

async function refreshDocuments() {
  state.documents = await api("/api/documents");
  elements.documentList.replaceChildren();
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
    const meta = document.createElement("span");
    meta.textContent = `${item.version ? `v${item.version} · ` : ""}${item.page_count} page${item.page_count === 1 ? "" : "s"} · ${item.chunk_count} blocks`;
    details.append(title, meta);
    meta.textContent = `${item.equipment_model || "Model unspecified"} · ${item.document_type} · ${meta.textContent}`;
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
  elements.uploadForm.classList.toggle("hidden");
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

function renderAnswerText(text) {
  elements.answerContent.replaceChildren();
  const lines = text.split("\n").map((line) => line.trim()).filter(Boolean);
  let list = null;
  for (const line of lines) {
    if (line.startsWith("- ")) {
      if (!list) {
        list = document.createElement("ul");
        elements.answerContent.append(list);
      }
      const item = document.createElement("li");
      item.textContent = line.slice(2);
      list.append(item);
    } else {
      list = null;
      const paragraph = document.createElement("p");
      paragraph.textContent = line;
      elements.answerContent.append(paragraph);
    }
  }
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

function renderApplicability(warnings, decision) {
  elements.applicabilityList.replaceChildren();
  const messages = [...warnings];
  if (decision && !decision.accepted) messages.unshift(decision.explanation);
  for (const message of messages) {
    const item = document.createElement("div");
    item.className = "warning applicability";
    item.textContent = message;
    elements.applicabilityList.append(item);
  }
}

function renderCitations(citations) {
  state.citations = citations;
  elements.citationList.replaceChildren();
  elements.citationCount.textContent = `${citations.length} citation${citations.length === 1 ? "" : "s"}`;
  for (const citation of citations) {
    const button = document.createElement("button");
    button.className = "citation-card";
    button.type = "button";
    const top = document.createElement("div");
    top.className = "citation-top";
    const index = document.createElement("span");
    index.className = "citation-index";
    index.textContent = citation.index;
    const type = document.createElement("span");
    type.className = "source-type";
    type.textContent = citation.source_type;
    top.append(index, type);
    const title = document.createElement("h4");
    title.textContent = citation.document_title;
    const meta = document.createElement("span");
    meta.className = "citation-meta";
    meta.textContent = `Page ${citation.page_number}${citation.document_version ? ` · v${citation.document_version}` : ""} · score ${citation.score.toFixed(2)}`;
    meta.textContent = `${citation.equipment_model || "Model unspecified"} · ${citation.document_type} · ${meta.textContent.replace("score", "ranking score")}`;
    const quote = document.createElement("p");
    quote.textContent = citation.quote;
    button.append(top, title, meta, quote);
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
  elements.askButton.querySelector("span").textContent = "Checking evidence…";
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
    elements.answerTitle.textContent = result.abstained ? "Insufficient evidence" : "Maintenance guidance";
    elements.answerContent.classList.toggle("abstained", result.abstained);
    elements.confidence.textContent = `${Math.round(result.evidence_support * 100)}%`;
    renderWarnings(result.warnings);
    renderApplicability(result.applicability_warnings, result.evidence_decision);
    renderAnswerText(result.answer);
    renderCitations(result.citations);
    elements.answerSection.scrollIntoView({ behavior: "smooth", block: "start" });
  } catch (error) {
    showToast(error.message);
  } finally {
    elements.askButton.disabled = false;
    elements.askButton.querySelector("span").textContent = "Find grounded answer";
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

function openEvidence(citation) {
  elements.dialogTitle.textContent = citation.document_title;
  elements.dialogMeta.textContent = `Page ${citation.page_number}${citation.document_version ? ` · Version ${citation.document_version}` : ""} · ${citation.source_type}`;
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
  elements.dialog.showModal();
}

elements.dialogClose.addEventListener("click", () => elements.dialog.close());
elements.dialog.addEventListener("click", (event) => {
  if (event.target === elements.dialog) elements.dialog.close();
});

Promise.all([refreshHealth(), refreshDocuments()]).catch((error) => showToast(error.message));
