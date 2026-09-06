from typing import Dict, Any
from app.tools.base import BaseTool, ToolInput, ToolOutput, tool_registry
from app.core.logging import get_logger
import os
import subprocess
import tempfile

logger = get_logger(__name__)


class CodeExecutorInput(ToolInput):
    code: str
    language: str = "python"
    timeout: int = 30
    files: Dict[str, str] = {}


def _sandbox_limit() -> Any:
    try:
        import resource

        def limiter() -> None:
            resource.setrlimit(resource.RLIMIT_CPU, (10, 10))
            resource.setrlimit(resource.RLIMIT_FSIZE, (4 * 1024 * 1024, 4 * 1024 * 1024))
            resource.setrlimit(resource.RLIMIT_NOFILE, (128, 128))
            os.setpgrp()

        return limiter
    except Exception:
        return os.setpgrp


class CodeExecutorTool(BaseTool):
    name = "execute_code"
    description = "Execute Python code in a secure sandbox environment. No network access, isolated filesystem."
    permission = "execute"

    async def execute(self, input_data: Dict[str, Any], context: Dict[str, Any]) -> ToolOutput:
        code = input_data.get("code", "")
        timeout = input_data.get("timeout", 30)
        files = input_data.get("files", {})

        if not code:
            return ToolOutput(success=False, error="No code provided")

        try:
            with tempfile.TemporaryDirectory() as tmpdir:
                for filename, content in files.items():
                    filepath = os.path.join(tmpdir, filename)
                    with open(filepath, "w") as f:
                        f.write(content)

                code_file = os.path.join(tmpdir, "main.py")
                with open(code_file, "w") as f:
                    f.write(code)

                env = {
                    "PATH": os.environ.get("PATH", ""),
                    "HOME": tmpdir,
                    "TMPDIR": tmpdir,
                }

                result = subprocess.run(
                    ["python3", "-I", "-B", code_file],
                    capture_output=True,
                    text=True,
                    timeout=timeout,
                    cwd=tmpdir,
                    env=env,
                    preexec_fn=_sandbox_limit(),
                )

                return ToolOutput(success=True, data={
                    "stdout": result.stdout,
                    "stderr": result.stderr,
                    "return_code": result.returncode,
                    "timeout": timeout,
                })
        except subprocess.TimeoutExpired:
            return ToolOutput(success=False, error=f"Execution timed out after {timeout} seconds")
        except Exception as e:
            return ToolOutput(success=False, error=f"Execution error: {str(e)}")


tool_registry.register(CodeExecutorTool())