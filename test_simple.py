#!/usr/bin/env python3
"""
Simple test script for the Proactive Research Agent
"""
import asyncio
import json
import os
import sys
from pathlib import Path

# Add src to path
sys.path.append(str(Path(__file__).parent / "src"))

# Mock environment for testing
os.environ["LLM_PROVIDER"] = "mock"

def test_research_agent_structure():
    """Test the Proactive Research Agent structure and basic functionality."""
    print("Testing Proactive Research Agent Structure...")

    try:
        # Test imports
        from agents.proactive_research_agent import (
            ProactiveResearchAgent,
            MonitoringType,
            Priority,
            MonitoringTarget,
            ResearchFinding
        )
        print("SUCCESS: All imports successful")

        # Test enums
        print("\nTesting enums...")
        monitoring_types = [t.value for t in MonitoringType]
        priorities = [p.value for p in Priority]

        print(f"   MonitoringType options: {monitoring_types}")
        print(f"   Priority options: {priorities}")

        expected_types = ["url", "keyword", "topic", "arxiv", "news"]
        expected_priorities = ["low", "medium", "high", "critical"]

        assert all(t in monitoring_types for t in expected_types), "Missing monitoring types"
        assert all(p in priorities for p in expected_priorities), "Missing priority levels"
        print("SUCCESS: Enums validation passed")

        # Test data classes
        print("\nTesting data structures...")

        # Test MonitoringTarget
        target = MonitoringTarget(
            id="test123",
            type=MonitoringType.URL,
            target="https://example.com",
            frequency_hours=24,
            priority=Priority.HIGH,
            keywords=["AI", "ML"],
            notification_threshold=0.5
        )

        assert target.id == "test123"
        assert target.type == MonitoringType.URL
        assert target.target == "https://example.com"
        assert target.created_at is not None
        print("SUCCESS: MonitoringTarget structure validated")

        # Test ResearchFinding
        finding = ResearchFinding(
            id="finding123",
            target_id="test123",
            title="Test Finding",
            summary="Test summary",
            content="Test content",
            significance_score=0.8,
            url="https://example.com"
        )

        assert finding.id == "finding123"
        assert finding.significance_score == 0.8
        assert finding.timestamp is not None
        print("SUCCESS: ResearchFinding structure validated")

        # Test method availability
        print("\nTesting method availability...")

        methods_to_check = [
            'add_monitoring_target',
            'remove_monitoring_target',
            'list_monitoring_targets',
            'start_monitoring',
            'stop_monitoring',
            'get_recent_findings',
            'generate_research_report'
        ]

        for method_name in methods_to_check:
            assert hasattr(ProactiveResearchAgent, method_name), f"Missing method: {method_name}"

        print(f"SUCCESS: All {len(methods_to_check)} required methods available")

        print("\nAll structure tests completed successfully!")
        print("="*60)
        print("PROACTIVE RESEARCH AGENT STRUCTURE TEST SUMMARY")
        print("="*60)
        print("SUCCESS: Module imports")
        print("SUCCESS: Enum definitions")
        print("SUCCESS: Data structures")
        print("SUCCESS: Method availability")
        print("="*60)
        print("\nThe Proactive Research Agent structure is valid!")

        return True

    except Exception as e:
        print(f"ERROR: Structure test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = test_research_agent_structure()
    if success:
        print("\nReady for integration testing!")
    else:
        print("\nStructure validation failed!")
        sys.exit(1)