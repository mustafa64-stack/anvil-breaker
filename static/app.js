// app.js - DSA Core Path & Dynamic Protocol HUD Logic

const HUD_PRESETS = {
  "15m": {
    name: "15m Speedrun Cap",
    totalMinutes: 15,
    phases: [
      { id: 1, name: "Read & Trace", minutes: 3 },
      { id: 2, name: "Pick a Pattern", minutes: 4 },
      { id: 3, name: "Code & Test", minutes: 6 },
      { id: 4, name: "Cut Your Losses", minutes: 2 },
    ]
  },
  "25m": {
    name: "25m Rule 2 Standard",
    totalMinutes: 25,
    phases: [
      { id: 1, name: "Read & Trace", minutes: 5 },
      { id: 2, name: "Pick a Pattern", minutes: 5 },
      { id: 3, name: "Code & Test", minutes: 11 },
      { id: 4, name: "Cut Your Losses", minutes: 4 },
    ]
  },
  "45m": {
    name: "45m FAANG Mock Interview",
    totalMinutes: 45,
    phases: [
      { id: 1, name: "Read & Trace", minutes: 8 },
      { id: 2, name: "Pick a Pattern", minutes: 8 },
      { id: 3, name: "Code & Test", minutes: 22 },
      { id: 4, name: "Cut Your Losses", minutes: 7 },
    ]
  }
};

let state = {
  problems: [],
  chapters: [],
  progress: {},
  currentProblemId: 1,
  activeFilter: 'all',
  searchQuery: '',
  curriculumFilter: 'all',
  curriculumSearchQuery: '',
  allAccordionsExpanded: true,
  activePresetKey: '15m',
  phaseConfig: null,
  timerSeconds: 15 * 60,
  timerElapsed: 0,
  timerInterval: null,
  timerRunning: false,
  activePhase: 1,
  soundEnabled: true,
  audioCtx: null,
  isCompactHud: false
};

// Bi-directional BroadcastChannel for Always-On-Top Mini HUD
const miniHudChannel = ('BroadcastChannel' in window) ? new BroadcastChannel('dsa_mini_hud_channel') : null;
if (miniHudChannel) {
  miniHudChannel.onmessage = (event) => {
    const msg = event.data;
    if (!msg) return;
    if (msg.action === 'TOGGLE_TIMER') toggleTimer();
    else if (msg.action === 'RESET_TIMER') resetTimer();
    else if (msg.action === 'NEXT_PHASE') {
      let nextP = state.activePhase + 1;
      if (nextP > 4) nextP = 1;
      setPhase(nextP);
      playSound('phase');
    }
    else if (msg.action === 'ADD_TIME') addExtraTime(msg.minutes || 1);
    else if (msg.action === 'SET_PHASE') setPhase(msg.phase);
    else if (msg.action === 'TOGGLE_SOUND') {
      state.soundEnabled = msg.enabled !== undefined ? msg.enabled : !state.soundEnabled;
      updateSoundIcon();
      saveSetting({ sound_enabled: state.soundEnabled });
    }
    else if (msg.action === 'REQUEST_STATE') broadcastHudState();
  };
}

function broadcastHudState() {
  if (!miniHudChannel) return;
  const prob = (state.problems && state.problems.find(p => p.id === state.currentProblemId)) || null;
  const payload = {
    action: 'STATE_UPDATE',
    timerSeconds: state.timerSeconds,
    timerRunning: state.timerRunning,
    activePhase: state.activePhase,
    soundEnabled: state.soundEnabled,
    problem: prob ? { id: prob.id, title: prob.title, level: prob.level, platform: prob.platform } : null,
    phaseConfig: state.phaseConfig
  };
  try {
    miniHudChannel.postMessage(payload);
    localStorage.setItem('dsa_mini_hud_cache', JSON.stringify(payload));
  } catch (e) {}
}

async function openMiniHudWindow() {
  try {
    if ('documentPictureInPicture' in window) {
      const pipWindow = await window.documentPictureInPicture.requestWindow({
        width: 380,
        height: 165
      });
      pipWindow.document.body.style.margin = '0';
      pipWindow.document.body.style.overflow = 'hidden';
      pipWindow.document.body.innerHTML = `
        <iframe src="/mini-hud" style="width:100%;height:100%;border:none;overflow:hidden;"></iframe>
      `;
      setTimeout(broadcastHudState, 200);
      showNotification("Always-On-Top Mini HUD PiP Launched!");
      return;
    }
  } catch (err) {
    console.warn("Document PiP fallback:", err);
  }

  const left = Math.max(10, window.screen.availWidth - 420);
  const top = 60;
  const win = window.open(
    '/mini-hud',
    'DSAMiniHUD',
    `width=380,height=165,left=${left},top=${top},menubar=no,toolbar=no,location=no,status=no,resizable=yes`
  );
  if (win) {
    win.focus();
    setTimeout(broadcastHudState, 300);
    showNotification("Mini HUD Window Opened! Keep it floating beside Brave.");
  } else {
    alert("Please allow popups for this site so the floating HUD can open!");
  }
}

function buildPhaseConfig(preset) {
  let accumSec = 0;
  const totalSec = preset.totalMinutes * 60;
  const colors = ["cyan", "violet", "emerald", "rose"];

  const builtPhases = preset.phases.map((p, idx) => {
    const durSec = p.minutes * 60;
    const startSec = accumSec;
    const endSec = accumSec + durSec;
    accumSec += durSec;

    const startMin = Math.floor(startSec / 60);
    const startRemSec = startSec % 60;
    const endMin = Math.floor(endSec / 60);
    const endRemSec = endSec % 60;

    const label = `${String(startMin).padStart(2, '0')}:${String(startRemSec).padStart(2, '0')} - ${String(endMin).padStart(2, '0')}:${String(endRemSec).padStart(2, '0')}`;
    const pct = Math.max(8, Math.round((durSec / totalSec) * 100));

    return {
      id: p.id,
      name: p.name,
      minutes: p.minutes,
      durationSec: durSec,
      startSec: startSec,
      endSec: endSec,
      label: label,
      pct: pct,
      color: colors[idx]
    };
  });

  return {
    totalMinutes: preset.totalMinutes,
    totalDurationSec: totalSec,
    phases: builtPhases
  };
}

// Apply HUD Preset dynamically
function applyHudPreset(presetKey, customObj = null, resetClock = true) {
  let presetData = customObj;
  if (!presetData) {
    presetData = HUD_PRESETS[presetKey] || HUD_PRESETS["15m"];
  }

  state.activePresetKey = presetKey;
  state.phaseConfig = buildPhaseConfig(presetData);

  // Update Stepper range text
  state.phaseConfig.phases.forEach(p => {
    const rangeEl = document.getElementById(`step-${p.id}-range`);
    if (rangeEl) rangeEl.textContent = p.label;
    const barEl = document.getElementById(`phase-bar-${p.id}`);
    if (barEl) barEl.style.width = `${p.pct}%`;
  });

  // Update Preset button styles
  document.querySelectorAll('.hud-preset-btn').forEach(btn => {
    if (btn.dataset.preset === presetKey) {
      btn.className = "hud-preset-btn active px-3 py-1.5 rounded-md bg-surface3 text-amber-400 border border-borderMedium font-bold transition text-xs shadow-sm";
    } else {
      btn.className = "hud-preset-btn px-3 py-1.5 rounded-md bg-surface2 text-slate-300 hover:text-white font-medium transition text-xs";
    }
  });

  const customBtn = document.getElementById('btn-custom-timer');
  if (customBtn) {
    if (presetKey === 'custom') {
      customBtn.className = "px-2.5 py-1.5 rounded-md bg-surface3 text-amber-400 font-bold border border-amber-500/50 transition text-xs";
      customBtn.innerHTML = `<span>Custom (${presetData.totalMinutes}m)</span>`;
    } else {
      customBtn.className = "px-2.5 py-1.5 rounded-md bg-surface2 text-slate-300 hover:text-amber-400 font-medium transition border border-dashed border-borderMedium text-xs";
      customBtn.innerHTML = `<span>Custom</span>`;
    }
  }

  // Save to localStorage
  try {
    localStorage.setItem('dsa_hud_preset', presetKey);
    if (customObj) {
      localStorage.setItem('dsa_hud_custom', JSON.stringify(customObj));
    }
  } catch (e) {}

  if (resetClock) {
    resetTimer();
  } else {
    updateTimerUI();
  }
}

// Add extra time (+1m / +5m)
function addExtraTime(minutes) {
  const extraSec = minutes * 60;
  state.timerSeconds += extraSec;
  updateTimerUI();
  showNotification(`+${minutes} minute${minutes > 1 ? 's' : ''} added to HUD!`);
}

// Toggle Compact / Focus view
function toggleCompactHud() {
  state.isCompactHud = !state.isCompactHud;
  const stepper = document.getElementById('protocol-stepper-container');
  const icon = document.getElementById('compact-icon');
  const text = document.getElementById('compact-text');

  if (state.isCompactHud) {
    if (stepper) stepper.classList.add('hidden');
    if (icon) icon.textContent = "⊞";
    if (text) text.textContent = "Full View";
    showNotification("Compact Focus HUD Active");
  } else {
    if (stepper) stepper.classList.remove('hidden');
    if (icon) icon.textContent = "⊟";
    if (text) text.textContent = "Compact View";
  }
}

// Initialize Application
async function initApp() {
  try {
    const res = await fetch('/api/init');
    const data = await res.json();
    state.activeSheetSlug = data.sheet_slug || 'core-path';
    state.problems = data.problems || [];
    state.chapters = data.chapters || [];
    state.progress = data.progress || {};
    state.soundEnabled = state.progress.sound_enabled !== false;
    
    // Set current problem from saved state
    state.currentProblemId = state.progress.current_problem_id || 1;

    // Update active sheet title
    const activeSheetNameEl = document.getElementById('active-sheet-name');
    if (activeSheetNameEl) {
      const titles = {
        'core-path': 'The Core Path (610)',
        'striver-sde': "Striver's SDE (95)",
        'neetcode-150': 'NeetCode 150',
        'blind-75': 'Blind 75'
      };
      activeSheetNameEl.textContent = titles[state.activeSheetSlug] || (data.sheet_title || state.activeSheetSlug);
    }

    // Load saved HUD preset or default 15m
    const savedPreset = localStorage.getItem('dsa_hud_preset') || '15m';
    let savedCustom = null;
    try {
      savedCustom = JSON.parse(localStorage.getItem('dsa_hud_custom'));
    } catch (e) {}
    applyHudPreset(savedPreset, savedPreset === 'custom' ? savedCustom : null, false);

    updateSoundIcon();
    renderStats();
    renderSidebar();
    renderCurriculumTable();
    selectProblem(state.currentProblemId, false);
    setupEventListeners();
    await loadSheetsList();
  } catch (err) {
    console.error("Failed to load initial data:", err);
  }
}

// Sound Synthesis using Web Audio API
function playSound(type) {
  if (!state.soundEnabled) return;
  try {
    if (!state.audioCtx) {
      state.audioCtx = new (window.AudioContext || window.webkitAudioContext)();
    }
    const ctx = state.audioCtx;
    if (ctx.state === 'suspended') {
      ctx.resume();
    }

    const now = ctx.currentTime;
    const osc = ctx.createOscillator();
    const gain = ctx.createGain();
    osc.connect(gain);
    gain.connect(ctx.destination);

    if (type === 'phase') {
      // Gentle dual-tone chime
      osc.type = 'sine';
      osc.frequency.setValueAtTime(587.33, now); // D5
      osc.frequency.exponentialRampToValueAtTime(880, now + 0.15); // A5
      gain.gain.setValueAtTime(0.2, now);
      gain.gain.exponentialRampToValueAtTime(0.001, now + 0.5);
      osc.start(now);
      osc.stop(now + 0.5);
    } else if (type === 'alert') {
      // Cap chime
      osc.type = 'triangle';
      osc.frequency.setValueAtTime(440, now);
      osc.frequency.setValueAtTime(554.37, now + 0.15);
      osc.frequency.setValueAtTime(659.25, now + 0.3);
      gain.gain.setValueAtTime(0.3, now);
      gain.gain.exponentialRampToValueAtTime(0.001, now + 0.7);
      osc.start(now);
      osc.stop(now + 0.7);
    } else if (type === 'success') {
      // Solved success arpeggio
      const notes = [523.25, 659.25, 783.99, 1046.5]; // C5, E5, G5, C6
      notes.forEach((freq, idx) => {
        const subOsc = ctx.createOscillator();
        const subGain = ctx.createGain();
        subOsc.connect(subGain);
        subGain.connect(ctx.destination);
        subOsc.type = 'sine';
        subOsc.frequency.setValueAtTime(freq, now + idx * 0.08);
        subGain.gain.setValueAtTime(0.18, now + idx * 0.08);
        subGain.gain.exponentialRampToValueAtTime(0.001, now + idx * 0.08 + 0.4);
        subOsc.start(now + idx * 0.08);
        subOsc.stop(now + idx * 0.08 + 0.45);
      });
    }
  } catch (e) {
    console.warn("Audio playback issue:", e);
  }
}

// Timer Logic
function startTimer() {
  if (state.timerRunning) return;
  state.timerRunning = true;
  updateTimerUI();

  state.timerInterval = setInterval(() => {
    if (state.timerSeconds > 0) {
      state.timerSeconds--;
      state.timerElapsed++;
      
      // Check Phase Transition
      checkPhaseTransition();
      updateTimerUI();
    } else {
      // Cap reached!
      pauseTimer();
      setPhase(4);
      playSound('alert');
      const totalMins = state.phaseConfig ? state.phaseConfig.totalMinutes : 15;
      alert(`⏱ ${totalMins}-Minute Cap Reached! Stop struggling. Switch to Phase 4: Read the hint, understand WHY, and code it from memory.`);
    }
  }, 1000);
}

function pauseTimer() {
  state.timerRunning = false;
  clearInterval(state.timerInterval);
  updateTimerUI();
}

function toggleTimer() {
  if (state.timerRunning) {
    pauseTimer();
  } else {
    startTimer();
  }
}

function resetTimer() {
  pauseTimer();
  if (!state.phaseConfig) {
    applyHudPreset('15m', null, false);
  }
  state.timerSeconds = state.phaseConfig.totalDurationSec;
  state.timerElapsed = 0;
  setPhase(1);
  updateTimerUI();
}

function checkPhaseTransition() {
  if (!state.phaseConfig) return;
  const elapsed = state.timerElapsed;
  let newPhase = 1;
  const phases = state.phaseConfig.phases;
  for (let i = 0; i < phases.length; i++) {
    if (elapsed >= phases[i].startSec) {
      newPhase = phases[i].id;
    }
  }

  if (newPhase !== state.activePhase) {
    setPhase(newPhase);
    playSound('phase');
  }
}

function setPhase(phaseNum) {
  state.activePhase = phaseNum;

  // Update Stepper buttons
  document.querySelectorAll('.protocol-step').forEach(btn => {
    const p = parseInt(btn.dataset.phase);
    if (p === phaseNum) {
      btn.classList.add('active');
      btn.style.opacity = '1';
    } else {
      btn.classList.remove('active');
      btn.style.opacity = '0.6';
    }
  });

  // Switch phase panels
  for (let i = 1; i <= 4; i++) {
    const el = document.getElementById(`phase-content-${i}`);
    if (el) {
      if (i === phaseNum) {
        el.classList.remove('hidden');
      } else {
        el.classList.add('hidden');
      }
    }
  }

  // Update Timer Ambient Glow & text from phaseConfig
  const glow = document.getElementById('timer-ambient-glow');
  const phaseTag = document.getElementById('timer-phase-tag');
  const instruction = document.getElementById('timer-instruction');

  const curPhase = state.phaseConfig?.phases.find(p => p.id === phaseNum);
  const phaseName = curPhase ? curPhase.name : (phaseNum === 1 ? "Read & Trace" : (phaseNum === 2 ? "Pick a Pattern" : (phaseNum === 3 ? "Code & Test" : "Cut Your Losses")));
  const phaseRange = curPhase ? curPhase.label : "";

  if (phaseNum === 1) {
    if (glow) glow.className = "hidden";
    phaseTag.className = "text-xs font-mono px-2 py-0.5 rounded font-bold uppercase bg-sky-500/15 text-sky-400 border border-sky-500/30";
    phaseTag.textContent = `Phase 1: ${phaseName} (${phaseRange})`;
    instruction.textContent = "Read constraints and sketch edge cases on pen & paper.";
  } else if (phaseNum === 2) {
    if (glow) glow.className = "hidden";
    phaseTag.className = "text-xs font-mono px-2 py-0.5 rounded font-bold uppercase bg-indigo-500/15 text-indigo-400 border border-indigo-500/30";
    phaseTag.textContent = `Phase 2: ${phaseName} (${phaseRange})`;
    instruction.textContent = "Map to known pattern. Start with brute force if needed.";
  } else if (phaseNum === 3) {
    if (glow) glow.className = "hidden";
    phaseTag.className = "text-xs font-mono px-2 py-0.5 rounded font-bold uppercase bg-emerald-500/15 text-emerald-400 border border-emerald-500/30";
    phaseTag.textContent = `Phase 3: ${phaseName} (${phaseRange})`;
    instruction.textContent = "Code cleanly in Brave. Dry-run test cases before submitting.";
  } else if (phaseNum === 4) {
    if (glow) glow.className = "hidden";
    phaseTag.className = "text-xs font-mono px-2 py-0.5 rounded font-bold uppercase bg-rose-500/15 text-rose-400 border border-rose-500/30";
    phaseTag.textContent = `Phase 4: ${phaseName} (${phaseRange})`;
    instruction.textContent = "Time cap reached! Stop struggling. Read the hint, understand WHY, code from memory.";
  }

  // Update In-Page Docked Floating Mini Timer
  const dockedDot = document.getElementById('docked-phase-dot');
  const dockedName = document.getElementById('docked-phase-name');
  if (dockedDot && dockedName) {
    if (phaseNum === 1) {
      dockedDot.className = "w-2.5 h-2.5 rounded-full bg-cyan-400 animate-pulse";
      dockedName.className = "text-[9px] font-mono font-bold px-1 rounded bg-cyan-500/20 text-cyan-300";
      dockedName.textContent = "P1 Read";
    } else if (phaseNum === 2) {
      dockedDot.className = "w-2.5 h-2.5 rounded-full bg-violet-400 animate-pulse";
      dockedName.className = "text-[9px] font-mono font-bold px-1 rounded bg-violet-500/20 text-violet-300";
      dockedName.textContent = "P2 Pattern";
    } else if (phaseNum === 3) {
      dockedDot.className = "w-2.5 h-2.5 rounded-full bg-emerald-400 animate-pulse";
      dockedName.className = "text-[9px] font-mono font-bold px-1 rounded bg-emerald-500/20 text-emerald-300";
      dockedName.textContent = "P3 Code";
    } else if (phaseNum === 4) {
      dockedDot.className = "w-2.5 h-2.5 rounded-full bg-rose-400 animate-ping";
      dockedName.className = "text-[9px] font-mono font-bold px-1 rounded bg-rose-500/20 text-rose-300";
      dockedName.textContent = "P4 Cut Losses";
    }
  }

  broadcastHudState();
}

function updateTimerUI() {
  const mins = Math.floor(state.timerSeconds / 60);
  const secs = state.timerSeconds % 60;
  const timerStr = `${String(mins).padStart(2, '0')}:${String(secs).padStart(2, '0')}`;
  
  const displayEl = document.getElementById('timer-display');
  if (displayEl) {
    displayEl.textContent = timerStr;
  }

  // Update Docked Mini Timer
  const dockedDisplay = document.getElementById('docked-timer-display');
  if (dockedDisplay) {
    dockedDisplay.textContent = timerStr;
  }

  const toggleBtn = document.getElementById('btn-timer-toggle');
  const toggleText = document.getElementById('timer-toggle-text');
  const toggleIcon = document.getElementById('timer-icon-play');

  const dockedBtn = document.getElementById('btn-docked-toggle');
  const dockedIcon = document.getElementById('docked-icon-play');

  if (state.timerRunning) {
    if (toggleBtn) {
      toggleBtn.classList.remove('bg-amber-500', 'hover:bg-amber-600');
      toggleBtn.classList.add('bg-amber-600', 'hover:bg-amber-700');
    }
    if (toggleText) toggleText.textContent = "Pause Timer";
    if (toggleIcon) toggleIcon.innerHTML = `<path fill-rule="evenodd" d="M18 10a8 8 0 11-16 0 8 8 0 0116 0zM7 8a1 1 0 012 0v4a1 1 0 11-2 0V8zm5-1a1 1 0 00-1 1v4a1 1 0 102 0V8a1 1 0 00-1-1z" clip-rule="evenodd"/>`;
    
    if (dockedBtn) {
      dockedBtn.classList.remove('bg-amber-500', 'hover:bg-amber-600');
      dockedBtn.classList.add('bg-amber-600', 'hover:bg-amber-700');
    }
    if (dockedIcon) dockedIcon.innerHTML = `<path fill-rule="evenodd" d="M18 10a8 8 0 11-16 0 8 8 0 0116 0zM7 8a1 1 0 012 0v4a1 1 0 11-2 0V8zm5-1a1 1 0 00-1 1v4a1 1 0 102 0V8a1 1 0 00-1-1z" clip-rule="evenodd"/>`;
  } else {
    if (toggleBtn) {
      toggleBtn.classList.add('bg-amber-500', 'hover:bg-amber-600');
      toggleBtn.classList.remove('bg-amber-600', 'hover:bg-amber-700');
    }
    if (toggleText) toggleText.textContent = "Start Timer";
    if (toggleIcon) toggleIcon.innerHTML = `<path fill-rule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zM9.555 7.168A1 1 0 008 8v4a1 1 0 001.555.832l3-2a1 1 0 000-1.664l-3-2z" clip-rule="evenodd"/>`;

    if (dockedBtn) {
      dockedBtn.classList.add('bg-amber-500', 'hover:bg-amber-600');
      dockedBtn.classList.remove('bg-amber-600', 'hover:bg-amber-700');
    }
    if (dockedIcon) dockedIcon.innerHTML = `<path fill-rule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zM9.555 7.168A1 1 0 008 8v4a1 1 0 001.555.832l3-2a1 1 0 000-1.664l-3-2z" clip-rule="evenodd"/>`;
  }

  broadcastHudState();
}

// Problem Selection & Workspace Update
function selectProblem(problemId, autoScroll = true) {
  const prob = state.problems.find(p => p.id === problemId);
  if (!prob) return;

  state.currentProblemId = problemId;
  resetTimer();

  // Update Problem Header
  document.getElementById('prob-id-badge').textContent = `#${prob.id}`;
  document.getElementById('prob-title').textContent = prob.title;
  document.getElementById('prob-chapter-badge').textContent = `Chapter ${prob.chapter_id} · ${prob.chapter_name}`;
  
  // Difficulty Level badge
  const lvlBadge = document.getElementById('prob-level-badge');
  if (prob.level === 'E') {
    lvlBadge.className = "px-2 py-0.5 rounded text-[11px] font-bold uppercase tracking-wider bg-emerald-500/20 text-emerald-400 border border-emerald-500/30";
    lvlBadge.textContent = "Easy";
  } else if (prob.level === 'M') {
    lvlBadge.className = "px-2 py-0.5 rounded text-[11px] font-bold uppercase tracking-wider bg-amber-500/20 text-amber-400 border border-amber-500/30";
    lvlBadge.textContent = "Medium";
  } else {
    lvlBadge.className = "px-2 py-0.5 rounded text-[11px] font-bold uppercase tracking-wider bg-rose-500/20 text-rose-400 border border-rose-500/30";
    lvlBadge.textContent = "Hard";
  }

  // Lists badges (Blind 75 / NeetCode 150)
  const listContainer = document.getElementById('prob-list-badges');
  listContainer.innerHTML = '';
  (prob.lists || []).forEach(lst => {
    const pill = document.createElement('span');
    pill.className = "px-1.5 py-0.5 rounded text-[10px] font-mono font-semibold bg-indigo-500/20 text-indigo-300 border border-indigo-500/30";
    pill.textContent = lst;
    listContainer.appendChild(pill);
  });

  // Platform badge
  document.getElementById('prob-platform-badge').textContent = prob.platform;

  // Subhint / Core takeaway
  document.getElementById('prob-subhint-text').textContent = prob.hint;

  // Phase 4 Hint box (hidden initially)
  const hintBox = document.getElementById('hint-display-box');
  hintBox.classList.add('hidden');
  hintBox.innerHTML = `<strong>Technique / Insight:</strong> ${escapeHtml(prob.hint)}<br><span class="text-slate-400 text-[11px] mt-1 block">Rule 2: Close this window, open a blank editor in Brave, and re-solve from memory!</span>`;
  document.getElementById('btn-reveal-hint').textContent = "👁 Reveal Hint & Technique";

  // Scratchpad
  const probData = (state.progress.problems && state.progress.problems[String(prob.id)]) || {};
  document.getElementById('scratchpad-input').value = probData.scratchpad || '';
  
  // Pattern selection
  const selectedPattern = probData.pattern || '';
  document.querySelectorAll('.pattern-pill').forEach(pill => {
    if (pill.dataset.pattern === selectedPattern) {
      pill.classList.add('active');
    } else {
      pill.classList.remove('active');
    }
  });

  // Uncheck checklist boxes
  document.querySelectorAll('.edge-check, .dryrun-check').forEach(cb => cb.checked = false);

  // Update Sidebar active state
  document.querySelectorAll('.problem-item').forEach(item => {
    if (parseInt(item.dataset.id) === prob.id) {
      item.classList.add('active');
      if (autoScroll) {
        item.scrollIntoView({ behavior: 'smooth', block: 'nearest' });
      }
    } else {
      item.classList.remove('active');
    }
  });

  // Update current badge text in sidebar
  document.getElementById('current-badge-text').textContent = `#${prob.id} ${prob.title.slice(0, 16)}`;

  // Save current problem ID to settings
  saveSetting({ current_problem_id: prob.id });
}

// Open In Brave Handler
async function openCurrentInBrave() {
  const prob = state.problems.find(p => p.id === state.currentProblemId);
  if (!prob) return;

  const btn = document.getElementById('btn-open-brave');
  const origText = btn.innerHTML;
  btn.innerHTML = `<span class="animate-spin text-white">⏳</span><span>Opening Brave...</span>`;

  try {
    const res = await fetch('/api/open-brave', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ problem_id: prob.id, url: prob.url })
    });
    const result = await res.json();
    if (!result.launched_in_brave) {
      // Fallback: open directly via window.open
      window.open(prob.url, '_blank');
    }
  } catch (err) {
    console.warn("Backend open error, using direct browser link:", err);
    window.open(prob.url, '_blank');
  } finally {
    setTimeout(() => {
      btn.innerHTML = origText;
    }, 600);
  }
}

// Save Status & Spaced Repetition Updates
async function saveStatus(status, errorType = "", errorNote = "", targetProbId = null) {
  const probId = targetProbId || state.currentProblemId;
  const timeSpent = (probId === state.currentProblemId) ? state.timerElapsed : 0;
  const scratchpad = (probId === state.currentProblemId) ? (document.getElementById('scratchpad-input')?.value || "") : "";
  
  // Find selected pattern
  let selectedPattern = "";
  const activePatternPill = document.querySelector('.pattern-pill.active');
  if (activePatternPill && probId === state.currentProblemId) {
    selectedPattern = activePatternPill.dataset.pattern || "";
  }

  const payload = {
    problem_id: probId,
    status: status,
    time_spent: timeSpent,
    pattern: selectedPattern,
    error_type: errorType,
    error_note: errorNote,
    scratchpad: scratchpad
  };

  try {
    const res = await fetch('/api/progress/status', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(payload)
    });
    const result = await res.json();
    if (result.status === 'ok') {
      if (!state.progress.problems) state.progress.problems = {};
      if (!state.progress.problems[String(probId)]) state.progress.problems[String(probId)] = {};
      state.progress.problems[String(probId)].status = status;
      state.progress.problems[String(probId)].time_spent = timeSpent;
      if (selectedPattern) state.progress.problems[String(probId)].pattern = selectedPattern;
      
      if (status === 'clean' || status === 'help') {
        playSound('success');
      }

      // Re-render UI
      renderStats();
      renderSidebar();
      renderCurriculumTable();

      // Show brief toast
      if (status === 'clean') showNotification('✓ Solved!');
      else if (status === 'help') showNotification('⚡ Scheduled for Re-solve (Rule 3)');
      else if (status === 'failed') showNotification('✕ Logged to Error Queue');
      else showNotification('Status reset to uncompleted');
    }
  } catch (e) {
    console.error("Failed to update status:", e);
  }
}

// Toggle Problem Completion Checkbox (Instant Sheet Roadmap Action)
function toggleProblemCheckbox(probId, e) {
  if (e) {
    e.stopPropagation();
  }
  const pData = (state.progress.problems && state.progress.problems[String(probId)]) || {};
  const currentStatus = pData.status || 'unsolved';
  
  if (currentStatus === 'clean' || currentStatus === 'help') {
    saveStatus('unsolved', '', '', probId);
  } else {
    saveStatus('clean', '', '', probId);
  }
}

// Scratchpad Auto-save
let saveNotesTimeout = null;
function handleScratchpadChange() {
  const statusEl = document.getElementById('scratchpad-status');
  statusEl.textContent = "Saving...";
  
  clearTimeout(saveNotesTimeout);
  saveNotesTimeout = setTimeout(async () => {
    const text = document.getElementById('scratchpad-input').value;
    try {
      await fetch('/api/progress/notes', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ problem_id: state.currentProblemId, scratchpad: text })
      });
      statusEl.textContent = "Auto-saved";
    } catch (e) {
      statusEl.textContent = "Save error";
    }
  }, 800);
}

// Render Sidebar Chapters & Problems
function renderSidebar() {
  const container = document.getElementById('chapter-list-container');
  container.innerHTML = '';

  const query = state.searchQuery.toLowerCase();
  const filter = state.activeFilter;

  // Filter problems
  const filteredProblems = state.problems.filter(p => {
    const pData = (state.progress.problems && state.progress.problems[String(p.id)]) || {};
    const status = pData.status || 'unsolved';

    // Search query match
    if (query) {
      const matchTitle = p.title.toLowerCase().includes(query);
      const matchHint = p.hint.toLowerCase().includes(query);
      const matchChapter = p.chapter_name.toLowerCase().includes(query);
      const matchId = String(p.id) === query;
      if (!matchTitle && !matchHint && !matchChapter && !matchId) return false;
    }

    // Filter pill match
    if (filter === 'sprint') {
      return (p.lists || []).some(l => l.includes('Blind 75') || l.includes('NeetCode 150'));
    } else if (filter === 'unsolved') {
      return status === 'unsolved' || status === 'failed';
    } else if (filter === 'solved') {
      return status === 'clean' || status === 'help';
    } else if (filter === 'review') {
      return status === 'help' || status === 'failed';
    }

    return true;
  });

  // Group by chapter
  const chapterGroups = {};
  filteredProblems.forEach(p => {
    if (!chapterGroups[p.chapter_id]) {
      chapterGroups[p.chapter_id] = [];
    }
    chapterGroups[p.chapter_id].push(p);
  });

  state.chapters.forEach(ch => {
    const probs = chapterGroups[ch.id] || [];
    if (probs.length === 0 && (query || filter !== 'all')) return;

    // Calculate chapter progress
    const allChProbs = state.problems.filter(p => p.chapter_id === ch.id);
    const solvedCount = allChProbs.filter(p => {
      const pData = (state.progress.problems && state.progress.problems[String(p.id)]) || {};
      return pData.status === 'clean' || pData.status === 'help';
    }).length;

    const chapterSection = document.createElement('div');
    chapterSection.className = "chapter-section";

    // Header
    const isCurrentCh = allChProbs.some(p => p.id === state.currentProblemId);
    const isExpanded = isCurrentCh || query !== '';
    const chPct = Math.round((solvedCount / ch.count) * 100);

    chapterSection.innerHTML = `
      <div class="chapter-header px-3.5 py-2.5 bg-surface1 hover:bg-surface2 cursor-pointer flex items-center justify-between text-xs transition select-none border-b border-borderSubtle">
        <div class="flex items-center space-x-2 truncate">
          <span class="text-amber-400 font-bold font-mono text-[11px] bg-surface3 px-1.5 py-0.5 rounded">Ch ${ch.id}</span>
          <span class="font-semibold text-slate-200 truncate">${escapeHtml(ch.name)}</span>
        </div>
        <div class="flex items-center space-x-2 text-[11px] font-mono shrink-0">
          <div class="w-10 h-1.5 bg-surface3 rounded-full overflow-hidden hidden sm:block">
            <div class="h-full bg-emerald-500 transition-all duration-300" style="width: ${chPct}%"></div>
          </div>
          <span class="${solvedCount === ch.count ? 'text-emerald-400 font-bold' : 'text-slate-400'}">${solvedCount}/${ch.count}</span>
          <svg class="w-3.5 h-3.5 text-slate-500 transform transition-transform ${isExpanded ? 'rotate-90' : ''}" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 5l7 7-7 7"/></svg>
        </div>
      </div>
      <div class="problem-sublist divide-y divide-borderSubtle ${isExpanded ? '' : 'hidden'}">
        ${probs.map(p => {
          const pData = (state.progress.problems && state.progress.problems[String(p.id)]) || {};
          const status = pData.status || 'unsolved';
          
          let statusIcon = `<span class="w-3.5 h-3.5 rounded-full border border-slate-600 inline-block"></span>`;
          if (status === 'clean') {
            statusIcon = `<span class="w-4 h-4 rounded-full bg-emerald-500/20 text-emerald-400 flex items-center justify-center font-bold text-[10px]">✓</span>`;
          } else if (status === 'help') {
            statusIcon = `<span class="w-4 h-4 rounded-full bg-amber-500/20 text-amber-400 flex items-center justify-center font-bold text-[10px]">↻</span>`;
          } else if (status === 'failed') {
            statusIcon = `<span class="w-4 h-4 rounded-full bg-rose-500/20 text-rose-400 flex items-center justify-center font-bold text-[10px]">✕</span>`;
          }

          let lvlBadge = `<span class="px-1.5 py-0.5 rounded text-[9px] font-bold font-mono bg-emerald-500/15 text-emerald-400 border border-emerald-500/25">EASY</span>`;
          if (p.level === 'M') {
            lvlBadge = `<span class="px-1.5 py-0.5 rounded text-[9px] font-bold font-mono bg-amber-500/15 text-amber-400 border border-amber-500/25">MED</span>`;
          } else if (p.level === 'H') {
            lvlBadge = `<span class="px-1.5 py-0.5 rounded text-[9px] font-bold font-mono bg-rose-500/15 text-rose-400 border border-rose-500/25">HARD</span>`;
          }

          const isCurrent = p.id === state.currentProblemId;

          return `
            <div class="problem-item px-3.5 py-2 cursor-pointer flex items-center justify-between text-xs transition ${isCurrent ? 'active' : ''}" data-id="${p.id}">
              <div class="flex items-center space-x-2.5 truncate mr-2">
                <span class="w-4 flex justify-center shrink-0">${statusIcon}</span>
                <span class="font-mono text-slate-500 text-[11px] shrink-0">#${p.id}</span>
                <span class="text-slate-200 truncate ${isCurrent ? 'font-bold text-white' : 'hover:text-slate-100'}">${escapeHtml(p.title)}</span>
              </div>
              <div class="flex items-center space-x-1.5 shrink-0">
                ${(p.lists && p.lists.length > 0) ? `<span class="text-[9px] px-1 rounded bg-surface3 text-slate-300 font-mono border border-borderSubtle">${p.lists[0].includes('75') ? 'B75' : 'NC'}</span>` : ''}
                ${lvlBadge}
              </div>
            </div>
          `;
        }).join('')}
      </div>
    `;

    // Toggle expand/collapse
    chapterSection.querySelector('.chapter-header').addEventListener('click', (e) => {
      const sublist = chapterSection.querySelector('.problem-sublist');
      const arrow = chapterSection.querySelector('svg');
      sublist.classList.toggle('hidden');
      arrow.classList.toggle('rotate-90');
    });

    // Item click
    chapterSection.querySelectorAll('.problem-item').forEach(item => {
      item.addEventListener('click', () => {
        const id = parseInt(item.dataset.id);
        selectProblem(id);
      });
    });

    container.appendChild(chapterSection);
  });
}

// Helper to check if a problem is completed
function isProblemSolved(probId) {
  const pData = (state.progress.problems && state.progress.problems[String(probId)]) || {};
  return pData.status === 'clean' || pData.status === 'help';
}

// Render Top Stats & Overall Progress (TakeUForward Gold Standard Metrics)
function renderStats() {
  const total = state.problems.length || 610;
  
  let easyTotal = 0;
  let easySolved = 0;
  let medTotal = 0;
  let medSolved = 0;
  let hardTotal = 0;
  let hardSolved = 0;

  state.problems.forEach(p => {
    const solved = isProblemSolved(p.id);
    if (p.level === 'E') {
      easyTotal++;
      if (solved) easySolved++;
    } else if (p.level === 'M') {
      medTotal++;
      if (solved) medSolved++;
    } else if (p.level === 'H') {
      hardTotal++;
      if (solved) hardSolved++;
    }
  });

  const totalSolved = easySolved + medSolved + hardSolved;
  const pct = total > 0 ? Math.round((totalSolved / total) * 100) : 0;

  // Header overall stat text
  const overallTextEl = document.getElementById('overall-progress-text');
  if (overallTextEl) {
    overallTextEl.textContent = `${totalSolved} / ${total} (${pct}%)`;
  }

  // Daily target
  const goal = state.progress.daily_goal || 3;
  const todayCount = state.progress.today_solved_count || 0;
  const dailyProgEl = document.getElementById('stat-daily-progress');
  if (dailyProgEl) {
    dailyProgEl.textContent = `${todayCount} / ${goal}`;
  }
  const dailyBarEl = document.getElementById('stat-daily-bar');
  if (dailyBarEl) {
    const barPct = Math.min(100, Math.round((todayCount / goal) * 100));
    dailyBarEl.style.width = `${barPct}%`;
  }

  // Streak
  const streakEl = document.getElementById('stat-streak');
  if (streakEl) {
    const streak = state.progress.streak || 1;
    streakEl.textContent = `${streak} day${streak > 1 ? 's' : ''}`;
  }

  // Hero Donut Ring (Circumference of r=42 is 2 * PI * 42 ~= 263.89)
  const donutPctEl = document.getElementById('hero-donut-pct');
  if (donutPctEl) {
    donutPctEl.textContent = `${pct}%`;
  }
  const donutCircleEl = document.getElementById('hero-donut-circle');
  if (donutCircleEl) {
    const circumference = 263.89;
    const offset = circumference - (pct / 100) * circumference;
    donutCircleEl.style.strokeDashoffset = offset;
  }

  // Difficulty metrics
  const easyCountEl = document.getElementById('stat-easy-count');
  if (easyCountEl) easyCountEl.textContent = `${easySolved} / ${easyTotal}`;
  const easyBarEl = document.getElementById('stat-easy-bar');
  if (easyBarEl) easyBarEl.style.width = `${easyTotal > 0 ? Math.round((easySolved / easyTotal) * 100) : 0}%`;

  const medCountEl = document.getElementById('stat-med-count');
  if (medCountEl) medCountEl.textContent = `${medSolved} / ${medTotal}`;
  const medBarEl = document.getElementById('stat-med-bar');
  if (medBarEl) medBarEl.style.width = `${medTotal > 0 ? Math.round((medSolved / medTotal) * 100) : 0}%`;

  const hardCountEl = document.getElementById('stat-hard-count');
  if (hardCountEl) hardCountEl.textContent = `${hardSolved} / ${hardTotal}`;
  const hardBarEl = document.getElementById('stat-hard-bar');
  if (hardBarEl) hardBarEl.style.width = `${hardTotal > 0 ? Math.round((hardSolved / hardTotal) * 100) : 0}%`;

  // Hero Curriculum Header details
  const badgeCountEl = document.getElementById('curriculum-badge-count');
  if (badgeCountEl) badgeCountEl.textContent = `${total} Problems`;

  const heroTitleEl = document.getElementById('curriculum-hero-title');
  if (heroTitleEl) {
    const titles = {
      'core-path': 'The Core Path (610)',
      'striver-sde': "Striver's SDE Sheet (95)",
      'neetcode-150': 'NeetCode 150',
      'blind-75': 'Blind 75'
    };
    heroTitleEl.textContent = titles[state.activeSheetSlug] || state.activeSheetSlug || 'Curriculum Sheet';
  }

  // Hero Resume Button problem title
  const currProb = state.problems.find(p => p.id === state.currentProblemId) || state.problems[0];
  const heroCurrentTitleEl = document.getElementById('hero-current-title');
  if (heroCurrentTitleEl && currProb) {
    heroCurrentTitleEl.textContent = `#${currProb.id} ${currProb.title}`;
  }
}

// Dual-Mode View Switcher: TakeUForward Sheet Roadmap vs 15m Protocol Solver HUD
function switchView(viewName) {
  const curriculumView = document.getElementById('view-curriculum');
  const solverView = document.getElementById('view-solver');
  const navCurriculum = document.getElementById('nav-btn-curriculum');
  const navSolver = document.getElementById('nav-btn-solver');

  if (viewName === 'solver') {
    if (curriculumView) curriculumView.classList.add('hidden');
    if (solverView) solverView.classList.remove('hidden');

    if (navCurriculum) {
      navCurriculum.classList.remove('active', 'bg-surface3', 'text-amber-400');
      navCurriculum.classList.add('text-slate-300');
    }
    if (navSolver) {
      navSolver.classList.add('active', 'bg-surface3', 'text-amber-400');
      navSolver.classList.remove('text-slate-300');
    }
    renderSidebar();
  } else {
    // viewName === 'curriculum'
    if (curriculumView) curriculumView.classList.remove('hidden');
    if (solverView) solverView.classList.add('hidden');

    if (navCurriculum) {
      navCurriculum.classList.add('active', 'bg-surface3', 'text-amber-400');
      navCurriculum.classList.remove('text-slate-300');
    }
    if (navSolver) {
      navSolver.classList.remove('active', 'bg-surface3', 'text-amber-400');
      navSolver.classList.add('text-slate-300');
    }
    renderCurriculumTable();
    renderStats();
  }
}

// Resume Current Problem in 15m Protocol Solver
function resumeCurrentProblem() {
  selectProblem(state.currentProblemId || 1);
  switchView('solver');
}

// Pick a Random Unsolved Problem
function pickRandomProblem() {
  if (!state.problems || state.problems.length === 0) return;
  const unsolved = state.problems.filter(p => !isProblemSolved(p.id));
  const pool = unsolved.length > 0 ? unsolved : state.problems;
  const chosen = pool[Math.floor(Math.random() * pool.length)];
  if (chosen) {
    selectProblem(chosen.id);
    switchView('solver');
    showNotification(`🎲 Picked Random Problem: #${chosen.id} ${chosen.title}`);
  }
}

// Toggle Expanding or Collapsing All Curriculum Accordions
function toggleAllAccordions() {
  state.allAccordionsExpanded = !state.allAccordionsExpanded;
  const btnText = document.getElementById('accordion-toggle-text');
  if (btnText) {
    btnText.textContent = state.allAccordionsExpanded ? "Collapse All" : "Expand All";
  }
  const bodies = document.querySelectorAll('.curriculum-accordion-body');
  const arrows = document.querySelectorAll('.accordion-arrow-btn svg');
  bodies.forEach(b => {
    if (state.allAccordionsExpanded) {
      b.classList.remove('hidden');
    } else {
      b.classList.add('hidden');
    }
  });
  arrows.forEach(a => {
    a.classList.toggle('rotate-180', state.allAccordionsExpanded);
  });
}

// Render Full TakeUForward-Style Sheet Roadmap with Topic Accordions & High-Density Tables
function renderCurriculumTable() {
  const container = document.getElementById('curriculum-table-container');
  if (!container) return;
  container.innerHTML = '';

  if (!state.problems || state.problems.length === 0) {
    container.innerHTML = `
      <div class="text-center py-16 bg-surface1 rounded-xl border border-borderDefault">
        <p class="text-slate-400 text-sm">No curriculum problems loaded for this sheet.</p>
      </div>
    `;
    return;
  }

  const query = (state.curriculumSearchQuery || '').toLowerCase().trim();
  const filter = state.curriculumFilter || 'all';

  // Filter problems
  const filteredProblems = state.problems.filter(p => {
    const solved = isProblemSolved(p.id);

    // Filter matching
    if (filter === 'unsolved' && solved) return false;
    if (filter === 'solved' && !solved) return false;
    if (filter === 'easy' && p.level !== 'E') return false;
    if (filter === 'medium' && p.level !== 'M') return false;
    if (filter === 'hard' && p.level !== 'H') return false;

    // Search query matching
    if (query) {
      const matchTitle = (p.title || '').toLowerCase().includes(query);
      const matchHint = (p.hint || '').toLowerCase().includes(query);
      const matchChapter = (p.chapter_name || '').toLowerCase().includes(query);
      const matchId = String(p.id) === query || `#${p.id}` === query;
      const matchLists = (p.lists || []).some(l => l.toLowerCase().includes(query));
      if (!matchTitle && !matchHint && !matchChapter && !matchId && !matchLists) return false;
    }

    return true;
  });

  // Group filtered problems by chapter_id
  const chapterGroups = {};
  filteredProblems.forEach(p => {
    if (!chapterGroups[p.chapter_id]) {
      chapterGroups[p.chapter_id] = [];
    }
    chapterGroups[p.chapter_id].push(p);
  });

  let visibleChapters = 0;

  state.chapters.forEach((ch) => {
    const probs = chapterGroups[ch.id] || [];
    if (probs.length === 0 && (query || filter !== 'all')) return;
    visibleChapters++;

    // Calculate chapter stats
    const allChProbs = state.problems.filter(p => p.chapter_id === ch.id);
    const totalInCh = allChProbs.length || ch.count || 1;
    const solvedInCh = allChProbs.filter(p => isProblemSolved(p.id)).length;
    const chPct = Math.round((solvedInCh / totalInCh) * 100);
    const isAllSolved = solvedInCh === totalInCh && totalInCh > 0;

    // Chapter Accordion Card
    const chCard = document.createElement('div');
    chCard.className = "bg-surface1 border border-borderDefault rounded-xl overflow-hidden transition shadow-sm mb-4";
    chCard.dataset.chapterId = ch.id;

    const isExpanded = state.allAccordionsExpanded !== false || query !== '';

    chCard.innerHTML = `
      <!-- Accordion Header -->
      <div class="curriculum-accordion-header px-4 sm:px-6 py-4 bg-surface1 hover:bg-surface2/60 cursor-pointer flex flex-col sm:flex-row sm:items-center justify-between gap-3 select-none transition border-b border-borderDefault">
        
        <div class="flex items-center space-x-3 truncate">
          <span class="px-2.5 py-1 rounded bg-amber-500/15 text-amber-400 font-mono text-xs font-bold shrink-0 border border-amber-500/25">
            Step ${ch.id}
          </span>
          <h3 class="text-sm sm:text-base font-bold text-slate-100 truncate">
            ${escapeHtml(ch.name)}
          </h3>
        </div>

        <div class="flex items-center justify-between sm:justify-end space-x-4 shrink-0 text-xs">
          <div class="flex items-center space-x-2">
            <div class="w-24 sm:w-32 h-2 bg-surface3 rounded-full overflow-hidden">
              <div class="h-full ${isAllSolved ? 'bg-emerald-400' : 'bg-amber-500'} transition-all duration-300" style="width: ${chPct}%"></div>
            </div>
            <span class="font-mono text-[11px] ${isAllSolved ? 'text-emerald-400 font-bold' : 'text-slate-400'}">
              ${solvedInCh}/${totalInCh} (${chPct}%)
            </span>
          </div>

          <button class="accordion-arrow-btn p-1 text-slate-400 hover:text-white transition" aria-label="Toggle Topic">
            <svg class="w-4 h-4 transform transition-transform duration-200 ${isExpanded ? 'rotate-180' : ''}" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 9l-7 7-7-7" />
            </svg>
          </button>
        </div>

      </div>

      <!-- Accordion Table Body -->
      <div class="curriculum-accordion-body ${isExpanded ? '' : 'hidden'} overflow-x-auto">
        <table class="w-full text-left text-xs border-collapse">
          <thead class="bg-surface2/60 text-slate-400 font-mono text-[10px] uppercase tracking-wider border-b border-borderSubtle">
            <tr>
              <th class="py-2.5 px-4 w-14 text-center">Status</th>
              <th class="py-2.5 px-3 w-16 text-slate-500 font-mono">#</th>
              <th class="py-2.5 px-4 font-semibold text-slate-300">Problem Title</th>
              <th class="py-2.5 px-3 w-24">Difficulty</th>
              <th class="py-2.5 px-4 hidden md:table-cell">Pattern / Technique</th>
              <th class="py-2.5 px-4 w-36 text-center">15m Protocol</th>
              <th class="py-2.5 px-4 w-24 text-right">Practice</th>
            </tr>
          </thead>
          <tbody class="divide-y divide-borderSubtle">
            ${probs.map(p => {
              const pData = (state.progress.problems && state.progress.problems[String(p.id)]) || {};
              const status = pData.status || 'unsolved';
              const isClean = status === 'clean';
              const isHelp = status === 'help';
              const isSolved = isClean || isHelp;

              let diffBadge = `<span class="px-2 py-0.5 rounded text-[10px] font-bold font-mono bg-emerald-500/15 text-emerald-400 border border-emerald-500/25">EASY</span>`;
              if (p.level === 'M') {
                diffBadge = `<span class="px-2 py-0.5 rounded text-[10px] font-bold font-mono bg-amber-500/15 text-amber-400 border border-amber-500/25">MED</span>`;
              } else if (p.level === 'H') {
                diffBadge = `<span class="px-2 py-0.5 rounded text-[10px] font-bold font-mono bg-rose-500/15 text-rose-400 border border-rose-500/25">HARD</span>`;
              }

              const isCurrent = p.id === state.currentProblemId;

              return `
                <tr class="curriculum-prob-row hover:bg-surface2/40 transition group ${isSolved ? 'bg-emerald-500/[0.02]' : ''} ${isCurrent ? 'bg-amber-500/[0.05]' : ''}" data-id="${p.id}">
                  
                  <!-- Status Checkbox -->
                  <td class="py-2.5 px-4 text-center shrink-0">
                    <button type="button" class="prob-checkbox-btn w-5 h-5 rounded-md border ${isSolved ? 'bg-emerald-500 border-emerald-400 text-slate-950 font-bold' : 'border-slate-600 bg-surface2 hover:border-amber-500'} flex items-center justify-center transition mx-auto" data-id="${p.id}" title="${isSolved ? 'Mark as Unsolved' : 'Mark as Solved'}">
                      ${isSolved ? '<svg class="w-3.5 h-3.5" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="3" d="M5 13l4 4L19 7"/></svg>' : ''}
                    </button>
                  </td>

                  <!-- Problem ID -->
                  <td class="py-2.5 px-3 font-mono text-slate-500 text-[11px]">
                    #${p.id}
                  </td>

                  <!-- Title & Tags -->
                  <td class="py-2.5 px-4">
                    <div class="flex items-center space-x-2">
                      <button class="btn-open-solver-title text-left font-medium ${isSolved ? 'text-slate-300' : 'text-slate-100'} hover:text-amber-400 transition" data-id="${p.id}">
                        ${escapeHtml(p.title)}
                      </button>
                      ${(p.lists && p.lists.length > 0) ? `
                        <span class="hidden sm:inline-block text-[9px] px-1.5 py-0.2 rounded bg-surface3 text-slate-400 font-mono border border-borderSubtle">
                          ${p.lists[0].includes('75') ? 'Blind 75' : (p.lists[0].includes('150') ? 'NC 150' : p.lists[0])}
                        </span>
                      ` : ''}
                    </div>
                  </td>

                  <!-- Difficulty -->
                  <td class="py-2.5 px-3 shrink-0">
                    ${diffBadge}
                  </td>

                  <!-- Pattern / Technique -->
                  <td class="py-2.5 px-4 hidden md:table-cell text-slate-400 font-mono text-[11px] truncate max-w-xs" title="${escapeHtml(p.hint || '')}">
                    ${escapeHtml(p.hint || 'Standard approach')}
                  </td>

                  <!-- 15m Protocol Execution Launcher -->
                  <td class="py-2.5 px-4 text-center shrink-0">
                    <button class="btn-launch-15m w-full px-2.5 py-1.5 rounded-lg bg-amber-500/10 hover:bg-amber-500 text-amber-400 hover:text-slate-950 font-bold font-mono text-[11px] border border-amber-500/30 transition flex items-center justify-center space-x-1 shadow-sm active:scale-98" data-id="${p.id}" title="Launch 15m Protocol HUD for #${p.id}">
                      <svg class="w-3 h-3" fill="currentColor" viewBox="0 0 20 20"><path fill-rule="evenodd" d="M11.3 1.046A1 1 0 0112 2v5h4a1 1 0 01.82 1.573l-7 10A1 1 0 018 18v-5H4a1 1 0 01-.82-1.573l7-10a1 1 0 011.12-.38z" clip-rule="evenodd"/></svg>
                      <span>⚡ Solve (15m)</span>
                    </button>
                  </td>

                  <!-- Practice Link -->
                  <td class="py-2.5 px-4 text-right shrink-0">
                    <a href="${p.url || `https://leetcode.com/problemset/all/?search=${encodeURIComponent(p.title)}`}" target="_blank" rel="noopener noreferrer" class="inline-flex items-center space-x-1 text-slate-400 hover:text-amber-400 font-medium transition text-[11px]" title="Open on LeetCode">
                      <span>LeetCode</span>
                      <svg class="w-3 h-3" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M10 6H6a2 2 0 00-2 2v10a2 2 0 002 2h10a2 2 0 002-2v-4M14 4h6m0 0v6m0-6L10 14"/></svg>
                    </a>
                  </td>

                </tr>
              `;
            }).join('')}
          </tbody>
        </table>
      </div>
    `;

    // Attach event listeners for accordion header toggle
    const header = chCard.querySelector('.curriculum-accordion-header');
    const body = chCard.querySelector('.curriculum-accordion-body');
    const arrow = chCard.querySelector('.accordion-arrow-btn svg');

    header.addEventListener('click', (e) => {
      if (e.target.closest('button')) return;
      const isHidden = body.classList.toggle('hidden');
      arrow.classList.toggle('rotate-180', !isHidden);
    });

    const arrowBtn = chCard.querySelector('.accordion-arrow-btn');
    arrowBtn.addEventListener('click', (e) => {
      e.stopPropagation();
      const isHidden = body.classList.toggle('hidden');
      arrow.classList.toggle('rotate-180', !isHidden);
    });

    // Attach Checkbox handlers
    chCard.querySelectorAll('.prob-checkbox-btn').forEach(btn => {
      btn.addEventListener('click', (e) => {
        e.stopPropagation();
        const pId = parseInt(btn.dataset.id);
        toggleProblemCheckbox(pId, e);
      });
    });

    // Attach Title Click -> Open in Solver
    chCard.querySelectorAll('.btn-open-solver-title').forEach(btn => {
      btn.addEventListener('click', () => {
        const pId = parseInt(btn.dataset.id);
        selectProblem(pId);
        switchView('solver');
      });
    });

    // Attach 15m Protocol Solve Button -> Open in Solver and start timer
    chCard.querySelectorAll('.btn-launch-15m').forEach(btn => {
      btn.addEventListener('click', () => {
        const pId = parseInt(btn.dataset.id);
        selectProblem(pId);
        switchView('solver');
        if (!state.timerRunning) {
          toggleTimer();
        }
      });
    });

    container.appendChild(chCard);
  });

  if (visibleChapters === 0) {
    container.innerHTML = `
      <div class="text-center py-16 bg-surface1 rounded-xl border border-borderDefault">
        <div class="w-12 h-12 rounded-full bg-surface2 flex items-center justify-center mx-auto mb-3 text-slate-500">
          <svg class="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z"/></svg>
        </div>
        <h3 class="text-slate-200 font-bold text-sm">No problems found</h3>
        <p class="text-slate-400 text-xs mt-1">Try clearing your search query or switching filters.</p>
      </div>
    `;
  }
}

// Show temporary notification toast
function showNotification(msg) {
  let toast = document.getElementById('app-toast');
  if (!toast) {
    toast = document.createElement('div');
    toast.id = 'app-toast';
    toast.className = 'fixed bottom-6 right-6 px-4 py-2.5 rounded-xl bg-surface2 text-slate-100 border border-borderMedium shadow-2xl text-xs font-semibold z-50 transition-all duration-300 transform translate-y-4 opacity-0 pointer-events-none flex items-center space-x-2';
    document.body.appendChild(toast);
  }
  toast.textContent = msg;
  toast.classList.remove('translate-y-4', 'opacity-0');
  setTimeout(() => {
    toast.classList.add('translate-y-4', 'opacity-0');
  }, 2200);
}

// Setup Event Listeners & Hotkeys
function setupEventListeners() {
  // Timer buttons
  document.getElementById('btn-timer-toggle').addEventListener('click', toggleTimer);
  document.getElementById('btn-timer-reset').addEventListener('click', resetTimer);
  document.getElementById('btn-next-phase').addEventListener('click', () => {
    let nextP = state.activePhase + 1;
    if (nextP > 4) nextP = 1;
    setPhase(nextP);
    playSound('phase');
  });

  // Protocol Stepper clicks
  document.querySelectorAll('.protocol-step').forEach(btn => {
    btn.addEventListener('click', () => {
      const p = parseInt(btn.dataset.phase);
      setPhase(p);
      playSound('phase');
    });
  });

  // Open in Brave button
  document.getElementById('btn-open-brave').addEventListener('click', openCurrentInBrave);

  // Prev / Next Problem buttons
  document.getElementById('btn-prev-problem').addEventListener('click', () => {
    if (state.currentProblemId > 1) {
      selectProblem(state.currentProblemId - 1);
    }
  });
  document.getElementById('btn-next-problem').addEventListener('click', advanceNext);
  document.getElementById('btn-advance-next').addEventListener('click', advanceNext);

  // Jump to Current button in sidebar
  document.getElementById('btn-jump-current').addEventListener('click', () => {
    selectProblem(state.currentProblemId);
  });

  // Outcome buttons
  document.getElementById('btn-solve-clean').addEventListener('click', () => {
    saveStatus('clean');
  });
  document.getElementById('btn-solve-help').addEventListener('click', () => {
    saveStatus('help');
  });
  document.getElementById('btn-solve-fail').addEventListener('click', () => {
    // Open Error Log Modal for Rule 4
    openModal('modal-error-log');
  });

  // Hint reveal button
  document.getElementById('btn-reveal-hint').addEventListener('click', () => {
    const hintBox = document.getElementById('hint-display-box');
    hintBox.classList.toggle('hidden');
  });

  // Scratchpad
  document.getElementById('scratchpad-input').addEventListener('input', handleScratchpadChange);

  // Pattern pills
  document.querySelectorAll('.pattern-pill').forEach(pill => {
    pill.addEventListener('click', () => {
      document.querySelectorAll('.pattern-pill').forEach(p => p.classList.remove('active'));
      pill.classList.add('active');
    });
  });

  // Search input
  document.getElementById('search-input').addEventListener('input', (e) => {
    state.searchQuery = e.target.value;
    renderSidebar();
  });

  // Filter buttons
  document.querySelectorAll('.filter-btn').forEach(btn => {
    btn.addEventListener('click', () => {
      document.querySelectorAll('.filter-btn').forEach(b => {
        b.classList.remove('active', 'bg-amber-500', 'text-slate-950', 'font-bold');
        b.classList.add('bg-surface2', 'text-slate-300', 'font-medium');
      });
      btn.classList.add('active', 'bg-amber-500', 'text-slate-950', 'font-bold');
      btn.classList.remove('bg-surface2', 'text-slate-300', 'font-medium');
      state.activeFilter = btn.dataset.filter;
      renderSidebar();
    });
  });

  // Sound toggle button
  document.getElementById('btn-toggle-sound').addEventListener('click', () => {
    state.soundEnabled = !state.soundEnabled;
    updateSoundIcon();
    saveSetting({ sound_enabled: state.soundEnabled });
  });

  // Modals
  document.getElementById('btn-brave-guide').addEventListener('click', () => openModal('modal-brave-guide'));
  document.getElementById('btn-open-reviews').addEventListener('click', openReviewsModal);
  document.getElementById('btn-open-settings').addEventListener('click', openSettingsModal);

  document.querySelectorAll('.btn-close-modal').forEach(btn => {
    btn.addEventListener('click', () => {
      document.querySelectorAll('.fixed.inset-0').forEach(m => m.classList.add('hidden'));
    });
  });

  // Test Brave launch button
  document.getElementById('btn-test-brave').addEventListener('click', async () => {
    await fetch('/api/open-brave', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ url: 'https://leetcode.com' })
    });
  });

  // Error Log Modal save
  document.getElementById('btn-save-error-log').addEventListener('click', () => {
    const activeCat = document.querySelector('.error-cat-btn.active')?.dataset.cat || 'idea';
    const note = document.getElementById('error-note-input').value;
    saveStatus('failed', activeCat, note);
    closeModals();
  });

  document.querySelectorAll('.error-cat-btn').forEach(btn => {
    btn.addEventListener('click', () => {
      document.querySelectorAll('.error-cat-btn').forEach(b => {
        b.classList.remove('active', 'bg-surface3', 'border-amber-500/40', 'text-amber-400');
        b.classList.add('bg-surface1', 'border-borderDefault', 'text-slate-300');
      });
      btn.classList.add('active', 'bg-surface3', 'border-amber-500/40', 'text-amber-400');
      btn.classList.remove('bg-surface1', 'border-borderDefault', 'text-slate-300');
    });
  });

  // Settings Save
  document.getElementById('btn-save-settings').addEventListener('click', async () => {
    const bravePath = document.getElementById('setting-brave-path').value;
    const activeGoal = parseInt(document.querySelector('.goal-opt-btn.active')?.dataset.goal || '3');
    await saveSetting({ brave_path: bravePath, daily_goal: activeGoal });
    state.progress.brave_path = bravePath;
    state.progress.daily_goal = activeGoal;
    renderStats();
    closeModals();
    showNotification("Settings saved!");
  });

  document.querySelectorAll('.goal-opt-btn').forEach(btn => {
    btn.addEventListener('click', () => {
      document.querySelectorAll('.goal-opt-btn').forEach(b => {
        b.classList.remove('active', 'bg-surface3', 'border-amber-500/40', 'text-amber-400', 'font-bold');
        b.classList.add('bg-surface1', 'border-borderDefault', 'text-slate-300', 'font-medium');
      });
      btn.classList.add('active', 'bg-surface3', 'border-amber-500/40', 'text-amber-400', 'font-bold');
      btn.classList.remove('bg-surface1', 'border-borderDefault', 'text-slate-300', 'font-medium');
    });
  });

  // Dynamic HUD Preset buttons
  document.querySelectorAll('.hud-preset-btn').forEach(btn => {
    btn.addEventListener('click', () => {
      applyHudPreset(btn.dataset.preset, null, true);
    });
  });

  // Quick Extend (+1m / +5m)
  document.getElementById('btn-add-1m').addEventListener('click', () => addExtraTime(1));
  document.getElementById('btn-add-5m').addEventListener('click', () => addExtraTime(5));

  // Toggle Compact Focus HUD
  document.getElementById('btn-toggle-compact-hud').addEventListener('click', toggleCompactHud);

  // Custom Timer Modal Setup
  const customTimerBtn = document.getElementById('btn-custom-timer');
  if (customTimerBtn) {
    customTimerBtn.addEventListener('click', () => {
      openModal('modal-custom-timer');
      updateCustomPreview();
    });
  }

  function updateCustomPreview() {
    const p1 = parseInt(document.getElementById('custom-p1').value) || 3;
    const p2 = parseInt(document.getElementById('custom-p2').value) || 4;
    const p3 = parseInt(document.getElementById('custom-p3').value) || 6;
    const p4 = parseInt(document.getElementById('custom-p4').value) || 2;
    const total = p1 + p2 + p3 + p4;
    const previewEl = document.getElementById('custom-total-preview');
    if (previewEl) previewEl.textContent = `${total} Minutes`;
  }

  ['custom-p1', 'custom-p2', 'custom-p3', 'custom-p4'].forEach(id => {
    const el = document.getElementById(id);
    if (el) el.addEventListener('input', updateCustomPreview);
  });

  const applyCustomBtn = document.getElementById('btn-apply-custom-timer');
  if (applyCustomBtn) {
    applyCustomBtn.addEventListener('click', () => {
      const p1 = Math.max(1, parseInt(document.getElementById('custom-p1').value) || 3);
      const p2 = Math.max(1, parseInt(document.getElementById('custom-p2').value) || 4);
      const p3 = Math.max(1, parseInt(document.getElementById('custom-p3').value) || 6);
      const p4 = Math.max(1, parseInt(document.getElementById('custom-p4').value) || 2);
      const customPreset = {
        name: `Custom (${p1 + p2 + p3 + p4}m)`,
        totalMinutes: p1 + p2 + p3 + p4,
        phases: [
          { id: 1, name: "Read & Trace", minutes: p1 },
          { id: 2, name: "Pick a Pattern", minutes: p2 },
          { id: 3, name: "Code & Test", minutes: p3 },
          { id: 4, name: "Cut Your Losses", minutes: p4 }
        ]
      };
      applyHudPreset('custom', customPreset, true);
      closeModals();
      showNotification(`Custom HUD Applied: ${customPreset.totalMinutes}m Total`);
    });
  }

  // Backup Export
  document.getElementById('btn-export-json').addEventListener('click', () => {
    window.location.href = '/api/export';
  });

  // Sheet Selector Dropdown Toggle & Click Outside
  const sheetSelectorBtn = document.getElementById('btn-sheet-selector');
  const sheetDropdown = document.getElementById('sheet-dropdown');
  if (sheetSelectorBtn && sheetDropdown) {
    sheetSelectorBtn.addEventListener('click', (e) => {
      e.stopPropagation();
      sheetDropdown.classList.toggle('hidden');
    });

    document.addEventListener('click', (e) => {
      if (!sheetDropdown.contains(e.target) && !sheetSelectorBtn.contains(e.target)) {
        sheetDropdown.classList.add('hidden');
      }
    });
  }

  // Open Create Self-Made Sheet Modal
  const openCreateSheetBtn = document.getElementById('btn-open-create-sheet');
  if (openCreateSheetBtn) {
    openCreateSheetBtn.addEventListener('click', () => {
      if (sheetDropdown) sheetDropdown.classList.add('hidden');
      openModal('modal-custom-sheet');
    });
  }

  // Save Self-Made Sheet
  const saveCustomSheetBtn = document.getElementById('btn-save-custom-sheet');
  if (saveCustomSheetBtn) {
    saveCustomSheetBtn.addEventListener('click', handleCreateCustomSheet);
  }

  // Open GitHub Badge Modal
  const openBadgeModalBtn = document.getElementById('btn-open-badge-modal');
  if (openBadgeModalBtn) {
    openBadgeModalBtn.addEventListener('click', openBadgeModal);
  }

  // Copy Badge Markdown
  const copyBadgeBtn = document.getElementById('btn-copy-badge-md');
  if (copyBadgeBtn) {
    copyBadgeBtn.addEventListener('click', copyBadgeMarkdown);
  }

  // Pop-out Mini HUD Buttons (Always-on-top PiP / detached popup)
  const popoutBtn = document.getElementById('btn-popout-timer');
  if (popoutBtn) popoutBtn.addEventListener('click', openMiniHudWindow);

  const headerPopoutBtn = document.getElementById('btn-header-popout');
  if (headerPopoutBtn) headerPopoutBtn.addEventListener('click', openMiniHudWindow);

  const dockedPopoutBtn = document.getElementById('btn-docked-popout');
  if (dockedPopoutBtn) dockedPopoutBtn.addEventListener('click', openMiniHudWindow);

  // In-Page Docked Mini Timer
  const dockedToggleBtn = document.getElementById('btn-docked-toggle');
  if (dockedToggleBtn) dockedToggleBtn.addEventListener('click', toggleTimer);

  const dockedScrollBtn = document.getElementById('btn-docked-scroll-top');
  const dockedClickArea = document.getElementById('docked-click-area');
  const scrollToTimer = () => {
    const el = document.getElementById('timer-hud-card');
    if (el) el.scrollIntoView({ behavior: 'smooth' });
  };
  if (dockedScrollBtn) dockedScrollBtn.addEventListener('click', scrollToTimer);
  if (dockedClickArea) dockedClickArea.addEventListener('click', scrollToTimer);

  // Global Keyboard Shortcuts
  window.addEventListener('keydown', (e) => {
    // If typing in input or textarea, skip global shortcuts
    if (['INPUT', 'TEXTAREA'].includes(e.target.tagName)) return;

    if (e.key === 'Escape') {
      closeModals();
      return;
    }

    if (e.code === 'Space') {
      e.preventDefault();
      toggleTimer();
    } else if (e.key === 'r' || e.key === 'R') {
      resetTimer();
    } else if (e.key === 'b' || e.key === 'B') {
      openCurrentInBrave();
    } else if (e.key === 'h' || e.key === 'H') {
      openMiniHudWindow();
    } else if (e.key === 'n' || e.key === 'N') {
      advanceNext();
    } else if (e.key === 'p' || e.key === 'P') {
      if (state.currentProblemId > 1) selectProblem(state.currentProblemId - 1);
    } else if (e.key === 'm' || e.key === 'M') {
      // Cycle HUD presets
      const modes = ['15m', '25m', '45m'];
      const nextIdx = (modes.indexOf(state.activePresetKey) + 1) % modes.length;
      applyHudPreset(modes[nextIdx], null, true);
      showNotification(`HUD Switched: ${modes[nextIdx]}`);
    } else if (e.key === '+' || e.key === '=') {
      addExtraTime(1);
    } else if (e.key === '1') {
      setPhase(1);
    } else if (e.key === '2') {
      setPhase(2);
    } else if (e.key === '3') {
      setPhase(3);
    } else if (e.key === '4') {
      setPhase(4);
    }
  });

  // View Switcher (TakeUForward Sheet Roadmap vs 15m Protocol Solver)
  const navCurriculumBtn = document.getElementById('nav-btn-curriculum');
  if (navCurriculumBtn) {
    navCurriculumBtn.addEventListener('click', () => switchView('curriculum'));
  }

  const navSolverBtn = document.getElementById('nav-btn-solver');
  if (navSolverBtn) {
    navSolverBtn.addEventListener('click', () => switchView('solver'));
  }

  // Hero Action Buttons
  const btnHeroResume = document.getElementById('btn-hero-resume');
  if (btnHeroResume) {
    btnHeroResume.addEventListener('click', resumeCurrentProblem);
  }

  const btnHeroRandom = document.getElementById('btn-hero-random');
  if (btnHeroRandom) {
    btnHeroRandom.addEventListener('click', pickRandomProblem);
  }

  // Curriculum Search
  const curriculumSearchInput = document.getElementById('curriculum-search-input');
  if (curriculumSearchInput) {
    curriculumSearchInput.addEventListener('input', (e) => {
      state.curriculumSearchQuery = e.target.value;
      renderCurriculumTable();
    });
  }

  // Curriculum Filter Buttons (All, Unsolved, Solved, Easy, Medium, Hard)
  document.querySelectorAll('.curriculum-filter-btn').forEach(btn => {
    btn.addEventListener('click', () => {
      document.querySelectorAll('.curriculum-filter-btn').forEach(b => {
        b.classList.remove('active', 'bg-amber-500', 'text-slate-950', 'font-bold');
        b.classList.add('bg-surface2', 'text-slate-300', 'font-medium');
      });
      btn.classList.add('active', 'bg-amber-500', 'text-slate-950', 'font-bold');
      btn.classList.remove('bg-surface2', 'text-slate-300', 'font-medium');
      state.curriculumFilter = btn.dataset.filter;
      renderCurriculumTable();
    });
  });

  // Toggle all accordions
  const btnToggleAccordions = document.getElementById('btn-toggle-all-accordions');
  if (btnToggleAccordions) {
    btnToggleAccordions.addEventListener('click', toggleAllAccordions);
  }
}

// Multi-Sheet Management Logic
async function loadSheetsList() {
  try {
    const res = await fetch('/api/sheets');
    const data = await res.json();
    const sheets = data.sheets || [];
    const container = document.getElementById('sheet-list-container');
    if (!container) return;
    
    container.innerHTML = sheets.map(s => {
      const isActive = s.slug === (state.activeSheetSlug || 'core-path');
      const badgeClass = s.is_system ? 'bg-surface3 text-slate-300 border border-borderSubtle' : 'bg-surface3 text-amber-400 border border-amber-500/30';
      const badgeText = s.is_system ? 'Curated' : 'Custom';
      return `
        <button class="sheet-select-btn w-full px-2.5 py-2 rounded-md text-left text-xs transition flex items-center justify-between ${isActive ? 'bg-surface3 text-amber-400 border border-amber-500/40 font-semibold' : 'hover:bg-surface2 text-slate-300'}" data-slug="${s.slug}">
          <div class="truncate mr-2">
            <div class="font-medium text-slate-200 truncate flex items-center gap-1.5">
              <span>${escapeHtml(s.title)}</span>
            </div>
            <div class="text-[10px] text-slate-400 truncate">${escapeHtml(s.author || '')} · ${s.problem_count} problems</div>
          </div>
          <span class="text-[9px] px-1.5 py-0.5 rounded font-mono uppercase shrink-0 ${badgeClass}">${badgeText}</span>
        </button>
      `;
    }).join('');

    container.querySelectorAll('.sheet-select-btn').forEach(btn => {
      btn.addEventListener('click', () => {
        const slug = btn.dataset.slug;
        switchSheet(slug);
        const dropdown = document.getElementById('sheet-dropdown');
        if (dropdown) dropdown.classList.add('hidden');
      });
    });

  } catch (err) {
    console.error("Failed to load sheets list:", err);
  }
}

async function switchSheet(slug) {
  try {
    showNotification("Loading Sheet...");
    const res = await fetch(`/api/sheets/${slug}`);
    if (!res.ok) throw new Error("Sheet fetch failed");
    const data = await res.json();

    state.activeSheetSlug = slug;
    state.problems = data.problems || [];
    state.chapters = data.chapters || [];
    if (data.progress) {
      state.progress = data.progress;
    }

    // Update Header active sheet name
    const activeSheetNameEl = document.getElementById('active-sheet-name');
    if (activeSheetNameEl) {
      const titles = {
        'core-path': 'The Core Path (610)',
        'striver-sde': "Striver's SDE (95)",
        'neetcode-150': 'NeetCode 150',
        'blind-75': 'Blind 75'
      };
      activeSheetNameEl.textContent = titles[slug] || (data.sheet_title || slug);
    }

    renderStats();
    renderSidebar();
    renderCurriculumTable();
    if (state.problems.length > 0) {
      selectProblem(state.problems[0].id, true);
    }

    // Save active sheet preference
    saveSetting({ active_sheet: slug });
    loadSheetsList();
    showNotification(`Switched to: ${activeSheetNameEl ? activeSheetNameEl.textContent : slug}`);
  } catch (err) {
    console.error("Failed to switch sheet:", err);
    showNotification("Error loading sheet!");
  }
}

// Parse and Save Custom Sheet
async function handleCreateCustomSheet() {
  const titleInput = document.getElementById('custom-sheet-title');
  const descInput = document.getElementById('custom-sheet-desc');
  const textInput = document.getElementById('custom-sheet-input');

  const title = (titleInput.value || '').trim();
  const desc = (descInput.value || '').trim();
  const text = (textInput.value || '').trim();

  if (!title) {
    alert("Please enter a sheet title (e.g. 'Google L4 Sprint' or 'Dynamic Programming 50')");
    titleInput.focus();
    return;
  }

  if (!text) {
    alert("Please enter at least one problem URL or problem title (one per line).");
    textInput.focus();
    return;
  }

  const lines = text.split('\n').map(l => l.trim()).filter(l => l.length > 0);
  if (lines.length === 0) {
    alert("Please enter valid problems.");
    return;
  }

  const problems = lines.map((line) => {
    let pTitle = line;
    let pUrl = line;
    let pTopic = "General Practice";

    if (line.startsWith('http://') || line.startsWith('https://')) {
      try {
        const u = new URL(line);
        const parts = u.pathname.split('/').filter(p => p.length > 0);
        if (parts.length >= 2 && parts[0] === 'problems') {
          const rawSlug = parts[1];
          pTitle = rawSlug.split('-').map(w => w.charAt(0).toUpperCase() + w.slice(1)).join(' ');
        } else if (parts.length > 0) {
          pTitle = parts[parts.length - 1].split('-').map(w => w.charAt(0).toUpperCase() + w.slice(1)).join(' ');
        }
      } catch (e) {}
    } else {
      const slug = line.toLowerCase().replace(/[^a-z0-9]+/g, '-').replace(/(^-|-$)/g, '');
      pUrl = `https://leetcode.com/problems/${slug}/`;
    }

    return {
      title: pTitle,
      url: pUrl,
      topic: pTopic,
      level: "M",
      hint: "Solve using strict 15-minute protocol."
    };
  });

  const saveBtn = document.getElementById('btn-save-custom-sheet');
  const origBtnText = saveBtn.textContent;
  saveBtn.disabled = true;
  saveBtn.textContent = "Saving...";

  try {
    const res = await fetch('/api/sheets/custom', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        title: title,
        description: desc,
        problems: problems
      })
    });

    const result = await res.json();
    if (result.status === 'ok') {
      titleInput.value = '';
      descInput.value = '';
      textInput.value = '';
      closeModals();
      await loadSheetsList();
      await switchSheet(result.slug);
      showNotification(`Self-Made Sheet "${title}" Created with ${result.count} problems!`);
    } else {
      alert("Failed to save sheet: " + (result.detail || "Unknown error"));
    }
  } catch (err) {
    console.error("Create custom sheet error:", err);
    alert("Error saving custom sheet: " + err.message);
  } finally {
    saveBtn.disabled = false;
    saveBtn.textContent = origBtnText;
  }
}

// GitHub Dynamic Badge Modal Handlers
function openBadgeModal() {
  const img = document.getElementById('badge-preview-img');
  if (img) {
    img.src = `/api/badge/local_user.svg?t=${Date.now()}`;
  }
  openModal('modal-badge-share');
}

function copyBadgeMarkdown() {
  const input = document.getElementById('badge-markdown-input');
  if (!input) return;
  input.select();
  navigator.clipboard.writeText(input.value).then(() => {
    showNotification("Badge Markdown copied to clipboard!");
  }).catch(() => {
    document.execCommand('copy');
    showNotification("Badge Markdown copied!");
  });
}

function advanceNext() {
  if (state.currentProblemId < state.problems.length) {
    selectProblem(state.currentProblemId + 1);
  }
}

function openModal(id) {
  document.getElementById(id).classList.remove('hidden');
}

function closeModals() {
  document.querySelectorAll('.fixed.inset-0').forEach(m => m.classList.add('hidden'));
}

function openSettingsModal() {
  document.getElementById('setting-brave-path').value = state.progress.brave_path || '';
  const goal = state.progress.daily_goal || 3;
  document.querySelectorAll('.goal-opt-btn').forEach(b => {
    if (parseInt(b.dataset.goal) === goal) {
      b.classList.add('active', 'bg-surface3', 'border-amber-500/40', 'text-amber-400', 'font-bold');
      b.classList.remove('bg-surface1', 'border-borderDefault', 'text-slate-300', 'font-medium');
    } else {
      b.classList.remove('active', 'bg-surface3', 'border-amber-500/40', 'text-amber-400', 'font-bold');
      b.classList.add('bg-surface1', 'border-borderDefault', 'text-slate-300', 'font-medium');
    }
  });
  openModal('modal-settings');
}

async function openReviewsModal() {
  const container = document.getElementById('reviews-list-container');
  container.innerHTML = '<div class="text-xs text-slate-500 py-4">Checking review schedule...</div>';
  openModal('modal-reviews');

  try {
    const res = await fetch('/api/init');
    const data = await res.json();
    const reviews = data.due_reviews || [];
    
    document.getElementById('stat-reviews-due').textContent = reviews.length;

    if (reviews.length === 0) {
      container.innerHTML = `
        <div class="py-8 text-center space-y-2">
          <svg class="w-8 h-8 text-amber-500 mx-auto" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z"/></svg>
          <p class="text-xs font-bold text-slate-200 uppercase tracking-wide">Queue Clear · No Reviews Due Today</p>
          <p class="text-[11px] text-slate-400">Keep solving problems cleanly. Any struggle triggers the SM-2 decay matrix.</p>
        </div>
      `;
      return;
    }

    container.innerHTML = reviews.map(r => `
      <div class="py-2.5 flex items-center justify-between text-xs">
        <div>
          <div class="flex items-center space-x-2">
            <span class="font-mono text-cyan-400 font-bold">#${r.problem_id}</span>
            <span class="font-semibold text-white">${r.title}</span>
            <span class="text-[10px] px-1.5 py-0.5 rounded bg-slate-800 text-slate-400">${r.chapter}</span>
          </div>
          <div class="text-[11px] text-amber-400 mt-0.5">${r.interval_type} · Due ${r.due_date}</div>
        </div>
        <div class="flex items-center space-x-2">
          <button class="btn-review-go px-3 py-1 bg-cyan-600 hover:bg-cyan-500 text-white rounded font-bold transition" data-id="${r.problem_id}">
            Re-solve
          </button>
        </div>
      </div>
    `).join('');

    container.querySelectorAll('.btn-review-go').forEach(b => {
      b.addEventListener('click', () => {
        const id = parseInt(b.dataset.id);
        closeModals();
        selectProblem(id);
      });
    });

  } catch (err) {
    container.innerHTML = '<div class="text-xs text-rose-400 py-4">Failed to load reviews.</div>';
  }
}

async function saveSetting(patch) {
  try {
    await fetch('/api/settings', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(patch)
    });
  } catch (e) {
    console.error("Failed to save setting:", e);
  }
}

function updateSoundIcon() {
  const icon = document.getElementById('sound-icon');
  if (icon) {
    icon.textContent = state.soundEnabled ? 'AUDIO' : 'MUTE';
    icon.className = state.soundEnabled ? "text-[10px] font-bold font-mono text-amber-400" : "text-[10px] font-bold font-mono text-slate-500";
  }
}

function escapeHtml(str) {
  if (!str) return '';
  return str.replace(/&/g, "&amp;").replace(/</g, "&lt;").replace(/>/g, "&gt;");
}

// Kickoff
document.addEventListener('DOMContentLoaded', initApp);

