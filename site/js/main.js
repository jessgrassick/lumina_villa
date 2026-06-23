/* Lumina Villa — Shared Scripts */

(function () {
  "use strict";

  // Scroll-aware nav
  var nav = document.getElementById("nav");
  if (nav) {
    var onScroll = function () {
      nav.classList.toggle("scrolled", window.scrollY > 40);
    };
    onScroll();
    window.addEventListener("scroll", onScroll, { passive: true });
  }

  // Mobile menu
  var toggle = document.getElementById("navToggle");
  var mobile = document.getElementById("mobileMenu");
  if (toggle && mobile) {
    toggle.addEventListener("click", function () {
      var open = mobile.classList.toggle("open");
      toggle.setAttribute("aria-expanded", open);
      document.body.style.overflow = open ? "hidden" : "";
    });
    mobile.querySelectorAll("a").forEach(function (a) {
      a.addEventListener("click", function () {
        mobile.classList.remove("open");
        document.body.style.overflow = "";
        toggle.setAttribute("aria-expanded", "false");
      });
    });
  }

  // FAQ accordion
  document.querySelectorAll(".faq-q").forEach(function (btn) {
    btn.addEventListener("click", function () {
      var item = btn.closest(".faq-item");
      var wasOpen = item.classList.contains("open");
      // Close all in same group
      var group = item.closest(".faq-group");
      if (group) {
        group.querySelectorAll(".faq-item.open").forEach(function (el) {
          el.classList.remove("open");
        });
      }
      if (!wasOpen) item.classList.add("open");
    });
  });

  // Audience tabs
  document.querySelectorAll(".audience-tab").forEach(function (tab) {
    tab.addEventListener("click", function () {
      var target = tab.getAttribute("data-audience");
      var wrapper = tab.closest(".audience-section");
      wrapper.querySelectorAll(".audience-tab").forEach(function (t) {
        t.classList.remove("active");
      });
      wrapper.querySelectorAll(".audience-content").forEach(function (c) {
        c.classList.remove("active");
      });
      tab.classList.add("active");
      var content = wrapper.querySelector(
        '[data-audience-content="' + target + '"]'
      );
      if (content) content.classList.add("active");
    });
  });

  // Reveal on scroll
  var reduce = false;
  try {
    reduce = window.matchMedia("(prefers-reduced-motion: reduce)").matches;
  } catch (e) {}

  if (!reduce && "IntersectionObserver" in window) {
    var io = new IntersectionObserver(
      function (entries) {
        entries.forEach(function (e) {
          if (e.isIntersecting) {
            e.target.classList.add("in");
            io.unobserve(e.target);
          }
        });
      },
      { threshold: 0.1 }
    );
    document.querySelectorAll(".reveal").forEach(function (el) {
      io.observe(el);
    });
  } else {
    document.querySelectorAll(".reveal").forEach(function (el) {
      el.classList.add("in");
    });
  }

  // WhatsApp enquiry builder
  var waForm = document.getElementById("waForm");
  if (waForm) {
    waForm.addEventListener("submit", function (e) {
      e.preventDefault();
      var v = function (id) {
        var el = document.getElementById(id);
        return el ? (el.value || "").trim() : "";
      };
      var name = v("f-name");
      var guests = v("f-guests");
      var ci = v("f-in");
      var co = v("f-out");
      var msg = v("f-msg");

      var t = "Hello Lumina Villa, I'd like to enquire about a stay.";
      if (name) t += "\nName: " + name;
      if (guests) t += "\nGuests: " + guests;
      if (ci) t += "\nCheck-in: " + ci;
      if (co) t += "\nCheck-out: " + co;
      if (msg) t += "\nMessage: " + msg;

      window.open(
        "https://wa.me/628212218471?text=" + encodeURIComponent(t),
        "_blank"
      );
    });
  }

  // Year in footer
  var yr = document.getElementById("yr");
  if (yr) yr.textContent = new Date().getFullYear();
})();
