// static/listview.js

document.addEventListener('DOMContentLoaded', loadMedications);

// Handle Add Medication Form
document.getElementById('medication-form').addEventListener('submit', async function (e) {
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

  try {
    const response = await fetch('/add_medication', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(medication)
    });

    if (!response.ok) {
      throw new Error('Failed to add medication');
    }

    // Clear the form after successful addition
    document.getElementById('medication-form').reset();

    // Reload the medications list
    loadMedications();
  } catch (error) {
    console.error('Error adding medication:', error);
    alert('There was a problem adding your medication. Please try again.');
  }
});

// Load medications and display them
async function loadMedications() {
  try {
    const response = await fetch('/get_medications');
    if (!response.ok) {
      throw new Error('Failed to fetch medications');
    }
    const meds = await response.json();
    const list = document.getElementById('medication-list');
    list.innerHTML = '';

    if (meds.length === 0) {
      list.innerHTML = '<li>No medications added yet.</li>';
      return;
    }

    meds.forEach((med, index) => {
      const li = document.createElement('li');
      li.innerHTML = `
        <div class="medication-info">
          <strong>${med.name}</strong><br>
          Dosage: ${med.dosage} mg<br>
          Daily Intake: ${med.daily_intake} times/day<br>
          Weekly Frequency: ${med.weekly_frequency}
        </div>
        <button class="delete-btn" onclick="deleteMedication(${index})">Delete</button>
      `;
      list.appendChild(li);
    });

  } catch (error) {
    console.error('Error loading medications:', error);
    alert('Unable to load medications.');
  }
}

// Delete a medication
async function deleteMedication(index) {
  if (!confirm('Are you sure you want to delete this medication?')) return;

  try {
    const response = await fetch(`/delete_medication/${index}`, {
      method: 'DELETE'
    });

    if (!response.ok) {
      throw new Error('Failed to delete medication');
    }

    loadMedications();
  } catch (error) {
    console.error('Error deleting medication:', error);
    alert('Failed to delete medication.');
  }
}
