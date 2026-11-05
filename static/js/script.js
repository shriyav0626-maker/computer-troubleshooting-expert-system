// script.js - small helpers for the troubleshooting pages.
// The application works without JavaScript; this only improves convenience.

document.addEventListener("DOMContentLoaded", function () {
  var form = document.getElementById("answer-form");
  if (!form) {
    return; // not on a question page
  }

  // 1. Prevent double submission (double clicks send the same answer twice).
  form.addEventListener("submit", function (event) {
    if (form.dataset.submitted === "true") {
      event.preventDefault();
      return;
    }
    form.dataset.submitted = "true";
    form.classList.add("is-sending");
  });

  // Reset when the page is shown again (for example with the browser Back button).
  window.addEventListener("pageshow", function () {
    form.dataset.submitted = "false";
    form.classList.remove("is-sending");
  });

  // 2. Keyboard shortcuts: Y = Yes, N = No, U = Not sure.
  document.addEventListener("keydown", function (event) {
    if (event.ctrlKey || event.altKey || event.metaKey || event.repeat) {
      return;
    }
    var button = form.querySelector('[data-key="' + event.key.toLowerCase() + '"]');
    if (button) {
      button.click();
    }
  });
});
