"""Build fleur-noir-site/index.html (iPad/touch build) from creative/fleur-noir.html.
Every edit is an exact-match replace; the script fails loudly if the desktop source drifts."""
import sys, pathlib

ROOT = pathlib.Path(r"C:\Users\ericd\Hermes Working Dir")
SRC = ROOT / "creative" / "fleur-noir.html"
DST = ROOT / "fleur-noir-site" / "index.html"
html = SRC.read_text(encoding="utf-8")

def rep(old, new, count=1):
    global html
    n = html.count(old)
    if n != count:
        sys.exit(f"expected {count} match(es), found {n}:\n{old[:120]}")
    html = html.replace(old, new)

# ---- head: viewport, PWA meta, manifest, icon, noindex ----
rep('<meta name="viewport" content="width=device-width, initial-scale=1.0, user-scalable=no">\n<title>Fleur Noir</title>',
    '<meta name="viewport" content="width=device-width, initial-scale=1.0, maximum-scale=1.0, user-scalable=no, viewport-fit=cover">\n'
    '<meta name="apple-mobile-web-app-capable" content="yes">\n'
    '<meta name="mobile-web-app-capable" content="yes">\n'
    '<meta name="apple-mobile-web-app-status-bar-style" content="black-translucent">\n'
    '<meta name="apple-mobile-web-app-title" content="Fleur Noir">\n'
    '<meta name="theme-color" content="#050505">\n'
    '<link rel="manifest" href="manifest.webmanifest">\n'
    '<link rel="apple-touch-icon" href="apple-touch-icon.png">\n'
    '<meta name="robots" content="noindex, nofollow">\n'
    '<title>Fleur Noir</title>')

# ---- css: touch layer ----
rep('  canvas { display: block; width: 100vw; height: 100vh; touch-action: none; }\n',
    '''  body { position: fixed; inset: 0; -webkit-user-select: none; user-select: none; -webkit-touch-callout: none; -webkit-tap-highlight-color: transparent; overscroll-behavior: none; }
  canvas { display: block; width: 100vw; height: 100vh; touch-action: none; }
  @supports (height: 100dvh) { canvas { height: 100dvh; } }

  /* ---------- touch toolbar (phones / iPad — no keyboard) ---------- */
  #tbar {
    position: fixed; left: max(18px, env(safe-area-inset-left)); bottom: max(18px, env(safe-area-inset-bottom));
    display: none; gap: 8px; transition: opacity .8s;
  }
  body.touch #tbar { display: flex; }
  #tbar.idle { opacity: 0.25; }
  #tbar button {
    width: 44px; height: 44px; border-radius: 50%;
    border: 1px solid rgba(255,255,255,0.14); background: rgba(8,8,8,0.55);
    color: rgba(220,230,225,0.6); font: 500 15px/1 "Segoe UI", system-ui, sans-serif;
    backdrop-filter: blur(6px); -webkit-backdrop-filter: blur(6px);
    display: flex; align-items: center; justify-content: center; padding: 0;
  }
  #tbar button:active { color: rgba(235,242,238,0.95); border-color: rgba(255,255,255,0.4); }
  body.nochrome #tbar { display: none !important; }

  /* bigger targets when the pointer is a finger */
  body.touch #gear { width: 44px; height: 44px; font-size: 16px; right: max(18px, env(safe-area-inset-right)); bottom: max(18px, env(safe-area-inset-bottom)); }
  body.touch #panel {
    width: 300px; right: max(18px, env(safe-area-inset-right)); bottom: calc(max(18px, env(safe-area-inset-bottom)) + 56px);
    max-height: calc(100vh - 100px); overflow-y: auto; -webkit-overflow-scrolling: touch; box-sizing: border-box;
    font-size: 12px; -webkit-backdrop-filter: blur(14px);
  }
  body.touch input[type=range] { width: 150px; height: 3px; }
  body.touch input[type=range]::-webkit-slider-thumb { width: 18px; height: 18px; }
  body.touch input[type=checkbox] { width: 17px; height: 17px; }
  body.touch .row { margin: 12px 0; }
  body.touch .sw { height: 28px; }
  body.touch .src { padding: 11px 6px; }
  body.touch #track button { width: 34px; height: 30px; }
  body.touch #keys { display: none; }
  body.touch #hint { bottom: max(76px, calc(env(safe-area-inset-bottom) + 58px)) !important; }
''')

# ---- toolbar markup ----
rep('<div id="hint">drag to stir &nbsp;·&nbsp; click for a burst &nbsp;·&nbsp; H for options</div>\n',
    '''<div id="hint">drag to stir &nbsp;·&nbsp; click for a burst &nbsp;·&nbsp; H for options</div>

<div id="tbar">
  <button id="tbPal" title="next palette">◐</button>
  <button id="tbBurst" title="burst">✦</button>
  <button id="tbHide" title="hide ui">◌</button>
</div>
''')

# ---- device detection + mobile sim budget (after CONFIG) ----
rep('''  AUTO: true,                  // autonomous choreography
};
''', '''  AUTO: true,                  // autonomous choreography
};

/* ---------- device: touch / iOS / iPadOS ----------
   iPadOS Safari reports a Mac UA — detect it via touch points. Mobile GPUs get a lighter sim. */
const IS_TOUCH = matchMedia('(pointer: coarse)').matches || navigator.maxTouchPoints > 1;
const IS_IOS = /iP(hone|ad|od)/.test(navigator.platform) || (navigator.platform === 'MacIntel' && navigator.maxTouchPoints > 1) || /iP(hone|ad|od)/.test(navigator.userAgent);
const IS_STANDALONE = !!navigator.standalone || matchMedia('(display-mode: standalone)').matches;
let MAX_DPR = 2;
if (IS_TOUCH) {
  document.body.classList.add('touch');
  CONFIG.DYE_RESOLUTION = 900;
  CONFIG.SIM_RESOLUTION = 192;
  CONFIG.PRESSURE_ITERATIONS = 20;
  MAX_DPR = 1.5;
  document.getElementById('hint').innerHTML = 'drag to stir &nbsp;·&nbsp; tap for a burst &nbsp;·&nbsp; ⋯ for options';
}
''')

# mobile: fewer viscosity sweeps (the MacCormack + viscosity passes are the new cost)
rep("  VISC_ITERATIONS: 12,", "  VISC_ITERATIONS: IS_TOUCH ? 8 : 12,")

rep("  const dpr = Math.min(window.devicePixelRatio || 1, 2);",
    "  const dpr = Math.min(window.devicePixelRatio || 1, MAX_DPR);")

# ---- pointer: pointercancel, single finger, block Safari gestures ----
rep('''canvas.addEventListener('pointerdown', e => {
  pointer.down = true;
  pointer.fam = Math.random() < 0.5 ? 0 : 1;
  pointer.color = famColor(pointer.fam, 0.85);
  pointer.x = e.clientX / canvas.clientWidth;
  pointer.y = 1.0 - e.clientY / canvas.clientHeight;
  burst(pointer.x, pointer.y, pointer.fam, 0.7);
  dismissHint();
});
window.addEventListener('pointermove', e => {
  wakeGear();
  if (!pointer.down) return;
  updatePointer(e.clientX, e.clientY);
});
window.addEventListener('pointerup', () => { pointer.down = false; });''',
'''canvas.addEventListener('pointerdown', e => {
  if (pointer.down && pointer.id !== e.pointerId) return;   /* one stirring finger; extra fingers only burst */
  pointer.id = e.pointerId;
  pointer.down = true;
  pointer.fam = Math.random() < 0.5 ? 0 : 1;
  pointer.color = famColor(pointer.fam, 0.85);
  pointer.x = e.clientX / canvas.clientWidth;
  pointer.y = 1.0 - e.clientY / canvas.clientHeight;
  burst(pointer.x, pointer.y, pointer.fam, 0.7);
  dismissHint();
  wakeGear();
});
window.addEventListener('pointermove', e => {
  wakeGear();
  if (!pointer.down || e.pointerId !== pointer.id) return;
  updatePointer(e.clientX, e.clientY);
});
const pointerEnd = e => { if (pointer.id === undefined || e.pointerId === pointer.id) pointer.down = false; };
window.addEventListener('pointerup', pointerEnd);
window.addEventListener('pointercancel', pointerEnd);
/* iOS: stop Safari's gestures from stealing the drag */
for (const ev of ['gesturestart', 'gesturechange', 'gestureend']) document.addEventListener(ev, e => e.preventDefault(), { passive: false });
document.addEventListener('touchmove', e => { if (e.target === canvas) e.preventDefault(); }, { passive: false });
document.addEventListener('dblclick', e => { if (e.target === canvas) e.preventDefault(); });''')

# ---- audio: resume in gesture, iOS message ----
rep('''  const ctx = new (window.AudioContext || window.webkitAudioContext)();
  try {
    if (mode === 'system') {
      if (!navigator.mediaDevices || !navigator.mediaDevices.getDisplayMedia)
        throw new Error('screen/tab capture not available here — open this file in Chrome');''',
'''  const ctx = new (window.AudioContext || window.webkitAudioContext)();
  if (ctx.state === 'suspended') ctx.resume().catch(() => {});   /* iOS: must resume inside the tap */
  try {
    if (mode === 'system') {
      if (!navigator.mediaDevices || !navigator.mediaDevices.getDisplayMedia)
        throw new Error(IS_IOS ? 'iOS can\\u2019t capture system audio — use the microphone or an audio file' : 'screen/tab capture not available here — open this file in Chrome');''')

# ---- toolbar wiring, fullscreen fallback, iOS tweaks ----
rep('''ui.gear.addEventListener('click', () => togglePanel());
window.addEventListener('keydown', e => {
  if (e.target && /INPUT|BUTTON/.test(e.target.tagName) && e.key !== 'Escape') return;
  const k = e.key.toLowerCase();
  if (k === 'h') togglePanel();
  if (e.key === 'Escape') togglePanel(false);
  if (k === 'f') { if (document.fullscreenElement) document.exitFullscreen(); else document.documentElement.requestFullscreen().catch(() => {}); }
  if (k === 'u') { document.body.classList.toggle('nochrome'); if (document.body.classList.contains('nochrome')) togglePanel(false); }''',
'''ui.gear.addEventListener('click', () => togglePanel());
function toggleFullscreen() {
  const d = document, el = d.documentElement;
  if (d.fullscreenElement || d.webkitFullscreenElement) { (d.exitFullscreen || d.webkitExitFullscreen).call(d); return; }
  const req = el.requestFullscreen || el.webkitRequestFullscreen;
  if (req) req.call(el).catch?.(() => {});
  else setStatus('iPad: share → “Add to Home Screen” for full-screen', false);
}
function toggleChrome() {
  document.body.classList.toggle('nochrome');
  if (document.body.classList.contains('nochrome')) togglePanel(false);
}

/* ---------- touch toolbar ---------- */
const tbar = document.getElementById('tbar');
document.getElementById('tbPal').addEventListener('click', () => { setPalette((PALETTES.indexOf(PAL) + 1) % (PALETTES.length - 1)); saveSettings(); });
document.getElementById('tbBurst').addEventListener('click', spaceBurst);
document.getElementById('tbHide').addEventListener('click', toggleChrome);
/* hidden UI: with no keyboard, a two-finger tap brings it back */
canvas.addEventListener('touchstart', e => {
  if (e.touches.length === 2 && document.body.classList.contains('nochrome')) toggleChrome();
}, { passive: true });
if (IS_IOS) {
  /* getDisplayMedia doesn't exist on iOS — don't offer it */
  document.querySelector('.src[data-src="system"]').style.display = 'none';
  ui.status.textContent = 'microphone or audio file · music app tracks are DRM-locked';
  if (!IS_STANDALONE) {
    const tip = document.createElement('div');
    tip.id = 'a2hs'; tip.style.cssText = 'font-size:9px;letter-spacing:.18em;color:rgba(215,225,220,.42);margin-top:12px;padding-top:10px;border-top:1px solid rgba(255,255,255,.08);line-height:1.8';
    tip.innerHTML = 'Full screen: share <b style="color:rgba(215,225,220,.7)">⎋</b> → Add to Home Screen';
    ui.panel.appendChild(tip);
  }
}
/* keep the audio clock alive when the tab regains focus (iOS suspends contexts in the background) */
document.addEventListener('visibilitychange', () => {
  if (!document.hidden && AUDIO.ctx && AUDIO.ctx.state === 'suspended') AUDIO.ctx.resume().catch(() => {});
});

window.addEventListener('keydown', e => {
  if (e.target && /INPUT|BUTTON/.test(e.target.tagName) && e.key !== 'Escape') return;
  const k = e.key.toLowerCase();
  if (k === 'h') togglePanel();
  if (e.key === 'Escape') togglePanel(false);
  if (k === 'f') toggleFullscreen();
  if (k === 'u') toggleChrome();''')

rep('''  ui.gear.classList.remove('idle');
  document.body.classList.remove('nocursor');
  clearTimeout(gearIdle);
  gearIdle = setTimeout(() => {
    if (!ui.panel.classList.contains('open')) { ui.gear.classList.add('idle'); document.body.classList.add('nocursor'); }''',
'''  ui.gear.classList.remove('idle'); tbar.classList.remove('idle');
  document.body.classList.remove('nocursor');
  clearTimeout(gearIdle);
  gearIdle = setTimeout(() => {
    if (!ui.panel.classList.contains('open')) { ui.gear.classList.add('idle'); tbar.classList.add('idle'); document.body.classList.add('nocursor'); }''')

DST.write_text(html, encoding="utf-8")
print(f"wrote {DST} ({len(html)} chars)")
