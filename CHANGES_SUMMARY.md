# Changes Summary - Karpathy Setup & Nexus Integration

## Timeline of Modifications After Applying `all_changes.patch`

---

## ✅ Phase 1: Initial Setup (Successful)
### Created Virtual Environment
```bash
python3.13 -m venv venv
uv sync  # Installed all 191 packages
```

### Applied Patch
```bash
git apply all_changes.patch
```
**Changes from patch:**
- Updated `pyproject.toml`: `requires-python = "==3.13"`
- Updated `README.md`: Changed to Nexus configuration
- Updated `.env.example`: Changed from OpenRouter to Nexus
- Modified `agent.py`: Added Nexus URL and API key configuration
- Created `CLAUDE.md`: Comprehensive documentation

### Copied Dataset
```bash
cp /path/to/ds_agent_test_set.csv sandbox/
# Result: 12MB file, 57,681 rows
```

---

## 🔧 Phase 2: Nexus Integration Fixes (Critical)

### Issue #1: Duplicate `/v1` in URL
**Problem:** URL was `https://nexus-master.lmndstaging.com/v1/v1/messages` (404 error)

**Fix in `karpathy/agent.py`:**
```python
# BEFORE (from patch):
model=LiteLlm(model=MODEL, api_base=f"{NEXUS_URL}/v1", api_key=NEXUS_API_KEY)

# AFTER:
model=LiteLlm(model=MODEL, api_base=NEXUS_URL, api_key=NEXUS_API_KEY)
```

### Issue #2: Model Name Routing
**Problem:** LiteLLM was stripping provider prefix causing "Invalid model name" errors

**Solution learned from Giora repo** (`apps/giora/src/nexus-chat/main.py`):
- Giora uses `litellm_proxy/` prefix for model names when using LiteLLM proxy

**Fix in `karpathy/agent.py`:**
```python
# BEFORE:
model=LiteLlm(model=MODEL, api_base=NEXUS_URL, api_key=NEXUS_API_KEY)

# AFTER (KEY CHANGE):
model=LiteLlm(
    model=f"litellm_proxy/{MODEL}",  # ← Added this prefix
    api_base=NEXUS_URL,
    api_key=NEXUS_API_KEY
)
```

**Why this works:**
- The `litellm_proxy/` prefix tells LiteLLM to pass the model name through to Nexus unchanged
- Without it, LiteLLM strips prefixes like `anthropic/` or `openai/` causing routing issues

### Issue #3: Model Selection
**Problem:** Bedrock Claude models don't support `tools` parameter needed for agents

**Models Tested:**
1. ❌ `anthropic/claude-opus-4-5-20251101` - Model name stripping issue
2. ❌ `bedrock/claude-opus-4-6` - Doesn't support `tools` parameter
3. ❌ `anthropic/claude-opus-4-6` - Model name stripping issue  
4. ✅ `openai/gpt-4.1` - **WORKS!**

**Final Configuration in `karpathy/.env`:**
```bash
AGENT_MODEL=openai/gpt-4.1
```

---

## 📊 Phase 3: Added Verbose Logging

### Enhanced `karpathy/tools.py`
Added comprehensive logging to track:
- Task delegation to experts
- Expert system prompts
- Full user prompts sent to Claude Code
- Tool and skill usage
- Message flow and completion

**Key additions:**
```python
import logging
from datetime import datetime
from pathlib import Path

# Dual logging: console + file
log_dir = Path("sandbox/logs")
log_file = log_dir / f"karpathy_{datetime.now().strftime('%Y%m%d_%H%M%S')}.log"

# Detailed logging in delegate_task():
logger.info("🚀 DELEGATING TASK TO EXPERT")
logger.info("👤 EXPERT SYSTEM PROMPT:")
logger.info("📝 FULL USER PROMPT SENT TO EXPERT:")
logger.info("⚙️  CONFIGURATION:")
# ... etc
```

### Created Monitoring Tools
1. **`monitor_logs.sh`** - Real-time log monitoring
2. **`view_agent_logs.sh`** - View detailed command logs
3. **`MONITORING.md`** - Complete monitoring guide

---

## 📁 New Files Created

```
/Users/or.tuchman/src/karpathy/
├── venv/                          # Python 3.13 virtual environment
├── sandbox/
│   ├── ds_agent_test_set.csv     # 12MB dataset (57,681 rows)
│   ├── .claude/skills/           # 142 scientific skills
│   ├── .venv/                    # Sandbox Python environment with ML packages
│   ├── .env                      # Copied from karpathy/.env
│   └── logs/                     # NEW: Detailed agent logs
│       └── karpathy_*.log
├── karpathy/.env                  # Created from .env.example
├── CLAUDE.md                      # From patch
├── monitor_logs.sh               # NEW: Real-time monitoring
├── view_agent_logs.sh            # NEW: Log viewer
├── MONITORING.md                 # NEW: Monitoring guide
└── CHANGES_SUMMARY.md            # This file
```

---

## 🎯 Final Working Configuration

### `karpathy/agent.py` (Complete)
```python
import os

from dotenv import load_dotenv
from google.adk.agents import LlmAgent
from google.adk.models.lite_llm import LiteLlm

from .tools import delegate_task
from .utils import load_instructions

load_dotenv()

# Configuration
NEXUS_URL = os.getenv("NEXUS_URL", "https://nexus-master.lmndstaging.com")
NEXUS_API_KEY = os.getenv("LITELLM_PROXY_API_KEY", "sk-12345")
MODEL = os.getenv("AGENT_MODEL", "openai/gpt-4.1")

# Main agent - use litellm_proxy prefix for proper Nexus routing
main_agent = LlmAgent(
    name="MainAgent",
    model=LiteLlm(
        model=f"litellm_proxy/{MODEL}",  # ← KEY FIX from Giora
        api_base=NEXUS_URL,               # ← No /v1 suffix
        api_key=NEXUS_API_KEY
    ),
    description="The main agent that makes sure the user's machine learning requests are successfully fulfilled",
    instruction=load_instructions("main_agent"),
    tools=[delegate_task],
    output_key="final_output",
)
```

### `karpathy/.env` (Complete)
```bash
NEXUS_URL=https://nexus-master.lmndstaging.com
LITELLM_PROXY_API_KEY='sk-12345'
AGENT_MODEL=openai/gpt-4.1
```

---

## 🔑 Key Learnings from Giora Repository

### 1. LiteLLM Proxy Prefix Pattern
**File:** `apps/giora/src/nexus-chat/main.py` (line 985)
```python
f"litellm_proxy/{actual_model}"
```
This pattern ensures proper model name routing through Nexus.

### 2. Direct OpenAI Client Pattern (Alternative)
**File:** `apps/giora/src/mint-talk-to-docs/chat_agent/llm_client.py` (line 114)
```python
llm = OpenAI(
    base_url=os.environ.get("NEXUS_URL"),
    api_key=os.environ.get("NEXUS_API_KEY", "123")
)
```
Giora also shows you can use OpenAI client directly with Nexus.

### 3. Model Configuration Patterns
**File:** `apps/giora/src/nexus-chat/main.py` (lines 176-226)
- Giora explicitly ignores Bedrock models for certain features
- Tracks which models support `tools`, `thinking`, etc.

---

## ✅ What Works Now

1. ✅ Server runs on http://localhost:8000
2. ✅ Nexus API integration with proper routing
3. ✅ Model: `openai/gpt-4.1` via `litellm_proxy/openai/gpt-4.1`
4. ✅ Dataset ready: `sandbox/ds_agent_test_set.csv`
5. ✅ 142 scientific skills available
6. ✅ Verbose logging with emoji indicators
7. ✅ Real-time monitoring tools
8. ✅ Detailed command logs in `sandbox/logs/`

---

## 🚫 What Doesn't Work (Yet)

### Claude Models via Anthropic Direct
- ❌ `anthropic/claude-opus-4-6` - LiteLLM strips prefix
- **Workaround:** Would need Nexus proxy configuration changes

### Bedrock Models
- ❌ `bedrock/claude-opus-4-6` - No `tools` parameter support
- **Impact:** Can't use for agent delegation (needs function calling)

---

## 🎓 Technical Insights

### Why `litellm_proxy/` Prefix?
When you specify `litellm_proxy/openai/gpt-4.1`:
1. LiteLLM recognizes the `litellm_proxy/` prefix
2. It strips the prefix and sends `openai/gpt-4.1` to Nexus unchanged
3. Nexus routes to the correct provider

Without the prefix:
1. LiteLLM tries to parse `openai/gpt-4.1`
2. It strips `openai/` thinking it's a provider indicator
3. Sends just `gpt-4.1` to Nexus
4. Nexus returns 400: "Invalid model name"

### API Base URL
- Nexus expects: `https://nexus-master.lmndstaging.com/v1/messages`
- LiteLLM auto-adds `/v1/` for Anthropic-compatible endpoints
- So we configure: `api_base=NEXUS_URL` (without `/v1`)
- Result: LiteLLM constructs the correct full URL

---

## 📊 Comparison: Before vs After

| Aspect | After Patch | After Giora Fixes |
|--------|-------------|-------------------|
| URL | `{NEXUS_URL}/v1` ❌ | `{NEXUS_URL}` ✅ |
| Model Name | `{MODEL}` ❌ | `litellm_proxy/{MODEL}` ✅ |
| Model | `anthropic/claude-opus-4-5-20251101` ❌ | `openai/gpt-4.1` ✅ |
| Logging | Basic ⚠️ | Verbose with emojis ✅ |
| Monitoring | None ❌ | 3 tools + docs ✅ |
| Status | 404/400 errors ❌ | Working ✅ |

---

## 🚀 How to Use Now

### Start Server
```bash
source .venv/bin/activate
adk web
```

### Monitor in Real-Time
```bash
./monitor_logs.sh
```

### View Detailed Commands
```bash
./view_agent_logs.sh follow
```

### Check Health
```bash
tail -30 ~/.cursor/projects/Users-or-tuchman-src-karpathy/terminals/*.txt | tail -10
```

---

## 📝 Summary of Critical Changes

**From Patch → Working System:**

1. **Removed duplicate `/v1`** from API base URL
2. **Added `litellm_proxy/` prefix** to model names (from Giora)
3. **Switched to OpenAI model** (Bedrock incompatible with tools)
4. **Added comprehensive logging** with file output
5. **Created monitoring tools** for debugging

**Most Important Fix:**
```python
model=f"litellm_proxy/{MODEL}"
```
This single line, learned from Giora's implementation, solved the model routing issues.

---

## 🔗 References

- **Giora Repo:** `/Users/or.tuchman/src/giora`
- **Key File:** `apps/giora/src/nexus-chat/main.py`
- **LiteLLM Docs:** Uses proxy prefix for proper routing
- **Nexus:** Lemonade's internal LiteLLM proxy gateway
