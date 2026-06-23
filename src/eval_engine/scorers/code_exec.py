from .base import BaseScorer, ScoreResult
from typing import Any
import asyncio
import tempfile
import os
import re

class CodeExecScorer(BaseScorer):
    """Executes generated code in a secure, isolated Docker container."""
    
    def __init__(self, image: str = "python:3.11-slim@sha256:eb8df54df11d88a10fc2b9340fca8e59ec2cc97732d84dbaf51efaeef29471f4", timeout: int = 10):
        self.image = image
        self.timeout = timeout
        
    async def score(self, expected: Any, actual: str, **kwargs) -> ScoreResult:
        # expected can be a test harness (e.g. asserts) to append to the generated code.
        # actual is the LLM generated code.
        # We extract Python code blocks from actual if they exist.
        code = self._extract_code(actual)
        
        # Append the test harness if provided
        if expected:
            code += "\n\n" + str(expected)
            
        # Write to a temporary file to mount into docker
        with tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False) as f:
            f.write(code)
            temp_path = f.name
            
        try:
            # Docker run command with strict security isolation
            cmd = [
                "docker", "run", "--rm",
                "--network=none",           # No internet access
                "--memory=128m",            # 128 MB RAM limit
                "--cpus=0.5",               # Half a core
                "--read-only",              # Read-only root filesystem
                "-v", f"{temp_path}:/app/script.py:ro", # Mount script read-only
                self.image,
                "python", "/app/script.py"
            ]
            
            try:
                process = await asyncio.create_subprocess_exec(
                    *cmd,
                    stdout=asyncio.subprocess.PIPE,
                    stderr=asyncio.subprocess.PIPE
                )
            except FileNotFoundError:
                return ScoreResult(
                    score=0.0,
                    passed=False,
                    reasoning="Docker is not installed or not on PATH. The code_exec scorer requires Docker — install it and retry."
                )
            
            try:
                stdout, stderr = await asyncio.wait_for(process.communicate(), timeout=self.timeout)
                exit_code = process.returncode
                
                out_str = stdout.decode('utf-8')[:500]
                err_str = stderr.decode('utf-8')[:500]
                
                # Check for Docker daemon errors
                if exit_code != 0 and "Cannot connect to the Docker daemon" in err_str:
                    return ScoreResult(
                        score=0.0,
                        passed=False,
                        reasoning="Docker is installed but the daemon is not running. Please start Docker and retry."
                    )
                
                passed = (exit_code == 0)
                reasoning = "Execution passed." if passed else f"Execution failed (Exit Code {exit_code})."
                
                if err_str:
                    reasoning += f" Stderr: {err_str}"
                elif out_str and not passed:
                    reasoning += f" Stdout: {out_str}"
                    
                return ScoreResult(
                    score=1.0 if passed else 0.0,
                    passed=passed,
                    reasoning=reasoning
                )
                
            except asyncio.TimeoutError:
                process.kill()
                return ScoreResult(
                    score=0.0,
                    passed=False,
                    reasoning=f"Code execution timed out after {self.timeout} seconds."
                )
        finally:
            if os.path.exists(temp_path):
                os.remove(temp_path)
                
    def _extract_code(self, text: str) -> str:
        """Extracts code from markdown code blocks if present."""
        match = re.search(r"```(?:python)?\n(.*?)\n```", text, re.DOTALL)
        if match:
            return match.group(1)
        return text
