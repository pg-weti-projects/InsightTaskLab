from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status

from .judge0 import Judge0Client, Judge0Error


class ExecuteCodeView(APIView):
    def post(self, request):
        code = request.data.get("code", "")
        stdin = request.data.get("stdin", "")

        if not code.strip():
            return Response(
                {"error": "No code C++"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        client = Judge0Client()

        try:
            submission = client.submit(
                source_code=code,
                stdin=stdin,
                language_id=54,
            )

            return Response(
                {
                    "token": submission["token"],
                    "status": "queued",
                },
                status=status.HTTP_202_ACCEPTED,
            )

        except Judge0Error as e:
            return Response(
                {"error": str(e)},
                status=status.HTTP_502_BAD_GATEWAY,
            )

        except Exception as e:
            return Response(
                {"error": f"Bad gateway Judge0: {str(e)}"},
                status=status.HTTP_502_BAD_GATEWAY,
            )


class ExecutionResultView(APIView):
    def get(self, request, token):
        client = Judge0Client()

        try:
            data = client.get_submission(token)

            judge0_status = data.get("status") or {}
            status_id = judge0_status.get("id")
            status_description = judge0_status.get(
                "description",
                "Unknown",
            )

            # Judge0:
            # 1 = In Queue
            # 2 = Processing
            if status_id in (1, 2):
                return Response(
                    {
                        "token": token,
                        "status": "processing",
                        "status_id": status_id,
                        "status_description": status_description,
                    }
                )

            stdout = data.get("stdout") or ""
            stderr = data.get("stderr") or ""
            compile_output = data.get("compile_output") or ""

            if status_description == "Accepted":
                output = stdout
            else:
                output = compile_output or stderr or stdout or status_description

            return Response(
                {
                    "token": token,
                    "status": status_description,
                    "status_id": status_id,
                    "output": output,
                    "stdout": stdout,
                    "stderr": stderr,
                    "compile_output": compile_output,
                    "time": data.get("time"),
                    "memory": data.get("memory"),
                    "exit_code": data.get("exit_code"),
                }
            )

        except Exception as e:
            return Response(
                {"error": f"Bad gateway Judge0: {str(e)}"},
                status=status.HTTP_502_BAD_GATEWAY,
            )
