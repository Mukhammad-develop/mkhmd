# Language AI Model - API Documentation

## 📋 Overview

This API provides text generation capabilities using a GPT-2 language model deployed on Google Cloud Run. It can generate human-like text based on prompts, similar to ChatGPT.

**Base URL**: `https://language-ai-api-atnpjnu3rq-nw.a.run.app`

**Model**: GPT-2 (124M parameters)

**Authentication**: No authentication required (public API)

---

## 🔌 Endpoints

### 1. Health Check

**Endpoint**: `GET /`

**Description**: Check if the API is running and healthy.

**Request**:
```bash
curl https://language-ai-api-atnpjnu3rq-nw.a.run.app/
```

**Response**:
```json
{
  "status": "healthy",
  "message": "Language AI Model API is running",
  "model": "gpt2"
}
```

---

### 2. Detailed Health Check

**Endpoint**: `GET /health`

**Description**: Get detailed health information about the model.

**Request**:
```bash
curl https://language-ai-api-atnpjnu3rq-nw.a.run.app/health
```

**Response**:
```json
{
  "status": "healthy",
  "model_loaded": true,
  "device": "cpu"
}
```

---

### 3. Generate Text

**Endpoint**: `POST /generate`

**Description**: Generate text based on a prompt. This is the main endpoint for text generation.

**Request Headers**:
```
Content-Type: application/json
```

**Request Body Parameters**:

| Parameter | Type | Required | Default | Range | Description |
|-----------|------|----------|---------|-------|-------------|
| `prompt` | string | **Yes** | - | - | The input text prompt |
| `max_tokens` | integer | No | 100 | 1-500 | Maximum number of tokens to generate |
| `temperature` | float | No | 0.8 | 0.0-2.0 | Controls randomness (higher = more random) |
| `top_k` | integer | No | 50 | 1-100 | Top-k sampling parameter |
| `top_p` | float | No | 0.95 | 0.0-1.0 | Nucleus sampling parameter |
| `num_sequences` | integer | No | 1 | 1-5 | Number of different texts to generate |

**Example Request (curl)**:
```bash
curl -X POST https://language-ai-api-atnpjnu3rq-nw.a.run.app/generate \
  -H 'Content-Type: application/json' \
  -d '{
    "prompt": "Once upon a time",
    "max_tokens": 100,
    "temperature": 0.7,
    "num_sequences": 1
  }'
```

**Example Request (Python)**:
```python
import requests

url = "https://language-ai-api-atnpjnu3rq-nw.a.run.app/generate"
payload = {
    "prompt": "Once upon a time",
    "max_tokens": 100,
    "temperature": 0.7,
    "num_sequences": 1
}

response = requests.post(url, json=payload)
result = response.json()
print(result["generated_texts"][0])
```

**Example Request (JavaScript)**:
```javascript
fetch('https://language-ai-api-atnpjnu3rq-nw.a.run.app/generate', {
  method: 'POST',
  headers: {
    'Content-Type': 'application/json'
  },
  body: JSON.stringify({
    prompt: "Once upon a time",
    max_tokens: 100,
    temperature: 0.7,
    num_sequences: 1
  })
})
.then(response => response.json())
.then(data => console.log(data.generated_texts[0]));
```

**Response**:
```json
{
  "generated_texts": [
    "Once upon a time, in a small village nestled in the mountains, there lived a young girl named Luna. She had always dreamed of exploring the world beyond her home..."
  ],
  "prompt": "Once upon a time",
  "model": "gpt2"
}
```

**Response Fields**:
- `generated_texts`: Array of generated text strings
- `prompt`: The original prompt that was provided
- `model`: The model name used for generation

---

### 4. Batch Generation

**Endpoint**: `POST /batch-generate`

**Description**: Generate text for multiple prompts in a single request (maximum 10 prompts).

**Request Body Parameters**:

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `prompts` | array[string] | **Yes** | Array of prompts (max 10) |
| `max_tokens` | integer | No | Maximum tokens per generation |

**Example Request**:
```bash
curl -X POST https://language-ai-api-atnpjnu3rq-nw.a.run.app/batch-generate \
  -H 'Content-Type: application/json' \
  -d '{
    "prompts": [
      "The future of AI is",
      "In the year 2050,",
      "Technology has changed"
    ],
    "max_tokens": 50
  }'
```

**Response**:
```json
{
  "results": [
    {
      "prompt": "The future of AI is",
      "generated_text": "The future of AI is bright and full of possibilities..."
    },
    {
      "prompt": "In the year 2050,",
      "generated_text": "In the year 2050, humans will have colonized Mars..."
    },
    {
      "prompt": "Technology has changed",
      "generated_text": "Technology has changed the way we live our lives..."
    }
  ],
  "count": 3
}
```

---

## 🎯 Parameter Guidelines

### Temperature
Controls the randomness of the output:
- **0.1-0.3**: Very focused and deterministic (good for factual content)
- **0.4-0.7**: Balanced creativity (recommended for most use cases)
- **0.8-1.0**: More creative and diverse
- **1.1-2.0**: Very creative, potentially chaotic

### Max Tokens
Controls the length of the generated text:
- **10-30**: Short responses (1-2 sentences)
- **50-100**: Medium responses (paragraph)
- **150-300**: Long responses (multiple paragraphs)
- **400-500**: Very long responses (article-length)

### Top-k and Top-p
Fine-tune the sampling strategy:
- **top_k (50)**: Consider top 50 most likely next tokens
- **top_p (0.95)**: Consider tokens whose cumulative probability is 95%

---

## 🚀 Building a ChatGPT-like Application

### Basic Chat Implementation (Python)

```python
import requests

class ChatBot:
    def __init__(self, api_url):
        self.api_url = api_url
        self.conversation_history = []
    
    def chat(self, user_message):
        # Add user message to history
        self.conversation_history.append(f"User: {user_message}")
        
        # Build prompt with conversation history
        prompt = "\n".join(self.conversation_history[-5:])  # Last 5 exchanges
        prompt += "\nAssistant:"
        
        # Generate response
        response = requests.post(
            f"{self.api_url}/generate",
            json={
                "prompt": prompt,
                "max_tokens": 150,
                "temperature": 0.7
            }
        )
        
        result = response.json()
        ai_response = result["generated_texts"][0]
        
        # Extract just the assistant's response
        ai_response = ai_response.split("Assistant:")[-1].strip()
        ai_response = ai_response.split("User:")[0].strip()
        
        # Add to history
        self.conversation_history.append(f"Assistant: {ai_response}")
        
        return ai_response
    
    def clear_history(self):
        self.conversation_history = []

# Usage
bot = ChatBot("https://language-ai-api-atnpjnu3rq-nw.a.run.app")

print("Bot:", bot.chat("Hello! How are you?"))
print("Bot:", bot.chat("Tell me a joke"))
print("Bot:", bot.chat("What was my first question?"))
```

### Web Interface (HTML + JavaScript)

```html
<!DOCTYPE html>
<html>
<head>
    <title>AI Chat</title>
    <style>
        body {
            font-family: Arial, sans-serif;
            max-width: 800px;
            margin: 50px auto;
            padding: 20px;
        }
        #chat-container {
            height: 400px;
            overflow-y: auto;
            border: 1px solid #ccc;
            padding: 20px;
            margin-bottom: 20px;
            background: #f9f9f9;
        }
        .message {
            margin: 10px 0;
            padding: 10px;
            border-radius: 5px;
        }
        .user {
            background: #007bff;
            color: white;
            text-align: right;
        }
        .assistant {
            background: #e9ecef;
            color: black;
        }
        #input-container {
            display: flex;
            gap: 10px;
        }
        #user-input {
            flex: 1;
            padding: 10px;
            font-size: 16px;
        }
        #send-btn {
            padding: 10px 20px;
            background: #007bff;
            color: white;
            border: none;
            cursor: pointer;
            font-size: 16px;
        }
    </style>
</head>
<body>
    <h1>AI Chat Assistant</h1>
    <div id="chat-container"></div>
    <div id="input-container">
        <input type="text" id="user-input" placeholder="Type your message...">
        <button id="send-btn">Send</button>
    </div>

    <script>
        const API_URL = 'https://language-ai-api-atnpjnu3rq-nw.a.run.app';
        const chatContainer = document.getElementById('chat-container');
        const userInput = document.getElementById('user-input');
        const sendBtn = document.getElementById('send-btn');
        let conversationHistory = [];

        function addMessage(text, isUser) {
            const messageDiv = document.createElement('div');
            messageDiv.className = `message ${isUser ? 'user' : 'assistant'}`;
            messageDiv.textContent = text;
            chatContainer.appendChild(messageDiv);
            chatContainer.scrollTop = chatContainer.scrollHeight;
        }

        async function sendMessage() {
            const message = userInput.value.trim();
            if (!message) return;

            // Add user message
            addMessage(message, true);
            userInput.value = '';

            // Build prompt with history
            conversationHistory.push(`User: ${message}`);
            const prompt = conversationHistory.slice(-5).join('\n') + '\nAssistant:';

            // Show loading
            sendBtn.disabled = true;
            sendBtn.textContent = 'Thinking...';

            try {
                const response = await fetch(`${API_URL}/generate`, {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({
                        prompt: prompt,
                        max_tokens: 150,
                        temperature: 0.7
                    })
                });

                const data = await response.json();
                let aiResponse = data.generated_texts[0];
                
                // Extract assistant's response
                aiResponse = aiResponse.split('Assistant:').pop().trim();
                aiResponse = aiResponse.split('User:')[0].trim();

                // Add AI message
                addMessage(aiResponse, false);
                conversationHistory.push(`Assistant: ${aiResponse}`);
            } catch (error) {
                addMessage('Error: Could not connect to API', false);
            }

            sendBtn.disabled = false;
            sendBtn.textContent = 'Send';
        }

        sendBtn.addEventListener('click', sendMessage);
        userInput.addEventListener('keypress', (e) => {
            if (e.key === 'Enter') sendMessage();
        });
    </script>
</body>
</html>
```

### React Component Example

```javascript
import React, { useState } from 'react';

const ChatBot = () => {
  const [messages, setMessages] = useState([]);
  const [input, setInput] = useState('');
  const [loading, setLoading] = useState(false);
  const API_URL = 'https://language-ai-api-atnpjnu3rq-nw.a.run.app';

  const sendMessage = async () => {
    if (!input.trim()) return;

    const userMessage = { text: input, isUser: true };
    setMessages(prev => [...prev, userMessage]);
    setInput('');
    setLoading(true);

    try {
      const history = messages.slice(-4);
      const prompt = history.map(m => 
        `${m.isUser ? 'User' : 'Assistant'}: ${m.text}`
      ).join('\n') + `\nUser: ${input}\nAssistant:`;

      const response = await fetch(`${API_URL}/generate`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          prompt: prompt,
          max_tokens: 150,
          temperature: 0.7
        })
      });

      const data = await response.json();
      let aiText = data.generated_texts[0];
      aiText = aiText.split('Assistant:').pop().trim();
      aiText = aiText.split('User:')[0].trim();

      setMessages(prev => [...prev, { text: aiText, isUser: false }]);
    } catch (error) {
      setMessages(prev => [...prev, { 
        text: 'Error connecting to API', 
        isUser: false 
      }]);
    }

    setLoading(false);
  };

  return (
    <div className="chatbot">
      <div className="messages">
        {messages.map((msg, idx) => (
          <div key={idx} className={msg.isUser ? 'user' : 'assistant'}>
            {msg.text}
          </div>
        ))}
        {loading && <div className="assistant">Thinking...</div>}
      </div>
      <div className="input-area">
        <input
          value={input}
          onChange={e => setInput(e.target.value)}
          onKeyPress={e => e.key === 'Enter' && sendMessage()}
          placeholder="Type your message..."
        />
        <button onClick={sendMessage} disabled={loading}>
          Send
        </button>
      </div>
    </div>
  );
};

export default ChatBot;
```

---

## ⚡ Usage Examples

### Example 1: Story Generation
```bash
curl -X POST https://language-ai-api-atnpjnu3rq-nw.a.run.app/generate \
  -H 'Content-Type: application/json' \
  -d '{
    "prompt": "Write a short story about a robot learning to feel emotions:",
    "max_tokens": 200,
    "temperature": 0.9
  }'
```

### Example 2: Code Explanation
```bash
curl -X POST https://language-ai-api-atnpjnu3rq-nw.a.run.app/generate \
  -H 'Content-Type: application/json' \
  -d '{
    "prompt": "Explain what this Python code does:\ndef factorial(n):\n    return 1 if n <= 1 else n * factorial(n-1)\n\nExplanation:",
    "max_tokens": 100,
    "temperature": 0.3
  }'
```

### Example 3: Creative Writing
```bash
curl -X POST https://language-ai-api-atnpjnu3rq-nw.a.run.app/generate \
  -H 'Content-Type: application/json' \
  -d '{
    "prompt": "Write a haiku about artificial intelligence:",
    "max_tokens": 50,
    "temperature": 0.8
  }'
```

### Example 4: Question Answering
```bash
curl -X POST https://language-ai-api-atnpjnu3rq-nw.a.run.app/generate \
  -H 'Content-Type: application/json' \
  -d '{
    "prompt": "Q: What is the capital of France?\nA:",
    "max_tokens": 30,
    "temperature": 0.3
  }'
```

---

## 🔧 Error Handling

### Error Response Format
```json
{
  "detail": "Error message description"
}
```

### Common Error Codes

| Status Code | Description | Solution |
|-------------|-------------|----------|
| 400 | Bad Request | Check request parameters |
| 422 | Validation Error | Ensure all required fields are present |
| 500 | Internal Server Error | The model encountered an error |
| 503 | Service Unavailable | Model is loading (wait 30-60 seconds) |

### Error Handling Example (Python)
```python
import requests

def generate_text(prompt, max_tokens=100):
    try:
        response = requests.post(
            "https://language-ai-api-atnpjnu3rq-nw.a.run.app/generate",
            json={"prompt": prompt, "max_tokens": max_tokens},
            timeout=60
        )
        response.raise_for_status()
        return response.json()["generated_texts"][0]
    except requests.exceptions.Timeout:
        return "Error: Request timed out. Model may be cold-starting."
    except requests.exceptions.HTTPError as e:
        return f"Error: HTTP {e.response.status_code}"
    except Exception as e:
        return f"Error: {str(e)}"
```

---

## 📊 Rate Limits & Performance

- **Cold Start**: First request may take 30-60 seconds (model loading)
- **Warm Requests**: 2-10 seconds per request
- **Concurrent Requests**: Supports multiple simultaneous requests
- **Rate Limit**: No specific rate limit (Google Cloud Run autoscaling)
- **Timeout**: 60 seconds per request

---

## 💡 Best Practices

### 1. Crafting Good Prompts
- **Be specific**: "Write a professional email" vs "Write something"
- **Provide context**: Include relevant information in the prompt
- **Use examples**: Show the model what you want
- **Set the tone**: "Write formally" or "Write casually"

### 2. Managing Conversations
- Keep the last 5-10 exchanges for context
- Don't send entire conversation history (increases latency)
- Format conversations clearly (User:/Assistant:)

### 3. Optimizing Performance
- Use lower `max_tokens` for faster responses
- Cache common responses
- Implement retry logic for cold starts
- Handle timeouts gracefully

### 4. Content Filtering
- The model generates based on patterns in training data
- Implement your own content filtering if needed
- Monitor generated content for appropriateness

---

## 🌐 CORS Support

The API supports Cross-Origin Resource Sharing (CORS), allowing you to call it from web browsers:

```javascript
// Works from any domain
fetch('https://language-ai-api-atnpjnu3rq-nw.a.run.app/generate', {
  method: 'POST',
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify({ prompt: 'Hello', max_tokens: 50 })
})
.then(response => response.json())
.then(data => console.log(data));
```

---

## 📞 Support & Additional Resources

- **API Base URL**: https://language-ai-api-atnpjnu3rq-nw.a.run.app
- **Health Check**: https://language-ai-api-atnpjnu3rq-nw.a.run.app/
- **Model**: GPT-2 (124M parameters)
- **Deployment**: Google Cloud Run (auto-scaling)

---

## 🎉 Quick Start Summary

1. **Test the API**:
   ```bash
   curl https://language-ai-api-atnpjnu3rq-nw.a.run.app/
   ```

2. **Generate text**:
   ```bash
   curl -X POST https://language-ai-api-atnpjnu3rq-nw.a.run.app/generate \
     -H 'Content-Type: application/json' \
     -d '{"prompt": "Hello!", "max_tokens": 50}'
   ```

3. **Build your app** using the examples above!

---

**Ready to build!** This API is production-ready and can handle real-world applications. Start building your ChatGPT-like app today! 🚀

