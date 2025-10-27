#!/usr/bin/env python3
"""
AutoSort Analytics Data Collection Script

This script demonstrates how to collect and analyze anonymous file type data
from AutoSort users using free/serverless solutions.

Usage:
    python3 analytics_collector.py [options]

Options:
    --github     Use GitHub Issues as data source
    --google     Use Google Forms as data source
    --local      Analyze local data only
    --export     Export data to CSV
"""

import json
import csv
import requests
import argparse
from pathlib import Path
from datetime import datetime, timedelta
from collections import Counter, defaultdict
from typing import Dict, List, Any, Optional
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class AnalyticsCollector:
    """Collects and analyzes AutoSort analytics data from various sources."""
    
    def __init__(self):
        self.data_sources = {
            "github": self._collect_from_github,
            "google_forms": self._collect_from_google_forms,
            "local": self._collect_from_local
        }
    
    def collect_data(self, source: str = "local") -> Dict[str, Any]:
        """
        Collect data from specified source.
        
        Args:
            source: Data source ('github', 'google_forms', 'local')
            
        Returns:
            Collected data dictionary
        """
        if source not in self.data_sources:
            raise ValueError(f"Unknown data source: {source}")
        
        logger.info(f"Collecting data from {source}...")
        return self.data_sources[source]()
    
    def _collect_from_local(self) -> Dict[str, Any]:
        """Collect data from local analytics files."""
        data = {
            "source": "local",
            "timestamp": datetime.now().isoformat(),
            "reports": [],
            "summary": {}
        }
        
        # Look for analytics data files
        home_dir = Path.home()
        analytics_dirs = [
            home_dir / ".autosort",
            Path.cwd() / "analytics_data",
            Path.cwd() / "user_data"
        ]
        
        for analytics_dir in analytics_dirs:
            if analytics_dir.exists():
                data_file = analytics_dir / "analytics_data.json"
                if data_file.exists():
                    try:
                        with open(data_file, 'r') as f:
                            local_data = json.load(f)
                            data["reports"].extend(local_data.get("reports", []))
                    except Exception as e:
                        logger.error(f"Failed to read {data_file}: {e}")
        
        # Generate summary
        data["summary"] = self._generate_summary(data["reports"])
        return data
    
    def _collect_from_github(self) -> Dict[str, Any]:
        """
        Collect data from GitHub Issues.
        
        This would require:
        1. GitHub repository with issues for unhandled file types
        2. GitHub API token
        3. Issue parsing logic
        """
        data = {
            "source": "github",
            "timestamp": datetime.now().isoformat(),
            "reports": [],
            "summary": {}
        }
        
        # Example implementation (would need actual GitHub API integration)
        logger.info("GitHub collection not implemented - requires API setup")
        
        # Mock data for demonstration
        mock_reports = [
            {
                "extension": ".xyz",
                "context": "unknown",
                "timestamp": datetime.now().isoformat(),
                "anonymous_id": "abc123",
                "version": "2.3",
                "count": 1
            },
            {
                "extension": ".custom",
                "context": "document",
                "timestamp": datetime.now().isoformat(),
                "anonymous_id": "def456",
                "version": "2.3",
                "count": 1
            }
        ]
        
        data["reports"] = mock_reports
        data["summary"] = self._generate_summary(mock_reports)
        return data
    
    def _collect_from_google_forms(self) -> Dict[str, Any]:
        """
        Collect data from Google Forms/Sheets.
        
        This would require:
        1. Google Forms with specific fields
        2. Google Sheets API access
        3. Data parsing logic
        """
        data = {
            "source": "google_forms",
            "timestamp": datetime.now().isoformat(),
            "reports": [],
            "summary": {}
        }
        
        logger.info("Google Forms collection not implemented - requires API setup")
        
        # Mock data for demonstration
        mock_reports = [
            {
                "extension": ".newformat",
                "context": "image",
                "timestamp": datetime.now().isoformat(),
                "anonymous_id": "ghi789",
                "version": "2.3",
                "count": 1
            }
        ]
        
        data["reports"] = mock_reports
        data["summary"] = self._generate_summary(mock_reports)
        return data
    
    def _generate_summary(self, reports: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Generate summary statistics from reports."""
        if not reports:
            return {
                "total_reports": 0,
                "unique_extensions": 0,
                "top_extensions": [],
                "context_breakdown": {},
                "version_breakdown": {}
            }
        
        # Count extensions
        extension_counts = Counter(report["extension"] for report in reports)
        
        # Count contexts
        context_counts = Counter(report["context"] for report in reports)
        
        # Count versions
        version_counts = Counter(report["version"] for report in reports)
        
        return {
            "total_reports": len(reports),
            "unique_extensions": len(extension_counts),
            "top_extensions": extension_counts.most_common(10),
            "context_breakdown": dict(context_counts),
            "version_breakdown": dict(version_counts),
            "recent_reports": len([
                r for r in reports 
                if datetime.fromisoformat(r["timestamp"]) > datetime.now() - timedelta(days=7)
            ])
        }
    
    def export_to_csv(self, data: Dict[str, Any], output_file: str) -> None:
        """Export data to CSV file."""
        reports = data.get("reports", [])
        if not reports:
            logger.warning("No reports to export")
            return
        
        with open(output_file, 'w', newline='', encoding='utf-8') as csvfile:
            fieldnames = ["extension", "context", "timestamp", "version", "count"]
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
            
            writer.writeheader()
            for report in reports:
                writer.writerow({
                    "extension": report["extension"],
                    "context": report["context"],
                    "timestamp": report["timestamp"],
                    "version": report["version"],
                    "count": report["count"]
                })
        
        logger.info(f"Exported {len(reports)} reports to {output_file}")
    
    def generate_report(self, data: Dict[str, Any]) -> str:
        """Generate a human-readable report."""
        summary = data["summary"]
        
        report = f"""
AutoSort Analytics Report
========================
Source: {data["source"]}
Generated: {data["timestamp"]}

Summary Statistics:
------------------
Total Reports: {summary["total_reports"]}
Unique Extensions: {summary["unique_extensions"]}
Recent Reports (7 days): {summary["recent_reports"]}

Top Unhandled File Types:
-------------------------
"""
        
        for extension, count in summary["top_extensions"][:10]:
            report += f"  {extension}: {count} reports\n"
        
        report += f"""
Context Breakdown:
-----------------
"""
        for context, count in summary["context_breakdown"].items():
            report += f"  {context}: {count} reports\n"
        
        report += f"""
Version Breakdown:
-----------------
"""
        for version, count in summary["version_breakdown"].items():
            report += f"  {version}: {count} reports\n"
        
        return report


def main():
    """Main function for command-line usage."""
    parser = argparse.ArgumentParser(description="AutoSort Analytics Data Collector")
    parser.add_argument("--source", choices=["github", "google_forms", "local"], 
                      default="local", help="Data source to collect from")
    parser.add_argument("--export", help="Export data to CSV file")
    parser.add_argument("--report", action="store_true", help="Generate human-readable report")
    
    args = parser.parse_args()
    
    collector = AnalyticsCollector()
    
    try:
        # Collect data
        data = collector.collect_data(args.source)
        
        # Export to CSV if requested
        if args.export:
            collector.export_to_csv(data, args.export)
        
        # Generate report if requested
        if args.report:
            report = collector.generate_report(data)
            print(report)
        
        # Always show basic summary
        summary = data["summary"]
        print(f"\nCollected {summary['total_reports']} reports with {summary['unique_extensions']} unique extensions")
        
    except Exception as e:
        logger.error(f"Data collection failed: {e}")
        return 1
    
    return 0


if __name__ == "__main__":
    exit(main())
