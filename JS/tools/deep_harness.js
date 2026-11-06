// Deep AI analysis harness (branch deeptest). Load the game page over http (cd JS; python -m http.server 8765), then in the page console:
//   const s = await (await fetch('tools/deep_harness.js?' + Date.now())).text(); (0, eval)(s);
//   deepStart({ minutes: 55 });     // runs everything in the background; read window.__P (status) and window.__R (results)
// Engine text is copied into 16 Web Workers; weights per side are set before each search, rules/setups are patched in the glue (index.html is untouched).
// Position tasks: 'list' (legal moves of a line of move signatures), 'eval' (exact, full-window minimax value from Blue's view of moves at depth d), 'game' (a whole AI game).
function deepBuildSrc() {
  const engine = document.getElementById('engine').textContent
    .replace('const AI_NOISE = 6;', 'let AI_NOISE = 0;')
    .replace('const EV = { astro: 100,', 'const EV = { drone: 40, shield: 40, astro: 100,')
    .replace("else if (p.type === 'drone') x = 40;", "else if (p.type === 'drone') x = EV.drone;")
    .replace("else if (p.type === 'shield') x = 40 - 15 * (p.dmg || 0);", "else if (p.type === 'shield') x = EV.shield - 15 * (p.dmg || 0);");
  const helpers = [add, posKey, drawCheck].map(f => f.toString()).join('\n');
  const glue = `
let seen = {}, NOISE_ON = false;
${helpers}
const DEFAULT_EV = { ...EV };
function setEV(w) { Object.assign(EV, DEFAULT_EV, w || {}); }
function setupGame(first, opt) {
  opt = opt || {}; pieces = []; turn = first; winner = null; seen = {};
  [0, 1].forEach(o => {
    const put = (type, col, row) => { const rr = o ? ROWS - 1 - row : row; add(type, o, toX(col, rr), rr); };
    put('core', MIDC, ROWS - 1);
    const n = 4 - ((opt.dropAstro && opt.dropAstro[o]) || 0);
    [MIDC - 1, MIDC + 1, 1, COLS - 2].slice(0, n).forEach(c => put('astro', c, ROWS - 1));
    if (!(opt.noShield && opt.noShield[o])) put('shield', MIDC, ROWS - 3);
    if (!(opt.noDrone && opt.noDrone[o])) put('drone', 2, ROWS - 1);
    if (!(opt.noSmasher && opt.noSmasher[o])) put('smasher', COLS - 3, ROWS - 1);
  });
  add('fire', 2, toX(1, MIDC), MIDC); add('fire', 2, toX(COLS - 2, MIDC), MIDC);
  seen[posKey()] = 1;
}
const sigOf = (s, mv) => msig(s.pieces[mv.i], mv.m);
const startState = () => { setupGame(0, {}); return { pieces: pieces.map(p => ({ ...p })), turn: 0, winner: null }; };
function advance(s, line) { for (const sg of line) { const mv = genMoves(s).find(x => sigOf(s, x) === sg); if (!mv) throw 'bad line ' + sg; s = child(s, mv); } return s; }
onmessage = e => {
  const t = e.data; AI_NOISE = t.t === 'game' ? 6 : 0;
  try {
    if (t.t === 'list') { setEV(); const s = advance(startState(), t.line); postMessage({ id: t.id, sigs: genMoves(s).map(x => sigOf(s, x)) }); return; }
    if (t.t === 'eval') {
      setEV(); const s = advance(startState(), t.line); aiSide = 0; const out = [];
      for (const sg of t.sigs) {
        const mv = genMoves(s).find(x => sigOf(s, x) === sg);
        hist.fill(0); killers = []; ttKey.fill(0); aiNodes = 0; aiDeadline = performance.now() + (t.until - Date.now());
        try { out.push({ sg, v: minimax(child(s, mv), t.depth - 1, -Infinity, Infinity, 1), ok: true, nodes: aiNodes }); }
        catch (err) { if (err !== 'timeout') throw err; out.push({ sg, ok: false }); }
      }
      postMessage({ id: t.id, out }); return;
    }
    if (t.t === 'game') {
      setupGame(t.first, t.setup); const log = []; const forced = (t.forced || []).slice(); let depthSum = 0, searches = 0;
      while (winner === null && log.length < t.cap) {
        setEV(turn === 0 ? t.wB : t.wR); let p, m;
        if (forced.length) { const sg = forced.shift(); const s = { pieces: pieces.map(q => ({ ...q })), turn, winner }; const mv = genMoves(s).find(x => sigOf(s, x) === sg); if (!mv) throw 'bad forced ' + sg; p = pieces[mv.i]; m = mv.m; }
        else { const r = aiSearch(turn, t.plies, t.ms); if (!r.mv) { winner = 2; break; } p = pieces[r.mv.i]; m = r.mv.m; depthSum += r.depth; searches++; }
        const side = turn, type = p.type; const text = step(p, m) || ''; log.push([side, type[0], m.kind, /destroy|smash|off the board|central fire|crush/i.test(text) ? 1 : 0]);
        if (winner === null) drawCheck();
      }
      postMessage({ id: t.id, winner: winner === null ? 3 : winner, log, first: t.first, tag: t.tag, vs: t.variantSide, depth: searches ? depthSum / searches : 0 }); return;
    }
  } catch (err) { postMessage({ id: t.id, error: String(err) }); }
};`;
  return 'let pieces, turn, winner;\n' + engine + glue;
}

class DeepPool {
  constructor(n) {
    this.url = URL.createObjectURL(new Blob([deepBuildSrc()], { type: 'text/javascript' }));
    this.workers = []; this.idle = []; this.queue = []; this.pending = new Map(); this.nextId = 1; this.done = 0; this.submitted = 0;
    for (let i = 0; i < n; i++) {
      const w = new Worker(this.url);
      w.onmessage = e => { const cb = this.pending.get(e.data.id); this.pending.delete(e.data.id); this.done++; this.idle.push(w); this.pump(); cb(e.data); };
      w.onerror = e => { window.__P && (window.__P.err = String(e.message)); };
      this.workers.push(w); this.idle.push(w);
    }
  }
  pump() { while (this.idle.length && this.queue.length) { const { task, resolve } = this.queue.shift(); const w = this.idle.shift(); task.id = this.nextId++; this.pending.set(task.id, resolve); w.postMessage(task); } }
  run(task) { this.submitted++; return new Promise(resolve => { this.queue.push({ task, resolve }); this.pump(); }); }
  stop() { this.workers.forEach(w => w.terminate()); }
}

const DEFAULT_GAME = { plies: 8, ms: 300, cap: 150 };
async function runGames(pool, specs, tag) {
  const res = await Promise.all(specs.map((sp, i) => pool.run({ t: 'game', ...DEFAULT_GAME, first: i % 2, tag, ...sp }).then(r => { __P.gamesDone++; return r; })));
  return res.filter(r => !r.error);
}
const winRate = (rs, side) => { const n = rs.length, w = rs.filter(r => r.winner === side).length, d = rs.filter(r => r.winner === 2 || r.winner === 3).length; return { n, win: w, draw: d, lose: n - w - d }; };

async function deepStart({ minutes = 55 } = {}) {
  const T0 = Date.now(), END = T0 + minutes * 60000;
  const pool = new DeepPool(16); window.__pool = pool;
  window.__P = { phase: 'init', depth: 0, note: '', gamesDone: 0, gamesTotal: 0, t0: T0, log: [], err: null };
  window.__R = { A: [], A2: [], B: null, C: null, D: null };
  const P = __P, note = s => { P.note = s; P.log.push(Math.round((Date.now() - T0) / 1000) + 's ' + s); };
  try {
    // ---------------- A: exact root values, iterative deepening (full window), parallel over root moves
    P.phase = 'A: root'; const untilA = T0 + Math.min(14, minutes * 0.25) * 60000;
    const sigs = (await pool.run({ t: 'list', line: [] })).sigs; note('root moves: ' + sigs.length);
    let cand = sigs.slice(), prev = null;
    for (let d = 3; Date.now() < untilA; d++) {
      if (d >= 7) cand = prev.slice(0, 12).map(x => x.sg); if (d >= 9) cand = prev.slice(0, 8).map(x => x.sg);
      P.depth = d; note('depth ' + d + ' on ' + cand.length + ' moves');
      const outs = (await Promise.all(cand.map(sg => pool.run({ t: 'eval', line: [], sigs: [sg], depth: d, until: untilA })))).map(r => r.out[0]);
      if (outs.some(o => !o.ok)) { note('depth ' + d + ' incomplete (time up), keeping depth ' + (d - 1)); break; }
      outs.sort((a, b) => b.v - a.v); prev = outs; __R.A.push({ d, ranking: outs.map(o => [o.sg, Math.round(o.v)]) });
      note('depth ' + d + ' done; best ' + outs[0].sg + ' = ' + Math.round(outs[0].v) + ', worst of ' + outs.length + ' = ' + Math.round(outs[outs.length - 1].v));
    }
    const Df = __R.A.length ? __R.A[__R.A.length - 1].d : 3;
    // ---------------- A2: Red's replies to the best three openings
    P.phase = 'A2: replies'; const untilA2 = Date.now() + Math.min(6, minutes * 0.1) * 60000, top3 = (prev || []).slice(0, 3);
    for (const o of top3) {
      const rs = (await pool.run({ t: 'list', line: [o.sg] })).sigs, dr = Math.max(4, Df - 1); P.depth = dr; note('replies to ' + o.sg + ' at depth ' + dr);
      const outs = (await Promise.all(rs.map(sg => pool.run({ t: 'eval', line: [o.sg], sigs: [sg], depth: dr, until: untilA2 })))).map(r => r.out[0]).filter(x => x.ok);
      outs.sort((a, b) => a.v - b.v); __R.A2.push({ open: o.sg, depth: dr, replies: outs.slice(0, 8).map(x => [x.sg, Math.round(x.v)]), n: outs.length });
      note('after ' + o.sg + ' Red best reply ' + (outs[0] && outs[0].sg) + ' = ' + (outs[0] && Math.round(outs[0].v)));
    }
    // ---------------- B: openings as games (forced first Blue move), + the free baseline
    P.phase = 'B: openings'; const rank = prev ? prev.map(x => x.sg) : sigs; const top = rank.slice(0, 10), worst = (__R.A[0] ? __R.A[0].ranking.slice(-3).map(x => x[0]) : []);
    const NB = Math.max(8, Math.floor(minutes / 4)), specsB = [];
    for (const sg of [...top, ...worst, null]) for (let i = 0; i < NB; i++) specsB.push({ forced: sg ? [sg] : [], first: 0, tag: sg || 'free', setup: {}, wB: {}, wR: {} });
    P.gamesDone = 0; P.gamesTotal = specsB.length; note('opening games: ' + specsB.length);
    const B = await runGames(pool, specsB.map(s => ({ ...s })), 'B');   // first fixed to 0 (Blue moves first) by the forced move
    __R.B = B;
    // ---------------- C: handicaps (Blue without X), first mover alternates
    P.phase = 'C: handicaps'; const NC = Math.max(24, Math.floor(minutes * 0.9)), variants = { baseline: {}, noShield: { noShield: { 0: 1 } }, noDrone: { noDrone: { 0: 1 } }, noSmasher: { noSmasher: { 0: 1 } }, oneAstroLess: { dropAstro: { 0: 1 } } };
    const specsC = []; for (const [k, setup] of Object.entries(variants)) for (let i = 0; i < NC; i++) specsC.push({ setup, tag: k, wB: {}, wR: {} });
    P.gamesDone = 0; P.gamesTotal = specsC.length; note('handicap games: ' + specsC.length);
    __R.C = await runGames(pool, specsC, 'C');
    // ---------------- D: weights (variant for BOTH colours against the default, colours swapped by alternating who gets the variant)
    P.phase = 'D: weights'; const ND = Math.max(24, Math.floor(minutes * 0.8));
    const W = { 'smasher120': { smasher: 120 }, 'smasher350': { smasher: 350 }, 'drone0': { drone: 0 }, 'drone100': { drone: 100 }, 'shield0': { shield: 0 }, 'shield100': { shield: 100 }, 'astro70': { astro: 70 }, 'astro140': { astro: 140 }, 'fuel30': { fuel: 30 }, 'fuel90': { fuel: 90 } };
    const specsD = []; for (const [k, w] of Object.entries(W)) for (let i = 0; i < ND; i++) { const vs = i % 2, first = (i >> 1) % 2; specsD.push({ first, tag: k, setup: {}, wB: vs === 0 ? w : {}, wR: vs === 1 ? w : {}, variantSide: vs }); }
    P.gamesDone = 0; P.gamesTotal = specsD.length; note('weight games: ' + specsD.length);
    const D = []; for (let i = 0; i < specsD.length; i += 160) { if (Date.now() > END) { note('time up, weights phase cut'); break; } D.push(...await runGames(pool, specsD.slice(i, i + 160), 'D')); }
    __R.D = D; P.phase = 'finished'; note('all done');
  } catch (e) { P.err = String(e); P.phase = 'error'; }
}

// ---------- analysis helpers (called from the console after / during the run)
function featuresOf(r) {
  const f = { winner: r.winner, plies: r.log.length };
  for (const side of [0, 1]) {
    const mine = r.log.map((m, i) => ({ m, i })).filter(x => x.m[0] === side);
    f['firstSmasher' + side] = (mine.findIndex(x => x.m[1] === 's') + 1) || 99;   // index among own moves
    f['firstDrone' + side] = (mine.findIndex(x => x.m[1] === 'd') + 1) || 99;
    f['drone' + side] = mine.filter(x => x.m[1] === 'd').length;
    f['refuel' + side] = mine.filter(x => x.m[2] === 'refuel').length;
    f['smasherMoves' + side] = mine.filter(x => x.m[1] === 's').length;
    f['kills' + side] = mine.filter(x => x.m[3]).length;
  }
  return f;
}
function bucketBy(rs, key, edges) {   // win rate of Blue by a bucketed feature of Blue's play
  const out = {};
  for (const r of rs) { const f = featuresOf(r), v = f[key]; const b = edges.find(e => v <= e) ?? 'more'; (out[b] = out[b] || []).push(r.winner); }
  return Object.fromEntries(Object.entries(out).map(([b, ws]) => [b, { n: ws.length, blueWin: +(ws.filter(w => w === 0).length / ws.length).toFixed(2) }]));
}
function summarize() {
  const R = __R, S = {};
  if (R.B) { S.openings = {}; for (const tag of [...new Set(R.B.map(r => r.tag))]) { const rs = R.B.filter(r => r.tag === tag); S.openings[tag] = winRate(rs, 0); } }
  if (R.C) { S.handicap = {}; for (const tag of [...new Set(R.C.map(r => r.tag))]) { const rs = R.C.filter(r => r.tag === tag); S.handicap[tag] = { ...winRate(rs, 0), plies: +(rs.reduce((a, r) => a + r.log.length, 0) / rs.length).toFixed(0) }; } }
  if (R.D) { S.weights = {}; for (const tag of [...new Set(R.D.map(r => r.tag))]) { const rs = R.D.filter(r => r.tag === tag); const w = rs.filter(r => r.winner === r.vs).length, d = rs.filter(r => r.winner >= 2).length; S.weights[tag] = { n: rs.length, variantWins: w, defaultWins: rs.length - w - d, draws: d }; } }
  return S;
}

Object.assign(window, { DeepPool, runGames, deepStart, summarize, featuresOf, bucketBy, winRate });
