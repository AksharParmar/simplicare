// Request notification permission
if (Notification.permission !== 'granted') {
    Notification.requestPermission();
}

document.getElementById('medication-form').addEventListener('submit', async function(event) {
  event.preventDefault();

  const medName = document.getElementById('med-name').value;
  const dosage = document.getElementById('dosage').value;
  const time = document.getElementById('time').value;

  const medication = { medName, dosage, time };

  await fetch('/add_medication', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(medication)
  });

  scheduleNotification(medication);
  document.getElementById('medication-form').reset();
  loadMedications();
});

async function loadMedications() {
  const response = await fetch('/get_medications');
  const meds = await response.json();

  const list = document.getElementById('medication-list');
  list.innerHTML = '';
  meds.forEach(med => {
    const li = document.createElement('li');
    li.textContent = `${med.medName} - ${med.dosage} at ${med.time}`;
    list.appendChild(li);
  });
}

// Function to schedule notification
function scheduleNotification(medication) {
  const now = new Date();
  const medTime = new Date();
  const [hours, minutes] = medication.time.split(':');
  medTime.setHours(hours);
  medTime.setMinutes(minutes);
  medTime.setSeconds(0);

  let timeout = medTime.getTime() - now.getTime();
  if (timeout < 0) {
    timeout += 24 * 60 * 60 * 1000; // If time already passed today, set for tomorrow
  }

  setTimeout(() => {
    new Notification(`Time for ${medication.medName}`, {
      body: `Take your dosage: ${medication.dosage}`,
      icon: 'https://img.icons8.com/fluency/48/000000/pill.png'
    });
  }, timeout);
}

window.onload = loadMedications;
