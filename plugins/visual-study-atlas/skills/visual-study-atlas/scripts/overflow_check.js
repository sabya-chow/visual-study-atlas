// Paste into the browser console (or javascript_tool) on a built chapter page. Reports SVG text that spills out of its box or the viewBox.
// Prints "clean" when nothing is wrong. Arrow-over-text overlaps still need an eye-check by screenshot (1100 px wide window).
(() => { const out = []; document.querySelectorAll('figure svg').forEach((svg, i) => { const vb = svg.viewBox.baseVal;
  const rects = [...svg.querySelectorAll('rect.bx')].map(r => ({ x: +r.getAttribute('x'), y: +r.getAttribute('y'), w: +r.getAttribute('width'), h: +r.getAttribute('height') }));
  svg.querySelectorAll('text').forEach(t => { const b = t.getBBox(), cx = b.x + b.width / 2, cy = b.y + b.height / 2;
    if (b.x < 0 || b.x + b.width > vb.width || b.y < 0 || b.y + b.height > vb.height) out.push(`fig${i} OUT-OF-VIEW "${t.textContent.slice(0, 40)}"`);
    let best = null; for (const r of rects) if (cx >= r.x && cx <= r.x + r.w && cy >= r.y && cy <= r.y + r.h && (!best || r.w * r.h < best.w * best.h)) best = r;
    if (best && (b.x < best.x + 1 || b.x + b.width > best.x + best.w - 1 || b.y < best.y || b.y + b.height > best.y + best.h)) out.push(`fig${i} OVERFLOW "${t.textContent.slice(0, 50)}" text ${Math.round(b.width)} box ${best.w}`); }); });
  return out.join('\n') || 'clean'; })()
