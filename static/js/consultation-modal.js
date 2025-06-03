// static/js/consultation-modal.js

document.addEventListener("DOMContentLoaded", function () {
  // — Grab the modal elements —
  const modalOverlay    = document.getElementById("consultation-modal");
  const openBtn         = document.getElementById("open-consult-btn");
  const closeButtons    = modalOverlay.querySelectorAll(".modal-close");
  const consultForm     = document.getElementById("consultForm");
  const successBox      = document.getElementById("consult_success");
  const errorBox        = document.getElementById("consult_error");

  // — 1) Show the modal when “Request Free Consultation” is clicked —
  openBtn.addEventListener("click", function (e) {
    e.preventDefault();
    modalOverlay.classList.remove("hidden");

    // Ensure the form is visible, and any messages are hidden
    consultForm.classList.remove("hidden");
    successBox.classList.add("hidden");
    errorBox.classList.add("hidden");
  });

  // — 2) Hide the modal when any “.modal-close” button is clicked —
  function closeModal() {
    modalOverlay.classList.add("hidden");

    // Reset form inputs and hide both success and error boxes
    consultForm.reset();
    consultForm.classList.remove("hidden");
    successBox.classList.add("hidden");
    errorBox.classList.add("hidden");
  }

  closeButtons.forEach((btn) => {
    btn.addEventListener("click", closeModal);
  });

  // — 3) Handle the form submission via AJAX (so we don’t navigate away) —
  consultForm.addEventListener("submit", function (e) {
    e.preventDefault();

    const formData = new FormData(consultForm);

    fetch(consultForm.action, {
      method: "POST",
      body: formData
    })
      .then((response) => {
        // If status is not 2xx, treat it as an error
        if (!response.ok) {
          throw new Error("Server responded with " + response.status);
        }
        return response.json();
      })
      .then((data) => {
        // Only show the success box if data.status === "OK"
        consultForm.classList.add("hidden");
        successBox.classList.remove("hidden");
      })
      .catch((error) => {
        console.error("Form submission failed:", error);
        consultForm.classList.add("hidden");
        errorBox.classList.remove("hidden");
      });
  });
});
