import os
import json
import asyncio
import aiohttp
from datetime import datetime
from typing import Dict, Any, List, Optional
from rich.console import Console
from rich.table import Table
from pydantic import BaseModel

console = Console()

class EvaluationResult(BaseModel):
    metric: str
    score: float
    passed: bool
    details: Optional[str] = None

class BaseRunner:
    """Base class for all evaluation loops."""
    
    def __init__(self, loop_name: str, tags: List[str], target_endpoint: str):
        self.loop_name = loop_name
        self.tags = tags
        self.target_endpoint = target_endpoint
        self.results: List[EvaluationResult] = []
        self.start_time = None
        self.end_time = None
        
    async def _send_payload(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        """Send a standard HTTP POST payload to the target endpoint."""
        async with aiohttp.ClientSession() as session:
            try:
                async with session.post(self.target_endpoint, json=payload, timeout=10) as response:
                    return await response.json()
            except Exception as e:
                return {"error": str(e)}

    def execute(self) -> Dict[str, Any]:
        """Entry point for executing the loop. Should be overridden or call async implementation."""
        console.print(f"[bold blue]Starting Loop:[/] {self.loop_name}")
        console.print(f"[dim]Target:[/] {self.target_endpoint}")
        self.start_time = datetime.utcnow()
        
        # Run async loop
        asyncio.run(self.run_async())
        
        self.end_time = datetime.utcnow()
        return self.generate_report()

    async def run_async(self):
        """Subclasses should implement their async testing logic here."""
        raise NotImplementedError("Subclasses must implement run_async")

    def generate_report(self) -> Dict[str, Any]:
        """Generate final execution report."""
        passed_count = sum(1 for r in self.results if r.passed)
        total = len(self.results)
        pass_rate = passed_count / total if total > 0 else 0.0
        
        report = {
            "loop_name": self.loop_name,
            "target": self.target_endpoint,
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
        with open(filepath, "w") as f:
            json.dump(report, f, indent=2)
            
        console.print(f"\\n[bold green]Report saved to:[/] {filepath}")
        
        table = Table(title=f"Results: {self.loop_name}")
        table.add_column("Metric", style="cyan")
        table.add_column("Score", justify="right", style="magenta")
        table.add_column("Passed", justify="center")
        table.add_column("Details", style="dim")
        
        for r in self.results:
            status = "[green]PASS[/]" if r.passed else "[red]FAIL[/]"
            table.add_row(r.metric, f"{r.score:.2f}", status, r.details or "")
            
        console.print(table)
