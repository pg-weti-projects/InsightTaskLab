from rest_framework.response import Response
from rest_framework.views import APIView

from apps.code_execution.client import ExecutionClient


class RunCodeView(APIView):
    """POST source_code (+ optional language/version) -> execution result."""

    def post(self, request):
        source_code = request.data.get("source_code", "")
        language = request.data.get("language", "c++")
        version = request.data.get("version", "10.2.0")

        client = ExecutionClient()
        result = client.run(source=source_code, language=language, version=version)

        return Response(
            {
                "stdout": result.run_stdout,
                "stderr": result.run_stderr,
                "compile_stdout": result.compile_stdout,
                "compile_stderr": result.compile_stderr,
                "exit_code": result.exit_code,
                "cpu_time_ms": result.cpu_time_ms,
                "wall_time_ms": result.wall_time_ms,
                "memory_bytes": result.memory_bytes,
            }
        )
