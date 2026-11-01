import hashlib
import logging

import httpx
from django.core.cache import cache
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.code_execution.client import ExecutionClient

logger = logging.getLogger(__name__)

CACHE_TTL_SECONDS = 10 * 60


def cache_key(source_code: str, language: str, version: str) -> str:
    digest = hashlib.sha256(
        f"{language}\0{version}\0{source_code}".encode()
    ).hexdigest()
    return f"code_execution:{digest}"


def is_cacheable(result) -> bool:
    """Cache real outcomes only, not runs killed because the server was busy."""
    return result.exit_code is not None or bool(result.compile_stderr)


class RunCodeView(APIView):
    """POST source_code (+ optional language/version) -> execution result."""

    def post(self, request):
        source_code = request.data.get("source_code")
        language = request.data.get("language", "c++")
        version = request.data.get("version", "10.2.0")

        if not isinstance(source_code, str) or not source_code.strip():
            return Response(
                {"error": "Field 'source_code' is required and must not be empty."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        key = cache_key(source_code, language, version)
        cached = cache.get(key)
        if cached is not None:
            return Response({**cached, "cached": True})

        client = ExecutionClient()
        try:
            result = client.run(source=source_code, language=language, version=version)
        except httpx.TimeoutException:
            logger.warning("Piston timed out after %ss", client.timeout)
            return Response(
                {"error": "The code execution server is busy. Please try again."},
                status=status.HTTP_504_GATEWAY_TIMEOUT,
            )
        except httpx.HTTPError as exc:
            logger.error("Piston request failed: %s", exc)
            return Response(
                {"error": "The code execution server is unavailable."},
                status=status.HTTP_502_BAD_GATEWAY,
            )

        data = {
            "stdout": result.run_stdout,
            "stderr": result.run_stderr,
            "compile_stdout": result.compile_stdout,
            "compile_stderr": result.compile_stderr,
            "exit_code": result.exit_code,
            "cpu_time_ms": result.cpu_time_ms,
            "wall_time_ms": result.wall_time_ms,
            "memory_bytes": result.memory_bytes,
        }
        if is_cacheable(result):
            cache.set(key, data, CACHE_TTL_SECONDS)

        return Response({**data, "cached": False})
