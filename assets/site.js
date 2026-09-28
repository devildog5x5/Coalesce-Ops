(function () {
  var toggle = document.getElementById("nav-toggle");
  var drawer = document.getElementById("nav-drawer");
  var settingsToggle = document.getElementById("settings-toggle");
  var settingsPanel = document.getElementById("settings-panel");
  var themeButtons = document.querySelectorAll(".theme-list button");
  var themes = {
    light: 1,
    dark: 1,
    green: 1,
    "light-green": 1,
    "dark-green": 1,
    blue: 1,
    "light-blue": 1
  };
  var hashPages = {
    practice: "practice.html",
    services: "services.html",
    approach: "method.html",
    engagements: "method.html",
    contact: "contact.html",
    work: "practice.html"
  };

  function closeNav() {
    if (!drawer || !toggle) return;
    drawer.hidden = true;
    toggle.setAttribute("aria-expanded", "false");
  }

  function closeSettings() {
    if (!settingsPanel || !settingsToggle) return;
    settingsPanel.hidden = true;
    settingsToggle.setAttribute("aria-expanded", "false");
  }

  function applyTheme(name, persist) {
    if (!themes[name]) name = "light";
    document.documentElement.setAttribute("data-theme", name);
    if (persist) {
      try { localStorage.setItem("spartanphalanx-theme", name); } catch (e) {}
    }
    var themeColor = getComputedStyle(document.documentElement).getPropertyValue("--theme-color").trim();
    var meta = document.querySelector('meta[name="theme-color"]');
    if (meta && themeColor) meta.setAttribute("content", themeColor);
    themeButtons.forEach(function (button) {
      button.setAttribute("aria-checked", button.getAttribute("data-theme") === name ? "true" : "false");
    });
  }

  if (toggle && drawer) {
    toggle.addEventListener("click", function () {
      if (drawer.hidden) {
        closeSettings();
        drawer.hidden = false;
        toggle.setAttribute("aria-expanded", "true");
      } else {
        closeNav();
      }
    });
    drawer.querySelectorAll("a").forEach(function (a) {
      a.addEventListener("click", closeNav);
    });
  }

  if (settingsToggle && settingsPanel) {
    settingsToggle.addEventListener("click", function () {
      if (settingsPanel.hidden) {
        closeNav();
        settingsPanel.hidden = false;
        settingsToggle.setAttribute("aria-expanded", "true");
      } else {
        closeSettings();
      }
    });
    themeButtons.forEach(function (button) {
      button.addEventListener("click", function () {
        applyTheme(button.getAttribute("data-theme"), true);
      });
    });
  }

  document.addEventListener("click", function (ev) {
    if (!settingsPanel || settingsPanel.hidden) return;
    if (settingsPanel.contains(ev.target) || settingsToggle.contains(ev.target)) return;
    closeSettings();
  });

  document.addEventListener("keydown", function (ev) {
    if (ev.key === "Escape") {
      closeNav();
      closeSettings();
    }
  });

  var path = location.pathname;
  var onHome = /(?:^|\/)(?:index\.html)?$/.test(path);
  if (onHome && location.hash && hashPages[location.hash.slice(1)]) {
    location.replace(hashPages[location.hash.slice(1)]);
    return;
  }

  applyTheme(document.documentElement.getAttribute("data-theme") || "light", false);
})();
