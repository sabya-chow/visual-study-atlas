/* Scored multiple-choice quizzes. Markup comes from atlas_kit.quiz(). Works without any ask engine.
   Progress is kept per page in localStorage (wrapped in try/catch; the quiz works without it). */
(function () {
  function store(key, val) { try { if (val === undefined) { var s = localStorage.getItem(key); return s ? JSON.parse(s) : {}; } localStorage.setItem(key, JSON.stringify(val)); } catch (e) {} return {}; }
  [].slice.call(document.querySelectorAll('.quiz')).forEach(function (qz) {
    var key = 'quiz:' + location.pathname + ':' + qz.getAttribute('data-qid');
    var qs = [].slice.call(qz.querySelectorAll('.qq')), saved = store(key) || {};
    var score = qz.querySelector('.qscore'), retry = qz.querySelector('.qretry');
    function paint(q, i) {
      var ans = +q.getAttribute('data-ans'), opts = [].slice.call(q.querySelectorAll('.qopt')), box = q.querySelector('.qx');
      q.setAttribute('data-chosen', i);
      opts.forEach(function (o, k) { o.disabled = true; o.classList.toggle('ok', k === ans); o.classList.toggle('bad', k === i && i !== ans); });
      box.hidden = false; box.className = 'qx ' + (i === ans ? 'good' : 'miss');
      box.querySelector('.qv').textContent = i === ans ? 'Correct.' : 'Not quite. The best answer is ' + String.fromCharCode(65 + ans) + '.';
    }
    function clear(q) {
      q.removeAttribute('data-chosen');
      [].slice.call(q.querySelectorAll('.qopt')).forEach(function (o) { o.disabled = false; o.classList.remove('ok', 'bad'); });
      q.querySelector('.qx').hidden = true;
    }
    function tally() {
      var done = 0, right = 0;
      qs.forEach(function (q) { var c = q.getAttribute('data-chosen'); if (c !== null) { done++; if (+c === +q.getAttribute('data-ans')) right++; } });
      score.textContent = 'Score ' + right + ' / ' + qs.length + '  (answered ' + done + ')';
      retry.hidden = !(done - right > 0);
      var s = {}; qs.forEach(function (q, n) { var c = q.getAttribute('data-chosen'); if (c !== null) s[n] = +c; }); store(key, s);
    }
    qs.forEach(function (q, n) { if (saved[n] !== undefined) paint(q, +saved[n]); });
    qz.addEventListener('click', function (e) {
      var b = e.target.closest('.qopt'); if (b && !b.disabled) { paint(b.closest('.qq'), +b.getAttribute('data-i')); tally(); return; }
      if (e.target.closest('.qreset')) { qs.forEach(clear); tally(); }
      if (e.target.closest('.qretry')) { qs.forEach(function (q) { var c = q.getAttribute('data-chosen'); if (c !== null && +c !== +q.getAttribute('data-ans')) clear(q); }); tally(); }
    });
    tally();
  });
})();
