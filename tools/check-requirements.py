#!/usr/bin/env python3
"""Validates loop requirements (Docker, Judge Model) pre-flight."""
import argparse
import os
import shutil
from pathlib import Path
from rich.console import Console
from rich.table import Table

console = Console()

def check_docker():
    return shutil.which("docker") is not None

def check_judge_model():
    # If OPENAI_API_KEY is in env, judge model is available.
    if os.environ.get("OPENAI_API_KEY"):
        return True
    
    # Or if there's a valid config.yaml with 'judge:' section
    config_path = Path("config.yaml")
    if config_path.exists():
        import yaml
        with open(config_path, "r", encoding="utf-8") as f:
            config = yaml.safe_load(f) or {}
            if "judge" in config:
                return True
                
    return False

def parse_requires(loop_dir: Path):
    loop_md = loop_dir / "LOOP.md"
    if not loop_md.exists():
        return []
        
    with open(loop_md, "r", encoding="utf-8") as f:
        content = f.read()
        
    if "---" not in content:
        return []
        
    fm = content.split("---", 2)[1]
    
    requires = []
    import yaml
    try:
        data = yaml.safe_load(fm) or {}
        requires = data.get("requires", [])
    except:
        pass
        
    return requires

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--all", action="store_true", help="Check all loops")
    args = parser.parse_args()
    
    if not args.all:
        print("Please provide --all")
        return
        
    has_docker = check_docker()
    has_judge = check_judge_model()
    
    table = Table(title="Requirement Pre-flight Check")
    table.add_column("Loop", style="cyan")
    table.add_column("Requires", style="magenta")
    table.add_column("Status", justify="center")
    
    loops_dir = Path("loops")
    ready_count = 0
    blocked_count = 0
    
    for loop_dir in sorted(loops_dir.iterdir()):
        if not loop_dir.is_dir():
            continue
            
        requires = parse_requires(loop_dir)
        missing = []
        
        for req in requires:
            if req == "docker" and not has_docker:
                missing.append("docker")
            elif req == "judge_model" and not has_judge:
                missing.append("judge_model")
                
        req_str = ", ".join(requires) if requires else "None"
        
        if missing:
            status = f"[red]BLOCKED (Missing: {', '.join(missing)})[/]"
            blocked_count += 1
        else:
            status = "[green]READY[/]"
            ready_count += 1
            
        table.add_row(loop_dir.name, req_str, status)
        
    console.print(table)
    console.print(f"\n[bold green]Ready:[/] {ready_count} | [bold red]Blocked:[/] {blocked_count}")
    
    if blocked_count > 0:
        console.print("\n[yellow]To fix blocked loops:[/]")
        if not has_docker:
            console.print(" - Install Docker and ensure the daemon is running.")
        if not has_judge:
            console.print(" - Set OPENAI_API_KEY environment variable OR provide a config.yaml with a 'judge:' section.")

if __name__ == "__main__":
    main()
