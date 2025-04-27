// static/settings.js

// Toggle expand sections
function toggleSection(id) {
    const section = document.getElementById(id);
    section.classList.toggle('hidden');
  }
  
  // Save profile
  document.getElementById('profile-form').addEventListener('submit', async function (e) {
    e.preventDefault();
  
    const formData = new FormData();
    formData.append('name', document.getElementById('profile-name').value);
    formData.append('username', document.getElementById('profile-username').value);
    formData.append('email', document.getElementById('profile-email').value);
    formData.append('password', document.getElementById('profile-password').value);
    
    const picInput = document.getElementById('upload-pic');
    if (picInput.files.length > 0) {
      formData.append('profile_pic', picInput.files[0]);
    }
  
    await fetch('/update_profile', {
      method: 'POST',
      body: formData
    });
  
    alert('Profile Updated! Refresh Dashboard to see changes.');
  });
  
  // Delete account
  document.getElementById('delete-account-btn').addEventListener('click', function () {
    if (confirm('Are you sure you want to delete your account? This cannot be undone!')) {
      fetch('/delete_account', { method: 'POST' })
        .then(res => {
          if (res.ok) {
            alert('Account deleted.');
            window.location.href = '/';
          }
        });
    }
  });
  function toggleSection(button, id) {
    const section = document.getElementById(id);
    const arrow = button.querySelector('.arrow');
  
    section.classList.toggle('hidden');
    
    if (section.classList.contains('hidden')) {
      arrow.textContent = '▼';
    } else {
      arrow.textContent = '▲';
    }
  }
  
  