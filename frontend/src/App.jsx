import { useState } from 'react'
import Editor from '@monaco-editor/react'
import './App.css'

function App() {
  const [code, setCode] = useState(
    '#include <iostream>\n\nint main() {\n    std::cout << "Hello from Monaco!";\n    return 0;\n}'
  )

  const [stdin, setStdin] = useState('')
  const [output, setOutput] = useState('')
  const [status, setStatus] = useState('idle')

  const sleep = (ms) => {
    return new Promise((resolve) => setTimeout(resolve, ms))
  }

  const runCode = async () => {
    setStatus('running')
    setOutput('Uruchamianie...')

    try {
      const response = await fetch('/api/code/run/', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          code,
          stdin,
        }),
      })

      const data = await response.json()

      if (!response.ok) {
        throw new Error(data.error || 'Nie udało się wysłać kodu')
      }

      const token = data.token

      while (true) {
        await sleep(500)

        const resultResponse = await fetch(
          `/api/code/run/${encodeURIComponent(token)}/`
        )

        const result = await resultResponse.json()

        if (!resultResponse.ok) {
          throw new Error(
            result.error || 'Nie udało się pobrać wyniku'
          )
        }

        if (result.status === 'processing') {
          setOutput('Uruchamianie...')
          continue
        }

        setStatus('finished')

        setOutput(
          result.output ||
            'Program nie zwrócił żadnego wyniku.'
        )

        break
      }
    } catch (error) {
      setStatus('error')
      setOutput(error.message)
    }
  }

  return (
    <div className="app">
      <header className="header">
        <h1>InsightTaskLab</h1>

        <button onClick={runCode}>
          Run
        </button>
      </header>

      <main className="main">
        <section className="editor-section">
          <Editor
            height="500px"
            defaultLanguage="cpp"
            theme="vs-dark"
            value={code}
            onChange={(value) => setCode(value ?? '')}
            options={{
              minimap: {
                enabled: false,
              },
              fontSize: 15,
              automaticLayout: true,
            }}
          />
        </section>

        <section className="stdin-section">
          <h2>Input</h2>

          <textarea
            value={stdin}
            onChange={(event) => setStdin(event.target.value)}
            placeholder="Dane wejściowe programu..."
          />
        </section>

        <section className="output-section">
          <h2>Output</h2>

          <pre>{output}</pre>
        </section>
      </main>
    </div>
  )
}

export default App
