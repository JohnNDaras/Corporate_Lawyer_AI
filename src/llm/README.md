# LLM Integration Layer

This directory contains the **language model client adapters** used by the contract analysis system.

The purpose of this module is to provide a **provider-independent interface** for interacting with large language models (LLMs).

Instead of tightly coupling the system to a specific API (OpenAI, HuggingFace, etc.), this layer introduces a **generic client interface** that allows multiple providers to be used interchangeably.

This design enables:

- flexible LLM provider selection  
- easier experimentation with different models  
- improved reproducibility for research experiments  
- cleaner separation between the contract analysis logic and external APIs  

---

# Architecture Overview

The module follows a **client adapter pattern**.

```
Core System
      │
      ▼
LLMClient Interface
      │
      ├── HuggingFaceClient
      └── OpenRouterClient
```

The core system only interacts with the **LLMClient interface**, while the concrete implementations handle the details of each provider.

---

# File Structure

```
src/llm/
│
├── __init__.py
├── base.py
├── hf_client.py
└── openrouter_client.py
```

---

# `base.py`

Defines the **abstract LLM interface** used by the rest of the system.

## LLMResponse

A minimal container for model responses.

Example:

```python
LLMResponse(
    text="Generated model output"
)
```

---

## LLMClient

Abstract base class that all model adapters must implement.

```python
class LLMClient:
    def complete(self, system: str, user: str, temperature: float):
        ...
```

### Parameters

| Parameter   | Description                    |
|-------------|--------------------------------|
| system      | system instruction prompt      |
| user        | user task prompt               |
| temperature | sampling temperature           |

The method returns an `LLMResponse`.

Because the core pipeline only depends on this interface, **any new LLM provider can be integrated easily**.

---

# `hf_client.py`

Implements an LLM adapter using the **Hugging Face Inference API**.

This client relies on:

```
huggingface_hub.InferenceClient
```

### Supported Capabilities

- chat-style completion  
- text generation fallback  
- provider routing through Hugging Face  

---

## Default Model

```
HuggingFaceTB/SmolLM3-3B
```

---

## Authentication

The client requires the environment variable:

```
HUGGINGFACEHUB_API_TOKEN
```

Example:

```bash
export HUGGINGFACEHUB_API_TOKEN=your_token_here
```

---

## Chat Completion Flow

The preferred execution path uses the chat completion interface:

```python
client.chat_completion(...)
```

Messages are formatted as:

```python
[
  {"role": "system", "content": system_prompt},
  {"role": "user", "content": user_prompt}
]
```

---

## Fallback Generation

Some models only support text generation instead of chat completion.

If the chat API fails, the client falls back to:

```python
client.text_generation(...)
```

A formatted instruction-style prompt is generated:

```
[INST] <<SYS>>
system_prompt
<</SYS>>

user_prompt
[/INST]
```

This ensures compatibility with instruction-tuned models.

---

# `openrouter_client.py`

Provides an adapter for the **OpenRouter API**.

OpenRouter allows access to multiple LLM providers through a unified interface.

### Example Supported Models

```
meta-llama/llama-3-8b-instruct
anthropic/claude
mistralai/mistral
```

---

## API Endpoint

Requests are sent to:

```
https://openrouter.ai/api/v1/chat/completions
```

---

## Authentication

The client requires the environment variable:

```
OPENROUTER_API_KEY
```

Example:

```bash
export OPENROUTER_API_KEY=your_api_key
```

---

## Request Format

Example request payload:

```json
{
  "model": "meta-llama/llama-3-8b-instruct",
  "temperature": 0.2,
  "messages": [
    {"role": "system", "content": "..."},
    {"role": "user", "content": "..."}
  ]
}
```

---

# Why Use an LLM Abstraction Layer?

Separating LLM access into a dedicated module provides several advantages.

## Provider Independence

The contract analysis pipeline does not depend on a specific API.

## Easy Model Swapping

Different models can be tested by simply replacing the client.

## Reproducible Experiments

Researchers can control which model is used during evaluation.

## Simplified Error Handling

API-specific logic is isolated from the main system.

---

# Adding a New LLM Provider

To integrate another model provider:

1. Create a new client class.

```python
class MyProviderClient(LLMClient):
    ...
```

2. Implement the `complete()` method.

3. Return an `LLMResponse`.

Example:

```python
return LLMResponse(text=generated_text)
```

The rest of the system will work automatically.

---

# Usage Example

Example usage from the contract analysis pipeline:

```python
from src.llm.openrouter_client import OpenRouterClient

llm = OpenRouterClient()

response = llm.complete(
    system="You are a legal analysis assistant",
    user="Analyze this clause...",
    temperature=0.2
)
```

---

# Role in the System

The LLM module enables the system to perform advanced reasoning tasks including:

- clause summarization  
- risk explanation  
- deviation detection  
- uncertainty estimation  

These capabilities complement rule-based and retrieval-based components, forming the **hybrid AI architecture described in the research paper**.
