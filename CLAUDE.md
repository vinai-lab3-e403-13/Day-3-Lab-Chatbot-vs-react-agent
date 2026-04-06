# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Lab Context

This is an educational lab (Phase 3 of an Agentic AI course) for building a ReAct Agent from a baseline chatbot. The code is a "Production Prototype" with industry-standard telemetry - not a toy project.

## Commands

```bash
# Install dependencies
pip install -r requirements.txt

# Copy environment file
cp .env.example .env

# Run local provider test
python tests/test_local.py

# Run all tests
pytest
```

## Architecture

### LLM Provider Pattern (`src/core/`)

Three LLM providers implement `LLMProvider` ABC:
- `OpenAIProvider` - GPT-4o, GPT-3.5
- `GeminiProvider` - Gemini 1.5 Flash
- `LocalProvider` - Phi-3-mini via llama-cpp-python (CPU-friendly GGUF format)

Each provider implements `generate()` and `stream()` methods returning `Dict[str, Any]` with `content`, `usage`, `latency_ms`, and `provider`.

### ReAct Agent (`src/agent/agent.py`)

The `ReActAgent` class is the core skeleton to implement. It follows the Thought-Action-Observation loop:

1. Generate Thought + Action from LLM
2. Parse and execute tool call
3. Append Observation back to prompt
4. Repeat until `Final Answer`

Key methods to implement:
- `get_system_prompt()` - Defines available tools and ReAct format
- `run()` - Main loop with max_steps guard
- `_execute_tool()` - Dynamic tool dispatch

### Telemetry (`src/telemetry/`)

- `logger.py` - `IndustryLogger` writes JSON structured logs to `logs/YYYY-MM-DD.log`
- `metrics.py` - `PerformanceTracker` records LLM metrics (tokens, latency, cost)

### Extension Point: Tools (`src/tools/`)

Students add custom tools here. Tools are dicts with `name` and `description` fields, passed to `ReActAgent` constructor.

## Provider Configuration

Set `DEFAULT_PROVIDER=openai|google|local` in `.env`. For local models:
1. Download `Phi-3-mini-4k-instruct-q4.gguf` from HuggingFace
2. Place in `models/` directory
3. Set `LOCAL_MODEL_PATH=./models/Phi-3-mini-4k-instruct-q4.gguf`
