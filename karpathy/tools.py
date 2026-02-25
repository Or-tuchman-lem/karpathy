import asyncio
import logging
from dataclasses import asdict
from datetime import datetime
from pathlib import Path

from dotenv import load_dotenv

from .utils import load_instructions

load_dotenv("karpathy/.env")

# Configure logging to both console and file
log_dir = Path("sandbox/logs")
log_dir.mkdir(exist_ok=True)
log_file = log_dir / f"karpathy_{datetime.now().strftime('%Y%m%d_%H%M%S')}.log"

# Create formatters
console_formatter = logging.Formatter('%(asctime)s - [KARPATHY] %(message)s', datefmt='%H:%M:%S')
file_formatter = logging.Formatter('%(asctime)s - %(levelname)s - [KARPATHY] %(message)s')

# Console handler
console_handler = logging.StreamHandler()
console_handler.setLevel(logging.INFO)
console_handler.setFormatter(console_formatter)

# File handler
file_handler = logging.FileHandler(log_file)
file_handler.setLevel(logging.DEBUG)
file_handler.setFormatter(file_formatter)

# Configure logger
logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)
logger.addHandler(console_handler)
logger.addHandler(file_handler)

logger.info(f"📁 Logging to: {log_file}")

COMMON_INSTRUCTIONS = load_instructions("common_instructions")

# Count delegations (main agent follow-up calls) for chain-of-thought visibility
_delegation_count = 0


async def delegate_task(
    prompt: str,
    append_system_prompt: str,
):
    """Delegate a task to an expert

    Args:
        prompt: The prompt describing the task to delegate
        append_system_prompt: The system prompt describing the expert
    Returns:
        The result of the delegation with todos tracking and progress updates
    """
    # Import here to avoid Pydantic schema generation issues at module load time
    from claude_agent_sdk import (
        AssistantMessage,
        ClaudeAgentOptions,
        ResultMessage,
        ToolUseBlock,
        query,
    )

    global _delegation_count
    _delegation_count += 1

    # Construct the full prompt that will be sent
    full_user_prompt = f"{COMMON_INSTRUCTIONS}\n\nUser Prompt: {prompt}"
    
    logger.info("=" * 80)
    logger.info(f"🚀 DELEGATION #{_delegation_count} (main agent follow-up)")
    logger.info("=" * 80)
    
    # Log the follow-up question / task the main agent is asking the expert
    logger.info("❓ FOLLOW-UP QUESTION / TASK TO EXPERT:")
    logger.info("-" * 80)
    logger.info(prompt)
    logger.info("-" * 80)
    
    # Log expert system prompt
    logger.info("👤 EXPERT SYSTEM PROMPT:")
    logger.info("-" * 80)
    logger.info(append_system_prompt)
    logger.info("-" * 80)
    
    # Log the full prompt being sent (common instructions + user prompt)
    logger.info("📝 FULL USER PROMPT SENT TO EXPERT:")
    logger.info("-" * 80)
    logger.info(full_user_prompt)
    logger.info("-" * 80)
    
    # Log configuration
    logger.info("⚙️  CONFIGURATION:")
    logger.info(f"   - Working Directory: sandbox")
    logger.info(f"   - Permission Mode: bypassPermissions")
    logger.info(f"   - Preset: claude_code")
    logger.info("=" * 80)

    result = None
    query_gen = query(
        prompt=full_user_prompt,
        options=ClaudeAgentOptions(
            system_prompt={
                "type": "preset",
                "preset": "claude_code",
                "append": append_system_prompt,
            },  # Use the preset
            setting_sources=["user", "project"],
            cwd="sandbox",
            permission_mode="bypassPermissions",
        ),
    )

    logger.info("⏳ Starting Claude Code query...")
    message_count = 0
    
    try:
        async for message in query_gen:
            message_count += 1
            logger.info(f"📨 Received message #{message_count}: {type(message).__name__}")
            
            # Log chain of thought (reasoning) and tool use
            if isinstance(message, AssistantMessage):
                logger.debug(f"   Content blocks: {len(message.content)}")
                for i, block in enumerate(message.content):
                    if isinstance(block, ToolUseBlock):
                        if block.name == "Skill":
                            skill_name = block.input.get('skill', 'unknown')
                            logger.info(f"  🔧 Using Skill: {skill_name}")
                            logger.debug(f"     Skill input: {block.input}")
                            print(f"Using the skill: {skill_name}")
                        else:
                            logger.info(f"  🛠️  Using Tool: {block.name}")
                            # Log tool arguments (truncated for readability)
                            if hasattr(block, 'input') and block.input:
                                tool_input_str = str(block.input)
                                if len(tool_input_str) > 200:
                                    logger.debug(f"     Tool input: {tool_input_str[:200]}...")
                                else:
                                    logger.debug(f"     Tool input: {tool_input_str}")
                            print(f"Using the tool: {block.name}")
                    else:
                        # Chain of thought: log expert reasoning / follow-up text at INFO
                        block_type = type(block).__name__
                        if hasattr(block, 'text') and getattr(block, 'text', None):
                            text = block.text
                            max_log = 4000
                            if len(text) > max_log:
                                text_log = text[:max_log] + f"\n... [truncated, total {len(text)} chars]"
                            else:
                                text_log = text
                            logger.info("💭 CHAIN OF THOUGHT / EXPERT REASONING:")
                            logger.info("-" * 40)
                            logger.info(text_log)
                            logger.info("-" * 40)
                            logger.debug(f"   [{block_type}] full length: {len(text)}")
                        else:
                            logger.debug(f"   [{block_type}]")

            # Check for ResultMessage and return the result
            elif isinstance(message, ResultMessage):
                logger.info("✅ Received ResultMessage - task complete!")
                logger.debug(f"   Result keys: {list(asdict(message).keys())}")
                result = asdict(message)
    finally:
        # Explicitly close the async generator
        await query_gen.aclose()
        logger.info(f"🏁 Task delegation finished. Processed {message_count} messages.")
        logger.info("=" * 80)

    return result


if __name__ == "__main__":
    # result = asyncio.run(conduct_research("What is the capital of France?"))
    # print(result)
    result = asyncio.run(
        delegate_task(
            "What Skills are available?",
            "You are a helpful assistant",
        )
    )
    print(result)
