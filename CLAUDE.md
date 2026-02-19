# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Overview

Karpathy is an agentic Machine Learning Engineer that trains state-of-the-art ML models using Claude Code SDK and Google ADK. It demonstrates Claude Scientific Skills for machine learning through a simple implementation.

The agent operates by delegating tasks to specialized experts via Claude Code SDK, working within a sandboxed environment that contains scientific skills and ML packages.

## Prerequisites

- Python 3.13 or higher
- [uv](https://github.com/astral-sh/uv) package manager
- Claude Code installed and authenticated
- Access to a LiteLLM proxy server (nexus)
- `.env` file in `karpathy/` directory with:
  - `NEXUS_URL` (defaults to `https://nexus-master.lmndstaging.com`)
  - `LITELLM_PROXY_API_KEY` (defaults to `sk-12345`)
  - `AGENT_MODEL` (model name in LiteLLM format, e.g., `anthropic/claude-opus-4-5-20251101`)

## Common Commands

### Setup and Installation
```bash
# Install dependencies
uv sync

# Setup sandbox manually (without starting web interface)
python -m karpathy.utils

# Full startup (setup sandbox + start ADK web interface)
python start.py
```

### Running the Agent
```bash
# Start ADK web interface (after sandbox setup)
adk web
# Navigate to http://localhost:8000
# Select 'karpathy' in top left under 'Select an agent'
```

### Testing Individual Components
```bash
# Test delegate_task function directly
python -m karpathy.tools
```

## Architecture

### Core Components

**agent.py** - Defines the main ADK agent (`MainAgent`) that:
- Uses LiteLlm model configured with nexus proxy (`NEXUS_URL`, `LITELLM_PROXY_API_KEY`, `AGENT_MODEL`)
- Loads instructions from `instructions.yaml`
- Uses `delegate_task` as its primary tool
- Outputs to `final_output` key

**tools.py** - Implements `delegate_task()` function that:
- Delegates tasks to Claude Code SDK via `query()` function
- Uses `claude_code` preset with custom system prompts
- Operates in `sandbox` directory with `bypassPermissions` mode
- Loads common instructions and appends expert-specific system prompts
- Streams tool use blocks and returns ResultMessage

**utils.py** - Provides sandbox management utilities:
- `load_instructions()` - Loads agent instructions from YAML
- `download_scientific_skills()` - Clones Claude Scientific Skills from GitHub
- `setup_uv_environment()` - Creates `.venv` in sandbox with default ML packages (PyTorch, transformers, scikit-learn, pandas, etc.)
- `copy_env_file()` - Copies `.env` from `karpathy/` to `sandbox/`
- `setup_sandbox()` - Orchestrates full sandbox setup

**instructions.yaml** - Contains two key instruction sets:
- `main_agent` - Instructions for MainAgent orchestration and expert delegation
- `common_instructions` - Shared instructions for all delegated experts

**__init__.py** - Exports `root_agent` for ADK web discovery

### Sandbox Architecture

The `sandbox/` directory is the isolated workspace where:
- All code execution and file writes happen
- `.claude/skills/` contains scientific skills from [Claude Scientific Skills](https://github.com/K-Dense-AI/claude-scientific-skills)
- `.venv/` contains Python virtual environment with ML packages
- `.env` file contains API keys (copied from `karpathy/.env`)
- User-provided datasets and scripts should be manually added here
- All agent outputs (experiments, configs, datasets, plans, research, etc.) are written here

### Expert System

MainAgent delegates to specialized experts via `delegate_task()`. Each expert is defined through:
- A descriptive system prompt appended to the `claude_code` preset
- A specific subgoal and expected outputs
- Access to Claude Skills and the sandbox environment

Available expert types (as documented in `instructions.yaml`):
- **Plan Creator/Reviewer** - Create and review plans (`plan.md`)
- **Research Agent** - Research topics using perplexity-search (`research.md`)
- **Data Discoverer** - Discover and describe datasets (`dataset_description.md`)
- **Data Engineer** - Prepare and manage datasets
- **Experiment Manager** - Design and run experiments with tracking
- **Evaluation Agent** - Define metrics and evaluate models
- **Code Planner/Reviewer/Writer/Executor** - Handle code lifecycle (`code_plan.md`)
- **Infra & Modal Operator** - Manage compute and infrastructure
- **Reviewer** - Monitor progress (`feedback.md`)

New experts can be created dynamically as needed.

### Delegation Flow

1. MainAgent receives user request
2. Loads `main_agent` instructions from YAML
3. Decides which expert(s) to use
4. Calls `delegate_task()` with:
   - Task prompt (includes `common_instructions` + user prompt)
   - Expert-specific system prompt
5. Claude Code SDK executes in `sandbox/` directory
6. Results are streamed back to MainAgent
7. MainAgent interprets results and continues orchestration

### Environment Variables

Configuration is loaded from `.env` files:
- Development: `karpathy/.env` (source of truth)
- Runtime: `sandbox/.env` (copied during setup)
- Accessed by experts via `dotenv` in sandbox environment

Key variables:
- `NEXUS_URL` - LiteLLM proxy server URL (defaults to `https://nexus-master.lmndstaging.com`)
- `LITELLM_PROXY_API_KEY` - API key for the proxy (defaults to `sk-12345`)
- `AGENT_MODEL` - Model name in LiteLLM format (e.g., `anthropic/claude-opus-4-5-20251101`)

### Dependencies

Core packages:
- `claude-agent-sdk>=0.1.6` - Claude Code SDK for expert delegation
- `google-adk>=1.18.0` - Google ADK for agent framework
- `litellm>=1.79.3` - Universal LLM interface
- `markitdown[all]>=0.1.3` - File format conversion
- `mcp>=1.21.1` - Model Context Protocol
- `modal>=1.2.2` - Compute infrastructure
- `python-dotenv>=1.2.1` - Environment variable management

Sandbox ML packages (installed via uv):
- PyTorch ecosystem: torch, torchvision, torchaudio, pytorch-lightning, torch-geometric
- ML frameworks: transformers, datasets, scikit-learn
- Data science: numpy, pandas, scipy, matplotlib, seaborn

## Key Principles

1. **Sandbox isolation** - All agent work happens in `sandbox/`, never in the main codebase
2. **Skill-first** - Prefer using available Claude Skills over custom implementations
3. **Expert delegation** - Break down complex tasks into expert-specific subtasks
4. **Iterative loops** - Check artifacts, plan, delegate, inspect, repeat
5. **Resource awareness** - Use `get-available-resources` before planning intensive work
6. **Organized outputs** - Group experiments, configs, and notes in named subdirectories
