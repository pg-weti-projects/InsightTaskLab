# code execution

Thin Django app that forwards source code from the frontend to a
self-hosted [Piston](https://github.com/engineer-man/piston) instance for
compilation/execution, and returns the result.


## Request flow (target / production shape)

```
User clicks "Run" in the Monaco editor (frontend)
        ↓
Frontend: POST /api/code-execution/run/  {"source_code": "..."}
        ↓
views.py       → RunCodeView.post()            ( endpoint)
        ↓
client.py      → ExecutionClient.run()          (talks to Piston over HTTP)
        ↓               calls PISTON_URL/api/v2/execute
        ↓
Piston container → compiles + runs the code in an isolated sandbox
        ↓
client.py      ← raw JSON response from Piston
        ↓
schemas.py     → ExecutionResult                (normalizes compile/run fields)
        ↓
views.py       → returns a clean JSON response to the frontend
        ↓
Frontend displays stdout / stderr / exit code
```
