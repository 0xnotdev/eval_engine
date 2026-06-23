import os
import json
import asyncio
import aiohttp
from datetime import datetime
from typing import Dict, Any, List, Optional
from rich.console import Console
from rich.table import Table
from pydantic import BaseModel

from ..config import ConfigLoader
from ..adapters import get_adapter, BaseAdapter

console = Console()

class EvaluationResult(BaseModel):
    metric: str
    score: float
    passed: bool
    details: Optional[str] = None

class BaseRunner:
    """Base class for all evaluation loops."""
    
    def __init__(self, loop_name: str, tags: List[str], target_endpoint: str, config_path: str = "config.yaml"):
        self.loop_name = loop_name
        self.tags = tags
        self.target_endpoint = target_endpoint
        self.config_path = config_path
        
        # Load Config
        self.config = ConfigLoader.load(config_path)
        
        # Initialize target adapter
        self.target_adapter: BaseAdapter = get_adapter(
            adapter_type=self.config.target.type,
            target_endpoint=self.target_endpoint,
            headers=self.config.target.headers,
            **self.config.target.kwargs
        )
        
        # Initialize judge adapter (if configured, defaults to target endpoint if none provided)
        if self.config.judge:
            self.judge_adapter: BaseAdapter = get_adapter(
                adapter_type=self.config.judge.type,
                # Typically judge is OpenAI or Anthropic API, not local endpoint, but can be overridden
                target_endpoint=self.config.judge.kwargs.get("endpoint", "https://api.openai.com/v1/chat/completions"),
                headers=self.config.judge.headers,
                **self.config.judge.kwargs
            )
        else:
            self.judge_adapter = None
        
        self.results: List[EvaluationResult] = []
        self.start_time = None
        self.end_time = None
        self.session: Optional[aiohttp.ClientSession] = None
        
        # Parse LOOP.md to get pass_threshold and other metadata
        self.pass_threshold = 0.8  # default
        self._read_frontmatter()
        
    def _read_frontmatter(self):
        """Reads LOOP.md and extracts pass_threshold if present."""
        loop_md_path = os.path.join("loops", self.loop_name, "LOOP.md")

        if os.path.exists(loop_md_path):
            try:
                with open(loop_md_path, "r", encoding="utf-8") as f:
                    content = f.read().strip()
                if content.startswith("---"):
                    parts = content.split("---", 2)
                    if len(parts) >= 3:
                        yaml_text = parts[1].strip()
                        for line in yaml_text.split("\n"):
                            line = line.strip()
                            if line.startswith("pass_threshold:"):
                                val = line.split(":", 1)[1].strip().strip("'\"")
                                try:
                                    self.pass_threshold = float(val)
                                except ValueError:
                                    pass
            except Exception as e:
                import logging
                logging.debug(f"Failed to read {loop_md_path}: {e}")

    def require_judge(self, scorer_type: str) -> None:
        """Fail fast (instead of silently scoring 0.0) when a judge is needed
        but none is configured.

        The 'llm_judge' scorer delegates scoring to a separate LLM. Without a
        judge adapter it cannot evaluate anything and previously returned
        score=0.0 for every item with only a low-visibility 'details' string.
        Raising here surfaces the misconfiguration immediately, at startup,
        with an actionable message pointing at config.yaml.
        """
        if scorer_type == "llm_judge" and self.judge_adapter is None:
            raise RuntimeError(
                f"Loop '{self.loop_name}' uses scorer 'llm_judge', which requires "
                f"a judge adapter, but none is configured.\n"
                f"  -> Create a config.yaml with a 'judge:' section (see "
                f"config.example.yaml) and pass it via --config.\n"
                f"     Source: config loaded from '{self.config_path}'."
            )
        
    async def _get_session(self) -> aiohttp.ClientSession:
        if self.session is None or self.session.closed:
            # Configure connection pooling
            connector = aiohttp.TCPConnector(limit=500, limit_per_host=100)
            self.session = aiohttp.ClientSession(connector=connector)
        return self.session

    async def _send_payload(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        """Send a standard HTTP POST payload to the target endpoint using the adapter layer.
        For backwards compatibility during the refactor, payload typically has 'messages'."""
        session = await self._get_session()
        messages = payload.get("messages", [])
        
        response = await self.target_adapter.send(session, messages)
        if response.error:
            return {"error": response.error}
        
        # Merge adapter response into legacy format for now
        data = response.raw
        data["_adapter_text"] = response.text
        data["_latency"] = response.latency_ms
        data["_ttft_ms"] = response.ttft_ms
        return data

    async def close(self):
        """Clean up resources."""
        if self.session and not self.session.closed:
            await self.session.close()

    def execute(self) -> Dict[str, Any]:
        """Entry point for executing the loop. Should be overridden or call async implementation."""
        console.print(f"[bold blue]Starting Loop:[/] {self.loop_name}")
        console.print(f"[dim]Target:[/] {self.target_endpoint}")
        self.start_time = datetime.utcnow()
        
        # Run async loop
        asyncio.run(self._run_wrapper())
        
        self.end_time = datetime.utcnow()
        return self.generate_report()

    async def _run_wrapper(self):
        try:
            await self.run_async()
        finally:
            await self.close()

    async def run_async(self):
        """Subclasses should implement their async testing logic here."""
        raise NotImplementedError("Subclasses must implement run_async")

    def generate_report(self) -> Dict[str, Any]:
        """Generate final execution report."""
        passed_count = sum(1 for r in self.results if r.passed)
        total = len(self.results)
        pass_rate = passed_count / total if total > 0 else 0.0
        
        metadata = {
            "target_adapter": self.config.target.type,
            "judge_adapter": self.config.judge.type if self.config.judge else None,
            "dataset": self.config.dataset_path or f"loops/{self.loop_name}/references/dataset.jsonl",
            "tags": self.tags
        }
        
        report = {
            "loop_name": self.loop_name,
            "target": self.target_endpoint,
            "metadata": metadata,
            "pass_rate": pass_rate,
            "total_metrics": total,
            "passed_metrics": passed_count,
            "start_time": self.start_time.isoformat() if self.start_time else None,
            "end_time": self.end_time.isoformat() if self.end_time else None,
            "metrics": [r.model_dump() for r in self.results]
        }
        return report

    def save_report(self, filepath: str = "results.json"):
        """Save report to disk and print summary table."""
        report = self.generate_report()
        with open(filepath, "w", encoding="utf-8") as f:
            json.dump(report, f, indent=2)
            
        console.print(f"\n[bold green]Report saved to:[/] {filepath}")
        
        table = Table(title=f"Results: {self.loop_name}")
        table.add_column("Metric", style="cyan")
        table.add_column("Score", justify="right", style="magenta")
        table.add_column("Passed", justify="center")
        table.add_column("Details", style="dim")
        
        for r in self.results:
            status = "[green]PASS[/]" if r.passed else "[red]FAIL[/]"
            table.add_row(r.metric, f"{r.score:.2f}", status, r.details or "")
            
        console.print(table)
        
    def save_junit_xml(self, filepath: str = "junit.xml"):
        """Export results to JUnit XML format for CI/CD integration."""
        from xml.sax.saxutils import escape
        
        total = len(self.results)
        failures = sum(1 for r in self.results if not r.passed)
        
        xml = [
            '<?xml version="1.0" encoding="UTF-8"?>',
            f'<testsuites name="{escape(self.loop_name)}" tests="{total}" failures="{failures}" errors="0" time="0">',
            f'  <testsuite name="{escape(self.loop_name)}" tests="{total}" failures="{failures}" errors="0" time="0">'
        ]
        
        for r in self.results:
            xml.append(f'    <testcase classname="{escape(self.loop_name)}" name="{escape(r.metric)}" time="0">')
            if not r.passed:
                xml.append(f'      <failure message="Score {r.score:.2f} below threshold">{escape(r.details or "")}</failure>')
            xml.append('    </testcase>')
            
        xml.append('  </testsuite>')
        xml.append('</testsuites>')
        
        with open(filepath, "w", encoding="utf-8") as f:
            f.write("\n".join(xml))
        console.print(f"[bold green]JUnit XML saved to:[/] {filepath}")
