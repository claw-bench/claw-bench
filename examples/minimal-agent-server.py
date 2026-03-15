#!/usr/bin/env python3
"""Minimal Claw Agent Protocol server (~40 lines).

This is a bare-bones example that shows how to implement the Agent Protocol.
Replace the `handle_task` function with your real agent logic.

Usage:
    pip install fastapi uvicorn openai
    python minimal-agent-server.py

Then run claw-bench against it:
    claw-bench run --agent-url http://localhost:3000 --agent-name "MinimalAgent" -t file-001 -n 1
"""

import os
import subprocess
from fastapi import FastAPI
from pydantic import BaseModel

app = FastAPI()


class TaskRequest(BaseModel):
    task_id: str
    instruction: str
    workspace: str
    timeout_seconds: int = 300


class TaskResponse(BaseModel):
    status: str  # "completed", "failed", "timeout"
    output: str
    tokens_used: int = 0
    duration_seconds: float = 0


@app.get("/v1/health")
def health():
    return {"name": "MinimalAgent", "status": "ready"}


@app.post("/v1/task", response_model=TaskResponse)
def handle_task(req: TaskRequest):
    """Replace this with your real agent logic.

    This example uses OpenAI's API to process the task.
    Your real Claw product would use its own agent runtime.
    """
    try:
        from openai import OpenAI

        client = OpenAI(
            base_url=os.environ.get("OPENAI_COMPAT_BASE_URL", "https://api.openai.com/v1"),
            api_key=os.environ.get("OPENAI_COMPAT_API_KEY", ""),
        )

        response = client.chat.completions.create(
            model=os.environ.get("MODEL", "gpt-4.1-mini"),
            messages=[
                {"role": "system", "content": "You are a helpful AI agent. Complete the task. Write any output files to the workspace directory."},
                {"role": "user", "content": f"Workspace: {req.workspace}\n\n{req.instruction}"},
            ],
            max_tokens=4096,
        )

        output = response.choices[0].message.content or ""
        tokens = response.usage.total_tokens if response.usage else 0

        # If the LLM generated shell commands, try to execute them
        if "```bash" in output or "```sh" in output:
            import re
            for block in re.findall(r"```(?:bash|sh)\n(.*?)```", output, re.DOTALL):
                try:
                    subprocess.run(["bash", "-c", block], cwd=req.workspace, timeout=30, capture_output=True)
                except Exception:
                    pass

        return TaskResponse(status="completed", output=output, tokens_used=tokens)

    except Exception as e:
        return TaskResponse(status="failed", output=f"Error: {e}")


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=3000)
