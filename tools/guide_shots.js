// Скриншоты для руководства: node tools/guide_shots.js (нужен дев-сервер на :8080), результат в www/img/guide/*.png
const { chromium } = require('/home/user/projects/jsclub/node_modules/playwright');
const out = require('path').join(__dirname, '../www/img/guide');
(async () => {
  const b = await chromium.launch();
  const ctx = await b.newContext({ viewport: { width: 412, height: 800 }, screen: { width: 412, height: 800 }, deviceScaleFactor: 2, locale: 'ru-RU' });
  const p = await ctx.newPage();
  await p.goto('http://127.0.0.1:8080/index.html?silent');
  await p.waitForSelector('.saveSlot');
  await p.click('.saveSlot >> nth=0');
  await p.waitForTimeout(1500);
  await p.evaluate(() => {
    const C = require('app/gamecontent'), B = require('app/entity/building'), K = require('app/entity/block'), GS = require('app/gamestate');
    GS.buildings = [];
    const add = (n, built, req) => { const b = new B({ type: C.getBuildingType(n) }); b.built = built; if (req) b.requiredResources = req; GS.buildings.push(b); };
    add('shack', true); add('bricklayer', true); add('weaver', true);
    add('blacksmith', false, { wood: 2, clay: 1 }); add('sawmill', false, { stone: 1, cloth: 2 });
    GS.stores = [];
    [['Stone', 18], ['Wood', 9], ['Clay', 24], ['Cloth', 13], ['Stone', 6]].forEach(([t, q]) => { const k = new K({ type: C.ResourceType[t] }); k._quantity = q; GS.stores.push(k); });
    GS.level = 3; GS.xp = 100; GS.health = 40; GS.prioritizedBuilding = 'blacksmith'; GS.save();
  });
  await p.reload();
  await p.waitForSelector('.saveSlot');
  await p.click('.saveSlot >> nth=0');
  await p.waitForTimeout(4000);
  // стрелка на ход, дающий три в ряд
  await p.evaluate(() => {
    const t = Array.from(document.querySelectorAll('.tile:not(.pooled):not(.hidden)')).map(e => { const r = e.getBoundingClientRect(); return { c: e.className.split(' ')[1], x: r.x + r.width / 2, y: r.y + r.height / 2 }; });
    const xs = [...new Set(t.map(e => Math.round(e.x)))].sort((a, b) => a - b), ys = [...new Set(t.map(e => Math.round(e.y)))].sort((a, b) => a - b);
    const g = ys.map(y => xs.map(x => t.find(e => Math.round(e.x) == x && Math.round(e.y) == y).c));
    const run = (g, r, c) => { const v = g[r][c]; let h = 1, k = c - 1; while (k >= 0 && g[r][k] == v) { h++; k--; } k = c + 1; while (k < xs.length && g[r][k] == v) { h++; k++; } let w = 1; k = r - 1; while (k >= 0 && g[k][c] == v) { w++; k--; } k = r + 1; while (k < ys.length && g[k][c] == v) { w++; k++; } return h >= 3 || w >= 3; };
    let best = null;
    for (let r = 0; r < 4 && !best; r++) for (let c = 0; c < xs.length && !best; c++) for (const [dr, dc] of [[0, 1], [1, 0]]) {
      const r2 = r + dr, c2 = c + dc; if (r2 >= 4 || c2 >= xs.length) continue;
      [g[r][c], g[r2][c2]] = [g[r2][c2], g[r][c]];
      const ok = run(g, r, c) || run(g, r2, c2);
      [g[r][c], g[r2][c2]] = [g[r2][c2], g[r][c]];
      if (ok) { best = [xs[c], ys[r], xs[c2], ys[r2]]; break; }
    }
    window.__swap = best;
    if (!best) return;
    const [x1, y1, x2, y2] = best, s = document.createElement('div');
    s.style.cssText = 'position:fixed;left:0;top:0;width:100vw;height:100vh;z-index:9999;pointer-events:none';
    s.innerHTML = '<svg width="100%" height="100%"><defs><marker id="ah" markerWidth="6" markerHeight="6" refX="4" refY="3" orient="auto"><path d="M0,0 L6,3 L0,6 z" fill="#fff"/></marker></defs>'
      + `<circle cx="${x1}" cy="${y1}" r="24" fill="none" stroke="#fff" stroke-width="3.5"/><circle cx="${x2}" cy="${y2}" r="24" fill="none" stroke="#fff" stroke-width="3.5" stroke-dasharray="5 4"/>`
      + `<line x1="${x1 + (x2 - x1) * .5}" y1="${y1 + (y2 - y1) * .5}" x2="${x2}" y2="${y2}" stroke="#fff" stroke-width="5" marker-end="url(#ah)" opacity=".0"/></svg>`;
    document.body.appendChild(s);
  });
  console.log('swap', await p.evaluate(() => window.__swap));
  await p.screenshot({ path: out + '/board.png', clip: { x: 5, y: 210, width: 402, height: 230 } });
  await p.screenshot({ path: out + '/world.png', clip: { x: 0, y: 100, width: 412, height: 112 } });
  await p.evaluate(() => { require('app/eventmanager').trigger('phaseChange', [true]); });
  await p.waitForTimeout(3500);
  await p.screenshot({ path: out + '/night.png', clip: { x: 5, y: 210, width: 402, height: 230 } });
  await b.close();
})();
