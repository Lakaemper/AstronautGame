// AI-vs-AI rule test harness (see NOTES.md / AI_FINDINGS.md). Load the game page over http, then in the page console:
//   const s = await (await fetch('tools/duel_harness.js')).text(); (0, eval)(s);
//   runRule({ DRONE_RANGE: [3, 99] }, { workersPerValue: 7, games: 8, plies: 8, ms: 300 });   // window.__duel fills up, __duel.done becomes true
// Both sides use the same engine; the engine text inside each worker has `let NAME = value` replaced, so index.html itself is untouched.
function runRule(param, o = {}) {
  const [name, values] = Object.entries(param)[0];
  const { workersPerValue = 7, games = 8, plies = 8, ms = 300, cap = 150 } = o;
  const engine = document.getElementById('engine').textContent;
  const helpers = [add, posKey, drawCheck].map(f => f.toString()).join('\n');
  const glue = `
let seen = {};
${helpers}
function setupGame(first) {
  pieces = []; turn = first; winner = null; seen = {};
  [0, 1].forEach(o => {
    const put = (type, col, row) => { const rr = o ? ROWS - 1 - row : row; add(type, o, toX(col, rr), rr); };
    put('core', MIDC, ROWS - 1);
    [1, MIDC - 1, MIDC + 1, COLS - 2].forEach(c => put('astro', c, ROWS - 1));
    put('shield', MIDC, ROWS - 3); put('drone', 2, ROWS - 1); put('smasher', COLS - 3, ROWS - 1);
  });
  add('fire', 2, toX(1, MIDC), MIDC); add('fire', 2, toX(COLS - 2, MIDC), MIDC);
  seen[posKey()] = 1;
}
onmessage = e => {
  const { games, plies, ms, cap, idx } = e.data;
  for (let g = 0; g < games; g++) {
    setupGame((g + idx) % 2);
    const st = { plies: 0, droneMoves: 0, droneKills: 0, smashKills: 0, firstMover: turn };
    while (winner === null && st.plies < cap) {
      const r = aiSearch(turn, plies, ms); if (!r.mv) { winner = 2; break; }
      const p = pieces[r.mv.i], type = p.type, text = step(p, r.mv.m) || '';
      st.plies++;
      if (type === 'drone') { st.droneMoves++; if (/pushes .* (off the board|into the central fire)|crushes/.test(text)) st.droneKills++; }
      if (type === 'smasher' && /destroy|smash/i.test(text)) st.smashKills++;
      if (winner === null) drawCheck();
    }
    postMessage({ winner: winner === null ? 3 : winner, ...st });
  }
};`;
  window.__duel = { workers: [], res: {}, done: false, total: values.length * workersPerValue * games, got: 0 };
  values.forEach(v => {
    window.__duel.res[v] = [];
    const src = 'let pieces, turn, winner;\n' + engine.replace(new RegExp('let ' + name + ' = [^;]+;'), 'let ' + name + ' = ' + v + ';') + glue;
    for (let w = 0; w < workersPerValue; w++) {
      const wk = new Worker(URL.createObjectURL(new Blob([src], { type: 'text/javascript' })));
      wk.onmessage = e => { __duel.res[v].push(e.data); if (++__duel.got >= __duel.total) __duel.done = true; };
      wk.onerror = e => { __duel.err = e.message; };
      wk.postMessage({ games, plies, ms, cap, idx: w });
      __duel.workers.push(wk);
    }
  });
}
function duelSummary() {
  const out = {};
  for (const [v, r] of Object.entries(__duel.res)) {
    const n = r.length, sum = k => r.reduce((a, x) => a + x[k], 0);
    out[v] = { games: n, blue: r.filter(x => x.winner === 0).length, red: r.filter(x => x.winner === 1).length, draw: r.filter(x => x.winner === 2).length, capped: r.filter(x => x.winner === 3).length,
      plies: +(sum('plies') / n).toFixed(1), droneMoves: +(sum('droneMoves') / n).toFixed(2), droneKills: +(sum('droneKills') / n).toFixed(2), smashKills: +(sum('smashKills') / n).toFixed(2) };
  }
  return out;
}
