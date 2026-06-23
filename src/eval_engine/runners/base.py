import os
import json
import asyncio
import logging
import shutil
import aiohttp
from datetime import datetime
from typing import Dict, Any, List, Optional
from rich.console import Console
from rich.table import Table
from pydantic import BaseModel

from ..config import ConfigLoader
from ..adapters import get_adapter, BaseAdapter
from ..stats import wilson_interval, confidence_band

console = Console()
logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# Compliance disclaimer — included verbatim in every report.
# ---------------------------------------------------------------------------
_COMPLIANCE_DISCLAIMER = (
    "This report documents test-loop results only. Framework tags (OWASP, NIST, "
    "MITRE) indicate which categories were tested, not certified compliance with "
    "those standards."
)

class EvaluationResult(BaseModel):
    metric: str
    score: float
    passed: bool
    details: Optional[str] = None

class BaseRunner:
    """Base class for all evaluation loops."""
    
    def __init__(self, loop_name: str, tags: List[str], target_endpoint: str,
                 config_path: str = "config.yaml",
                 dataset_override: Optional[str] = None):
        self.loop_name = loop_name
        self.tags = tags
        self.target_endpoint = target_endpoint
        self.config_path = config_path
        self.dataset_override = dataset_override
        
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
        
        # Parse LOOP.md to get pass_threshold, framework mappings, and requirements
        self.pass_threshold = 0.8  # default
        self.framework_mappings: List[str] = []
        self.requires: List[str] = []
        self._dataset_row_count: int = 0
        self._using_example_dataset: bool = False
        self._read_frontmatter()
        
    def _read_frontmatter(self):
        """Reads LOOP.md and extracts pass_threshold, framework mappings,
        and requires list if present."""
        loop_md_path = os.path.join("loops", self.loop_name, "LOOP.md")

        if os.path.exists(loop_md_path):
            try:
                with open(loop_md_path, "r", encoding="utf-8") as f:
                    content = f.read().strip()
                if content.startswith("---"):
                    parts = content.split("---", 2)
                    if len(parts) >= 3:
                        yaml_text = parts[1].strip()
                        # Use a simple line-based parser for the fields we need
                        current_list_key = None
                        current_list: List[str] = []
                        for line in yaml_text.split("\n"):
                            stripped = line.strip()

                            # Collect list items
                            if stripped.startswith("- ") and current_list_key:
                                current_list.append(stripped[2:].strip().strip("'\""))
                                continue

                            # When we hit a new key, flush any open list
                            if ":" in stripped and not stripped.startswith("-"):
                                if current_list_key and current_list:
                                    self._store_frontmatter_field(current_list_key, current_list)
                                current_list_key = None
                                current_list = []

                            if stripped.startswith("pass_threshold:"):
                                val = stripped.split(":", 1)[1].strip().strip("'\"")
                                try:
                                    self.pass_threshold = float(val)
                                except ValueError:
                                    pass
                            elif stripped.startswith("owasp_llm:"):
                                val = stripped.split(":", 1)[1].strip()
                                if val and val not in ("", "|", ">-", ">"):
                                    # Inline list or single value
                                    for v in val.strip("[]").split(","):
                                        if v.strip():
                                            self.framework_mappings.append("OWASP-" + v.strip().strip("'\""))
                                else:
                                    current_list_key = "owasp_llm"
                                    current_list = []
                            elif stripped.startswith("nist_ai_rmf:"):
                                val = stripped.split(":", 1)[1].strip()
                                if val and val not in ("", "|", ">-", ">"):
                                    for v in val.strip("[]").split(","):
                                        if v.strip():
                                            self.framework_mappings.append("NIST-" + v.strip().strip("'\""))
                                else:
                                    current_list_key = "nist_ai_rmf"
                                    current_list = []
                            elif stripped.startswith("mitre_atlas:"):
                                val = stripped.split(":", 1)[1].strip()
                                if val and val not in ("", "|", ">-", ">"):
                                    for v in val.strip("[]").split(","):
                                        if v.strip():
                                            self.framework_mappings.append("MITRE-" + v.strip().strip("'\""))
                                else:
                                    current_list_key = "mitre_atlas"
                                    current_list = []
                            elif stripped.startswith("requires:"):
                                val = stripped.split(":", 1)[1].strip()
                                if val.startswith("[") and val.endswith("]"):
                                    self.requires = [v.strip().strip("'\"") for v in val[1:-1].split(",") if v.strip()]
                                elif val and val not in ("", "|", ">-", ">"):
                                    self.requires = [val.strip("'\"")]
                                else:
                                    current_list_key = "requires"
                                    current_list = []

                        # Flush any trailing list
                        if current_list_key and current_list:
                            self._store_frontmatter_field(current_list_key, current_list)

                        # Deduplicate framework mappings to prevent redundant tags
                        self.framework_mappings = list(dict.fromkeys(self.framework_mappings))

            except Exception as e:
                logger.debug(f"Failed to read {loop_md_path}: {e}")

    def _store_frontmatter_field(self, key: str, values: List[str]):
        """Store parsed multi-line YAML list values into the correct attribute."""
        if key == "owasp_llm":
            self.framework_mappings.extend(f"OWASP-{v}" for v in values)
        elif key == "nist_ai_rmf":
            self.framework_mappings.extend(f"NIST-{v}" for v in values)
        elif key == "mitre_atlas":
            self.framework_mappings.extend(f"MITRE-{v}" for v in values)
        elif key == "requires":
            self.requires = values

    def _load_dataset(self) -> list:
        """Load dataset rows from the override path, config path, or bundled
        example file.  Sets ``self._dataset_row_count`` and
        ``self._using_example_dataset`` for report metadata.

        Resolution order:
        1. ``--dataset`` CLI override (``self.dataset_override``).
        2. ``config.dataset_path`` from config.yaml.
        3. Bundled ``references/dataset.example.jsonl`` (with a warning).
        """
        from pathlib import Path

        if self.dataset_override:
            dataset_path = Path(self.dataset_override)
            self._using_example_dataset = False
        elif self.config.dataset_path:
            dataset_path = Path(self.config.dataset_path)
            self._using_example_dataset = False
        else:
            dataset_path = Path("loops") / self.loop_name / "references" / "dataset.example.jsonl"
            self._using_example_dataset = True

        dataset: list = []
        if dataset_path.exists():
            with open(dataset_path, "r", encoding="utf-8") as f:
                for line in f:
                    if line.strip():
                        dataset.append(json.loads(line))

        self._dataset_row_count = len(dataset)

        if self._using_example_dataset and dataset:
            console.print(
                f"[yellow]⚠ Using bundled example dataset ({self._dataset_row_count} rows). "
                f"Pass --dataset to use your own.[/yellow]"
            )

        return dataset

    def _preflight_checks(self):
        """Fail fast if declared requirements are not met.

        Reads ``self.requires`` (parsed from ``requires:`` in LOOP.md
        frontmatter) and verifies each requirement before any network
        requests are made.
        """
        for req in self.requires:
            if req == "docker":
                if shutil.which("docker") is None:
                    raise RuntimeError(
                        f"Loop '{self.loop_name}' requires Docker (declared in "
                        f"LOOP.md 'requires: [docker]'), but 'docker' is not on "
                        f"PATH.\n  -> Install Docker and ensure it is running."
                    )
            elif req == "judge_model":
                # Delegate to the existing require_judge logic — the scorer
                # type is not known here so we just verify a judge adapter
                # exists at all.
                if self.judge_adapter is None:
                    raise RuntimeError(
                        f"Loop '{self.loop_name}' requires a judge model "
                        f"(declared in LOOP.md 'requires: [judge_model]'), but "
                        f"no judge adapter is configured.\n"
                        f"  -> Create a config.yaml with a 'judge:' section "
                        f"(see config.example.yaml) and pass it via --config.\n"
                        f"     Source: config loaded from '{self.config_path}'."
                    )

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

        # Pre-flight requirement checks
        self._preflight_checks()

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

        # Statistical confidence
        ci_low, ci_high = wilson_interval(passed_count, total)
        band = confidence_band(self._dataset_row_count or total)

        # Dataset path for metadata
        if self.dataset_override:
            dataset_display = self.dataset_override
        elif self.config.dataset_path:
            dataset_display = self.config.dataset_path
        else:
            dataset_display = f"loops/{self.loop_name}/references/dataset.example.jsonl"

        metadata = {
            "target_adapter": self.config.target.type,
            "judge_adapter": self.config.judge.type if self.config.judge else None,
            "dataset": dataset_display,
            "tags": self.tags,
            "maps_to": self.framework_mappings,
        }
        
        report = {
            "loop_name": self.loop_name,
            "target": self.target_endpoint,
            "compliance_disclaimer": _COMPLIANCE_DISCLAIMER,
            "metadata": metadata,
            "sample_size": self._dataset_row_count or total,
            "coverage_note": (
                f"Mapping coverage is based on {self._dataset_row_count or total} "
                f"test items. This is a directional signal, not an exhaustive audit."
            ),
            "pass_rate": pass_rate,
            "confidence_interval": [ci_low, ci_high],
            "confidence_band": band,
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
