// Initialize highlight.js
hljs.highlightAll();

// Initialize the markdown-it parser
const md = markdownit({
    highlight: function (str, lang) {
      if (lang && hljs.getLanguage(lang)) {
        try {
          return '<pre><code class="hljs">' +
                 hljs.highlight(str, { language: lang, ignoreIllegals: true }).value +
                 '</code></pre>';
        } catch (__) {}
      }
  
      return '<pre><code class="hljs">' + md.utils.escapeHtml(str) + '</code></pre>';
    }
  });

// Object to store all text messages received from the LLM as-is
var llmResponses = {};

// This function makes all input/output divs dynamically resize to the height of their content.
function autoResizeDivs() {
    document.querySelectorAll('[contenteditable=true]').forEach(div => {
        div.style.height = 'auto'; // Reset height to auto before calculating
        div.style.height = div.scrollHeight + 'px'; // Set height to scroll height
    });
}

// Call it initially to set the correct height
autoResizeDivs();

// Add event listeners to all input/output divs to resize on input
document.querySelectorAll('[contenteditable=true]').forEach(div => {
    div.addEventListener('input', autoResizeDivs);
});

document.addEventListener('DOMContentLoaded', function() {
    var coll = document.getElementsByClassName("collapsible");
    for (var i = 0; i < coll.length; i++) {
        coll[i].addEventListener("click", function() {
            this.classList.toggle("active");
            var content = this.nextElementSibling;
            if (content.style.display === "block") {
                content.style.display = "none";
            } else {
                content.style.display = "block";
            }
        });
    }
});

function addLLMMessage(userMessage) {
    const chatContainer = document.querySelector('.interaction');

    // Add the LLM message
    const llmMessageDiv = document.createElement('div');
    llmMessageDiv.classList.add('message');

    const llmMessageHeader = document.createElement('div');
    llmMessageHeader.classList.add('message-header');

    const llmLabel = document.createElement('label');
    llmLabel.textContent = 'LLM:';
    llmLabel.setAttribute('for', `llm-output-${crypto.randomUUID().slice(0,6)}`);
    llmMessageHeader.appendChild(llmLabel);

    const deleteLLMButton = document.createElement('button');
    deleteLLMButton.textContent = 'Delete';
    deleteLLMButton.classList.add('delete-btn');
    deleteLLMButton.onclick = function() {
        deleteMessage(llmMessageDiv);
    };
    llmMessageHeader.appendChild(deleteLLMButton);

    const llmOutput = document.createElement('div');
    llmOutput.id = `llm-output-${crypto.randomUUID().slice(0,6)}`;
    llmOutput.classList.add('llm-output');
    llmOutput.contentEditable = true;

    const llmMessageContent = document.createElement('div');
    llmMessageContent.classList.add('message-content');
    llmMessageContent.appendChild(llmMessageHeader);
    llmMessageContent.appendChild(llmOutput);

    llmMessageDiv.appendChild(llmMessageContent);
    chatContainer.appendChild(llmMessageDiv);

    // Add the user message
    const userMessageDiv = document.createElement('div');
    userMessageDiv.classList.add('message');

    const userMessageHeader = document.createElement('div');
    userMessageHeader.classList.add('message-header');

    const userLabel = document.createElement('label');
    userLabel.textContent = 'User:';
    userLabel.setAttribute('for', `user-input-${crypto.randomUUID().slice(0,6)}`);
    userMessageHeader.appendChild(userLabel);

    const deleteUserButton = document.createElement('button');
    deleteUserButton.textContent = 'Delete';
    deleteUserButton.classList.add('delete-btn');
    deleteUserButton.onclick = function() {
        deleteMessage(userMessageDiv);
    };
    userMessageHeader.appendChild(deleteUserButton);

    const userInput = document.createElement('div');
    userInput.id = `user-input-${crypto.randomUUID().slice(0,6)}`;
    userInput.classList.add('user-input');
    userInput.contentEditable = true;
    userInput.value = userMessage;

    const userMessageContent = document.createElement('div');
    userMessageContent.classList.add('message-content');
    userMessageContent.appendChild(userMessageHeader);
    userMessageContent.appendChild(userInput);

    userMessageDiv.appendChild(userMessageContent);
    chatContainer.appendChild(userMessageDiv);

    // Auto-resize divs
    autoResizeDivs();

    // Add event listener to all input divs to trigger LLM response
    document.querySelectorAll('[contenteditable=true]').forEach(div => {
        div.addEventListener('keydown', handleSubmit);
    });

    // Select the text area of the new user message
    userInput.focus();
}

// Add event listener to all input divs to trigger LLM response
document.querySelectorAll('[contenteditable=true]').forEach(div => {
    div.addEventListener('keydown', handleSubmit);
});

// Define async function to handle message submission
async function handleSubmit(event) {
    if (event.ctrlKey && event.key === 'Enter') {
        const userMessage = "";
        const isUserMessageDiv = event.target.parentNode.querySelector('label').textContent === 'User:';

        if (isUserMessageDiv) {
            addLLMMessage(userMessage);
        }

        // Get the system prompt and all of the user/LLM messages in order of appearance in the main chat div
        const systemPrompt = document.querySelector('#system-prompt').textContent;
        const previousMessages = Array.from(document.querySelectorAll('.user-input, .llm-output')).slice(0,-2);
        
        // Combine messages into an array of objects matching the OpenAI Specification
        var messages = previousMessages.map((message) => ({
            role: message.id.includes("llm-output") ? 'assistant' : 'user',
            content: message.id.includes("llm-output") ? llmResponses[message.id] : message.textContent
        }));

        // Add system prompt as the first message
        messages.unshift({
            role: 'system',
            content: systemPrompt
        });

        // Get generation parameters
        const model = document.querySelector('#model').value;
        const temperature = document.querySelector('#temperature').value;
        const topP = document.querySelector('#top-p').value;
        const maxTokens = document.querySelector('#max-tokens').value;

        // Combine messages and generation parameters into a single object matching the OpenAI Specification
        const payload = {
            model: model,
            messages: messages,
            temperature: parseFloat(temperature),
            top_p: parseFloat(topP),
            max_tokens: parseInt(maxTokens)
        };

        // Send the payload via POST request to the /payload endpoint, and handle the generator response
        const response = await fetch('/payload', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify(payload)
        });

        let token_count = 0;
        let full_response = "";
        if (response.ok) {
            const reader = response.body.getReader();
            const decoder = new TextDecoder('utf-8');

            // Find the last LLM message div by getting all input/output divs and selecting the 2nd to last one
            const llmOutput = Array.from(document.querySelectorAll('.user-input, .llm-output')).slice(-2)[0];

            while (true) {
                const { done, value } = await reader.read();
                if (done) {
                    autoResizeDivs();
                    llmOutput.scrollIntoView();
                    break;
                }
                const text = decoder.decode(value);
                
                // Update the full response with the new text
                full_response += text;
                llmResponses[llmOutput.id] = full_response;

                // Format with markdown-it
                const md_response = md.render(full_response);

                llmOutput.innerHTML = md_response;
                token_count += 1

                // Resize the text area after every 50 tokens, and scroll to make sure the latest message is visible
                if (token_count % 50 === 0) {
                    autoResizeDivs();
                    llmOutput.scrollIntoView();
                }

            }
        } else {
            // Handle non-200 status codes
            const errorText = await response.text();
            // outputElement.textContent = `Error: ${errorText}`;
        }
    }
}

// Function to delete a message
function deleteMessage(messageDiv) {
    messageDiv.parentNode.removeChild(messageDiv);
}

// Global keyboard shortcuts
document.addEventListener('keydown', function(event) {
    // Check if the Ctrl + M key combination is pressed
    if (event.ctrlKey && event.key === 'm') {
        // Prevent the default behavior of Ctrl + M
        event.preventDefault();

        // Expand the parameters dropdown div
        var parametersDropdown = document.querySelector('.collapsible');
        parametersDropdown.click();

        // Select the model selection tool
        var modelSelect = document.querySelector('#model');
        modelSelect.focus();
    }

    // Check if the Escape key is pressed
    if (event.key === 'Escape') {
        // Get the parameters dropdown div content element
        var parametersDropdownContent = document.querySelector('.content');

        // Check if the dropdown is open
        if (parametersDropdownContent.style.display === 'block') {
        // Minimize the parameters dropdown div
        parametersDropdownContent.parentElement.querySelector('.collapsible').click();
        }

        // Select the last user message text box
        var messageContents = document.querySelectorAll('.interaction .message .message-content');
        var lastUserMessageTextbox = messageContents[messageContents.length - 1].querySelector('.user-input');

        if (lastUserMessageTextbox) {
            lastUserMessageTextbox.focus();
        }
    }

    // Delete currently selected message with control + d
    if (event.ctrlKey && event.key === 'd') {
        // Suppress the default behavior of Ctrl + D
        event.preventDefault();

        // Get the current active element
        var activeElement = document.activeElement;

        // Check if the active element is a editable div
        if (activeElement.tagName === 'DIV' && activeElement.contentEditable === 'true') {
            // Get the parent message content
            var messageContent = activeElement.parentNode.parentNode;

            // Delete the parent message content
            if (messageContent) {
                deleteMessage(messageContent);
            }

            // Select the now latest user message text box
            var messageContents = document.querySelectorAll('.interaction .message .message-content');
            var latestUserMessageTextbox = Array.from(document.querySelectorAll('.user-input, .llm-output')).slice(-1)[0];

            if (latestUserMessageTextbox) {
                latestUserMessageTextbox.focus();
            }
        }
    }

    // Check for control + up/down to select the previous/next message
    if (event.ctrlKey && event.key === 'ArrowUp') {
        // Get the current active element
        var activeElement = document.activeElement;

        // Check if the active element is an editable div
        if (activeElement.tagName === 'DIV' && activeElement.contentEditable === 'true') {
            // Get the previous message content
            var previousMessageContent = activeElement.parentNode.parentNode.previousElementSibling;

            // Check if the previous message content exists
            if (previousMessageContent) {
                // Get the previous message div
                var previousMessageDiv = previousMessageContent.querySelector('.user-input, .llm-output');

                // Focus on the previous message div
                if (previousMessageDiv) {
                    previousMessageDiv.focus();
                }
            }
        }
    }
    if (event.ctrlKey && event.key === 'ArrowDown') {
        // Get the current active element
        var activeElement = document.activeElement;

        // Check if the active element is an editable div
        if (activeElement.tagName === 'DIV' && activeElement.contentEditable === 'true') {
            // Get the next message content
            var nextMessageContent = activeElement.parentNode.parentNode.nextElementSibling;

            // Check if the next message content exists
            if (nextMessageContent) {
                // Get the next message div
                var nextMessageDiv = nextMessageContent.querySelector('.user-input, .llm-output');

                // Focus on the next message div
                if (nextMessageDiv) {
                    nextMessageDiv.focus();
                }
            }
        }
    }
});

// Define startup tasks on page load
document.addEventListener('DOMContentLoaded', function() {
    // Select the first user message text box
    var firstUserMessageTextbox = document.querySelector('.interaction .message .message-content:first-child .user-input');

    if (firstUserMessageTextbox) {
        firstUserMessageTextbox.focus();
    }

    // Get available model names from the /models GET endpoint
    fetch('/models')
        .then(response => response.json())
        .then(data => {
            // Get the model selection dropdown
            var modelSelect = document.querySelector('#model');

            // Populate the model selection dropdown with the available models
            data.forEach(model => {
                var option = document.createElement('option');
                option.value = model;
                option.text = model;
                modelSelect.appendChild(option);
            });
        });
});