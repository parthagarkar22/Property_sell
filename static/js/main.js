(function () {
  const navToggle = document.getElementById("navToggle");
  const siteNav = document.getElementById("siteNav");
  if (navToggle && siteNav) {
    navToggle.addEventListener("click", function () {
      const open = siteNav.classList.toggle("open");
      navToggle.setAttribute("aria-expanded", open ? "true" : "false");
    });
  }

  const filterToggle = document.getElementById("filterToggle");
  const filterFields = document.getElementById("filterFields");
  if (filterToggle && filterFields) {
    filterToggle.addEventListener("click", function () {
      filterFields.classList.toggle("open");
    });
    if (window.matchMedia("(min-width: 760px)").matches) {
      filterFields.classList.add("open");
    }
  }

  const mainImg = document.getElementById("galleryMainImg");
  const thumbs = document.querySelectorAll("[data-gallery-src]");
  thumbs.forEach(function (btn) {
    btn.addEventListener("click", function () {
      if (mainImg) {
        mainImg.src = btn.getAttribute("data-gallery-src");
        mainImg.alt = btn.getAttribute("data-gallery-alt") || "Property photo";
      }
    });
  });

  var passwordInput = document.getElementById("password");
  var confirmInput = document.getElementById("password2");
  var ruleList = document.getElementById("pwRules");
  if (passwordInput && confirmInput && ruleList) {
    var checks = {
      length: function (value) { return value.length >= 8; },
      upper: function (value) { return /[A-Z]/.test(value); },
      lower: function (value) { return /[a-z]/.test(value); },
      digit: function (value) { return /\d/.test(value); },
      special: function (value) { return /[^A-Za-z0-9]/.test(value); },
      match: function (value) { return value.length > 0 && value === confirmInput.value; },
    };

    function refreshRules() {
      var value = passwordInput.value;
      var started = value.length > 0 || confirmInput.value.length > 0;
      var allMet = true;
      var form = passwordInput.closest("form");
      form.querySelectorAll(".pw-rules").forEach(function (list) {
        list.classList.toggle("is-checked", started);
      });
      form.querySelectorAll("[data-rule]").forEach(function (item) {
        var rule = item.getAttribute("data-rule");
        var met = checks[rule] ? checks[rule](value) : false;
        item.classList.toggle("is-met", met);
        if (!met) allMet = false;
      });
      return allMet;
    }

    passwordInput.addEventListener("input", refreshRules);
    confirmInput.addEventListener("input", refreshRules);
    var form = passwordInput.closest("form");
    if (form) {
      form.addEventListener("submit", function (event) {
        if (!refreshRules()) {
          event.preventDefault();
          ruleList.scrollIntoView({ block: "nearest" });
          passwordInput.focus();
        }
      });
    }
  }

  // Auto-dismiss flashes after a while (still readable for older users)
  setTimeout(function () {
    document.querySelectorAll(".flash").forEach(function (el) {
      el.style.transition = "opacity 0.4s";
      el.style.opacity = "0";
      setTimeout(function () {
        el.remove();
      }, 450);
    });
  }, 8000);
})();
