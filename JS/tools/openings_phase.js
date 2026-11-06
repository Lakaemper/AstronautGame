// Opening catalog generator (branch deeptest). Needs deep_harness.js loaded first (deepBuildSrc) and a quiet CPU (run after deepStart has finished).
//   const s = await (await fetch('tools/openings_phase.js?' + Date.now())).text(); (0, eval)(s); openingsRun({ n: 140 });   // fills window.__O
// Each task plays 8 plies (4 moves per side) with a deep search (forced first Blue move from the best root moves, noise for variety), then rates the final position
// with a depth-N search from Blue's view. Notation helpers: fmtMove(), fmtLine().
const OPEN_GLUE = `
const __old = onmessage;
onmessage = e => {
  const t = e.data;
  if (t.t === 'opening') {
    try {
      AI_NOISE = t.noise; setupGame(0, {}); const line = [], types = [], forced = (t.forced || []).slice();
      for (let k = 0; k < t.len && winner === null; k++) {
        setEV(); let p, m;
        if (forced.length) { const sg = forced.shift(); const s = { pieces: pieces.map(q => ({ ...q })), turn, winner }; const mv = genMoves(s).find(x => sigOf(s, x) === sg); if (!mv) throw 'bad forced ' + sg; p = pieces[mv.i]; m = mv.m; }
        else { const r = aiSearch(turn, t.plies, t.ms); if (!r.mv) break; p = pieces[r.mv.i]; m = r.mv.m; }
        line.push(msig(p, m)); types.push(p.type[0]); step(p, m); if (winner === null) drawCheck();
      }
      const s = { pieces: pieces.map(q => ({ ...q })), turn, winner }; AI_NOISE = 0; aiSide = 0; hist.fill(0); killers = []; ttKey.fill(0); aiNodes = 0; aiDeadline = performance.now() + t.evalMs;
      let v = null; try { v = minimax(s, t.depthEval, -Infinity, Infinity, 0); } catch (err) { if (err !== 'timeout') throw err; }
      postMessage({ id: t.id, line, types, v, fin: winner !== null, win: winner });
    } catch (err) { postMessage({ id: t.id, error: String(err) }); }
    return;
  }
  __old(e);
};`;

// notation: files a..i = column, ranks 1..9 bottom to top (Blue's home row is rank 1, Red's rank 9)
const FILES = 'abcdefghi';
function sq(x, y) { const col = colOf(x, y); return FILES[col] + (ROWS - y); }
const PIECE_LETTER = { a: 'A', s: 'S', d: 'D', h: 'H', c: 'C' };
function fmtMove(sig, typeLetter) {   // "x,y>x2,y2:kind" -> e.g. Ac1-c2 (step), Ac1~c3 (jet jump), Sg1*g3 (smash landing), Dc1>c4 (drone push), Ad4+ (refuel at the fire), Ac1=d1 (fuel from a drone)
  const [from, rest] = sig.split('>'), [to, kind] = rest.split(':'), [x1, y1] = from.split(',').map(Number), [x2, y2] = to.split(',').map(Number);
  const p = PIECE_LETTER[typeLetter] || '?', a = sq(x1, y1), b = sq(x2, y2);
  switch (kind) {
    case 'walk': case 'cover': return p + a + '-' + b;
    case 'jump': return p + a + '~' + b;
    case 'capture': return p + a + 'x' + b;
    case 'smash': return p + a + '*' + b;
    case 'push': return p + a + '>' + b;
    case 'refuel': return p + a + '+';
    case 'feed': return p + a + '=' + b;
    default: return p + a + '?' + b;
  }
}
function fmtLine(line, types) { const out = []; for (let i = 0; i < line.length; i += 2) out.push((i / 2 + 1) + '. ' + fmtMove(line[i], types[i]) + (line[i + 1] ? ' ' + fmtMove(line[i + 1], types[i + 1]) : '')); return out.join('  '); }

async function openingsRun({ n = 140, plies = 9, ms = 700, depthEval = 6, evalMs = 20000, firsts = null } = {}) {
  const T0 = Date.now(); window.__O = { done: 0, total: n, res: [], t0: T0, finished: false, err: null };
  const src = deepBuildSrc() + '\n' + OPEN_GLUE, url = URL.createObjectURL(new Blob([src], { type: 'text/javascript' }));
  const workers = [], idle = [], queue = [], pending = new Map(); let nextId = 1;
  const pump = () => { while (idle.length && queue.length) { const { task, resolve } = queue.shift(); const w = idle.shift(); task.id = nextId++; pending.set(task.id, resolve); w.postMessage(task); } };
  for (let i = 0; i < 16; i++) { const w = new Worker(url); w.onmessage = e => { const cb = pending.get(e.data.id); pending.delete(e.data.id); idle.push(w); pump(); cb(e.data); }; w.onerror = e => { __O.err = String(e.message); }; workers.push(w); idle.push(w); }
  const run = task => new Promise(resolve => { queue.push({ task, resolve }); pump(); });
  try {
    const f = firsts || (__R.A.length ? __R.A[__R.A.length - 1].ranking.slice(0, 12).map(x => x[0]) : null);
    await Promise.all(Array.from({ length: n }, (_, i) => run({ t: 'opening', len: 8, plies, ms, noise: 7, depthEval, evalMs, forced: f ? [f[i % f.length]] : [] }).then(r => { __O.done++; if (!r.error) __O.res.push(r); else __O.err = r.error; })));
  } catch (e) { __O.err = String(e); }
  workers.forEach(w => w.terminate()); __O.finished = true;
}
function openingsTable() {
  const seen = new Set(), rows = [];
  for (const r of window.__O.res.slice().sort((a, b) => (b.v ?? -1e9) - (a.v ?? -1e9))) { const k = r.line.join('|'); if (seen.has(k) || r.v === null) continue; seen.add(k); rows.push({ text: fmtLine(r.line, r.types), v: Math.round(r.v), first: fmtMove(r.line[0], r.types[0]), reply: fmtMove(r.line[1], r.types[1]) }); }
  return rows;
}
Object.assign(window, { openingsRun, openingsTable, fmtMove, fmtLine, OPEN_GLUE });
