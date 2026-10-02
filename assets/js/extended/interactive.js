/* FK's Lab — small, dependency-free interactive layer.
   Progressive enhancement only: every element below is fully
   visible/usable without this script running. */
(function () {
  "use strict";

  var reduceMotion = window.matchMedia("(prefers-reduced-motion: reduce)").matches;

  /* Sticky header: add a background/shadow once the page scrolls */
  var header = document.querySelector(".header");
  if (header) {
    var onScroll = function () {
      header.classList.toggle("fk-scrolled", window.scrollY > 8);
    };
    onScroll();
    window.addEventListener("scroll", onScroll, { passive: true });
  }

  /* Hero: rotating keyword (first word is already in the HTML) */
  var rot = document.querySelector(".fk-rotator-word");
  if (rot && !reduceMotion) {
    var words = [];
    try { words = JSON.parse(rot.getAttribute("data-words")); } catch (e) {}
    if (words.length > 1) {
      var idx = 0;
      setInterval(function () {
        rot.classList.add("fk-out");
        setTimeout(function () {
          idx = (idx + 1) % words.length;
          rot.textContent = words[idx];
          rot.classList.remove("fk-out");
        }, 350);
      }, 2600);
    }
  }

  /* Cursor spotlight on cards */
  document.addEventListener("pointermove", function (e) {
    var card = e.target.closest && e.target.closest(".service-card, .stat-card");
    if (!card) return;
    var r = card.getBoundingClientRect();
    card.style.setProperty("--mx", e.clientX - r.left + "px");
    card.style.setProperty("--my", e.clientY - r.top + "px");
  }, { passive: true });

  /* Visit counter in the footer (GoatCounter public counter; silently skipped on failure) */
  if (window.fkCounter) {
    fetch(window.fkCounter.url)
      .then(function (r) { return r.ok ? r.json() : Promise.reject(); })
      .then(function (d) {
        var footer = document.querySelector(".footer");
        if (!footer || !d || d.count == null) return;
        var el = document.createElement("span");
        el.className = "fk-visits";
        var html = window.fkCounter.views + ": <b></b>";
        if (d.count_unique != null) html += " · " + window.fkCounter.uniq + ": <b></b>";
        el.innerHTML = html;
        var nums = el.querySelectorAll("b");
        nums[0].textContent = d.count;
        if (nums[1]) nums[1].textContent = d.count_unique;
        footer.appendChild(el);
      })
      .catch(function () {});
  }

  /* Dashboard fullscreen button (hidden without JS + Fullscreen API) */
  document.querySelectorAll("[data-fk-fullscreen]").forEach(function (btn) {
    var frame = btn.closest(".dashboard-frame");
    if (!frame || !frame.requestFullscreen) {
      btn.hidden = true;
      return;
    }
    btn.addEventListener("click", function () {
      frame.requestFullscreen();
    });
  });

  /* Reveal-on-scroll + animated stat counters.
     Elements opt in via [data-animate]; the class that hides them
     (.reveal) is only added here, so without JS nothing is hidden. */
  var animated = document.querySelectorAll("[data-animate]");
  if (!animated.length) return;

  var animateCounter = function (el) {
    var target = parseFloat(el.getAttribute("data-counter-target"));
    if (isNaN(target)) return;
    var suffix = el.getAttribute("data-counter-suffix") || "";
    if (reduceMotion) {
      el.textContent = target + suffix;
      return;
    }
    var duration = 1100;
    var start = null;
    var from = 0;
    var step = function (ts) {
      if (start === null) start = ts;
      var progress = Math.min((ts - start) / duration, 1);
      var eased = 1 - Math.pow(1 - progress, 3);
      var value = from + (target - from) * eased;
      el.textContent = (Number.isInteger(target) ? Math.round(value) : value.toFixed(1)) + suffix;
      if (progress < 1) window.requestAnimationFrame(step);
    };
    window.requestAnimationFrame(step);
  };

  if (!("IntersectionObserver" in window)) {
    animated.forEach(function (el) {
      var counter = el.querySelector ? el.querySelector("[data-counter-target]") : null;
      if (counter) animateCounter(counter);
    });
    return;
  }

  animated.forEach(function (el) {
    el.classList.add("reveal");
  });

  var observer = new IntersectionObserver(
    function (entries) {
      entries.forEach(function (entry) {
        if (!entry.isIntersecting) return;
        entry.target.classList.add("fk-in-view");
        var counter = entry.target.hasAttribute("data-counter-target")
          ? entry.target
          : entry.target.querySelector("[data-counter-target]");
        if (counter) animateCounter(counter);
        observer.unobserve(entry.target);
      });
    },
    { threshold: 0.15, rootMargin: "0px 0px -40px 0px" }
  );

  animated.forEach(function (el) {
    observer.observe(el);
  });
})();
