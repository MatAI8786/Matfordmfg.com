document.addEventListener('DOMContentLoaded', () => {
  const openBtn    = document.getElementById('open-consult-btn');
  const modal      = document.getElementById('consultation-modal');
  const closeBtns  = modal.querySelectorAll('.modal-close');
  const form       = document.getElementById('consultForm');
  const successBox = document.getElementById('consult_success');
  const errorBox   = document.getElementById('consult_error');
  const errorMsg   = document.getElementById('consult_error_message');

  function openModal(e) {
    e && e.preventDefault();
    // reset states
    form.classList.remove('hidden');
    successBox.classList.add('hidden');
    errorBox.classList.add('hidden');
    modal.classList.remove('hidden');
  }

  function closeModal() {
    modal.classList.add('hidden');
  }

  openBtn.addEventListener('click', openModal);
  closeBtns.forEach(btn => btn.addEventListener('click', closeModal));

  form.addEventListener('submit', async e => {
    e.preventDefault();

    // Prepare form data
    const formData = new FormData(form);

    try {
      const resp = await fetch(form.action, {
        method: 'POST',
        body: formData
      });
      const payload = await resp.json();

      if (resp.ok && payload.status === 'OK') {
        // Success!
        form.classList.add('hidden');
        successBox.classList.remove('hidden');
      } else {
        // Server responded with a validation or other error
        form.classList.add('hidden');
        errorBox.classList.remove('hidden');
        errorMsg.textContent = payload.error || 'Something went wrong.';
      }
    } catch (networkErr) {
      // Network failure
      console.error('Network error:', networkErr);
      form.classList.add('hidden');
      errorBox.classList.remove('hidden');
      errorMsg.textContent = 'Network error. Please check your connection.';
    }
  });
});
