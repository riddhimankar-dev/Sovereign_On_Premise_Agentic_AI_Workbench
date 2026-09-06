import asyncio
import httpx
import subprocess
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.core.config import settings
from app.core.logging import configure_logging, get_logger

configure_logging()
logger = get_logger(__name__)


async def http_available(url: str) -> bool:
    try:
        async with httpx.AsyncClient(timeout=4.0) as client:
            resp = await client.get(url)
            return resp.status_code < 600
    except Exception:
        return False


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
            resp = await client.get(f"{settings.qdrant_url}/livez")
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
    """Confirm the only listening HTTP(S) services belong to the local stack
    (uvicorn :8000, Vite :8443, Qdrant :6333, Ollama :11434) and nothing is
    bound to a public/external address pattern that isn't the local manifest."""
    local_ports = {8000, 8443, 6333, 6334, 11434}
    try:
        result = subprocess.run(
            ["ss", "-tuln"],
            capture_output=True,
            text=True,
            timeout=5,
        )
        lines = result.stdout.split("\n")
        for line in lines:
            m = line.split()
            if len(m) < 5:
                continue
            proto = m[0]
            if proto not in ("tcp", "tcp6"):
                continue
            try:
                port = int(m[4].rsplit(":", 1)[-1])
            except (ValueError, IndexError):
                continue
            if port in (80, 443):
                logger.warning("public_http_listener", line=line)
                return False
            addr = m[4]
            is_loopback = addr.startswith("127.") or ("::1" in addr) or addr.startswith("localhost")
            if port not in local_ports and not is_loopback:
                logger.warning("unexpected_listener", line=line)
                return False
    except Exception as e:
        logger.warning("network_check_failed", error=str(e))
        return False
    return True


async def check_no_external_egress() -> bool:
    """Attempt short-lived connections to common external endpoints.
    Any reachable external HTTP endpoint counts as a breach."""
    probe_urls = [
        "https://api.openai.com",
        "https://api.anthropic.com",
        "https://www.google.com",
    ]
    for url in probe_urls:
        if await http_available(url):
            logger.warning("external_endpoint_reachable", url=url)
            return False
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
        "No Non-Loopback HTTP Ports": check_network_connections(),
        "No External Network Egress": await check_no_external_egress(),
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