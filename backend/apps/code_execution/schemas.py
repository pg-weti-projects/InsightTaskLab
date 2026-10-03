from dataclasses import dataclass


@dataclass
class ExecutionResult:
    compile_stdout: str
    compile_stderr: str
    run_stdout: str
    run_stderr: str
    exit_code: int | None
    cpu_time_ms: float | None
    wall_time_ms: float | None
    memory_bytes: int | None

    @classmethod
    def from_piston_response(cls, data: dict) -> "ExecutionResult":
        compile_stage = data.get("compile") or {}
        run_stage = data.get("run") or {}
        return cls(
            compile_stdout=compile_stage.get("stdout", ""),
            compile_stderr=compile_stage.get("stderr", ""),
            run_stdout=run_stage.get("stdout", ""),
            run_stderr=run_stage.get("stderr", ""),
            exit_code=run_stage.get("code"),
            cpu_time_ms=run_stage.get("cpu_time"),
            wall_time_ms=run_stage.get("wall_time"),
            memory_bytes=run_stage.get("memory"),
        )
