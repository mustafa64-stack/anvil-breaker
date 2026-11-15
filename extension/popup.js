// extension/popup.js
document.addEventListener('DOMContentLoaded', async () => {
  const displayEl = document.getElementById('ext-timer-display');
  const phaseEl = document.getElementById('ext-phase-display');
  const toggleBtn = document.getElementById('btn-ext-toggle');
  const resetBtn = document.getElementById('btn-ext-reset');
  const nextBtn = document.getElementById('btn-ext-next');

  // Load saved state
  chrome.storage.local.get(['anvil_timer_seconds', 'anvil_running', 'anvil_phase'], (data) => {
    const sec = data.anvil_timer_seconds !== undefined ? data.anvil_timer_seconds : 15 * 60;
    const running = data.anvil_running || false;
    const phase = data.anvil_phase || 1;
    updateUI(sec, running, phase);
  });

  function updateUI(seconds, running, phase) {
    const m = Math.floor(seconds / 60);
    const s = seconds % 60;
    displayEl.textContent = `${String(m).padStart(2, '0')}:${String(s).padStart(2, '0')}`;
    
    toggleBtn.textContent = running ? "Pause" : "Start Timer";
    toggleBtn.style.background = running ? "#d97706" : "#4f46e5";

    const names = ["1: Read & Trace", "2: Pick a Pattern", "3: Code & Test", "4: Cut Losses"];
    const colors = ["#06b6d4", "#a855f7", "#10b981", "#f43f5e"];
    phaseEl.textContent = `Phase ${names[phase - 1] || names[0]}`;
    phaseEl.style.color = colors[phase - 1] || colors[0];
  }

  toggleBtn.addEventListener('click', () => {
    chrome.runtime.sendMessage({ action: 'TOGGLE_TIMER' }, (resp) => {
      if (resp) updateUI(resp.seconds, resp.running, resp.phase);
    });
  });

  resetBtn.addEventListener('click', () => {
    chrome.runtime.sendMessage({ action: 'RESET_TIMER' }, (resp) => {
      if (resp) updateUI(resp.seconds, resp.running, resp.phase);
    });
  });

  nextBtn.addEventListener('click', () => {
    chrome.runtime.sendMessage({ action: 'NEXT_PHASE' }, (resp) => {
      if (resp) updateUI(resp.seconds, resp.running, resp.phase);
    });
  });

  // Listen for background tick updates
  chrome.runtime.onMessage.addListener((msg) => {
    if (msg.action === 'TICK') {
      updateUI(msg.seconds, msg.running, msg.phase);
    }
  });
});

