"""Client for the self-hosted Piston instance.

PISTON_URL comes from the environment so the same code works unchanged
locally (http://localhost:2000) and on a server where Piston runs as a
sibling container (http://piston:2000) — see docker-compose.yaml.
"""

import os

import httpx

from apps.code_execution.schemas import ExecutionResult

PISTON_URL = os.environ.get("PISTON_URL", "http://localhost:2000")


class ExecutionClient:
    """Thin wrapper around the Piston /execute endpoint."""

    def __init__(self, base_url: str = PISTON_URL, timeout: float = 15.0) -> None:
        self.base_url = base_url.rstrip("/")
        self.timeout = timeout

    def run(
        self,
        source: str,
        language: str = "c++",
        version: str = "10.2.0",
    ) -> ExecutionResult:
        response = httpx.post(
            f"{self.base_url}/api/v2/execute",
            json={
                "language": language,
                "version": version,
                "files": [{"content": source}],
            },
            timeout=self.timeout,
        )
        response.raise_for_status()
        return ExecutionResult.from_piston_response(response.json())
