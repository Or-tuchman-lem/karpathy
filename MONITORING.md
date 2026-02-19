# Monitoring Karpathy Agent

## 🔍 How to Tell if the App is Stuck

The Karpathy agent can take time to process tasks, especially when:
- Analyzing large datasets (57K+ rows)
- Running complex ML operations
- Using Claude Code to execute code in the sandbox

Here's how to monitor progress:

## 📊 Method 1: Watch Logs in Real-Time (Recommended)

### Option A: Use the Monitor Script
In a new terminal window:
```bash
cd /Users/or.tuchman/src/karpathy
./monitor_logs.sh
```

This will show:
- 🚀 Task delegation events
- 🔧 Skills being used
- 🛠️ Tools being executed
- ✅ Task completion status
- 🔴 Any errors

### Option B: Tail the Terminal Log Manually
```bash
# Find the latest terminal file
tail -f ~/.cursor/projects/Users-or-tuchman-src-karpathy/terminals/*.txt | grep -E "KARPATHY|ERROR|skill|tool"
```

## 📈 What Normal Progress Looks Like

You should see:
```
[KARPATHY] 🚀 DELEGATING TASK TO EXPERT
[KARPATHY] 📝 Prompt: Please analyze sandbox/ds_agent_test_set.csv
[KARPATHY] 👤 Expert: You are a Data Discoverer...
[KARPATHY] ⏳ Starting Claude Code query...
[KARPATHY] 📨 Received message #1: AssistantMessage
[KARPATHY]   🔧 Using Skill: exploratory-data-analysis
[KARPATHY] 📨 Received message #2: AssistantMessage
[KARPATHY]   🛠️ Using Tool: Read
[KARPATHY] ✅ Received ResultMessage - task complete!
[KARPATHY] 🏁 Task delegation finished. Processed 5 messages.
```

## 🚨 Signs the App is Stuck

### Bad Signs:
- ❌ No log activity for >2 minutes
- ❌ Repeated "ERROR" messages
- ❌ Browser shows loading forever with no updates

### Good Signs (App is Working):
- ✅ Regular "LiteLLM completion()" messages
- ✅ "Using the skill:" or "Using the tool:" messages
- ✅ Incrementing message counts
- ✅ File operations in sandbox (check with `ls -lt sandbox/`)

## 🐛 Check if Stuck

Run this command to see recent activity:
```bash
tail -20 ~/.cursor/projects/Users-or-tuchman-src-karpathy/terminals/*.txt | grep -E "KARPATHY|ERROR"
```

## 📁 Check Sandbox Activity

See if files are being created/modified:
```bash
ls -lt sandbox/ | head -10
```

If you see new files or recent modifications, the agent is working!

## ⏱️ Expected Timings

- **Simple questions**: 5-15 seconds
- **Dataset analysis**: 30-90 seconds
- **Model training**: 2-10 minutes
- **Complex ML pipelines**: 5-30 minutes

## 🔄 If Actually Stuck

1. Check the browser console (F12) for errors
2. Look for ERROR in logs: `grep ERROR ~/.cursor/projects/Users-or-tuchman-src-karpathy/terminals/*.txt`
3. Check if Claude Code is waiting for something: `ps aux | grep claude`
4. Restart the server if needed (refresh will create new session)

## 💡 Pro Tips

- Keep a terminal open with `./monitor_logs.sh` running
- The agent tells you which expert it's using - this helps understand progress
- Check sandbox files to see intermediate results
- Agent outputs are streamed in the web interface - you should see partial responses

## 🎯 Quick Health Check

Run this one-liner:
```bash
tail -30 ~/.cursor/projects/Users-or-tuchman-src-karpathy/terminals/*.txt | tail -10
```

If you see recent timestamps (within last minute), app is alive!
