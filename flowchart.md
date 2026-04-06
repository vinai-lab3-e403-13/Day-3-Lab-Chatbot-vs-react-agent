# Crypto Investment Agent - Flowchart

## ReAct Loop Flowchart

```mermaid
flowchart TD
    Start([User Input]) --> BuildPrompt[Build System Prompt<br/>with Tools + ReAct Format]

    BuildPrompt --> LoopEntry{Step < Max Steps?}

    LoopEntry -->|Yes| Generate[LLM.generate<br/>current_prompt<br/>system_prompt]
    LoopEntry -->|No| MaxSteps[Return:<br/>Max Steps Exceeded]

    Generate --> Parse[Parse Response]
    Parse --> Extract{Extract Components}

    Extract -->|Thought| StoreThought[Store Thought<br/>in Step Record]
    Extract -->|Action Found| Execute[Execute Tool<br/>tool_name(args)]
    Extract -->|Final Answer| Return[Return Final Answer]

    StoreThought --> HasAction{Has Action?}

    HasAction -->|Yes| Execute
    HasAction -->|No| NoAction[Append Thought Only<br/>Continue Loop]

    Execute --> Observe[Build Observation<br/>from Tool Result]
    Observe --> Append[Append to Prompt:<br/>Thought + Action + Observation]

    Append --> LoopEntry

    Return --> Output[Return Result + Trace<br/>answer, tokens, latency_ms]
    MaxSteps --> Output
    NoAction --> LoopEntry

    Output --> LogEnd[Log CRYPTO_AGENT_END<br/>to telemetry]
    LogEnd --> Done([Done])
```

## Tool Execution Flow

```mermaid
flowchart LR
    A[Action: get_crypto_price] --> B{coin in list?}
    B -->|Yes| C[Fetch from CoinGecko]
    B -->|No| D[Return Error:<br/>not found]
    C --> E[Return JSON:<br/>price, 24h_change]
    D --> E
```

## Trace Structure

```mermaid
flowchart TD
    subgraph "Full Trace Object"
        T1[input: str]
        T2[steps: Array]
        T3[model: str]
        T4[total_steps: int]
        T5[latency_ms: int]
        T6[final_answer: str]
    end

    subgraph "Step Object"
        S1[step: int]
        S2[llm_output: str]
        S3[thought: str]
        S4[action: str]
        S5[action_args: dict]
        S6[observation: str]
        S7[tokens: dict]
    end

    T2 --> S1
    T2 --> S2
    T2 --> S3
    T2 --> S4
```
