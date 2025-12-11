document.addEventListener('DOMContentLoaded', async () => {
  await loadActivities();
  setupSignupForm();
});

async function loadActivities() {
  try {
    const response = await fetch('/activities');
    const activities = await response.json();
    
    displayActivities(activities);
    populateActivityDropdown(activities);
  } catch (error) {
    console.error('Error loading activities:', error);
    document.getElementById('activities-list').innerHTML = 
      '<p class="error">Failed to load activities. Please try again later.</p>';
  }
}

function displayActivities(activities) {
  const container = document.getElementById('activities-list');
  container.innerHTML = '';
  
  for (const [name, details] of Object.entries(activities)) {
    const card = document.createElement('div');
    card.className = 'activity-card';
    
    const participantsList = details.participants.length > 0
      ? `<ul>${details.participants.map(email => `<li>${email}</li>`).join('')}</ul>`
      : '<p style="color: #999; font-style: italic;">No participants yet</p>';
    
    card.innerHTML = `
      <h4>${name}</h4>
      <p><strong>Description:</strong> ${details.description}</p>
      <p><strong>Schedule:</strong> ${details.schedule}</p>
      <p><strong>Spots Available:</strong> ${details.max_participants - details.participants.length} / ${details.max_participants}</p>
      <div class="activity-participants">
        <h5>Current Participants <span class="participants-count">(${details.participants.length})</span></h5>
        ${participantsList}
      </div>
    `;
    
    container.appendChild(card);
  }
}

function populateActivityDropdown(activities) {
  const select = document.getElementById('activity');
  select.innerHTML = '<option value="">-- Select an activity --</option>';
  
  for (const name of Object.keys(activities)) {
    const option = document.createElement('option');
    option.value = name;
    option.textContent = name;
    select.appendChild(option);
  }
}

function setupSignupForm() {
  const form = document.getElementById('signup-form');
  form.addEventListener('submit', async (e) => {
    e.preventDefault();
    
    const email = document.getElementById('email').value;
    const activity = document.getElementById('activity').value;
    
    await signupForActivity(activity, email);
  });
}

async function signupForActivity(activityName, email) {
  const messageDiv = document.getElementById('message');
  
  try {
    const response = await fetch(`/activities/${encodeURIComponent(activityName)}/signup?email=${encodeURIComponent(email)}`, {
      method: 'POST'
    });
    
    const data = await response.json();
    
    if (response.ok) {
      showMessage(data.message, 'success');
      document.getElementById('signup-form').reset();
      await loadActivities(); // Refresh the activities list
    } else {
      showMessage(data.detail || 'Failed to sign up', 'error');
    }
  } catch (error) {
    console.error('Error signing up:', error);
    showMessage('An error occurred. Please try again.', 'error');
  }
}

function showMessage(text, type) {
  const messageDiv = document.getElementById('message');
  messageDiv.textContent = text;
  messageDiv.className = `message ${type}`;
  messageDiv.classList.remove('hidden');
  
  setTimeout(() => {
    messageDiv.classList.add('hidden');
  }, 5000);
}
