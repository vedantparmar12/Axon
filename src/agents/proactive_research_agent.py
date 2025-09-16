
import difflib
import json
import time
import hashlib
from datetime import datetime, timedelta
from typing import List, Dict, Any, Optional, Set, Callable
from dataclasses import dataclass, asdict
from enum import Enum
import asyncio
import aiofiles
from pathlib import Path
import sys
import os

# Add the parent directory to the path to allow imports from other modules
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from supabase import Client
from llm.manager import LLMManager

class Priority(Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"

class MonitoringType(Enum):
    URL = "url"
    KEYWORD = "keyword"
    TOPIC = "topic"
    ARXIV = "arxiv"
    NEWS = "news"

@dataclass
class MonitoringTarget:
    """Configuration for a monitoring target."""
    id: str
    type: MonitoringType
    target: str  # URL, keyword, topic, etc.
    frequency_hours: int = 24  # How often to check
    priority: Priority = Priority.MEDIUM
    keywords: Optional[List[str]] = None  # Keywords to look for in content
    notification_threshold: float = 0.3  # Similarity threshold for notifications
    last_checked: Optional[str] = None
    last_content_hash: Optional[str] = None
    created_at: Optional[str] = None

    def __post_init__(self):
        if self.created_at is None:
            self.created_at = datetime.now().isoformat()

@dataclass
class ResearchFinding:
    """Represents a significant finding from the research agent."""
    id: str
    target_id: str
    title: str
    summary: str
    content: str
    significance_score: float
    url: Optional[str] = None
    keywords_matched: Optional[List[str]] = None
    timestamp: Optional[str] = None

    def __post_init__(self):
        if self.timestamp is None:
            self.timestamp = datetime.now().isoformat()

class ProactiveResearchAgent:
    """
    An autonomous research agent that monitors sources for changes,
    discovers trends, and proactively notifies users of significant findings.
    """

    def __init__(self, config_path: Optional[str] = None):
        """Initialize the agent with local Ollama DeepSeek model."""
        self.llm_manager = LLMManager(default_provider=os.getenv("LLM_PROVIDER", "ollama"))
        self.config_path = config_path or os.path.join(os.path.dirname(__file__), "research_config.json")
        self.targets: Dict[str, MonitoringTarget] = {}
        self.findings: List[ResearchFinding] = []
        self.notification_callbacks: List[Callable] = []
        self.is_running = False
        self._load_config()

    async def check_for_updates(self, url: str, supabase_client: Client) -> str:
        """
        Checks for updates for a given URL, compares the two most recent versions,
        and returns a summary of the changes.

        Args:
            url: The URL to check for updates.
            supabase_client: The Supabase client instance.

        Returns:
            A string summarizing the changes, or a message indicating no changes or lack of history.
        """
        try:
            # 1. Fetch all chunks for the URL, ordered by crawl_time
            response = supabase_client.table("crawled_pages").select("content", "metadata").eq("url", url).execute()

            if not response.data:
                return "No content found for this URL. Please crawl it first."

            # 2. Group chunks by crawl_time
            versions = {}
            for chunk in response.data:
                crawl_time = chunk.get("metadata", {}).get("crawl_time")
                if crawl_time:
                    if crawl_time not in versions:
                        versions[crawl_time] = []
                    versions[crawl_time].append(chunk)

            if len(versions) < 2:
                return "Only one version of this document exists. Cannot compare for changes."

            # 3. Get the two most recent versions
            sorted_versions = sorted(versions.keys(), reverse=True)
            latest_crawl_time = sorted_versions[0]
            previous_crawl_time = sorted_versions[1]

            # 4. Reconstruct the full documents
            latest_chunks = sorted(versions[latest_crawl_time], key=lambda x: x.get("metadata", {}).get("chunk_index", 0))
            previous_chunks = sorted(versions[previous_crawl_time], key=lambda x: x.get("metadata", {}).get("chunk_index", 0))

            latest_content = "\n".join([chunk['content'] for chunk in latest_chunks])
            previous_content = "\n".join([chunk['content'] for chunk in previous_chunks])

            if latest_content == previous_content:
                return f"No changes detected between the crawl at {previous_crawl_time} and {latest_crawl_time}."

            # 5. Compute the difference
            diff = difflib.unified_diff(
                previous_content.splitlines(keepends=True),
                latest_content.splitlines(keepends=True),
                fromfile=f"version from {previous_crawl_time}",
                tofile=f"version from {latest_crawl_time}",
            )
            diff_text = "".join(diff)

            if not diff_text:
                 return f"No textual changes detected between the crawl at {previous_crawl_time} and {latest_crawl_time}."

            # 6. Summarize the diff using local Ollama DeepSeek model
            summary_prompt = "Please provide a concise summary of the changes in the document based on the provided diff. Focus on what was added, removed, or significantly changed. Keep it under 200 words."
            system_prompt = f"""You are an expert at analyzing document changes. Below is a diff showing the changes between two versions of a document from the URL {url}.

<diff>
{diff_text[:15000]}
</diff>

Analyze the changes and provide a clear, concise summary focusing on the most important modifications."""

            try:
                summary = await self.llm_manager.generate(
                    prompt=summary_prompt,
                    system_prompt=system_prompt,
                    temperature=0.3,
                    max_tokens=300
                )
            except Exception as e:
                print(f"LLM analysis failed, using fallback: {e}")
                # Fallback to basic analysis
                lines = diff_text.split('\n')
                added_lines = [line for line in lines if line.startswith('+') and not line.startswith('+++')]
                removed_lines = [line for line in lines if line.startswith('-') and not line.startswith('---')]
                summary = f"Document changes: {len(added_lines)} lines added, {len(removed_lines)} lines removed"

            return f"Changes detected between {previous_crawl_time} and {latest_crawl_time}:\n\n{summary}"

        except Exception as e:
            return f"An error occurred while checking for updates: {e}"

    def _load_config(self) -> None:
        """Load monitoring configuration from file."""
        try:
            if os.path.exists(self.config_path):
                with open(self.config_path, 'r') as f:
                    config_data = json.load(f)
                    for target_data in config_data.get("targets", []):
                        target = MonitoringTarget(
                            id=target_data["id"],
                            type=MonitoringType(target_data["type"]),
                            target=target_data["target"],
                            frequency_hours=target_data.get("frequency_hours", 24),
                            priority=Priority(target_data.get("priority", "medium")),
                            keywords=target_data.get("keywords"),
                            notification_threshold=target_data.get("notification_threshold", 0.3),
                            last_checked=target_data.get("last_checked"),
                            last_content_hash=target_data.get("last_content_hash"),
                            created_at=target_data.get("created_at")
                        )
                        self.targets[target.id] = target
        except Exception as e:
            print(f"Error loading config: {e}")

    async def _save_config(self) -> None:
        """Save monitoring configuration to file."""
        try:
            config_data = {
                "targets": [asdict(target) for target in self.targets.values()],
                "last_updated": datetime.now().isoformat()
            }
            async with aiofiles.open(self.config_path, 'w') as f:
                await f.write(json.dumps(config_data, indent=2))
        except Exception as e:
            print(f"Error saving config: {e}")

    def add_monitoring_target(
        self,
        target: str,
        monitoring_type: MonitoringType,
        frequency_hours: int = 24,
        priority: Priority = Priority.MEDIUM,
        keywords: Optional[List[str]] = None,
        notification_threshold: float = 0.3
    ) -> str:
        """Add a new monitoring target."""
        target_id = hashlib.md5(f"{monitoring_type.value}:{target}".encode()).hexdigest()[:8]

        monitoring_target = MonitoringTarget(
            id=target_id,
            type=monitoring_type,
            target=target,
            frequency_hours=frequency_hours,
            priority=priority,
            keywords=keywords,
            notification_threshold=notification_threshold
        )

        self.targets[target_id] = monitoring_target
        asyncio.create_task(self._save_config())
        return target_id

    def remove_monitoring_target(self, target_id: str) -> bool:
        """Remove a monitoring target."""
        if target_id in self.targets:
            del self.targets[target_id]
            asyncio.create_task(self._save_config())
            return True
        return False

    def list_monitoring_targets(self) -> List[Dict[str, Any]]:
        """List all monitoring targets."""
        return [asdict(target) for target in self.targets.values()]

    def add_notification_callback(self, callback: Callable) -> None:
        """Add a notification callback function."""
        self.notification_callbacks.append(callback)

    async def start_monitoring(self, supabase_client: Client) -> None:
        """Start the autonomous monitoring loop."""
        self.is_running = True
        print("🔍 Proactive Research Agent started monitoring...")

        while self.is_running:
            try:
                await self._monitoring_cycle(supabase_client)
                await asyncio.sleep(3600)  # Check every hour
            except Exception as e:
                print(f"Error in monitoring cycle: {e}")
                await asyncio.sleep(300)  # Wait 5 minutes before retrying

    def stop_monitoring(self) -> None:
        """Stop the monitoring loop."""
        self.is_running = False
        print("🛑 Proactive Research Agent stopped monitoring")

    async def _monitoring_cycle(self, supabase_client: Client) -> None:
        """Execute one monitoring cycle."""
        current_time = datetime.now()

        for target in self.targets.values():
            try:
                # Check if it's time to monitor this target
                if self._should_check_target(target, current_time):
                    await self._check_target(target, supabase_client)
                    target.last_checked = current_time.isoformat()
            except Exception as e:
                print(f"Error checking target {target.id}: {e}")

        await self._save_config()

    def _should_check_target(self, target: MonitoringTarget, current_time: datetime) -> bool:
        """Determine if a target should be checked based on frequency and priority."""
        if target.last_checked is None:
            return True

        last_checked = datetime.fromisoformat(target.last_checked)
        hours_since_check = (current_time - last_checked).total_seconds() / 3600

        # Adjust frequency based on priority
        frequency_multiplier = {
            Priority.CRITICAL: 0.25,  # Check 4x more often
            Priority.HIGH: 0.5,      # Check 2x more often
            Priority.MEDIUM: 1.0,    # Normal frequency
            Priority.LOW: 2.0        # Check half as often
        }

        adjusted_frequency = target.frequency_hours * frequency_multiplier[target.priority]
        return hours_since_check >= adjusted_frequency

    async def _check_target(self, target: MonitoringTarget, supabase_client: Client) -> None:
        """Check a specific target for updates."""
        if target.type == MonitoringType.URL:
            await self._check_url_target(target, supabase_client)
        elif target.type == MonitoringType.ARXIV:
            await self._check_arxiv_target(target, supabase_client)
        elif target.type == MonitoringType.NEWS:
            await self._check_news_target(target, supabase_client)
        elif target.type == MonitoringType.TOPIC:
            await self._check_topic_target(target, supabase_client)
        elif target.type == MonitoringType.KEYWORD:
            await self._check_keyword_target(target, supabase_client)

    async def _check_url_target(self, target: MonitoringTarget, supabase_client: Client) -> None:
        """Check a URL target for changes."""
        try:
            # Import the crawling function
            sys.path.append(os.path.dirname(os.path.dirname(__file__)))
            from crawl4ai_mcp import crawl_single_page

            # Create a mock context for the crawl function
            class MockContext:
                def __init__(self, supabase_client):
                    self.request_context = type('', (), {})()
                    self.request_context.lifespan_context = type('', (), {})()
                    self.request_context.lifespan_context.supabase_client = supabase_client

            ctx = MockContext(supabase_client)

            # Get current content
            content_summary = await self.check_for_updates(target.target, supabase_client)

            if "Changes detected" in content_summary:
                # Analyze the significance of changes
                significance = await self._analyze_content_significance(
                    content_summary, target.keywords
                )

                if significance["score"] >= target.notification_threshold:
                    finding = ResearchFinding(
                        id=hashlib.md5(f"{target.id}:{datetime.now().isoformat()}".encode()).hexdigest()[:8],
                        target_id=target.id,
                        title=f"Significant update detected: {target.target}",
                        summary=significance["summary"],
                        content=content_summary,
                        significance_score=significance["score"],
                        url=target.target,
                        keywords_matched=significance.get("keywords_matched", [])
                    )

                    await self._notify_finding(finding)
                    self.findings.append(finding)

        except Exception as e:
            print(f"Error checking URL target {target.target}: {e}")

    async def _check_arxiv_target(self, target: MonitoringTarget, supabase_client: Client) -> None:
        """Check arXiv for new papers on a topic."""
        try:
            import requests
            from xml.etree import ElementTree

            # Search arXiv API
            search_query = target.target.replace(" ", "+")
            arxiv_url = f"http://export.arxiv.org/api/query?search_query=all:{search_query}&start=0&max_results=10&sortBy=submittedDate&sortOrder=descending"

            response = requests.get(arxiv_url)
            if response.status_code == 200:
                root = ElementTree.fromstring(response.content)

                # Parse results
                papers = []
                for entry in root.findall('.//{http://www.w3.org/2005/Atom}entry'):
                    paper = {
                        'title': entry.find('.//{http://www.w3.org/2005/Atom}title').text.strip(),
                        'summary': entry.find('.//{http://www.w3.org/2005/Atom}summary').text.strip(),
                        'url': entry.find('.//{http://www.w3.org/2005/Atom}id').text,
                        'published': entry.find('.//{http://www.w3.org/2005/Atom}published').text
                    }
                    papers.append(paper)

                # Check if any papers are new and significant
                for paper in papers:
                    significance = await self._analyze_content_significance(
                        f"{paper['title']}\n\n{paper['summary']}", target.keywords
                    )

                    if significance["score"] >= target.notification_threshold:
                        finding = ResearchFinding(
                            id=hashlib.md5(f"{target.id}:{paper['url']}".encode()).hexdigest()[:8],
                            target_id=target.id,
                            title=f"New arXiv paper: {paper['title']}",
                            summary=significance["summary"],
                            content=paper['summary'],
                            significance_score=significance["score"],
                            url=paper['url'],
                            keywords_matched=significance.get("keywords_matched", [])
                        )

                        await self._notify_finding(finding)
                        self.findings.append(finding)

        except Exception as e:
            print(f"Error checking arXiv target {target.target}: {e}")

    async def _check_news_target(self, target: MonitoringTarget, supabase_client: Client) -> None:
        """Check news sources for relevant articles."""
        # This would integrate with news APIs like NewsAPI, Google News, etc.
        # For now, implement as a placeholder
        print(f"Checking news target: {target.target}")

    async def _check_topic_target(self, target: MonitoringTarget, supabase_client: Client) -> None:
        """Check for general topic-based content across sources."""
        # This would search across multiple sources for a topic
        # For now, implement as a placeholder
        print(f"Checking topic target: {target.target}")

    async def _check_keyword_target(self, target: MonitoringTarget, supabase_client: Client) -> None:
        """Check existing database for new content matching keywords."""
        try:
            # Search the database for recent content matching keywords
            yesterday = (datetime.now() - timedelta(days=1)).isoformat()

            # Query for recent content
            response = supabase_client.table("crawled_pages")\
                .select("*")\
                .gte("metadata->crawl_time", yesterday)\
                .execute()

            if response.data:
                relevant_content = []
                for item in response.data:
                    content = item.get("content", "")
                    if any(keyword.lower() in content.lower() for keyword in target.keywords or []):
                        relevant_content.append(item)

                if relevant_content:
                    # Analyze significance
                    combined_content = "\n\n".join([item["content"] for item in relevant_content])
                    significance = await self._analyze_content_significance(
                        combined_content, target.keywords
                    )

                    if significance["score"] >= target.notification_threshold:
                        finding = ResearchFinding(
                            id=hashlib.md5(f"{target.id}:{datetime.now().isoformat()}".encode()).hexdigest()[:8],
                            target_id=target.id,
                            title=f"New content matching keywords: {', '.join(target.keywords or [])}",
                            summary=significance["summary"],
                            content=combined_content[:1000] + "..." if len(combined_content) > 1000 else combined_content,
                            significance_score=significance["score"],
                            keywords_matched=significance.get("keywords_matched", [])
                        )

                        await self._notify_finding(finding)
                        self.findings.append(finding)

        except Exception as e:
            print(f"Error checking keyword target {target.target}: {e}")

    async def _analyze_content_significance(self, content: str, keywords: Optional[List[str]] = None) -> Dict[str, Any]:
        """Analyze the significance of content using local Ollama DeepSeek model."""
        try:
            # First do basic keyword matching for immediate filtering
            content_lower = content.lower()
            keywords_matched = []
            basic_score = 0.0

            if keywords:
                for keyword in keywords:
                    if keyword.lower() in content_lower:
                        keywords_matched.append(keyword)
                        basic_score += 0.15

            # If no keywords matched and threshold is high, skip expensive LLM analysis
            if basic_score == 0.0 and len(keywords or []) > 0:
                return {
                    "score": 0.0,
                    "summary": "No keyword matches found",
                    "keywords_matched": []
                }

            # Use local DeepSeek model for intelligent analysis
            keyword_context = ""
            if keywords:
                keyword_context = f"Pay special attention to content related to: {', '.join(keywords)}"

            prompt = f"""Analyze the following content for significance and novelty. {keyword_context}

Content:
{content[:8000]}

Please evaluate this content and provide:
1. A significance score from 0.0 to 1.0 (where 1.0 is extremely significant/newsworthy)
2. A brief summary explaining why this content is significant or not
3. Any keywords from the provided list that were matched

Consider factors like:
- Novelty and importance of information
- Presence of specific keywords
- Technical depth and research value
- Business impact or market relevance

Respond in JSON format: {{"score": 0.0-1.0, "summary": "explanation", "keywords_matched": ["keyword1", "keyword2"]}}"""

            try:
                response = await self.llm_manager.generate(
                    prompt=prompt,
                    temperature=0.3,
                    max_tokens=400
                )

                # Try to parse JSON response
                try:
                    analysis = json.loads(response)
                    score = float(analysis.get("score", basic_score))
                    summary = analysis.get("summary", "Content analyzed with local model")
                    ai_keywords = analysis.get("keywords_matched", [])

                    # Combine AI-detected keywords with basic matching
                    all_keywords = list(set(keywords_matched + ai_keywords))

                    return {
                        "score": min(score, 1.0),  # Ensure score is capped at 1.0
                        "summary": summary,
                        "keywords_matched": all_keywords
                    }
                except json.JSONDecodeError:
                    # If JSON parsing fails, extract score from text
                    import re
                    score_match = re.search(r'score["\s:]*([0-9.]+)', response.lower())
                    extracted_score = float(score_match.group(1)) if score_match else basic_score

                    return {
                        "score": min(max(extracted_score, basic_score), 1.0),
                        "summary": response[:200] + "..." if len(response) > 200 else response,
                        "keywords_matched": keywords_matched
                    }

            except Exception as e:
                print(f"DeepSeek analysis failed, using keyword-based scoring: {e}")
                # Enhanced fallback analysis
                significant_phrases = [
                    "breakthrough", "new", "announce", "release", "update", "launch",
                    "major", "significant", "important", "critical", "urgent",
                    "research", "discovery", "findings", "results", "paper"
                ]

                phrase_matches = sum(1 for phrase in significant_phrases if phrase in content_lower)
                enhanced_score = basic_score + min(phrase_matches * 0.05, 0.3)

                return {
                    "score": min(enhanced_score, 1.0),
                    "summary": f"Keyword-based analysis: {len(keywords_matched)} matched keywords, {phrase_matches} significant phrases",
                    "keywords_matched": keywords_matched
                }

        except Exception as e:
            print(f"Error analyzing content significance: {e}")
            return {"score": 0.0, "summary": "Analysis failed", "keywords_matched": []}

    async def _notify_finding(self, finding: ResearchFinding) -> None:
        """Notify about a significant finding."""
        print(f"""
🔬 Research Agent Discovery:
═══════════════════════════════════════
📌 {finding.title}
🎯 Significance: {finding.significance_score:.2f}
📝 {finding.summary}
🔗 URL: {finding.url or 'N/A'}
🏷️  Keywords: {', '.join(finding.keywords_matched or [])}
⏰ {finding.timestamp}
═══════════════════════════════════════
""")

        # Call notification callbacks
        for callback in self.notification_callbacks:
            try:
                if asyncio.iscoroutinefunction(callback):
                    await callback(finding)
                else:
                    callback(finding)
            except Exception as e:
                print(f"Error in notification callback: {e}")

    def get_recent_findings(self, hours: int = 24) -> List[ResearchFinding]:
        """Get findings from the last N hours."""
        cutoff_time = datetime.now() - timedelta(hours=hours)
        return [
            finding for finding in self.findings
            if datetime.fromisoformat(finding.timestamp) > cutoff_time
        ]

    def get_findings_by_target(self, target_id: str) -> List[ResearchFinding]:
        """Get all findings for a specific target."""
        return [finding for finding in self.findings if finding.target_id == target_id]

    async def generate_research_report(self, hours: int = 24) -> str:
        """Generate a comprehensive research report using rule-based analysis."""
        recent_findings = self.get_recent_findings(hours)

        if not recent_findings:
            return "No significant findings in the specified time period."

        # Group findings by target
        findings_by_target = {}
        target_info = {}

        for finding in recent_findings:
            if finding.target_id not in findings_by_target:
                findings_by_target[finding.target_id] = []
                # Get target info
                target = self.targets.get(finding.target_id)
                if target:
                    target_info[finding.target_id] = {
                        "type": target.type.value,
                        "target": target.target,
                        "priority": target.priority.value
                    }
            findings_by_target[finding.target_id].append(finding)

        # Try to generate AI-enhanced report using local DeepSeek model
        try:
            # Prepare data for AI analysis
            findings_summary = []
            for finding in recent_findings[:10]:  # Limit to top 10 findings
                findings_summary.append({
                    "title": finding.title,
                    "significance": finding.significance_score,
                    "summary": finding.summary,
                    "keywords": finding.keywords_matched
                })

            # Get trending keywords
            all_keywords = []
            for finding in recent_findings:
                if finding.keywords_matched:
                    all_keywords.extend(finding.keywords_matched)

            from collections import Counter
            trending_keywords = Counter(all_keywords).most_common(5)

            report_prompt = f"""Generate a comprehensive research report based on the following findings from the last {hours} hours:

SUMMARY STATISTICS:
- Total findings: {len(recent_findings)}
- Active targets: {len(findings_by_target)}
- Average significance: {sum(f.significance_score for f in recent_findings) / len(recent_findings):.2f}
- High-priority findings: {len([f for f in recent_findings if f.significance_score >= 0.7])}

TOP FINDINGS:
{json.dumps(findings_summary, indent=2)}

TRENDING KEYWORDS:
{dict(trending_keywords)}

Please provide:
1. Executive summary of key trends and discoveries
2. Analysis of significant findings
3. Identified patterns and insights
4. Recommendations for further investigation

Format as a well-structured markdown report."""

            ai_report = await self.llm_manager.generate(
                prompt=report_prompt,
                temperature=0.7,
                max_tokens=2000
            )

            # Add timestamp and statistics to AI report
            final_report = f"# AI-Generated Research Report - Last {hours} Hours\n"
            final_report += f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')} (Local DeepSeek Model)\n\n"
            final_report += ai_report

            # Append raw data section
            final_report += f"\n\n---\n\n## Raw Data Summary\n\n"
            final_report += f"**Total Findings**: {len(recent_findings)}\n"
            final_report += f"**Active Targets**: {len(findings_by_target)}\n"

            if trending_keywords:
                final_report += f"\n**Top Keywords**: {', '.join([f'{kw} ({count})' for kw, count in trending_keywords[:3]])}\n"

            return final_report

        except Exception as e:
            print(f"AI report generation failed, using structured fallback: {e}")

            # Fallback to structured report
            report = f"# Research Report - Last {hours} Hours\n"
            report += f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')} (Structured Format)\n\n"

            # Executive Summary
            report += "## Executive Summary\n"
            report += f"- Total findings: {len(recent_findings)}\n"
            report += f"- Active targets: {len(findings_by_target)}\n"

            avg_significance = sum(f.significance_score for f in recent_findings) / len(recent_findings)
            report += f"- Average significance score: {avg_significance:.2f}\n"

            high_priority_findings = [f for f in recent_findings if f.significance_score >= 0.7]
            report += f"- High-priority findings: {len(high_priority_findings)}\n\n"

            # Key findings
            if high_priority_findings:
                report += "## Key Discoveries\n\n"
                for finding in sorted(high_priority_findings, key=lambda x: x.significance_score, reverse=True)[:5]:
                    report += f"### {finding.title}\n"
                    report += f"**Score**: {finding.significance_score:.2f}\n"
                    report += f"**Summary**: {finding.summary}\n"
                    if finding.keywords_matched:
                        report += f"**Keywords**: {', '.join(finding.keywords_matched)}\n"
                    report += "\n"

            # Trending keywords
            all_keywords = []
            for finding in recent_findings:
                if finding.keywords_matched:
                    all_keywords.extend(finding.keywords_matched)

            if all_keywords:
                from collections import Counter
                keyword_counts = Counter(all_keywords)
                report += "## Trending Topics\n\n"
                for keyword, count in keyword_counts.most_common(5):
                    report += f"- **{keyword}**: {count} mentions\n"
                report += "\n"

            return report

