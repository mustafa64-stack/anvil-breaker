// extension/content.js - Injected directly into LeetCode problem pages
(function() {
  if (document.getElementById('anvil-breaker-hud-root')) return;

  const root = document.createElement('div');
  root.id = 'anvil-breaker-hud-root';
  root.innerHTML = `
    <div class="anvil-hud-container" id="anvil-hud-drag">
      <div class="anvil-hud-brand">
        <span>⚒️</span>
        <span>ANVIL</span>
      </div>
      <div>
        <div style="display:flex; align-items:baseline; gap:6px;">
          <span class="anvil-hud-digits" id="anvil-digits">15:00</span>
          <span class="anvil-hud-phase phase-1" id="anvil-phase-tag">P1 Read</span>
        </div>
      </div>
      <div style="display:flex; gap:4px; align-items:center;">
        <button class="anvil-hud-btn" id="anvil-btn-toggle">Start</button>
        <button class="anvil-hud-btn-sec" id="anvil-btn-next" title="Next Phase">⏭</button>
        <button class="anvil-hud-btn-sec" id="anvil-btn-reset" title="Reset (R)">↺</button>
      </div>
    </div>
  `;
  document.body.appendChild(root);

  const digitsEl = document.getElementById('anvil-digits');
  const phaseTagEl = document.getElementById('anvil-phase-tag');
  const toggleBtn = document.getElementById('anvil-btn-toggle');
  const nextBtn = document.getElementById('anvil-btn-next');
  const resetBtn = document.getElementById('anvil-btn-reset');
  const container = document.getElementById('anvil-hud-drag');

  // Make HUD Draggable
  let isDragging = false;
  let currentX, currentY, initialX, initialY, xOffset = 0, yOffset = 0;

  container.addEventListener('mousedown', dragStart);
  document.addEventListener('mouseup', dragEnd);
  document.addEventListener('mousemove', drag);

  function dragStart(e) {
    if (['BUTTON', 'A', 'INPUT'].includes(e.target.tagName)) return;
    initialX = e.clientX - xOffset;
    initialY = e.clientY - yOffset;
    isDragging = true;
  }

  function dragEnd() {
    initialX = currentX;
    initialY = currentY;
    isDragging = false;
  }

  function drag(e) {
    if (isDragging) {
      e.preventDefault();
      currentX = e.clientX - initialX;
      currentY = e.clientY - initialY;
      xOffset = currentX;
      yOffset = currentY;
      container.style.transform = `translate3d(${currentX}px, ${currentY}px, 0)`;
    }
  }

  function render(seconds, running, phase) {
    const m = Math.floor(seconds / 60);
    const s = seconds % 60;
    digitsEl.textContent = `${String(m).padStart(2, '0')}:${String(s).padStart(2, '0')}`;
    toggleBtn.textContent = running ? "Pause" : "Start";
    toggleBtn.style.background = running ? "#d97706" : "#4f46e5";

    const labels = ["P1 Read", "P2 Pattern", "P3 Code", "P4 Cut Losses"];
    phaseTagEl.textContent = labels[phase - 1] || labels[0];
    phaseTagEl.className = `anvil-hud-phase phase-${phase}`;
  }

  // Load initial state
  chrome.storage.local.get(['anvil_timer_seconds', 'anvil_running', 'anvil_phase'], (data) => {
    render(data.anvil_timer_seconds || 15 * 60, data.anvil_running || false, data.anvil_phase || 1);
  });

  // Action listeners
  toggleBtn.addEventListener('click', () => {
    chrome.runtime.sendMessage({ action: 'TOGGLE_TIMER' }, (r) => {
      if (r) render(r.seconds, r.running, r.phase);
    });
  });

  nextBtn.addEventListener('click', () => {
    chrome.runtime.sendMessage({ action: 'NEXT_PHASE' }, (r) => {
      if (r) render(r.seconds, r.running, r.phase);
    });
  });

  resetBtn.addEventListener('click', () => {
    chrome.runtime.sendMessage({ action: 'RESET_TIMER' }, (r) => {
      if (r) render(r.seconds, r.running, r.phase);
    });
  });

  // Listen to background tick updates
  chrome.runtime.onMessage.addListener((msg) => {
    if (msg.action === 'TICK') {
      render(msg.seconds, msg.running, msg.phase);
    }
  });

  // Observe LeetCode Submissions for "Accepted" status
  let hasLoggedSolve = false;
  const observer = new MutationObserver(() => {
    if (hasLoggedSolve) return;
    const bodyText = document.body.innerText;
    // Check for LeetCode Accepted text in submission result
    const acceptedPills = document.querySelectorAll('span[data-e2e-locator="submission-result"]');
    const isAccepted = Array.from(acceptedPills).some(el => el.textContent.includes('Accepted')) || 
                       bodyText.includes('Runtime: ') && bodyText.includes('Beats ') && bodyText.includes('Accepted');

    if (isAccepted) {
      hasLoggedSolve = true;
      // Trigger celebrate
      container.style.boxShadow = '0 0 30px #10b981';
      container.style.borderColor = '#10b981';
      
      // Auto-notify background to log clean solve
      const problemSlug = window.location.pathname.split('/')[2] || 'unknown';
      chrome.runtime.sendMessage({
        action: 'SOLVED_ACCEPTED',
        slug: problemSlug,
        url: window.location.href
      });

      setTimeout(() => {
        container.style.boxShadow = '';
        container.style.borderColor = '';
      }, 4000);
    }
  });

  observer.observe(document.body, { childList: true, subtree: true });
})();
