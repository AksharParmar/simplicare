// auth.js - For login page frontend behavior

document.addEventListener('DOMContentLoaded', function() {
    const form = document.querySelector('.login-form');
  
    form.addEventListener('submit', function(event) {
      const usernameInput = form.querySelector('input[name="username"]');
  
      // Basic validation
      if (!usernameInput.value.trim()) {
        event.preventDefault();
        alert('Please enter your name to continue.');
        return false;
      }
  
      // Optionally: disable button to prevent multiple submissions
      const submitButton = form.querySelector('button[type="submit"]');
      submitButton.disabled = true;
      submitButton.textContent = 'Logging in...';
    });
  });
  