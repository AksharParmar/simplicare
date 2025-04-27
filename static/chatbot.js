// --- chatbot.js (Updated) ---

// Send the user's message
async function sendMessage() {
  const userInput = document.getElementById('user-input').value.trim();

  if (!userInput) {
      return; // Skip sending empty or whitespace-only messages
  }

  displayUserMessage(userInput); // Instantly show user message

  try {
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
  } catch (error) {
      console.error('Error sending message:', error);
      displayBotMessage("Oops! Something went wrong.");
  }

  document.getElementById('user-input').value = ""; // Clear input after send
}

// Display the user's message
function displayUserMessage(message) {
  const chatbox = document.getElementById('chatbox');
  const userMessage = document.createElement('div');
  userMessage.classList.add('chat-message', 'user');
  userMessage.innerText = message;
  chatbox.appendChild(userMessage);
  chatbox.scrollTop = chatbox.scrollHeight; // Auto-scroll to bottom
}

// Display the bot's message (with markdown formatting)
function displayBotMessage(message) {
  const chatbox = document.getElementById('chatbox');
  const botMessage = document.createElement('div');
  botMessage.classList.add('chat-message', 'bot');
  botMessage.innerHTML = formatMarkdownToHTML(message); // <- Markdown support
  chatbox.appendChild(botMessage);
  chatbox.scrollTop = chatbox.scrollHeight; // Auto-scroll to bottom
}

// Simple Markdown Formatter (Bold, Italic, Inline Code, Line Breaks)
function formatMarkdownToHTML(markdown) {
  let html = markdown
    .replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>') // Bold **text**
    .replace(/\*(.*?)\*/g, '<em>$1</em>')             // Italic *text*
    .replace(/`([^`]+)`/g, '<code>$1</code>')         // Inline `code`
    .replace(/\n/g, '<br>');                          // Line breaks
  return html;
}

// Attach to form submit
document.getElementById('chat-form').addEventListener('submit', function(e) {
  e.preventDefault();
  sendMessage();
});
