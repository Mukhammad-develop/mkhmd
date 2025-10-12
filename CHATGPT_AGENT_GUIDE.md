# 🤖 Building ChatGPT-Like Agents with Your API

## Complete Developer Guide for Conversational AI Applications

**API Endpoint**: `https://language-ai-api-atnpjnu3rq-nw.a.run.app`  
**Model**: Mistral 7B Instruct (GPU-powered via HuggingFace)  
**Best For**: Chatbots, AI assistants, conversational agents

---

## 📋 Table of Contents

1. [Quick Start](#quick-start)
2. [API Overview](#api-overview)
3. [Building a Chat Interface](#building-a-chat-interface)
4. [Managing Conversation Context](#managing-conversation-context)
5. [Code Examples](#code-examples)
6. [Best Practices](#best-practices)
7. [Advanced Patterns](#advanced-patterns)
8. [Troubleshooting](#troubleshooting)

---

## 🚀 Quick Start

### **Step 1: Test the API**

```bash
curl -X POST https://language-ai-api-atnpjnu3rq-nw.a.run.app/generate \
  -H 'Content-Type: application/json' \
  -d '{
    "prompt": "Hello! How can I help you today?",
    "max_tokens": 100,
    "temperature": 0.7
  }'
```

### **Step 2: Understand the Response**

```json
{
  "generated_texts": [
    "Hello! How can I help you today? I'm here to assist you with any questions..."
  ],
  "prompt": "Hello! How can I help you today?",
  "model": "mistralai/Mistral-7B-Instruct-v0.2",
  "powered_by": "HuggingFace Inference API (GPU)"
}
```

### **Step 3: Build Your Chat Agent!**

See code examples below →

---

## 📡 API Overview

### **Endpoint**

```
POST https://language-ai-api-atnpjnu3rq-nw.a.run.app/generate
```

### **Request Parameters**

| Parameter | Type | Required | Default | Description |
|-----------|------|----------|---------|-------------|
| `prompt` | string | ✅ Yes | - | The input text/conversation |
| `max_tokens` | integer | ❌ No | 100 | Maximum length of response (1-1000) |
| `temperature` | float | ❌ No | 0.8 | Creativity level (0.0-2.0) |
| `top_k` | integer | ❌ No | 50 | Top-k sampling (1-100) |
| `top_p` | float | ❌ No | 0.95 | Nucleus sampling (0.0-1.0) |
| `num_sequences` | integer | ❌ No | 1 | Number of responses (1-3) |

### **Response Format**

```json
{
  "generated_texts": ["AI response text here"],
  "prompt": "Your input prompt",
  "model": "mistralai/Mistral-7B-Instruct-v0.2",
  "powered_by": "HuggingFace Inference API (GPU)"
}
```

### **HTTP Status Codes**

| Code | Meaning | Action |
|------|---------|--------|
| 200 | Success | Process the response |
| 429 | Rate limit | Wait and retry |
| 500 | Server error | Retry after a moment |
| 503 | Model loading | Wait 30s and retry |

---

## 💬 Building a Chat Interface

### **Key Concepts**

1. **Conversation Context**: Maintain chat history
2. **Prompt Engineering**: Format messages properly
3. **State Management**: Track conversation state
4. **User Experience**: Handle loading, errors, typing indicators

### **Chat Architecture**

```
User Message → Format with Context → API Request → Parse Response → Display → Update Context
```

---

## 🎯 Managing Conversation Context

### **Basic Pattern**

For ChatGPT-like behavior, include conversation history in your prompts:

```javascript
// Build conversation context
const formatConversation = (messages) => {
  let context = "You are a helpful AI assistant. Respond naturally and helpfully.\n\n";
  
  messages.forEach(msg => {
    if (msg.role === 'user') {
      context += `User: ${msg.content}\n`;
    } else if (msg.role === 'assistant') {
      context += `Assistant: ${msg.content}\n`;
    }
  });
  
  context += "Assistant:";
  return context;
};

// Example usage
const messages = [
  { role: 'user', content: 'Hello! What is AI?' },
  { role: 'assistant', content: 'AI stands for Artificial Intelligence...' },
  { role: 'user', content: 'Can you explain more?' }
];

const prompt = formatConversation(messages);
```

### **Context Window Management**

Mistral 7B has a ~32K token context window. For long conversations:

```javascript
const MAX_CONTEXT_MESSAGES = 10; // Keep last 10 messages

const trimContext = (messages) => {
  if (messages.length > MAX_CONTEXT_MESSAGES) {
    // Keep system message + last N messages
    const systemMsg = messages.find(m => m.role === 'system');
    const recentMessages = messages.slice(-MAX_CONTEXT_MESSAGES);
    
    return systemMsg ? [systemMsg, ...recentMessages] : recentMessages;
  }
  return messages;
};
```

---

## 💻 Code Examples

### **Example 1: Simple Python Chatbot**

```python
import requests
import json

API_URL = "https://language-ai-api-atnpjnu3rq-nw.a.run.app/generate"

class ChatBot:
    def __init__(self):
        self.conversation_history = []
        self.system_prompt = "You are a helpful AI assistant."
    
    def format_prompt(self, user_message):
        """Format conversation history into a prompt"""
        prompt = f"{self.system_prompt}\n\n"
        
        # Add conversation history
        for msg in self.conversation_history:
            if msg['role'] == 'user':
                prompt += f"User: {msg['content']}\n"
            elif msg['role'] == 'assistant':
                prompt += f"Assistant: {msg['content']}\n"
        
        # Add new user message
        prompt += f"User: {user_message}\n"
        prompt += "Assistant:"
        
        return prompt
    
    def chat(self, user_message):
        """Send a message and get a response"""
        # Format prompt with context
        prompt = self.format_prompt(user_message)
        
        # Make API request
        response = requests.post(API_URL, json={
            "prompt": prompt,
            "max_tokens": 200,
            "temperature": 0.7,
            "top_p": 0.95
        })
        
        if response.status_code == 200:
            data = response.json()
            assistant_message = data['generated_texts'][0]
            
            # Extract just the assistant's response
            if "Assistant:" in assistant_message:
                assistant_message = assistant_message.split("Assistant:")[-1].strip()
            
            # Update conversation history
            self.conversation_history.append({
                'role': 'user',
                'content': user_message
            })
            self.conversation_history.append({
                'role': 'assistant',
                'content': assistant_message
            })
            
            # Keep only last 10 messages
            if len(self.conversation_history) > 20:
                self.conversation_history = self.conversation_history[-20:]
            
            return assistant_message
        else:
            return f"Error: {response.status_code}"

# Usage
bot = ChatBot()

print("ChatBot: Hello! How can I help you today?")
while True:
    user_input = input("You: ")
    if user_input.lower() in ['quit', 'exit', 'bye']:
        print("ChatBot: Goodbye!")
        break
    
    response = bot.chat(user_input)
    print(f"ChatBot: {response}")
```

---

### **Example 2: JavaScript/Node.js Chat Agent**

```javascript
const axios = require('axios');

const API_URL = 'https://language-ai-api-atnpjnu3rq-nw.a.run.app/generate';

class ChatAgent {
  constructor(systemPrompt = 'You are a helpful AI assistant.') {
    this.systemPrompt = systemPrompt;
    this.conversationHistory = [];
  }

  formatPrompt(userMessage) {
    let prompt = `${this.systemPrompt}\n\n`;
    
    // Add conversation history
    this.conversationHistory.forEach(msg => {
      if (msg.role === 'user') {
        prompt += `User: ${msg.content}\n`;
      } else if (msg.role === 'assistant') {
        prompt += `Assistant: ${msg.content}\n`;
      }
    });
    
    // Add new user message
    prompt += `User: ${userMessage}\n`;
    prompt += 'Assistant:';
    
    return prompt;
  }

  async chat(userMessage) {
    try {
      // Format prompt with context
      const prompt = this.formatPrompt(userMessage);
      
      // Make API request
      const response = await axios.post(API_URL, {
        prompt: prompt,
        max_tokens: 200,
        temperature: 0.7,
        top_p: 0.95
      });
      
      let assistantMessage = response.data.generated_texts[0];
      
      // Extract just the assistant's response
      if (assistantMessage.includes('Assistant:')) {
        assistantMessage = assistantMessage.split('Assistant:').pop().trim();
      }
      
      // Update conversation history
      this.conversationHistory.push({
        role: 'user',
        content: userMessage
      });
      this.conversationHistory.push({
        role: 'assistant',
        content: assistantMessage
      });
      
      // Keep only last 20 messages
      if (this.conversationHistory.length > 20) {
        this.conversationHistory = this.conversationHistory.slice(-20);
      }
      
      return assistantMessage;
    } catch (error) {
      console.error('Error:', error.message);
      return 'Sorry, I encountered an error. Please try again.';
    }
  }

  resetConversation() {
    this.conversationHistory = [];
  }
}

// Usage
const agent = new ChatAgent('You are a friendly AI assistant.');

(async () => {
  console.log('ChatBot: Hello! How can I help you today?');
  
  const response1 = await agent.chat('What is machine learning?');
  console.log('ChatBot:', response1);
  
  const response2 = await agent.chat('Can you give me an example?');
  console.log('ChatBot:', response2);
})();
```

---

### **Example 3: React Chat Component**

```jsx
import React, { useState } from 'react';
import axios from 'axios';

const API_URL = 'https://language-ai-api-atnpjnu3rq-nw.a.run.app/generate';

function ChatInterface() {
  const [messages, setMessages] = useState([
    { role: 'assistant', content: 'Hello! How can I help you today?' }
  ]);
  const [input, setInput] = useState('');
  const [loading, setLoading] = useState(false);

  const formatPrompt = (messages, newMessage) => {
    let prompt = 'You are a helpful AI assistant.\n\n';
    
    messages.forEach(msg => {
      if (msg.role === 'user') {
        prompt += `User: ${msg.content}\n`;
      } else if (msg.role === 'assistant') {
        prompt += `Assistant: ${msg.content}\n`;
      }
    });
    
    prompt += `User: ${newMessage}\n`;
    prompt += 'Assistant:';
    
    return prompt;
  };

  const sendMessage = async () => {
    if (!input.trim() || loading) return;

    const userMessage = input.trim();
    setInput('');
    
    // Add user message to chat
    const newMessages = [...messages, { role: 'user', content: userMessage }];
    setMessages(newMessages);
    setLoading(true);

    try {
      // Format prompt with context
      const prompt = formatPrompt(messages, userMessage);
      
      // Call API
      const response = await axios.post(API_URL, {
        prompt: prompt,
        max_tokens: 200,
        temperature: 0.7
      });

      let assistantMessage = response.data.generated_texts[0];
      
      // Extract assistant response
      if (assistantMessage.includes('Assistant:')) {
        assistantMessage = assistantMessage.split('Assistant:').pop().trim();
      }

      // Add assistant message
      setMessages([...newMessages, {
        role: 'assistant',
        content: assistantMessage
      }]);
    } catch (error) {
      console.error('Error:', error);
      setMessages([...newMessages, {
        role: 'assistant',
        content: 'Sorry, I encountered an error. Please try again.'
      }]);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="chat-container">
      <div className="messages">
        {messages.map((msg, idx) => (
          <div key={idx} className={`message ${msg.role}`}>
            <strong>{msg.role === 'user' ? 'You' : 'AI'}:</strong>
            <p>{msg.content}</p>
          </div>
        ))}
        {loading && <div className="loading">AI is typing...</div>}
      </div>
      
      <div className="input-area">
        <input
          type="text"
          value={input}
          onChange={(e) => setInput(e.target.value)}
          onKeyPress={(e) => e.key === 'Enter' && sendMessage()}
          placeholder="Type your message..."
          disabled={loading}
        />
        <button onClick={sendMessage} disabled={loading}>
          Send
        </button>
      </div>
    </div>
  );
}

export default ChatInterface;
```

---

### **Example 4: Flask Backend for Chat App**

```python
from flask import Flask, request, jsonify
from flask_cors import CORS
import requests

app = Flask(__name__)
CORS(app)

API_URL = "https://language-ai-api-atnpjnu3rq-nw.a.run.app/generate"

# Store conversations (use Redis/database in production)
conversations = {}

def format_prompt(messages):
    """Format conversation into prompt"""
    prompt = "You are a helpful AI assistant.\n\n"
    
    for msg in messages:
        if msg['role'] == 'user':
            prompt += f"User: {msg['content']}\n"
        elif msg['role'] == 'assistant':
            prompt += f"Assistant: {msg['content']}\n"
    
    prompt += "Assistant:"
    return prompt

@app.route('/api/chat', methods=['POST'])
def chat():
    data = request.json
    user_message = data.get('message')
    session_id = data.get('session_id', 'default')
    
    if not user_message:
        return jsonify({'error': 'Message is required'}), 400
    
    # Get or create conversation history
    if session_id not in conversations:
        conversations[session_id] = []
    
    # Add user message
    conversations[session_id].append({
        'role': 'user',
        'content': user_message
    })
    
    # Format prompt
    prompt = format_prompt(conversations[session_id])
    
    try:
        # Call your AI API
        response = requests.post(API_URL, json={
            'prompt': prompt,
            'max_tokens': 200,
            'temperature': 0.7
        }, timeout=30)
        
        if response.status_code == 200:
            data = response.json()
            assistant_message = data['generated_texts'][0]
            
            # Extract assistant response
            if 'Assistant:' in assistant_message:
                assistant_message = assistant_message.split('Assistant:')[-1].strip()
            
            # Add to conversation
            conversations[session_id].append({
                'role': 'assistant',
                'content': assistant_message
            })
            
            # Keep last 20 messages
            if len(conversations[session_id]) > 20:
                conversations[session_id] = conversations[session_id][-20:]
            
            return jsonify({
                'response': assistant_message,
                'session_id': session_id
            })
        else:
            return jsonify({'error': 'API error'}), 500
            
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/chat/reset', methods=['POST'])
def reset_chat():
    """Reset conversation"""
    data = request.json
    session_id = data.get('session_id', 'default')
    
    if session_id in conversations:
        del conversations[session_id]
    
    return jsonify({'status': 'reset'})

if __name__ == '__main__':
    app.run(debug=True, port=5000)
```

---

## 🎨 Best Practices

### **1. System Prompts**

Define the assistant's personality and behavior:

```python
system_prompts = {
    'helpful': 'You are a helpful AI assistant. Be friendly and informative.',
    'professional': 'You are a professional AI assistant. Be concise and factual.',
    'creative': 'You are a creative AI assistant. Be imaginative and engaging.',
    'technical': 'You are a technical AI assistant. Provide detailed explanations.'
}
```

### **2. Temperature Settings**

Adjust based on use case:

```javascript
const temperatures = {
  factual: 0.3,      // Focused, consistent answers
  balanced: 0.7,     // Good for general chat
  creative: 1.0,     // More diverse responses
  brainstorm: 1.2    // Highly creative
};
```

### **3. Error Handling**

Always handle errors gracefully:

```javascript
async function callAPI(prompt) {
  try {
    const response = await fetch(API_URL, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ prompt, max_tokens: 200 })
    });
    
    if (response.status === 429) {
      // Rate limited
      return { error: 'Rate limit exceeded. Please wait a moment.' };
    }
    
    if (response.status === 503) {
      // Model loading
      return { error: 'AI is waking up. Please try again in 30 seconds.' };
    }
    
    return await response.json();
  } catch (error) {
    return { error: 'Connection error. Please check your internet.' };
  }
}
```

### **4. User Experience**

Provide feedback during generation:

```jsx
// Show typing indicator
<div className="typing-indicator">
  <span></span><span></span><span></span>
  AI is thinking...
</div>

// Show estimated time
const estimatedTime = Math.ceil(maxTokens / 20); // ~20 tokens/sec
<div>Response will be ready in ~{estimatedTime} seconds</div>
```

### **5. Context Management**

```javascript
// Summarize old messages when context gets too long
const summarizeContext = async (oldMessages) => {
  const summary = await callAPI({
    prompt: `Summarize this conversation in 2-3 sentences:\n${oldMessages}`,
    max_tokens: 100
  });
  
  return summary;
};
```

---

## 🔥 Advanced Patterns

### **Pattern 1: Multi-Turn Conversations**

```python
class ConversationManager:
    def __init__(self, api_url):
        self.api_url = api_url
        self.conversations = {}
    
    def get_conversation(self, user_id):
        if user_id not in self.conversations:
            self.conversations[user_id] = {
                'messages': [],
                'created_at': datetime.now(),
                'metadata': {}
            }
        return self.conversations[user_id]
    
    def add_message(self, user_id, role, content):
        conv = self.get_conversation(user_id)
        conv['messages'].append({
            'role': role,
            'content': content,
            'timestamp': datetime.now()
        })
    
    def generate_response(self, user_id, user_message):
        conv = self.get_conversation(user_id)
        self.add_message(user_id, 'user', user_message)
        
        # Format and send to API
        prompt = self.format_conversation(conv['messages'])
        response = self.call_api(prompt)
        
        self.add_message(user_id, 'assistant', response)
        return response
```

### **Pattern 2: Intent Detection**

```javascript
const detectIntent = (userMessage) => {
  const intents = {
    greeting: /^(hi|hello|hey)/i,
    farewell: /^(bye|goodbye|see you)/i,
    question: /\?$/,
    help: /(help|assist|support)/i
  };
  
  for (const [intent, pattern] of Object.entries(intents)) {
    if (pattern.test(userMessage)) {
      return intent;
    }
  }
  
  return 'general';
};

// Adjust system prompt based on intent
const getSystemPrompt = (intent) => {
  const prompts = {
    greeting: 'You are a friendly AI. Greet the user warmly.',
    help: 'You are a helpful support assistant.',
    general: 'You are a knowledgeable AI assistant.'
  };
  
  return prompts[intent] || prompts.general;
};
```

### **Pattern 3: Streaming Responses (Simulated)**

```javascript
// Since API doesn't support streaming, simulate it
const simulateStreaming = (fullResponse, onChunk, delay = 50) => {
  const words = fullResponse.split(' ');
  let buffer = '';
  
  words.forEach((word, index) => {
    setTimeout(() => {
      buffer += word + ' ';
      onChunk(buffer.trim());
      
      if (index === words.length - 1) {
        onChunk(buffer.trim(), true); // Final chunk
      }
    }, delay * index);
  });
};

// Usage
const response = await callAPI(prompt);
simulateStreaming(response.generated_texts[0], (chunk, isDone) => {
  updateUI(chunk);
  if (isDone) {
    enableInput();
  }
});
```

### **Pattern 4: Conversation Branching**

```python
class ConversationTree:
    def __init__(self):
        self.nodes = {}
        self.current_node = None
    
    def add_branch(self, parent_id, message, response):
        node_id = str(uuid.uuid4())
        self.nodes[node_id] = {
            'parent': parent_id,
            'message': message,
            'response': response,
            'children': []
        }
        
        if parent_id and parent_id in self.nodes:
            self.nodes[parent_id]['children'].append(node_id)
        
        return node_id
    
    def get_path_to_root(self, node_id):
        """Get full conversation path from root to current node"""
        path = []
        current = node_id
        
        while current:
            if current in self.nodes:
                path.insert(0, self.nodes[current])
                current = self.nodes[current]['parent']
            else:
                break
        
        return path
```

---

## 🐛 Troubleshooting

### **Problem 1: Rate Limiting**

**Symptom**: 429 status code

**Solution**:
```javascript
const retryWithBackoff = async (fn, maxRetries = 3) => {
  for (let i = 0; i < maxRetries; i++) {
    try {
      return await fn();
    } catch (error) {
      if (error.status === 429 && i < maxRetries - 1) {
        const delay = Math.pow(2, i) * 1000; // Exponential backoff
        await new Promise(resolve => setTimeout(resolve, delay));
        continue;
      }
      throw error;
    }
  }
};
```

### **Problem 2: Context Too Long**

**Symptom**: Slow responses or errors

**Solution**:
```python
def trim_conversation(messages, max_tokens=4000):
    """Keep conversation within token limit"""
    # Estimate tokens (rough: 1 token ≈ 4 characters)
    total_chars = sum(len(m['content']) for m in messages)
    estimated_tokens = total_chars / 4
    
    if estimated_tokens > max_tokens:
        # Keep system message + recent messages
        chars_to_keep = max_tokens * 4
        
        recent_messages = []
        char_count = 0
        
        for msg in reversed(messages):
            char_count += len(msg['content'])
            if char_count > chars_to_keep:
                break
            recent_messages.insert(0, msg)
        
        return recent_messages
    
    return messages
```

### **Problem 3: Inconsistent Responses**

**Symptom**: AI gives different answers to same question

**Solution**: Lower temperature for consistency
```javascript
const settings = {
  temperature: 0.3,  // More consistent
  top_p: 0.9,        // More focused
  top_k: 40          // Limit choices
};
```

### **Problem 4: Response Cutoff**

**Symptom**: Responses end abruptly

**Solution**: Increase `max_tokens`
```python
response = call_api({
    'prompt': prompt,
    'max_tokens': 300,  # Increase from 100
    'temperature': 0.7
})
```

---

## 📊 Performance Tips

### **1. Cache Common Responses**

```javascript
const responseCache = new Map();

const getCachedResponse = (prompt) => {
  const hash = simpleHash(prompt);
  return responseCache.get(hash);
};

const cacheResponse = (prompt, response) => {
  const hash = simpleHash(prompt);
  responseCache.set(hash, response);
  
  // Limit cache size
  if (responseCache.size > 100) {
    const firstKey = responseCache.keys().next().value;
    responseCache.delete(firstKey);
  }
};
```

### **2. Parallel Requests for Multiple Users**

```python
import asyncio
import aiohttp

async def handle_multiple_users(user_requests):
    async with aiohttp.ClientSession() as session:
        tasks = [
            generate_response(session, req['user_id'], req['message'])
            for req in user_requests
        ]
        responses = await asyncio.gather(*tasks)
        return responses
```

### **3. Debounce User Input**

```javascript
const debounce = (func, delay) => {
  let timeoutId;
  return (...args) => {
    clearTimeout(timeoutId);
    timeoutId = setTimeout(() => func(...args), delay);
  };
};

const debouncedSend = debounce(sendMessage, 300);
```

---

## 🎯 Complete Example: Full-Featured Chat App

See `examples/chat-app-complete/` folder for:
- ✅ React frontend with beautiful UI
- ✅ Node.js backend with session management
- ✅ Database integration (MongoDB/PostgreSQL)
- ✅ User authentication
- ✅ Conversation history
- ✅ Export conversations
- ✅ Multi-user support
- ✅ Real-time features

---

## 📚 Additional Resources

- **API Base Documentation**: `API_DOCUMENTATION.md`
- **Usage Guide**: `USAGE_GUIDE.md`
- **HuggingFace Setup**: `HUGGINGFACE_SETUP.md`
- **Model Comparison**: `MISTRAL_VS_GPT4O_COMPARISON.md`

---

## 💡 Pro Tips

1. **Start Simple**: Begin with basic request/response, add features incrementally
2. **Test Prompts**: Different phrasings can dramatically affect quality
3. **Monitor Usage**: Track API calls to avoid rate limits
4. **Handle Errors**: Always have fallback responses
5. **User Feedback**: Let users rate responses to improve prompts
6. **Context is Key**: More context = better responses
7. **Temperature Matters**: Adjust based on use case
8. **Test Edge Cases**: Empty messages, very long prompts, special characters

---

## 🚀 Ready to Build?

You now have everything you need to build amazing ChatGPT-like agents!

**Need help?** Contact: [Your Contact Info]

**API Status**: https://language-ai-api-atnpjnu3rq-nw.a.run.app/health

**Happy Building!** 🎉

