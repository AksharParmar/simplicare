// static/app.js

// Request Notification Permission
if (Notification.permission !== 'granted') {
  Notification.requestPermission();
}

// Find elements
const medForm = document.getElementById('medication-form');
const confirmBtn = document.getElementById('confirm-button');
const dashboardMedList = document.getElementById('dashboard-medication-list'); // For dashboard meds only

// --- Handle ListView (Add Medications) ---
if (medForm) {
  medForm.addEventListener('submit', async function (e) {
    e.preventDefault();

    const medicineName = document.getElementById('medicine-name').value.trim();
    const dosage = document.getElementById('dosage').value.trim();
    const dailyIntake = document.getElementById('daily-intake').value.trim();
    const weeklyFrequency = document.getElementById('weekly-frequency').value.trim();

    if (!medicineName || !dosage || !dailyIntake) {
      alert('Please fill out all required fields!');
      return;
    }

    const medication = {
      name: medicineName,
      dosage: dosage,
      daily_intake: dailyIntake,
      weekly_frequency: weeklyFrequency || 'N/A'
    };

    const response = await fetch('/add_medication', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(medication)
    });

    if (response.ok) {
      document.getElementById('medication-form').reset();
      loadMedications(); // Refresh list
    }
  });
}

// --- Handle Dashboard Intake Confirmation ---
if (confirmBtn) {
  confirmBtn.addEventListener('click', function () {
    const confirmationMessage = document.getElementById('confirmation-message');
    confirmationMessage.textContent = "✅ Great job staying on track!";
    setTimeout(() => {
      confirmationMessage.textContent = "";
    }, 3000);
  });
}

// --- Load Medications on ListView ---
async function loadMedications() {
  const response = await fetch('/get_medications');
  const meds = await response.json();
  const list = document.getElementById('medication-list'); // ListView only
  if (!list) return;

  list.innerHTML = '';

  if (meds.length === 0) {
    list.innerHTML = '<li>No medications added yet!</li>';
    return;
  }

  meds.forEach((med, index) => {
    const li = document.createElement('li');
    li.innerHTML = `
      <strong>${med.name}</strong> (${med.dosage}mg) - ${med.daily_intake}x/day
      <button onclick="deleteMedication(${index})" class="delete-btn">Delete</button>
    `;
    list.appendChild(li);
  });
}

// --- Load Medications on Dashboard (NO DELETE) ---
async function loadDashboardMedications() {
  const response = await fetch('/get_medications');
  const meds = await response.json();
  const list = document.getElementById('dashboard-medication-list'); // Dashboard only
  if (!list) return;

  list.innerHTML = '';

  if (meds.length === 0) {
    list.innerHTML = '<li>No medications added yet!</li>';
    return;
  }

  meds.slice(0, 3).forEach(med => {
    const dosage = med.dosage || 'Unknown';
    const name = med.name || 'Unknown';
    const dailyIntake = med.daily_intake || 'Unknown';
    const timesText = dailyIntake === "1" ? "time" : "times";

    const li = document.createElement('li');
    li.innerHTML = `Take <strong>${dosage}mg</strong> of <strong>${name}</strong> <strong>${dailyIntake}</strong> ${timesText} today.`;
    list.appendChild(li);
  });
}

// --- Delete Medication (only from ListView) ---
async function deleteMedication(index) {
  if (!confirm('Are you sure you want to delete this medication?')) return;

  await fetch(`/delete_medication/${index}`, {
    method: 'DELETE'
  });

  loadMedications(); // Refresh after deletion
}

// --- On Page Load ---
window.addEventListener('DOMContentLoaded', () => {
  loadMedications();            // Load meds if on ListView
  loadDashboardMedications();   // Load meds if on Dashboard
});

