# 🔬 Proactive Research Agent - User Guide

## Overview

The Proactive Research Agent is an autonomous research system that monitors sources for changes, discovers trends, and proactively notifies you of significant findings. Instead of waiting for you to ask questions, it acts as your personal research assistant, continuously scanning the web and databases for relevant information.

## 🚀 Quick Start

### 1. Start the MCP Server
```bash
cd mcp-crawl4ai-rag
python src/crawl4ai_mcp.py
```

### 2. Configure Monitoring Targets
Use the MCP tools to add targets for monitoring:

```javascript
// Add arXiv monitoring for AI research
add_research_target({
  "target": "artificial intelligence",
  "monitoring_type": "arxiv",
  "frequency_hours": 12,
  "priority": "high",
  "keywords": ["neural networks", "deep learning", "transformer"],
  "notification_threshold": 0.6
})

// Monitor a specific URL for changes
add_research_target({
  "target": "https://openai.com/blog",
  "monitoring_type": "url",
  "frequency_hours": 6,
  "priority": "critical",
  "keywords": ["GPT", "ChatGPT", "language model"],
  "notification_threshold": 0.4
})

// Track keywords in your existing database
add_research_target({
  "target": "machine learning research",
  "monitoring_type": "keyword",
  "frequency_hours": 24,
  "priority": "medium",
  "keywords": ["ML", "research", "algorithm"],
  "notification_threshold": 0.3
})
```

### 3. Start Autonomous Monitoring
```javascript
start_research_monitoring()
```

### 4. Get Research Findings
```javascript
// Get findings from the last 24 hours
get_research_findings({"hours": 24})

// Generate a comprehensive report
generate_research_report({"hours": 24})
```

## 📋 Available MCP Tools

### Target Management

#### `add_research_target`
Configure a new monitoring target.

**Parameters:**
- `target` (string): URL, topic, or search term to monitor
- `monitoring_type` (string): "url", "keyword", "topic", "arxiv", or "news"
- `frequency_hours` (int): How often to check (default: 24)
- `priority` (string): "low", "medium", "high", or "critical" (default: "medium")
- `keywords` (array): Optional keywords to look for
- `notification_threshold` (float): Significance threshold 0.0-1.0 (default: 0.3)

#### `remove_research_target`
Remove a monitoring target.

**Parameters:**
- `target_id` (string): ID of target to remove

#### `list_research_targets`
List all configured monitoring targets.

### Monitoring Control

#### `start_research_monitoring`
Start autonomous monitoring of all configured targets.

#### `stop_research_monitoring`
Stop the monitoring process.

#### `get_research_status`
Get current status of the research agent.

### Results & Reports

#### `get_research_findings`
Get recent research findings.

**Parameters:**
- `hours` (int): Number of hours to look back (default: 24)

#### `generate_research_report`
Generate AI-powered research report from findings.

**Parameters:**
- `hours` (int): Timeframe for report (default: 24)

## 🎯 Monitoring Types

### 1. URL Monitoring
Monitors specific websites for changes and updates.

**Use Cases:**
- Company blogs and news pages
- Documentation sites
- Product update pages
- Research institution websites

**Example:**
```javascript
add_research_target({
  "target": "https://research.google.com/blog",
  "monitoring_type": "url",
  "keywords": ["AI", "machine learning", "research"]
})
```

### 2. arXiv Monitoring
Searches arXiv for new research papers on specific topics.

**Use Cases:**
- Latest research in your field
- Tracking specific authors or topics
- Monitoring breakthrough papers

**Example:**
```javascript
add_research_target({
  "target": "quantum computing",
  "monitoring_type": "arxiv",
  "keywords": ["quantum", "qubits", "algorithms"]
})
```

### 3. Keyword Monitoring
Monitors your existing database for new content matching keywords.

**Use Cases:**
- Track mentions of technologies
- Monitor competitor discussions
- Find relevant content in crawled data

**Example:**
```javascript
add_research_target({
  "target": "AI safety",
  "monitoring_type": "keyword",
  "keywords": ["alignment", "safety", "ethics", "AI risk"]
})
```

### 4. Topic Monitoring
General topic-based monitoring across multiple sources.

**Use Cases:**
- Industry trend tracking
- Broad research areas
- Market intelligence

### 5. News Monitoring
Monitor news sources for relevant articles (planned feature).

## 🔥 Priority Levels

The agent adjusts monitoring frequency based on priority:

- **Critical**: Checks 4x more often than specified frequency
- **High**: Checks 2x more often
- **Medium**: Normal frequency
- **Low**: Checks half as often

## 🧠 AI-Powered Analysis

The agent uses AI to:

1. **Analyze Content Significance**: Determines if changes/content are noteworthy
2. **Match Keywords**: Identifies relevant keywords in discovered content
3. **Generate Summaries**: Creates concise summaries of findings
4. **Score Relevance**: Assigns significance scores to filter noise
5. **Create Reports**: Generates comprehensive research reports with insights

## 📊 Configuration Management

### Persistent Storage
Configurations are automatically saved to `src/agents/research_config.json`.

### Example Configuration
```json
{
  "targets": [
    {
      "id": "arxiv001",
      "type": "arxiv",
      "target": "artificial intelligence",
      "frequency_hours": 12,
      "priority": "high",
      "keywords": ["neural networks", "deep learning"],
      "notification_threshold": 0.6,
      "last_checked": null,
      "created_at": "2024-01-01T00:00:00"
    }
  ],
  "last_updated": "2024-01-01T00:00:00"
}
```

## 🔔 Notifications

When significant findings are discovered, the agent:

1. **Console Output**: Displays formatted notifications
2. **Structured Data**: Stores findings with metadata
3. **Callbacks**: Supports custom notification functions
4. **Reports**: Generates periodic summary reports

### Example Finding Output
```
🔬 Research Agent Discovery:
═══════════════════════════════════════
📌 New arXiv paper: Breakthrough in Neural Architecture
🎯 Significance: 0.85
📝 This paper introduces a novel attention mechanism...
🔗 URL: https://arxiv.org/abs/2024.12345
🏷️  Keywords: transformer, attention, efficiency
⏰ 2024-01-15T10:30:00
═══════════════════════════════════════
```

## 🛡️ Best Practices

### 1. Start Small
- Begin with 2-3 high-priority targets
- Test notification thresholds
- Adjust frequencies based on results

### 2. Optimize Thresholds
- **High threshold (0.7-1.0)**: Only breakthrough discoveries
- **Medium threshold (0.4-0.6)**: Important updates
- **Low threshold (0.1-0.3)**: All relevant mentions

### 3. Use Keywords Effectively
- Include synonyms and variations
- Balance specificity with coverage
- Update based on findings

### 4. Monitor Performance
- Check agent status regularly
- Review findings quality
- Adjust configurations as needed

## 🔧 Troubleshooting

### Agent Not Starting
1. Check environment variables are set
2. Verify Supabase connection
3. Ensure LLM provider is configured

### No Findings
1. Lower notification threshold
2. Broaden keywords
3. Check target configuration
4. Verify monitoring is running

### Too Many Notifications
1. Raise notification threshold
2. Narrow keywords
3. Adjust priority levels
4. Reduce monitoring frequency

## 🎯 Use Case Examples

### Academic Researcher
```javascript
// Monitor arXiv for papers in your field
add_research_target({
  "target": "computer vision",
  "monitoring_type": "arxiv",
  "frequency_hours": 12,
  "priority": "high",
  "keywords": ["object detection", "segmentation", "CNN"],
  "notification_threshold": 0.5
})

// Track conference websites
add_research_target({
  "target": "https://neurips.cc",
  "monitoring_type": "url",
  "frequency_hours": 24,
  "priority": "medium"
})
```

### Tech Professional
```javascript
// Monitor competitor blogs
add_research_target({
  "target": "https://engineering.company.com/blog",
  "monitoring_type": "url",
  "frequency_hours": 8,
  "priority": "high",
  "keywords": ["architecture", "scaling", "performance"]
})

// Track industry keywords
add_research_target({
  "target": "cloud computing trends",
  "monitoring_type": "keyword",
  "keywords": ["kubernetes", "serverless", "microservices"]
})
```

### Investment Research
```javascript
// Monitor company announcements
add_research_target({
  "target": "https://investor.company.com/news",
  "monitoring_type": "url",
  "priority": "critical",
  "keywords": ["earnings", "partnership", "acquisition"]
})

// Track market research
add_research_target({
  "target": "fintech innovation",
  "monitoring_type": "keyword",
  "keywords": ["blockchain", "DeFi", "digital payments"]
})
```

## 🚀 Advanced Features

### Custom Notification Callbacks
```python
# Add custom notification handling
def my_notification_handler(finding):
    # Send to Slack, email, etc.
    send_to_slack(finding.title, finding.summary)

agent.add_notification_callback(my_notification_handler)
```

### Programmatic Configuration
```python
from agents.proactive_research_agent import ProactiveResearchAgent, MonitoringType, Priority

agent = ProactiveResearchAgent()

# Add targets programmatically
target_id = agent.add_monitoring_target(
    target="https://example.com",
    monitoring_type=MonitoringType.URL,
    frequency_hours=6,
    priority=Priority.HIGH,
    keywords=["important", "update"],
    notification_threshold=0.4
)
```

## 📈 Future Enhancements

Planned features include:

- **News API Integration**: Monitor news sources
- **Social Media Monitoring**: Track Twitter, Reddit, etc.
- **Email Notifications**: Send findings via email
- **Web Dashboard**: Visual monitoring interface
- **ML Model Training**: Improve significance detection
- **Integration APIs**: Webhook support for external systems

---

🎉 **Congratulations!** You now have an autonomous research agent working for you 24/7, discovering relevant information and trends before you even know to look for them.