import { useState, useRef } from "react";
import Editor from "@monaco-editor/react";

const DEFAULT_CODE = `#include <iostream>
int main() {
  std::cout << "Hello";
}`;

function App() {
  const editorRef = useRef(null);
  const [output, setOutput] = useState(null);
  const [loading, setLoading] = useState(false);

  function handleEditorMount(editor) {
    editorRef.current = editor;
  }

  async function handleRun() {
    const sourceCode = editorRef.current.getValue();
    setLoading(true);
    setOutput(null);

    try {
      const response = await fetch("http://localhost:8000/api/code-execution/run/", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ source_code: sourceCode }),
      });
      const data = await response.json();
      setOutput(data);
    } catch (error) {
      setOutput({ stderr: `Request failed: ${error.message}` });
    } finally {
      setLoading(false);
    }
  }

  return (
    <div style={{ padding: "20px" }}>
      <Editor
        height="400px"
        defaultLanguage="cpp"
        defaultValue={DEFAULT_CODE}
        onMount={handleEditorMount}
      />

      <button onClick={handleRun} disabled={loading} style={{ marginTop: "10px" }}>
        {loading ? "Running..." : "Run"}
      </button>

      {output && (
        <pre
          style={{
            background: "#1e1e1e",
            color: "#d4d4d4",
            padding: "10px",
            marginTop: "10px",
            whiteSpace: "pre-wrap",
          }}
        >
          {output.stdout && `${output.stdout}\n`}
          {output.stderr && `stderr:\n${output.stderr}\n`}
          {output.compile_stderr && `compile error:\n${output.compile_stderr}\n`}
        </pre>
      )}
    </div>
  );
}

export default App;
