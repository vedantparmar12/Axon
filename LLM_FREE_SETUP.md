# 🚀 LLM-Free Proactive Research Agent Setup

## Overview

This version of the Proactive Research Agent has been optimized to work **without any external LLM dependencies**. It uses rule-based analysis instead of AI for content significance detection, making it lightweight, fast, and cost-free while still providing powerful autonomous research capabilities.

## ✅ What's Changed

### Removed Dependencies:
- ❌ OpenAI API calls
- ❌ Local LLM providers (Ollama, HuggingFace)
- ❌ Embedding providers
- ❌ LLM-based content analysis
- ❌ AI-powered report generation

### Rule-Based Replacements:
- ✅ **Content Significance Analysis**: Uses keyword matching, phrase detection, and statistical analysis
- ✅ **Change Detection**: Diff-based analysis with sample content extraction
- ✅ **Report Generation**: Structured markdown reports with analytics
- ✅ **Keyword Matching**: Direct string matching with case-insensitive search
- ✅ **Priority Scoring**: Rule-based significance scoring (0.0-1.0)

## 🔧 Configuration

### 1. Environment File (`.env`)
Your `.env` file should only contain:

```bash
# MCP Server Configuration
HOST=0.0.0.0
PORT=8051
TRANSPORT=stdio

# ===== PROACTIVE RESEARCH AGENT =====
# No LLM dependencies - uses rule-based analysis
RESEARCH_AGENT_ENABLED=true

# ===== RAG STRATEGIES (DISABLED FOR LLM-FREE MODE) =====
USE_CONTEXTUAL_EMBEDDINGS=false
USE_HYBRID_SEARCH=false
USE_AGENTIC_RAG=false
USE_RERANKING=false

# ===== hiRAG SETTINGS (DISABLED FOR LLM-FREE MODE) =====
USE_HIRAG=false

# ===== DATABASE CONFIGURATION =====
SUPABASE_URL=your_supabase_url_here
SUPABASE_SERVICE_KEY=your_supabase_service_key_here
```

### 2. Claude Desktop Configuration
Add this to your `claude_desktop_config.json`:

```json
{
  "mcpServers": {
    "crawl4ai-research-agent": {
      "command": "C:\\Users\\vedan\\miniconda3\\python.exe",
      "args": [
        "C:\\Users\\vedan\\Desktop\\mcp-rag\\mcp-crawl4ai-rag\\src\\crawl4ai_mcp.py"
      ],
      "env": {
        "TRANSPORT": "stdio"
      }
    }
  }
}
```

**Note**: Only `TRANSPORT=stdio` is required in the environment. All other settings are read from the `.env` file.

## 🧠 How Rule-Based Analysis Works

### Content Significance Scoring

The system analyzes content using multiple factors:

1. **Base Score** (0.0-0.3):
   - Content length: >1000 chars = +0.2, >5000 chars = +0.1

2. **Keyword Matching** (0.0-unlimited):
   - Each matched keyword = +0.15

3. **Significant Phrases** (0.0-0.3 max):
   - Detects: "breakthrough", "new", "announce", "release", "update", "launch"
   - Research terms: "research", "discovery", "findings", "results", "paper"
   - Business terms: "acquisition", "merger", "funding", "partnership"
   - Each phrase = +0.05 (capped at 0.3)

4. **Statistics/Numbers** (0.0-0.1 max):
   - Detects percentages, dollar amounts, decimal numbers
   - Each number = +0.02 (capped at 0.1)

**Final Score**: Sum of all factors, capped at 1.0

### Example Scoring:
```
Content: "New breakthrough in AI research shows 95% improvement"
- Base score: +0.2 (>1000 chars)
- Keywords ("AI"): +0.15
- Phrases ("new", "breakthrough", "research"): +0.15
- Numbers ("95%"): +0.02
Total: 0.52 (High significance)
```

## 🚀 Quick Start

### 1. Start the Server
```bash
cd mcp-crawl4ai-rag
python src/crawl4ai_mcp.py
```

### 2. Configure Targets (via Claude Desktop)
```javascript
// Monitor arXiv for AI research
add_research_target({
  "target": "artificial intelligence",
  "monitoring_type": "arxiv",
  "frequency_hours": 12,
  "priority": "high",
  "keywords": ["neural networks", "deep learning", "transformer"],
  "notification_threshold": 0.4
})

// Monitor a company blog
add_research_target({
  "target": "https://openai.com/blog",
  "monitoring_type": "url",
  "frequency_hours": 6,
  "priority": "critical",
  "keywords": ["GPT", "ChatGPT", "release"],
  "notification_threshold": 0.3
})
```

### 3. Start Monitoring
```javascript
start_research_monitoring()
```

### 4. Get Results
```javascript
// View recent findings
get_research_findings({"hours": 24})

// Generate report
generate_research_report({"hours": 24})
```

## 📊 Available MCP Tools

All original tools are available:

### Target Management
- `add_research_target` - Configure monitoring
- `remove_research_target` - Remove targets
- `list_research_targets` - View all targets

### Monitoring Control
- `start_research_monitoring` - Begin monitoring
- `stop_research_monitoring` - Stop monitoring
- `get_research_status` - Check status

### Results & Reports
- `get_research_findings` - View discoveries
- `generate_research_report` - Structured reports

## 🎯 Optimizing Rule-Based Detection

### 1. Keyword Strategy
```javascript
// Good: Specific, relevant terms
"keywords": ["GPT-4", "transformer", "attention mechanism"]

// Better: Include variations and synonyms
"keywords": ["GPT", "transformer", "attention", "neural network", "LLM", "language model"]
```

### 2. Notification Thresholds
```javascript
// High precision (fewer, higher-quality alerts)
"notification_threshold": 0.7

// Balanced (moderate filtering)
"notification_threshold": 0.4

// High sensitivity (catch everything relevant)
"notification_threshold": 0.2
```

### 3. Priority Levels
- **Critical**: Check 4x more often (every 6h if set to 24h)
- **High**: Check 2x more often (every 12h if set to 24h)
- **Medium**: Normal frequency (every 24h)
- **Low**: Check half as often (every 48h if set to 24h)

## 🔍 What Gets Detected

### High-Significance Content (0.7-1.0):
- ✅ Press releases with multiple keywords
- ✅ Research papers with target terms
- ✅ Major announcements with statistics
- ✅ Product launches with feature details

### Medium-Significance Content (0.4-0.6):
- ✅ Blog posts mentioning keywords
- ✅ News articles with relevant terms
- ✅ Updates containing numbers/metrics
- ✅ Documentation changes

### Low-Significance Content (0.1-0.3):
- ✅ Brief mentions of keywords
- ✅ General content with weak signals
- ✅ Tangentially related material

## 📈 Benefits of Rule-Based Approach

### Advantages:
- 🚀 **Fast**: No API calls or model inference
- 💰 **Free**: No LLM usage costs
- 🔒 **Private**: No data sent to external services
- 🎯 **Predictable**: Deterministic scoring
- ⚡ **Lightweight**: Minimal resource usage
- 🔧 **Customizable**: Easy to modify rules

### Trade-offs:
- 📊 **Less nuanced**: Cannot understand context like LLMs
- 🔍 **Keyword-dependent**: Requires good keyword selection
- 📝 **Simpler summaries**: Rule-based instead of natural language

## 🛠️ Troubleshooting

### No Findings Detected
1. **Lower threshold**: Try 0.2 instead of 0.4
2. **Expand keywords**: Add synonyms and variations
3. **Check targets**: Ensure URLs are accessible
4. **Verify frequency**: Make sure enough time has passed

### Too Many Notifications
1. **Raise threshold**: Try 0.6 instead of 0.4
2. **Narrow keywords**: Use more specific terms
3. **Adjust priority**: Lower priority = less frequent checks

### Missing Important Updates
1. **Add more keywords**: Include industry terminology
2. **Lower threshold**: Increase sensitivity
3. **Check priority**: Higher priority = more frequent checks

## 📋 Example Use Cases

### Academic Researcher
```javascript
add_research_target({
  "target": "computer vision",
  "monitoring_type": "arxiv",
  "keywords": ["object detection", "YOLO", "CNN", "vision transformer"],
  "notification_threshold": 0.5
})
```

### Tech Professional
```javascript
add_research_target({
  "target": "https://kubernetes.io/blog",
  "monitoring_type": "url",
  "keywords": ["release", "security", "performance", "feature"],
  "notification_threshold": 0.4
})
```

### Startup Founder
```javascript
add_research_target({
  "target": "startup funding",
  "monitoring_type": "keyword",
  "keywords": ["Series A", "Series B", "funding", "investment", "valuation"],
  "notification_threshold": 0.3
})
```

---

🎉 **Success!** You now have a completely LLM-free autonomous research agent that works directly with Claude Desktop, providing intelligent monitoring without any external AI dependencies or costs!