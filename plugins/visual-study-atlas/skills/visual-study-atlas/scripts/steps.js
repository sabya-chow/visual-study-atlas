/* Step-through for flow diagrams (figures with data-step groups). Default view shows everything; "Step through" dims later steps. */
(function () {
  [].slice.call(document.querySelectorAll('figure.stepfig')).forEach(function (fig) {
    var bar = fig.querySelector('.stepbar'), n = +bar.getAttribute('data-n'), caps = []; try { caps = JSON.parse(bar.getAttribute('data-caps') || '[]'); } catch (e) {}
    var go = bar.querySelector('.sgo'), prev = bar.querySelector('.sprev'), next = bar.querySelector('.snext'), all = bar.querySelector('.sall'), cap = bar.querySelector('.scap'), cur = 0;
    function render() {
      var on = cur > 0; fig.classList.toggle('stepping', on);
      [].slice.call(fig.querySelectorAll('[data-step]')).forEach(function (g) { var k = +g.getAttribute('data-step'); g.classList.toggle('dim', on && k > cur); g.classList.toggle('cur', on && k === cur); });
      go.hidden = on; prev.hidden = next.hidden = all.hidden = !on; prev.disabled = cur <= 1; next.disabled = cur >= n;
      cap.textContent = on ? ('Step ' + cur + ' of ' + n + (caps[cur - 1] ? ': ' + caps[cur - 1] : '')) : '';
    }
    go.onclick = function () { cur = 1; render(); }; prev.onclick = function () { if (cur > 1) { cur--; render(); } };
    next.onclick = function () { if (cur < n) { cur++; render(); } }; all.onclick = function () { cur = 0; render(); }; render();
  });
})();
