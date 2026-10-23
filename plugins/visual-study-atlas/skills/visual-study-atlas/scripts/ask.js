(function () {
  var RULES = "You are an expert tutor inside a study atlas of '__SOURCE__'. __READER__ They clicked one part of the page and asked about it.\n\nWrite a genuinely clarifying explanation, not a restatement of the clicked text:\n1. Start with the direct answer in one plain sentence.\n2. Explain HOW or WHY it works: the mechanism, step by step, naming the actors and what each does. Define every technical term the first time in a few words. __MATHNOTE__\n3. Give one concrete, specific example with real-looking details, and say what makes it that kind of case and not a neighbouring one.\n4. __LENSNOTE__\nLength: __LENGTH__. Short paragraphs, plain text, no headings. For a follow-up, answer exactly that and build on earlier turns. Use the context given; say briefly if something is uncertain or goes beyond the source. The closing panels titled __LENSES__ are the atlas author's additions, not the source text.";
  var sample = null, on = true, panel, logEl, input, quoteEl, turns = [], ctxText = '', ctl = null, busy = false, deeper = false, hovEl = null, raf = 0;
  var $ = function (s, r) { return (r || document).querySelector(s); };
  try { if (localStorage.getItem('askon') === '0') on = false; } catch (e) {}

  function clip(s, n) { s = (s || '').replace(/\s+/g, ' ').trim(); return s.length > n ? s.slice(0, n) + '...' : s; }

  function pickSvg(svg, e) {
    var pt = svg.createSVGPoint(); pt.x = e.clientX; pt.y = e.clientY;
    var ctm = svg.getScreenCTM(); if (!ctm) return null;
    var p = pt.matrixTransform(ctm.inverse()), vb = svg.viewBox.baseVal, total = vb.width * vb.height, best = null, ba = 1e12;
    svg.querySelectorAll('rect').forEach(function (r) {
      var x = +r.getAttribute('x'), y = +r.getAttribute('y'), w = +r.getAttribute('width'), h = +r.getAttribute('height');
      if (p.x >= x && p.x <= x + w && p.y >= y && p.y <= y + h && w * h < total * 0.5 && w * h < ba) { best = r; ba = w * h; }
    });
    var fig = svg.getAttribute('aria-label') || '', cap = svg.closest('figure'); cap = cap && $('figcaption', cap) ? $('figcaption', cap).textContent : '';
    if (best) {
      var x0 = +best.getAttribute('x'), y0 = +best.getAttribute('y'), w0 = +best.getAttribute('width'), h0 = +best.getAttribute('height'), parts = [];
      svg.querySelectorAll('text').forEach(function (t) {
        var b = t.getBBox(), cx = b.x + b.width / 2, cy = b.y + b.height / 2;
        if (cx >= x0 && cx <= x0 + w0 && cy >= y0 && cy <= y0 + h0) parts.push(t.textContent);
      });
      return { el: best, text: parts.join(' / '), kind: 'diagram box', fig: fig, cap: cap };
    }
    if (e.target.tagName === 'text') return { el: e.target, text: e.target.textContent, kind: 'diagram label', fig: fig, cap: cap };
    return null;
  }

  function pick(e) {
    var t = e.target;
    if (!t || !t.closest || t.closest('#askpanel,#asktoggle,a,button,input,textarea,summary,nav')) return null;
    if (!t.closest('.view')) return null;
    var svg = t.closest('svg');
    if (svg) return pickSvg(svg, e);
    var el = t.closest('p,li,td,th,figcaption,h1,h2,h3,.lead,.note,.claim');
    if (!el) return null;
    var blk = el.closest('tr') ? el.closest('tr') : (el.closest('.card,.lens,details') || el.parentElement), extra = '';
    if (el.closest('tr')) { var tb = el.closest('table'), hr = tb && $('thead tr', tb); extra = hr ? 'Table columns: ' + clip(hr.innerText, 200) + '. Row: ' : ''; }
    return { el: el, text: clip(el.innerText, 600), kind: 'text', around: extra + clip(blk.innerText, 1200) };
  }

  function ctxOf(info, selText) {
    var view = info.el.closest('.view'), h1 = view && $('h1', view), sec = info.el.closest('section'), h2 = sec && $('h2', sec);
    var cl = sec && $('.claim', sec); var s = (cl ? 'Section summary: ' + clip(cl.textContent, 500) + '\n' : '') + 'Chapter page: ' + (h1 ? h1.textContent : '') + '\nSection: ' + (h2 ? h2.textContent : '(top of page)') + '\nClicked part (' + info.kind + '): ' + (selText || info.text);
    if (selText) s += '\nWhole element it sits in: ' + clip(info.text, 500);
    if (info.around) s += '\nSurrounding text: ' + info.around;
    if (info.fig) s += '\nDiagram description: ' + info.fig;
    if (info.cap) s += '\nDiagram caption: ' + clip(info.cap, 500);
    return s;
  }

  function setHov(el) {
    if (hovEl === el) return;
    if (hovEl) hovEl.classList.remove('ask-hov');
    hovEl = el; if (el) el.classList.add('ask-hov');
  }

  function show(el, text) {
    // 'Textbook p.N' in an answer becomes a link to that page when the atlas has a local textbook copy
    el.textContent = '';
    var has = !!document.querySelector('a[href^="textbook.pdf"]'), re = /Textbook p\.(\d+)/g, last = 0, m;
    if (!has) { el.textContent = text; return; }
    while ((m = re.exec(text))) {
      el.appendChild(document.createTextNode(text.slice(last, m.index)));
      var a = document.createElement('a'); a.href = 'textbook.pdf#page=' + m[1]; a.target = '_blank'; a.rel = 'noopener'; a.textContent = m[0]; el.appendChild(a); last = m.index + m[0].length;
    }
    el.appendChild(document.createTextNode(text.slice(last)));
  }
  function msg(cls, text) { var d = document.createElement('div'); d.className = 'am ' + cls; d.textContent = text; logEl.appendChild(d); logEl.scrollTop = logEl.scrollHeight; return d; }

  function chips(show) {
    var c = $('.achips', panel); c.innerHTML = '';
    if (!show) return;
    var list = busy ? [] : (turns.length ? ['Go deeper', 'Another example', 'Simpler'] : ['Explain simply', 'Walk me through step by step', 'Give a real-world example', 'Why does it matter?', 'How could this be tested?']);
    list.forEach(function (q) { var b = document.createElement('button'); b.type = 'button'; b.textContent = q; b.onclick = function () { ask(/^Go deeper/.test(q) ? 'Go deeper: explain the underlying mechanism more fully, with a second, different example.' : q, /^Go deeper/.test(q)); }; c.appendChild(b); });
  }

  function open(info, selText) {
    ctxText = ctxOf(info, selText); turns = []; logEl.innerHTML = '';
    quoteEl.textContent = clip(selText || info.text, 140); panel.hidden = false; chips(true);
    input.value = ''; input.focus({ preventScroll: true });
  }
  function close() { if (ctl) ctl.abort(); panel.hidden = true; busy = false; }

  var ERR = { not_granted: 'Asking is switched off for this page. Allow Claude for this artifact to use it.', rate_limited: 'Too many questions just now. Wait a moment and try again.', session_expired: 'Sign in again to keep asking.', upstream_error: 'Something interrupted the answer. Try again.', sampling_disabled: 'Claude is not available on this account.' };

  function ask(q, goDeep) {
    q = (q || '').trim(); if (!q || busy || !sample) return;
    msg('q', q); turns.push({ role: 'user', content: q });
    var out = msg('a', 'Thinking...'), stop = $('.astop', panel);
    ctl = new AbortController(); busy = true; chips(false); input.value = ''; stop.hidden = false;
    sample([{ role: 'user', content: RULES + '\n\nCONTEXT\n' + ctxText }].concat(turns.slice(-8)), {
      cache: turns.length === 1 ? { gcTime: 3600000 } : false, signal: ctl.signal, modelTier: goDeep ? 'complex' : 'default',
      onText: function (u) { show(out, u.text); logEl.scrollTop = logEl.scrollHeight; }
    }).then(function (r) { show(out, r.text); turns.push({ role: 'assistant', content: r.text }); })
      .catch(function (e) {
        if (e && e.code === 'cancelled') { out.textContent = e.text || 'Stopped.'; if (e.text) turns.push({ role: 'assistant', content: e.text }); else turns.pop(); }
        else { out.textContent = (e && e.text ? e.text + '\n\n' : '') + (ERR[e && e.code] || ERR.upstream_error); out.classList.add('err'); if (e && e.text) turns.push({ role: 'assistant', content: e.text }); else turns.pop(); }
      }).finally(function () { busy = false; ctl = null; stop.hidden = true; chips(true); });
  }

  function build() {
    var tg = document.createElement('button'); tg.id = 'asktoggle'; tg.type = 'button';
    function lab() { tg.textContent = on ? 'Click to ask: on' : 'Click to ask: off'; tg.setAttribute('aria-pressed', on); }
    tg.onclick = function () { on = !on; try { localStorage.setItem('askon', on ? '1' : '0'); } catch (e) {} lab(); if (!on) { setHov(null); close(); } };
    lab(); document.body.appendChild(tg);
    panel = document.createElement('div'); panel.id = 'askpanel'; panel.hidden = true; panel.setAttribute('role', 'dialog'); panel.setAttribute('aria-label', 'Ask about this part');
    panel.innerHTML = '<div class="ah"><span class="aq"></span><button type="button" class="ax" aria-label="Close">×</button></div><div class="alog" aria-live="polite"></div><div class="achips"></div><form class="af"><input id="askinput" placeholder="What is unclear? Type and press Enter" autocomplete="off"><button type="submit">Ask</button><button type="button" class="astop" hidden>Stop</button></form>';
    document.body.appendChild(panel);
    logEl = $('.alog', panel); input = $('#askinput', panel); quoteEl = $('.aq', panel);
    $('.ax', panel).onclick = close;
    $('.astop', panel).onclick = function () { if (ctl) ctl.abort(); };
    $('.af', panel).onsubmit = function (e) { e.preventDefault(); ask(input.value); };
    document.addEventListener('keydown', function (e) { if (e.key === 'Escape' && !panel.hidden) close(); });
    document.addEventListener('mousemove', function (e) {
      if (!on || raf) return; raf = requestAnimationFrame(function () { raf = 0; var i = pick(e); setHov(i ? i.el : null); });
    });
    document.addEventListener('click', function (e) {
      if (!on) return;
      var i = pick(e); if (!i) return;
      var sel = window.getSelection ? window.getSelection().toString().trim() : '';
      open(i, sel.length >= 3 && sel.length < 600 ? sel : '');
    });
    var tip = document.getElementById('asktip'); if (tip) tip.hidden = false;
  }

  var views = [].slice.call(document.querySelectorAll('.view'));
  function route() {
    var h = decodeURIComponent((location.hash || '').slice(1)) || 'index', vid = h, anchor = null, m = h.match(/^(ch\d+|appendix)-(s\d+)$/);
    if (m) { vid = m[1]; anchor = h; }
    var v = document.getElementById('v-' + vid) || document.getElementById('v-index');
    views.forEach(function (x) { x.hidden = x !== v; });
    var el = anchor && document.getElementById(anchor);
    if (el) el.scrollIntoView(); else window.scrollTo(0, 0);
  }
  window.addEventListener('hashchange', route); route();

  if (window.claude && claude.use) {
    claude.use('sample').then(function (s) { if (s) { sample = s; build(); } }).catch(function () {});
  }
})();
