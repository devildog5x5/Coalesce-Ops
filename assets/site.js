(function () {
  var menu = document.querySelector(".menu-details");
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

  function closeSettings() {
    if (!settingsPanel || !settingsToggle) return;
    settingsPanel.hidden = true;
    settingsToggle.setAttribute("aria-expanded", "false");
  }

  function closeSections() {
    document.querySelectorAll(".nav-sections[open]").forEach(function (panel) {
      panel.removeAttribute("open");
    });
  }

  function applyTheme(name, persist) {
    if (!themes[name]) name = "light";
    document.documentElement.setAttribute("data-theme", name);
    if (persist) {
      try { localStorage.setItem("coalesceops-theme", name); } catch (e) {}
    }
    var themeColor = getComputedStyle(document.documentElement).getPropertyValue("--theme-color").trim();
    var meta = document.querySelector('meta[name="theme-color"]');
    if (meta && themeColor) meta.setAttribute("content", themeColor);
    themeButtons.forEach(function (button) {
      button.setAttribute("aria-checked", button.getAttribute("data-theme") === name ? "true" : "false");
    });
  }

  if (settingsToggle && settingsPanel) {
    settingsToggle.addEventListener("click", function () {
      if (settingsPanel.hidden) {
        closeSections();
        if (menu) menu.removeAttribute("open");
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

  document.querySelectorAll(".nav-sections").forEach(function (panel) {
    panel.addEventListener("toggle", function () {
      if (!panel.open) return;
      closeSettings();
      document.querySelectorAll(".nav-sections[open]").forEach(function (other) {
        if (other !== panel) other.removeAttribute("open");
      });
    });
  });

  document.querySelectorAll("#site-nav a").forEach(function (link) {
    link.addEventListener("click", function () {
      if (window.matchMedia("(max-width: 900px)").matches && menu) {
        menu.removeAttribute("open");
      }
      closeSections();
    });
  });

  document.addEventListener("click", function (ev) {
    if (settingsPanel && !settingsPanel.hidden) {
      if (!settingsPanel.contains(ev.target) && !settingsToggle.contains(ev.target)) closeSettings();
    }
    document.querySelectorAll(".nav-sections[open]").forEach(function (panel) {
      if (!panel.contains(ev.target)) panel.removeAttribute("open");
    });
  });

  document.addEventListener("keydown", function (ev) {
    if (ev.key !== "Escape") return;
    closeSections();
    closeSettings();
    if (menu) menu.removeAttribute("open");
  });

  var path = location.pathname.split("/").pop() || "index.html";
  if (!path || path === "" || path === "index.html") path = "index.html";
  document.querySelectorAll("#site-nav a.nav-link").forEach(function (link) {
    var href = (link.getAttribute("href") || "").split("#")[0];
    if (href === "/" || href === "" || href === "index.html") href = "index.html";
    if (href === path) link.setAttribute("aria-current", "page");
  });

  var onHome = /(?:^|\/)(?:index\.html)?$/.test(location.pathname);
  if (onHome && location.hash && hashPages[location.hash.slice(1)]) {
    location.replace(hashPages[location.hash.slice(1)]);
    return;
  }

  applyTheme(document.documentElement.getAttribute("data-theme") || "light", false);
})();
