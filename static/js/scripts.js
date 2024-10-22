document.addEventListener("DOMContentLoaded", function() {
  console.log("Document loaded");
  
  // Add any JavaScript functionality here
});
document.addEventListener('DOMContentLoaded', function () {
  AOS.init();
});

/* global bootstrap: false */
(() => {
  'use strict'
  const tooltipTriggerList = Array.from(document.querySelectorAll('[data-bs-toggle="tooltip"]'))
  tooltipTriggerList.forEach(tooltipTriggerEl => {
    new bootstrap.Tooltip(tooltipTriggerEl)
  })
})()
