"""Streamlit GUI for Crypto Investment Agent."""

import streamlit as st
import time
import json
import os
import pandas as pd
from datetime import datetime

# Page config
st.set_page_config(
    page_title="Crypto Agent Lab",
    page_icon="",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS
st.markdown("""
<style>
    .stApp { background-color: #0e1117; }
    .chat-message { padding: 1rem; border-radius: 10px; margin-bottom: 1rem; }
    .user-msg { background-color: #1a73e8; color: white; }
    .agent-msg { background-color: #2d2d2d; color: white; }
    .thought-box { background-color: #1e1e1e; padding: 10px; border-radius: 5px; margin: 5px 0; border-left: 3px solid #ffd700; }
    .action-box { background-color: #1e1e1e; padding: 10px; border-radius: 5px; margin: 5px 0; border-left: 3px solid #00ff00; }
    .observation-box { background-color: #1e1e1e; padding: 10px; border-radius: 5px; margin: 5px 0; border-left: 3px solid #00bfff; }
    .final-box { background-color: #1e1e1e; padding: 10px; border-radius: 5px; margin: 5px 0; border-left: 3px solid #ff6b6b; }
    .metric-card { background-color: #2d2d2d; padding: 15px; border-radius: 10px; text-align: center; }
    .stMetric { background-color: #2d2d2d; padding: 10px; border-radius: 5px; }
</style>
""", unsafe_allow_html=True)

# Import agent components
sys_path = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
import sys
sys.path.insert(0, sys_path)

from crypto_agent.agent import CryptoReActAgent
from crypto_agent.tools import get_all_tools
from src.core.openai_provider import OpenAIProvider
from src.core.gemini_provider import GeminiProvider
from src.core.local_provider import LocalProvider
from dotenv import load_dotenv

load_dotenv()


def create_provider(provider_type: str, model_name: str = None):
    """Create LLM provider based on type."""
    if provider_type == "openai":
        return OpenAIProvider(
            model_name=model_name or os.getenv("DEFAULT_MODEL", "gpt-4o"),
            api_key=os.getenv("OPENAI_API_KEY")
        )
    elif provider_type == "google":
        return GeminiProvider(
            model_name=model_name or "gemini-1.5-flash",
            api_key=os.getenv("GEMINI_API_KEY")
        )
    elif provider_type == "local":
        return LocalProvider(
            model_path=os.getenv("LOCAL_MODEL_PATH")
        )


def init_session():
    """Initialize session state."""
    if "messages" not in st.session_state:
        st.session_state.messages = []
    if "agent" not in st.session_state:
        st.session_state.agent = None
    if "stats" not in st.session_state:
        st.session_state.stats = {
            "total_requests": 0,
            "total_tokens": 0,
            "total_latency_ms": 0,
            "tools_used": {},
            "sessions": []
        }


def display_thought_chain(step_data: dict):
    """Display a step's thought chain with visual formatting."""
    with st.container():
        col1, col2 = st.columns([1, 4])

        with col1:
            step_num = step_data.get("step", 0)
            st.markdown(f"### Step {step_num}")
            st.markdown("---")

            if step_data.get("thought"):
                st.markdown("**Thought**")
            if step_data.get("action"):
                st.markdown("**Action**")
            if step_data.get("observation"):
                st.markdown("**Obs**")
            if step_data.get("final_answer"):
                st.markdown("**Final**")

        with col2:
            if step_data.get("thought"):
                st.markdown(f'<div class="thought-box"><b>Thought:</b><br/>{step_data["thought"]}</div>', unsafe_allow_html=True)

            if step_data.get("action"):
                args = json.dumps(step_data.get("action_args", {}))
                st.markdown(f'<div class="action-box"><b>Action:</b> {step_data["action"]}({args})</div>', unsafe_allow_html=True)

            if step_data.get("observation"):
                obs = step_data["observation"]
                try:
                    obs_json = json.loads(obs)
                    obs = json.dumps(obs_json, indent=2)
                except:
                    pass
                st.markdown(f'<div class="observation-box"><b>Observation:</b><br/><pre>{obs}</pre></div>', unsafe_allow_html=True)

            if step_data.get("final_answer"):
                st.markdown(f'<div class="final-box"><b>Final Answer:</b><br/>{step_data["final_answer"]}</div>', unsafe_allow_html=True)


def display_metrics_panel(result: dict, stats: dict):
    """Display metrics in sidebar."""
    st.sidebar.markdown("## Session Metrics")

    # Current request metrics
    col1, col2 = st.sidebar.columns(2)
    with col1:
        st.metric("Tokens", result.get("tokens_used", 0))
    with col2:
        st.metric("Latency", f"{result.get('latency_ms', 0)}ms")

    # Token breakdown
    if result.get("trace", {}).get("steps"):
        step = result["trace"]["steps"][0]
        tokens = step.get("tokens", {})
        st.markdown("### Token Breakdown")
        df_tokens = pd.DataFrame({
            "Type": ["Prompt", "Completion", "Total"],
            "Tokens": [tokens.get("prompt_tokens", 0), tokens.get("completion_tokens", 0), tokens.get("total_tokens", 0)]
        })
        st.bar_chart(df_tokens.set_index("Type"))

    # Cumulative stats
    st.sidebar.markdown("---")
    st.sidebar.markdown("### Cumulative Stats")
    col3, col4 = st.sidebar.columns(2)
    with col3:
        st.metric("Total Requests", stats["total_requests"])
    with col4:
        st.metric("Total Tokens", stats["total_tokens"])

    # Tools usage
    st.sidebar.markdown("### Tools Used")
    if stats["tools_used"]:
        df_tools = pd.DataFrame([
            {"Tool": k, "Count": v} for k, v in stats["tools_used"].items()
        ])
        st.bar_chart(df_tools.set_index("Tool"))
    else:
        st.write("No tools used yet")


def main():
    init_session()

    # Header
    st.title("")
    st.markdown("## Crypto Investment Agent Lab")
    st.markdown("### ReAct Agent with Chain-of-Thought Visualization")

    # Sidebar settings
    st.sidebar.markdown("## Settings")

    provider_type = st.sidebar.selectbox(
        "LLM Provider",
        ["openai", "google", "local"],
        index=0
    )

    if st.sidebar.button("Initialize Agent"):
        with st.spinner("Initializing agent..."):
            try:
                provider = create_provider(provider_type)
                tools = get_all_tools()
                st.session_state.agent = CryptoReActAgent(provider, tools, max_steps=5)
                st.sidebar.success(f"Agent initialized with {len(tools)} tools")
            except Exception as e:
                st.sidebar.error(f"Error: {str(e)}")

    st.sidebar.markdown("---")

    # Display stats
    display_metrics_panel(
        {"tokens_used": 0, "latency_ms": 0},
        st.session_state.stats
    )

    st.sidebar.markdown("---")

    # Available tools info
    st.sidebar.markdown("### Available Tools")
    tools = get_all_tools()
    for tool in tools:
        st.sidebar.markdown(f"- **{tool['name']}**")

    st.sidebar.markdown("---")

    # Clear chat button
    if st.sidebar.button("Clear Chat"):
        st.session_state.messages = []
        st.rerun()

    # Main chat area
    col_chat, col_thoughts = st.columns([1, 1])

    with col_chat:
        st.markdown("### Chat")

        # Display messages
        for msg in st.session_state.messages:
            if msg["role"] == "user":
                st.markdown(f'<div class="chat-message user-msg"><b>You:</b> {msg["content"]}</div>', unsafe_allow_html=True)
            else:
                st.markdown(f'<div class="chat-message agent-msg"><b>Agent:</b> {msg["content"]}</div>', unsafe_allow_html=True)

        # Chat input
        if prompt := st.chat_input("Ask about crypto prices, portfolios, or investments..."):
            # Add user message
            st.session_state.messages.append({"role": "user", "content": prompt})

            if st.session_state.agent is None:
                st.error("Please initialize the agent first!")
            else:
                with st.chat_message("user"):
                    st.markdown(prompt)

                with st.chat_message("assistant"):
                    with st.spinner("Thinking..."):
                        result = st.session_state.agent.run(prompt)

                        # Update stats
                        st.session_state.stats["total_requests"] += 1
                        st.session_state.stats["total_tokens"] += result.get("tokens_used", 0)
                        st.session_state.stats["total_latency_ms"] += result.get("latency_ms", 0)

                        # Track tools used
                        for step in result.get("trace", {}).get("steps", []):
                            if step.get("action"):
                                tool_name = step["action"]
                                st.session_state.stats["tools_used"][tool_name] = \
                                    st.session_state.stats["tools_used"].get(tool_name, 0) + 1

                        # Store session
                        st.session_state.stats["sessions"].append({
                            "timestamp": datetime.now().isoformat(),
                            "input": prompt,
                            "result": result
                        })

                        # Display answer
                        st.markdown(result["answer"])

                        # Display metrics
                        st.markdown("---")
                        col1, col2, col3 = st.columns(3)
                        with col1:
                            st.metric("Tokens Used", result.get("tokens_used", 0))
                        with col2:
                            st.metric("Latency", f"{result.get('latency_ms', 0)}ms")
                        with col3:
                            steps = len(result.get("trace", {}).get("steps", []))
                            st.metric("Steps", steps)

                # Add to messages
                st.session_state.messages.append({
                    "role": "assistant",
                    "content": result["answer"]
                })

    # Chain of thoughts visualization
    with col_thoughts:
        st.markdown("### Chain of Thoughts")

        if st.session_state.messages:
            # Get last result
            if st.session_state.stats["sessions"]:
                last_session = st.session_state.stats["sessions"][-1]
                trace = last_session["result"].get("trace", {})

                for step in trace.get("steps", []):
                    with st.expander(f"Step {step.get('step', 0)}", expanded=True):
                        display_thought_chain(step)
        else:
            st.info("Send a message to see the chain of thoughts visualization")

    # Stats dashboard at bottom
    if st.session_state.stats["sessions"]:
        st.markdown("---")
        st.markdown("## Session Statistics")

        # Create stats dataframe
        session_data = []
        for i, sess in enumerate(st.session_state.stats["sessions"]):
            session_data.append({
                "Session": i + 1,
                "Input": sess["input"][:50] + "..." if len(sess["input"]) > 50 else sess["input"],
                "Tokens": sess["result"].get("tokens_used", 0),
                "Latency (ms)": sess["result"].get("latency_ms", 0),
                "Steps": len(sess["result"].get("trace", {}).get("steps", []))
            })

        df = pd.DataFrame(session_data)
        st.dataframe(df, use_container_width=True)

        # Visualization
        if len(session_data) > 1:
            st.markdown("### Token Usage Over Time")
            chart_data = pd.DataFrame({
                "Session": [s["Session"] for s in session_data],
                "Tokens": [s["Tokens"] for s in session_data],
                "Latency": [s["Latency (ms)"] for s in session_data]
            })
            st.line_chart(chart_data.set_index("Session"))


if __name__ == "__main__":
    main()
