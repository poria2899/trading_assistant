/**
 * Trade Assistant — small, framework-free interaction helpers.
 *
 * Only handles what CSS can't: opening/closing the mobile nav drawer and
 * auto-dismissing toast messages after a delay (errors get longer).
 */
(function () {
  "use strict";

  var prefersReducedMotion = window.matchMedia(
    "(prefers-reduced-motion: reduce)"
  ).matches;

  function initMobileNav() {
    var toggle = document.querySelector("[data-nav-toggle]");
    var drawer = document.querySelector("[data-nav-drawer]");
    var overlay = document.querySelector("[data-nav-overlay]");
    if (!toggle || !drawer || !overlay) return;

    function open() {
      drawer.classList.remove("-translate-x-full");
      overlay.classList.remove("hidden", "opacity-0");
      overlay.classList.add("opacity-100");
      toggle.setAttribute("aria-expanded", "true");
    }

    function close() {
      drawer.classList.add("-translate-x-full");
      overlay.classList.add("opacity-0");
      toggle.setAttribute("aria-expanded", "false");
      window.setTimeout(function () {
        overlay.classList.add("hidden");
      }, prefersReducedMotion ? 0 : 200);
    }

    toggle.addEventListener("click", function () {
      var isOpen = toggle.getAttribute("aria-expanded") === "true";
      isOpen ? close() : open();
    });
    overlay.addEventListener("click", close);
    document.addEventListener("keydown", function (event) {
      if (event.key === "Escape") close();
    });
  }

  function initToasts() {
    var toasts = document.querySelectorAll("[data-toast]");
    toasts.forEach(function (toast) {
      var isError =
        toast.classList.contains("toast-error") ||
        toast.classList.contains("toast-danger");
      var delay = isError ? 8000 : 4500;

      var dismissBtn = toast.querySelector("[data-toast-dismiss]");
      function dismiss() {
        if (prefersReducedMotion) {
          toast.remove();
          return;
        }
        toast.classList.add("opacity-0", "-translate-y-1");
        window.setTimeout(function () {
          toast.remove();
        }, 200);
      }

      if (dismissBtn) dismissBtn.addEventListener("click", dismiss);
      window.setTimeout(dismiss, delay);
    });
  }

  document.addEventListener("DOMContentLoaded", function () {
    initMobileNav();
    initToasts();
  });
})();
