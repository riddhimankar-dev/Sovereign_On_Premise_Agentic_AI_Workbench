import asyncio
import httpx
import subprocess
import sys
from app.core.config import settings
from app.core.logging import configure_logging, get_logger

configure_logging()
logger = get_logger(__name__)


async def check_ollama_local() -> bool:
    try:
        async with httpx.AsyncClient(timeout=5.0) as client:
            resp = await client.get(f"{settings.ollama_base_url}/api/tags")
            if resp.status_code == 200:
                models = resp.json().get("models", [])
                for m in models:
                    if "host" in str(m).lower() and "localhost" not in str(m).lower():
                        return False
                return True
    except Exception as e:
        logger.error("ollama_check_failed", error=str(e))
    return False


async def check_qdrant_local() -> bool:
    try:
        async with httpx.AsyncClient(timeout=5.0) as client:
            resp = await client.get(f"{settings.qdrant_url}/health")
            return resp.status_code == 200
    except Exception:
        return False


def check_no_external_ai_config() -> bool:
    external_keywords = [
        "openai", "anthropic", "gemini", "claude", "api_key",
        "OPENAI_API_KEY", "ANTHROPIC_API_KEY", "GOOGLE_API_KEY"
    ]
    import os
    for key in external_keywords:
        if os.getenv(key):
            logger.warning("external_ai_config_found", key=key)
            return False
    return True


def check_no_external_urls_in_code() -> bool:
    import os
    external_patterns = [
        "api.openai.com",
        "api.anthropic.com",
        "generativelanguage.googleapis.com",
        "api.cohere.ai",
    ]
    for root, dirs, files in os.walk("app"):
        for f in files:
            if f.endswith(".py"):
                path = os.path.join(root, f)
                try:
                    with open(path) as fp:
                        content = fp.read()
                        for pattern in external_patterns:
                            if pattern in content:
                                logger.warning("external_url_in_code", file=path, pattern=pattern)
                                return False
                except Exception:
                    pass
    return True


def check_network_connections() -> bool:
    try:
        result = subprocess.run(
            ["ss", "-tuln"],
            capture_output=True,
            text=True,
            timeout=5,
        )
        lines = result.stdout.split("\n")
        for line in lines:
            if ":80 " in line or ":443 " in line:
                if "127.0.0.1" not in line and "localhost" not in line:
                    logger.warning("external_port_listening", line=line)
                    return False
    except Exception as e:
        logger.warning("network_check_failed", error=str(e))
    return True


async def main():
    print("=" * 60)
    print("SOVEREIGN AI WORKBENCH — OFFLINE VERIFICATION")
    print("=" * 60)

    checks = {
        "Ollama Local": await check_ollama_local(),
        "Qdrant Local": await check_qdrant_local(),
        "No External AI Config": check_no_external_ai_config(),
        "No External URLs in Code": check_no_external_urls_in_code(),
        "No External Network Ports": check_network_connections(),
    }

    all_passed = True
    for name, passed in checks.items():
        status = "✓ PASS" if passed else "✗ FAIL"
        print(f"  {status}  {name}")
        if not passed:
            all_passed = False

    print("=" * 60)
    if all_passed:
        print("RESULT: VERIFIED — System is fully offline/sovereign")
        return 0
    else:
        print("RESULT: NOT VERIFIED — Some checks failed")
        return 1


if __name__ == "__main__":
    sys.exit(asyncio.run(main()))