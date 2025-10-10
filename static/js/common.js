function qs(id) {
  return document.getElementById(id);
}

function getSelectedValues(selectId) {
  const el = qs(selectId);
  if (!el) return [];
  return Array.from(el.selectedOptions).map((opt) => opt.value);
}

function setLoadingState(isLoading, options = {}) {
  const { spinnerId = 'spinner', buttonId } = options;
  const spinner = qs(spinnerId);
  const button = buttonId ? qs(buttonId) : null;
  if (spinner) spinner.style.display = isLoading ? 'flex' : 'none';
  if (button) button.disabled = isLoading;
}

function formatNumber(num, decimals = 2) {
  if (num === undefined || num === null || Number.isNaN(num)) return 'N/A';
  try { return Number(num).toFixed(decimals); } catch { return 'N/A'; }
}

function insertHtml(container, html) {
  if (!container) return;
  container.insertAdjacentHTML('beforeend', html);
}

async function fetchJson(url, options) {
  const resp = await fetch(url, options);
  if (!resp.ok) throw new Error('Network error');
  return await resp.json();
}

function showInlineMessage(container, type, text) {
  if (!container) return;
  const cls = type === 'error' ? 'alert-danger' : type === 'warn' ? 'alert-warning' : 'alert-info';
  container.innerHTML = `<div class="alert ${cls}" role="alert">${text}</div>`;
}


