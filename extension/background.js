// extension/background.js - Anvil Breaker Service Worker
let timerSeconds = 15 * 60;
let isRunning = false;
let currentPhase = 1;
let intervalId = null;

// Initialize state
chrome.storage.local.get(['anvil_timer_seconds', 'anvil_running', 'anvil_phase'], (data) => {
  if (data.anvil_timer_seconds !== undefined) timerSeconds = data.anvil_timer_seconds;
  if (data.anvil_phase !== undefined) currentPhase = data.anvil_phase;
});

function broadcastTick() {
  chrome.storage.local.set({
    anvil_timer_seconds: timerSeconds,
    anvil_running: isRunning,
    anvil_phase: currentPhase
  });

  const msg = {
    action: 'TICK',
    seconds: timerSeconds,
    running: isRunning,
    phase: currentPhase
  };

  chrome.runtime.sendMessage(msg).catch(() => {});
  chrome.tabs.query({ url: "*://*.leetcode.com/*" }, (tabs) => {
    tabs.forEach(tab => {
      chrome.tabs.sendMessage(tab.id, msg).catch(() => {});
    });
  });
}

function startTimer() {
  if (isRunning) return;
  isRunning = true;
  intervalId = setInterval(() => {
    if (timerSeconds > 0) {
      timerSeconds--;
      // Phase calculation (15m preset: 0-3m -> P1, 3-7m -> P2, 7-13m -> P3, 13-15m -> P4)
      const elapsed = 15 * 60 - timerSeconds;
      if (elapsed < 3 * 60) currentPhase = 1;
      else if (elapsed < 7 * 60) currentPhase = 2;
      else if (elapsed < 13 * 60) currentPhase = 3;
      else currentPhase = 4;

      broadcastTick();
    } else {
      pauseTimer();
      currentPhase = 4;
      broadcastTick();
    }
  }, 1000);
  broadcastTick();
}

function pauseTimer() {
  isRunning = false;
  clearInterval(intervalId);
  broadcastTick();
}

function resetTimer() {
  pauseTimer();
  timerSeconds = 15 * 60;
  currentPhase = 1;
  broadcastTick();
}

// Message handler from Popup or Content Script
chrome.runtime.onMessage.addListener((request, sender, sendResponse) => {
  if (request.action === 'TOGGLE_TIMER') {
    if (isRunning) pauseTimer();
    else startTimer();
    sendResponse({ seconds: timerSeconds, running: isRunning, phase: currentPhase });
  } else if (request.action === 'RESET_TIMER') {
    resetTimer();
    sendResponse({ seconds: timerSeconds, running: isRunning, phase: currentPhase });
  } else if (request.action === 'NEXT_PHASE') {
    currentPhase = currentPhase < 4 ? currentPhase + 1 : 1;
    broadcastTick();
    sendResponse({ seconds: timerSeconds, running: isRunning, phase: currentPhase });
  } else if (request.action === 'GET_STATE') {
    sendResponse({ seconds: timerSeconds, running: isRunning, phase: currentPhase });
  } else if (request.action === 'SOLVED_ACCEPTED') {
    // Attempt to log solve to local or cloud Anvil Breaker backend
    fetch('http://localhost:8765/api/progress/status', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        problem_id: 1,
        status: 'clean',
        time_spent: 15 * 60 - timerSeconds,
        pattern: 'LeetCode Extension Sync',
        scratchpad: `Solved via Anvil Breaker Extension on LeetCode: ${request.slug}`
      })
    }).catch(err => console.log('Backend sync offline:', err));
  }
  return true;
});

