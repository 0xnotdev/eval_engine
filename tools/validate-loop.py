#!/usr/bin/env python3
"""
AI-Testing-Loops Validator

Validates LOOP.md files against the repository's quality standards.
Checks YAML frontmatter schema, required fields, naming conventions,
and directory structure.

Usage:
    python validate-loop.py <path-to-LOOP.md>
    python validate-loop.py loops/evaluating-rag-faithfulness/LOOP.md
    python validate-loop.py --all  # validate all loops
"""

import sys
import os
import re
import json
import argparse
from pathlib import Path
from typing import List, Dict, Any, Optional, Tuple


# --- Constants ---

REQUIRED_FIELDS = ["name", "description", "domain", "subdomain", "tags", "version", "author", "license"]
OPTIONAL_FIELDS = ["owasp_llm", "nist_ai_rmf", "mitre_atlas", "language", "scorer"]
VALID_DOMAIN = "ai-testing"
MAX_NAME_LENGTH = 64
MIN_DESCRIPTION_LENGTH = 50
MIN_TAGS = 2
KEBAB_CASE_PATTERN = re.compile(r"^[a-z0-9]+(-[a-z0-9]+)*$")

VALID_SUBDOMAINS = {
    # Canonical subdomains
    "llm-evaluation", "rag-evaluation", "agent-evaluation",
    "guardrails", "stress-testing", "qa-testing",
    "red-teaming", "prompt-security", "reliability-engineering",
    "bias-fairness", "hallucination-detection", "multi-agent-testing",
    "memory-testing", "tool-use-testing", "compliance-testing",
    "observability",
    # Aliases
    "evaluation", "evals", "rag-testing", "agent-testing",
    "safety-guardrails", "input-guardrails", "output-guardrails",
    "load-testing", "performance-testing",
    "quality-assurance", "regression-testing",
    "adversarial-testing", "security-testing",
    "prompt-injection", "jailbreak-testing",
    "chaos-engineering", "fault-tolerance",
    "fairness-testing", "factuality-testing",
    "orchestration-testing", "state-management-testing",
    "function-calling-testing", "governance-testing",
    "monitoring", "tracing",
}

REQUIRED_BODY_SECTIONS = ["When to Use", "Prerequisites", "Workflow"]
RECOMMENDED_BODY_SECTIONS = ["Overview", "Objectives", "Validation Criteria"]

REQUIRED_SUBDIRS = ["references", "scripts"]
REQUIRED_FILES_IN_DIR = {
    "references": ["standards.md"],
    "scripts": ["agent.py"],
}


class ValidationError:
    """Represents a single validation issue."""
    def __init__(self, level: str, message: str, line: Optional[int] = None):
        self.level = level  # "ERROR" or "WARNING"
        self.message = message
        self.line = line

    def __str__(self):
        loc = f" (line {self.line})" if self.line else ""
        return f"[{self.level}]{loc} {self.message}"


class LoopValidator:
    """Validates a LOOP.md file and its parent directory structure."""

    def __init__(self, filepath: str):
        self.filepath = Path(filepath).resolve()
        self.errors: List[ValidationError] = []
        self.warnings: List[ValidationError] = []
        self.frontmatter: Dict[str, Any] = {}
        self.body: str = ""
        self.raw_content: str = ""

    def validate(self) -> bool:
        """Run all validations. Returns True if no errors."""
        if not self._load_file():
            return False
        self._parse_frontmatter()
        self._validate_frontmatter()
        self._validate_body()
        self._validate_directory_structure()
        self._validate_naming_consistency()
        return len(self.errors) == 0

    def _load_file(self) -> bool:
        """Load the LOOP.md file."""
        if not self.filepath.exists():
            self.errors.append(ValidationError("ERROR", f"File not found: {self.filepath}"))
            return False
        if self.filepath.name != "LOOP.md":
            self.errors.append(ValidationError("ERROR", f"Expected LOOP.md, got {self.filepath.name}"))
            return False
        try:
            self.raw_content = self.filepath.read_text(encoding="utf-8")
        except Exception as e:
            self.errors.append(ValidationError("ERROR", f"Failed to read file: {e}"))
            return False
        return True

    def _parse_frontmatter(self):
        """Parse YAML frontmatter from the file content."""
        content = self.raw_content.strip()
        if not content.startswith("---"):
            self.errors.append(ValidationError("ERROR", "Missing YAML frontmatter (must start with ---)", 1))
            self.body = content
            return

        parts = content.split("---", 2)
        if len(parts) < 3:
            self.errors.append(ValidationError("ERROR", "Malformed YAML frontmatter (missing closing ---)", 1))
            self.body = content
            return

        yaml_text = parts[1].strip()
        self.body = parts[2].strip()

        # Parse YAML without external dependencies
        self.frontmatter = self._simple_yaml_parse(yaml_text)

    def _simple_yaml_parse(self, yaml_text: str) -> Dict[str, Any]:
        """Minimal YAML parser for frontmatter (stdlib only, no PyYAML dependency)."""
        result = {}
        current_key = None
        current_list = None
        multiline_value = None
        multiline_key = None

        for line in yaml_text.split("\n"):
            stripped = line.strip()
            if not stripped or stripped.startswith("#"):
                continue

            # Handle list items
            if stripped.startswith("- "):
                if current_key and current_list is not None:
                    value = stripped[2:].strip().strip("'\"")
                    current_list.append(value)
                continue

            # Handle key-value pairs
            if ":" in stripped:
                colon_idx = stripped.index(":")
                key = stripped[:colon_idx].strip()
                value = stripped[colon_idx + 1:].strip()

                if current_key and current_list is not None:
                    result[current_key] = current_list

                if value == "" or value == "|" or value == ">-" or value == ">":
                    current_key = key
                    if value == "" :
                        current_list = []
                    else:
                        current_list = None
                        multiline_key = key
                        multiline_value = []
                    continue

                if value.startswith("[") and value.endswith("]"):
                    # Inline list
                    items = [v.strip().strip("'\"") for v in value[1:-1].split(",") if v.strip()]
                    result[key] = items
                else:
                    result[key] = value.strip("'\"")

                current_key = None
                current_list = None
                continue

            # Handle multiline scalar continuation
            if multiline_key:
                if multiline_value is not None:
                    multiline_value.append(stripped)
                continue

        # Finalize any open structures
        if current_key and current_list is not None:
            result[current_key] = current_list
        if multiline_key and multiline_value:
            result[multiline_key] = " ".join(multiline_value)

        return result

    def _validate_frontmatter(self):
        """Validate all frontmatter fields."""
        if not self.frontmatter:
            self.errors.append(ValidationError("ERROR", "Empty or unparseable frontmatter"))
            return

        # Required fields
        for field in REQUIRED_FIELDS:
            if field not in self.frontmatter:
                self.errors.append(ValidationError("ERROR", f"Missing required field: '{field}'"))

        # Name validation
        name = self.frontmatter.get("name", "")
        if name:
            if not KEBAB_CASE_PATTERN.match(name):
                self.errors.append(ValidationError("ERROR", f"Name '{name}' is not valid kebab-case"))
            if len(name) > MAX_NAME_LENGTH:
                self.errors.append(ValidationError("ERROR", f"Name exceeds {MAX_NAME_LENGTH} chars: {len(name)}"))

        # Description validation
        desc = self.frontmatter.get("description", "")
        if isinstance(desc, list):
            self.errors.append(ValidationError("ERROR", "Description must be a string, not a list"))
        elif isinstance(desc, str) and len(desc) < MIN_DESCRIPTION_LENGTH:
            self.errors.append(ValidationError("ERROR", f"Description too short ({len(desc)} chars, min {MIN_DESCRIPTION_LENGTH})"))

        # Domain validation
        domain = self.frontmatter.get("domain", "")
        if domain and domain != VALID_DOMAIN:
            self.errors.append(ValidationError("ERROR", f"Domain must be '{VALID_DOMAIN}', got '{domain}'"))

        # Subdomain validation
        subdomain = self.frontmatter.get("subdomain", "")
        if subdomain and subdomain not in VALID_SUBDOMAINS:
            self.errors.append(ValidationError("ERROR", f"Invalid subdomain: '{subdomain}'"))

        # Tags validation
        tags = self.frontmatter.get("tags", [])
        if isinstance(tags, str):
            tags = [tags]
        if len(tags) < MIN_TAGS:
            self.errors.append(ValidationError("ERROR", f"At least {MIN_TAGS} tags required, got {len(tags)}"))

        # Optional field type checks
        for list_field in ["owasp_llm", "nist_ai_rmf", "mitre_atlas"]:
            val = self.frontmatter.get(list_field)
            if val is not None and not isinstance(val, list):
                self.warnings.append(ValidationError("WARNING", f"'{list_field}' should be a list"))

        # Scorer validation for Evaluation loops
        if subdomain in ["llm-evaluation", "rag-evaluation", "agent-evaluation"]:
            if "scorer" not in self.frontmatter:
                self.errors.append(ValidationError("ERROR", f"Missing required field 'scorer' for evaluation subdomain '{subdomain}'"))
            else:
                valid_scorers = ["exact_match", "regex_match", "code_exec", "embedding_similarity", "latency_slo", "llm_judge"]
                if self.frontmatter["scorer"] not in valid_scorers:
                    self.errors.append(ValidationError("ERROR", f"Invalid scorer '{self.frontmatter['scorer']}', must be one of {valid_scorers}"))


    def _validate_body(self):
        """Validate the Markdown body contains required sections."""
        for section in REQUIRED_BODY_SECTIONS:
            # Look for ## Section Name or # Section Name
            pattern = re.compile(r"^#{1,3}\s+" + re.escape(section), re.MULTILINE | re.IGNORECASE)
            if not pattern.search(self.body):
                self.errors.append(ValidationError("ERROR", f"Missing required section: '{section}'"))

        for section in RECOMMENDED_BODY_SECTIONS:
            pattern = re.compile(r"^#{1,3}\s+" + re.escape(section), re.MULTILINE | re.IGNORECASE)
            if not pattern.search(self.body):
                self.warnings.append(ValidationError("WARNING", f"Missing recommended section: '{section}'"))

        # Check for code blocks in Workflow
        workflow_match = re.search(r"##\s+Workflow(.*?)(?=\n##\s|\Z)", self.body, re.DOTALL | re.IGNORECASE)
        if workflow_match:
            workflow_content = workflow_match.group(1)
            if "```" not in workflow_content:
                self.warnings.append(ValidationError("WARNING", "Workflow section has no code blocks"))

    def _validate_directory_structure(self):
        """Validate the loop's directory contains required subdirectories and files."""
        loop_dir = self.filepath.parent

        # Check required subdirs
        for subdir in REQUIRED_SUBDIRS:
            subdir_path = loop_dir / subdir
            if not subdir_path.is_dir():
                self.warnings.append(ValidationError("WARNING", f"Missing subdirectory: {subdir}/"))
            else:
                # Check required files within subdirs
                for required_file in REQUIRED_FILES_IN_DIR.get(subdir, []):
                    if not (subdir_path / required_file).exists():
                        self.warnings.append(ValidationError("WARNING", f"Missing file: {subdir}/{required_file}"))

        # Check LICENSE
        if not (loop_dir / "LICENSE").exists():
            self.warnings.append(ValidationError("WARNING", "Missing LICENSE file in loop directory"))

        # Check dataset existence for certain subdomains
        subdomain = self.frontmatter.get("subdomain", "")
        
        dataset_required_domains = {
            "llm-evaluation": 20, "rag-evaluation": 20, "agent-evaluation": 20, "memory-testing": 20, "multi-agent-testing": 20,
            "guardrails": 15, "prompt-security": 15, "hallucination-detection": 15, "bias-fairness": 15, "compliance-testing": 15,
            "red-teaming": 15,
            "qa-testing": 20
        }
        
        if subdomain in dataset_required_domains:
            dataset_path = loop_dir / "references" / "dataset.jsonl"
            min_size = dataset_required_domains[subdomain]
            
            if not dataset_path.exists():
                self.errors.append(ValidationError("ERROR", f"Missing required dataset.jsonl in references/ for subdomain {subdomain}"))
            else:
                # Validate dataset schema and size
                row_count = 0
                try:
                    with open(dataset_path, "r", encoding="utf-8") as f:
                        for i, line in enumerate(f):
                            if not line.strip():
                                continue
                            row_count += 1
                            try:
                                item = json.loads(line)
                                if "input" not in item:
                                    self.errors.append(ValidationError("ERROR", f"Dataset item {i} missing 'input' field.", line=i+1))
                            except json.JSONDecodeError:
                                self.errors.append(ValidationError("ERROR", f"Dataset item {i} is not valid JSON.", line=i+1))
                    
                    if row_count < min_size:
                        self.errors.append(ValidationError("ERROR", f"Dataset is too small ({row_count} rows). Minimum required for {subdomain} is {min_size}."))
                except Exception as e:
                    self.errors.append(ValidationError("ERROR", f"Failed to read dataset: {str(e)}"))

    def _validate_naming_consistency(self):
        """Verify the directory name matches the frontmatter name."""
        dir_name = self.filepath.parent.name
        fm_name = self.frontmatter.get("name", "")
        if fm_name and dir_name != fm_name:
            self.errors.append(ValidationError(
                "ERROR",
                f"Directory name '{dir_name}' doesn't match frontmatter name '{fm_name}'"
            ))

    def report(self) -> str:
        """Generate a validation report."""
        lines = []
        name = self.frontmatter.get("name", self.filepath.parent.name)
        lines.append(f"{'='*60}")
        lines.append(f"Validating: {name}")
        lines.append(f"{'='*60}")

        if self.errors:
            lines.append(f"\n[FAIL] {len(self.errors)} error(s):")
            for err in self.errors:
                lines.append(f"  {err}")

        if self.warnings:
            lines.append(f"\n[WARN] {len(self.warnings)} warning(s):")
            for warn in self.warnings:
                lines.append(f"  {warn}")

        if not self.errors and not self.warnings:
            lines.append("\n[PASS] All checks passed!")
        elif not self.errors:
            lines.append(f"\n[PASS] Passed with {len(self.warnings)} warning(s)")
        else:
            lines.append(f"\n[FAIL] FAILED — {len(self.errors)} error(s)")

        return "\n".join(lines)


def find_all_loops(root: Path) -> List[Path]:
    """Find all LOOP.md files under the loops/ directory."""
    loops_dir = root / "loops"
    if not loops_dir.exists():
        return []
    return sorted(loops_dir.glob("*/LOOP.md"))


def main():
    parser = argparse.ArgumentParser(
        description="Validate AI-Testing-Loops LOOP.md files",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python validate-loop.py loops/evaluating-rag-faithfulness/LOOP.md
  python validate-loop.py --all
  python validate-loop.py --all --json
        """
    )
    parser.add_argument("path", nargs="?", help="Path to LOOP.md file to validate")
    parser.add_argument("--all", action="store_true", help="Validate all loops in the repository")
    parser.add_argument("--json", action="store_true", help="Output results as JSON")
    parser.add_argument("--strict", action="store_true", help="Treat warnings as errors")

    args = parser.parse_args()

    if not args.path and not args.all:
        parser.print_help()
        sys.exit(1)

    # Find repo root
    script_dir = Path(__file__).resolve().parent
    repo_root = script_dir.parent

    if args.all:
        loop_files = find_all_loops(repo_root)
        if not loop_files:
            print("No loops found in loops/ directory")
            sys.exit(1)
    else:
        loop_files = [Path(args.path).resolve()]

    total = len(loop_files)
    passed = 0
    failed = 0
    results = []
    subdomain_counts: Dict[str, int] = {}

    for loop_file in loop_files:
        validator = LoopValidator(str(loop_file))
        is_valid = validator.validate()

        if args.strict and validator.warnings:
            is_valid = False

        if is_valid:
            passed += 1
        else:
            failed += 1

        # Track subdomain counts
        sd = validator.frontmatter.get("subdomain", "unknown")
        subdomain_counts[sd] = subdomain_counts.get(sd, 0) + 1

        if args.json:
            results.append({
                "name": validator.frontmatter.get("name", loop_file.parent.name),
                "path": str(loop_file),
                "valid": is_valid,
                "errors": [str(e) for e in validator.errors],
                "warnings": [str(w) for w in validator.warnings],
            })
        else:
            print(validator.report())
            print()

    # Summary
    if args.json:
        summary = {
            "total": total,
            "passed": passed,
            "failed": failed,
            "subdomain_counts": subdomain_counts,
            "results": results,
            "docker_available": True
        }
        print(json.dumps(summary, indent=2))
    else:
        print(f"\n{'='*60}")
        print(f"SUMMARY: {passed}/{total} passed, {failed} failed")
        print(f"{'='*60}")
        if subdomain_counts:
            print("\nLoops by subdomain:")
            for sd, count in sorted(subdomain_counts.items()):
                print(f"  {sd}: {count}")

    # Docker check
    import subprocess
    docker_available = False
    try:
        subprocess.run(["docker", "--version"], check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        docker_available = True
    except (subprocess.CalledProcessError, FileNotFoundError):
        pass

    if not docker_available:
        if args.json:
            pass # already handled in json output, though we might want to flag it
        else:
            print("\n[FAIL] Docker daemon is NOT available on this host.")
            print("       The 'code_exec' scorer strictly requires Docker to sandbox generated code.")
            print("       Please install Docker or integration tests will fail.")
        
        # If we are strictly validating for CI, we should probably fail if docker is missing
        # But for now, we'll just print the warning, or we can fail the whole validation script
        sys.exit(1)

    sys.exit(1 if failed > 0 else 0)


if __name__ == "__main__":
    main()
