// static/js/consultation-modal.js

document.addEventListener("DOMContentLoaded", function () {
  // Grab the modal elements
  const modalOverlay = document.getElementById("consultation-modal");
  const openBtn = document.getElementById("open-consultation-btn");
  const closeButtons = modalOverlay.querySelectorAll(".modal-close");
  const consultForm = document.getElementById("consultForm");
  const successBox = document.getElementById("consult_success");

  // 1) Show the modal when “Request Free Consultation” is clicked
  openBtn.addEventListener("click", function () {
    modalOverlay.classList.remove("hidden");
    // Ensure form is visible if user opens again
    consultForm.style.display = "block";
    successBox.classList.add("hidden");
  });

  // 2) Hide the modal when any “.modal-close” button is clicked
  closeButtons.forEach((btn) => {
    btn.addEventListener("click", function () {
      modalOverlay.classList.add("hidden");
    });
  });

  // 3) Handle the form submission via AJAX (so we don’t navigate away)
  consultForm.addEventListener("submit", function (e) {
    e.preventDefault();

    const formData = new FormData(consultForm);

    fetch(consultForm.action, {
      method: "POST",
      body: formData,
    })
      .then((response) => response.json())
      .then((data) => {
        if (data.status === "ok") {
          // Hide the form itself
          consultForm.style.display = "none";
          // Show the “thank you” block
          successBox.classList.remove("hidden");
        } else {
          alert("There was an error sending your request. Please try again.");
        }
      })
      .catch((err) => {
        console.error("Fetch error:", err);
        alert("Network error. Please try again later.");
      });
  });
});
