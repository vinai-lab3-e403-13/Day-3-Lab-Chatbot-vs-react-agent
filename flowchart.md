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

    Return --> Output[Return Result + Trace<br/>answer, tokens, latency]
    MaxSteps --> Output
    NoAction --> LoopEntry

    Output --> LogEnd[Log CRYPTO_AGENT_END<br/>to telemetry]
    LogEnd --> Done([Done])
```

## Tool Execution Flow

```mermaid
flowchart LR
    subgraph Tools[Available Tools]
        T1[get_crypto_price<br/>crypto_id -> price, change_24h]
        T2[get_portfolio<br/>user_id -> holdings, total_value]
        T3[calculate_investment<br/>amount, crypto, gain% -> profit]
    end

    Action -->|tool_name| Match{Match Tool?}

    Match -->|Yes| Exec[Execute Tool Function]
    Match -->|No| Error[Return: Tool not found]

    Exec --> Result[Return JSON Result]
    Error --> Result
```

## Chain of Thoughts Logging

```mermaid
flowchart LR
    subgraph Events[Event Types]
        E1[USER_INPUT]
        E2[LLM_OUTPUT]
        E3[CHAIN_OF_THOUGHT]
        E4[ACTION]
        E5[FINAL_ANSWER]
    end

    subgraph LogFile["logs/chain_of_thoughts_YYYY-MM-DD.json"]
        L1["{timestamp, session_id,<br/>event_type: USER_INPUT,<br/>user_input}"]
        L2["{timestamp, session_id,<br/>event_type: LLM_OUTPUT,<br/>step, llm_raw_output,<br/>tokens}"]
        L3["{timestamp, session_id,<br/>event_type: CHAIN_OF_THOUGHT,<br/>step, thought}"]
        L4["{timestamp, session_id,<br/>event_type: ACTION,<br/>step, action, action_args,<br/>observation, tools_used}"]
        L5["{timestamp, session_id,<br/>event_type: FINAL_ANSWER,<br/>step, final_answer}"]
    end

    E1 --> L1
    E2 --> L2
    E3 --> L3
    E4 --> L4
    E5 --> L5
```

## Trace Structure

```mermaid
flowchart TD
    subgraph FullTrace["Full Trace Object"]
        T1[input: str]
        T2[steps: Array]
        T3[model: str]
        T4[total_steps: int]
        T5[latency_ms: int]
        T6[final_answer: str]
        T7[session_id: str]
        T8[tools_used: Array]
    end

    subgraph StepObject["Step Object"]
        S1[step: int]
        S2[llm_output: str]
        S3[thought: str]
        S4[action: str]
        S5[action_args: dict]
        S6[observation: str]
        S7[tokens: dict]
    end

    T2 --> StepObject
    T8 -->|tools| TB1["get_crypto_price"]
    T8 -->|tools| TB2["get_portfolio"]
    T8 -->|tools| TB3["calculate_investment"]
```

## Tools Specification

```mermaid
flowchart TD
    subgraph get_crypto_price["Tool: get_crypto_price"]
        P1["Input: crypto_id<br/>bitcoin | ethereum | solana | cardano"]
        P2["Output: {crypto, price_usd, change_24h}"]
    end

    subgraph get_portfolio["Tool: get_portfolio"]
        O1["Input: user_id (default: 'default')"]
        O2["Output: {total_value_usd, holdings:<br/>[{crypto, amount, value_usd}]}"]
    end

    subgraph calculate_investment["Tool: calculate_investment"]
        C1["Input: amount_usd, crypto_id,<br/>expected_gain_pct (optional)"]
        C2["Output: {investment_usd, crypto_id,<br/>amount_crypto, current_price,<br/>expected_gain_pct, final_value_usd,<br/>profit_usd}"]
    end
```
