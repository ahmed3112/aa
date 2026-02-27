const backupForm = document.getElementById('backupForm');
const payloadPreview = document.getElementById('payloadPreview');
const historyRows = document.getElementById('historyRows');
const emptyState = document.getElementById('emptyState');
const seedBtn = document.getElementById('seedBtn');
const clearBtn = document.getElementById('clearBtn');
const storageKey = 'ciscoBackupHistory';

function now() {
  return new Date().toLocaleString();
}

function readForm() {
  return {
    deviceName: document.getElementById('deviceName').value.trim(),
    ipAddress: document.getElementById('ipAddress').value.trim(),
    username: document.getElementById('username').value.trim(),
    password: document.getElementById('password').value,
    enableSecret: document.getElementById('enableSecret').value,
    protocol: document.getElementById('protocol').value,
    configType: document.getElementById('configType').value,
    scheduleType: document.getElementById('scheduleType').value,
  };
}

function updatePreview() {
  const payload = readForm();
  payloadPreview.textContent = JSON.stringify(payload, null, 2);
}

function loadHistory() {
  return JSON.parse(localStorage.getItem(storageKey) || '[]');
}

function saveHistory(entries) {
  localStorage.setItem(storageKey, JSON.stringify(entries));
}

function downloadConfig(entry) {
  const template = document.getElementById('downloadTemplate').textContent;
  const body = template.replace('{{device}}', entry.deviceName).replace('{{ip}}', entry.ipAddress);
  const blob = new Blob([body], { type: 'text/plain' });
  const url = URL.createObjectURL(blob);
  const link = document.createElement('a');
  link.href = url;
  link.download = `${entry.deviceName}-${entry.configType}.cfg`;
  link.click();
  URL.revokeObjectURL(url);
}

function renderHistory() {
  const entries = loadHistory();
  historyRows.innerHTML = '';

  entries.forEach((entry, index) => {
    const row = document.createElement('tr');
    row.innerHTML = `
      <td>${entry.createdAt}</td>
      <td>${entry.deviceName}</td>
      <td>${entry.ipAddress}</td>
      <td>${entry.protocol}</td>
      <td class="status-ok">${entry.status}</td>
      <td><button type="button" data-download="${index}">Download</button></td>
    `;
    historyRows.appendChild(row);
  });

  emptyState.hidden = entries.length > 0;

  historyRows.querySelectorAll('button[data-download]').forEach((button) => {
    button.addEventListener('click', () => {
      const idx = Number(button.getAttribute('data-download'));
      const selected = loadHistory()[idx];
      if (selected) downloadConfig(selected);
    });
  });
}

backupForm.addEventListener('input', updatePreview);

backupForm.addEventListener('submit', (event) => {
  event.preventDefault();
  const payload = readForm();
  const entries = loadHistory();

  entries.unshift({
    ...payload,
    status: 'Backup Complete',
    createdAt: now(),
  });

  saveHistory(entries.slice(0, 20));
  renderHistory();
  backupForm.reset();
  updatePreview();
});

seedBtn.addEventListener('click', () => {
  const entries = loadHistory();
  entries.unshift({
    deviceName: 'Distribution-SW-02',
    ipAddress: '10.10.2.12',
    username: 'netbackup',
    password: '***',
    enableSecret: '***',
    protocol: 'SSH',
    configType: 'running-config',
    scheduleType: 'Daily 02:00',
    status: 'Backup Complete',
    createdAt: now(),
  });
  saveHistory(entries.slice(0, 20));
  renderHistory();
});

clearBtn.addEventListener('click', () => {
  localStorage.removeItem(storageKey);
  renderHistory();
});

updatePreview();
renderHistory();
