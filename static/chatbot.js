async function sendMessage() {
  const userInput = document.getElementById('user-input').value;

  if (!userInput.trim()) {
      return; // Skip sending empty messages
  }

  displayUserMessage(userInput); // Show user message immediately

  const response = await fetch('/ask', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ message: userInput })
  });

  const data = await response.json();

  if (data.response) {
      displayBotMessage(data.response);
  } else {
      displayBotMessage("Sorry, I couldn't get a response.");
  }

  document.getElementById('user-input').value = ""; // Clear input
}

function displayUserMessage(message) {
  const chatbox = document.getElementById('chatbox');
  const msgDiv = document.createElement('div');
  msgDiv.classList.add('chat-message', 'user');
  msgDiv.innerText = message;
  chatbox.appendChild(msgDiv);
  chatbox.scrollTop = chatbox.scrollHeight;
}

function displayBotMessage(message) {
  const chatbox = document.getElementById('chatbox');
  const msgDiv = document.createElement('div');
  msgDiv.classList.add('chat-message', 'bot');
  msgDiv.innerText = message;
  chatbox.appendChild(msgDiv);
  chatbox.scrollTop = chatbox.scrollHeight;
}

// Attach sendMessage to form submit
document.getElementById('chat-form').addEventListener('submit', function(e) {
  e.preventDefault();
  sendMessage();
});
