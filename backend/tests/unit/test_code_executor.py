import pytest

from app.tools.code_executor import CodeExecutorTool


@pytest.mark.asyncio
async def test_executor_runs_simple_code():
    tool = CodeExecutorTool()
    result = await tool.execute({"code": "print(42 - 40)"}, {})
    assert result.success is True
    assert result.data["return_code"] == 0
    assert "2" in result.data["stdout"]


@pytest.mark.asyncio
async def test_executor_timeout():
    import asyncio
    tool = CodeExecutorTool()
    result = await tool.execute({"code": "import time; time.sleep(3)", "timeout": 1}, {})
    assert result.success is False
    assert "timed out" in (result.error or "").lower()


@pytest.mark.asyncio
async def test_executor_reports_stderr():
    tool = CodeExecutorTool()
    result = await tool.execute({"code": "import sys; print('oops', file=sys.stderr)"}, {})
    assert result.success is True
    assert "oops" in result.data["stderr"]


@pytest.mark.asyncio
async def test_executor_empty_code_fails():
    tool = CodeExecutorTool()
    result = await tool.execute({"code": ""}, {})
    assert result.success is False


@pytest.mark.asyncio
async def test_executor_writes_passed_files():
    tool = CodeExecutorTool()
    result = await tool.execute(
        {"code": "import os; print(os.path.exists('data.txt'))", "files": {"data.txt": "hello"}},
        {},
    )
    assert result.success is True
    assert "True" in result.data["stdout"]
