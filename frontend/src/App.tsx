import { useMemo, useState, type ChangeEvent } from 'react';
import { apiBaseUrl, askChat, ingestPdf, type ChatResponse, type IngestResponse } from './api';

const magicText = 'Upload PDFs, ingest knowledge, and ask questions with a clean RAG interface.';

function App() {
  const [theme, setTheme] = useState<'light' | 'dark'>('light');
  const [file, setFile] = useState<File | null>(null);
  const [status, setStatus] = useState<string>('Ready to ingest or query.');
  const [loading, setLoading] = useState(false);
  const [ingestResult, setIngestResult] = useState<IngestResponse | null>(null);
  const [query, setQuery] = useState('');
  const [topK, setTopK] = useState(4);
  const [chatResult, setChatResult] = useState<ChatResponse | null>(null);
  const [error, setError] = useState<string | null>(null);

  const themeLabel = theme === 'light' ? 'Light Mode' : 'Dark Mode';

  const themeClass = useMemo(() => (theme === 'dark' ? 'theme-dark' : 'theme-light'), [theme]);

  const handleFileChange = (event: ChangeEvent<HTMLInputElement>) => {
    setIngestResult(null);
    setChatResult(null);
    setError(null);
    const selected = event.target.files?.[0] ?? null;
    setFile(selected);
    setStatus(selected ? `Selected ${selected.name}` : 'Ready to ingest or query.');
  };

  const handleIngest = async () => {
    if (!file) {
      setError('Please choose a PDF file to ingest.');
      return;
    }

    setLoading(true);
    setError(null);
    setStatus('Uploading PDF and ingesting content...');

    try {
      const result = await ingestPdf(file);
      setIngestResult(result);
      setStatus(`Ingested ${result.ingested_chunks} chunks from ${result.file_name}.`);
      setChatResult(null);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Ingestion failed.');
      setStatus('Ingestion failed.');
    } finally {
      setLoading(false);
    }
  };

  const handleAsk = async () => {
    if (!query.trim()) {
      setError('Enter a question to ask the study buddy.');
      return;
    }

    setLoading(true);
    setError(null);
    setStatus('Querying the backend for an answer...');

    try {
      const result = await askChat(query.trim(), topK);
      setChatResult(result);
      setStatus('Answer received.');
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Chat request failed.');
      setStatus('Chat request failed.');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className={`app-shell ${themeClass}`} data-theme={theme}>
      <header className="topbar">
        <div>
          <p className="eyebrow">CRAG Study Buddy</p>
          <h1>Modern PDF Study Assistant</h1>
          <p className="subtitle">{magicText}</p>
        </div>
        <button className="theme-toggle" type="button" onClick={() => setTheme(theme === 'light' ? 'dark' : 'light')}>
          {themeLabel}
        </button>
      </header>

      <main className="grid-layout">
        <section className="panel card highlight-panel">
          <div className="panel-header">
            <div>
              <h2>Quick Start</h2>
              <p>Upload a PDF, ingest its content, then ask any question.</p>
            </div>
          </div>
          <div className="panel-body">
            <ol>
              <li>Choose a PDF using the upload control below.</li>
              <li>Click the Ingest button and wait for processing.</li>
              <li>Ask a question and review the answer with retrieved chunks.</li>
            </ol>
            <div className="status-box">
              <span>Status</span>
              <p>{status}</p>
            </div>
          </div>
        </section>

        <section className="panel card form-panel">
          <div className="panel-header">
            <h2>PDF Ingestion</h2>
            <span className="badge">/ingest</span>
          </div>
          <div className="panel-body">
            <label className="file-input-label">
              <input type="file" accept="application/pdf" onChange={handleFileChange} />
              <span>{file?.name ?? 'Select a PDF file'}</span>
            </label>
            <button className="primary-button" type="button" onClick={handleIngest} disabled={loading || !file}>
              {loading ? 'Processing…' : 'Ingest PDF'}
            </button>
            {ingestResult && (
              <div className="result-card">
                <h3>Ingestion Complete</h3>
                <p>
                  Loaded <strong>{ingestResult.ingested_chunks}</strong> chunks from{' '}
                  <strong>{ingestResult.file_name}</strong>.
                </p>
                <p>{ingestResult.inserted_ids.length} vector ids persisted.</p>
              </div>
            )}
          </div>
        </section>

        <section className="panel card chat-panel">
          <div className="panel-header">
            <h2>Ask the Study Buddy</h2>
            <span className="badge">/chat</span>
          </div>
          <div className="panel-body">
            <label className="field-label" htmlFor="query">
              Question
            </label>
            <textarea
              id="query"
              value={query}
              onChange={(event) => setQuery(event.target.value)}
              rows={4}
              placeholder="Ask something about the ingested documents..."
            />
            <div className="options-row">
              <label className="field-label small">Top chunks</label>
              <input
                type="range"
                min={1}
                max={10}
                value={topK}
                onChange={(event) => setTopK(Number(event.target.value))}
              />
              <span>{topK}</span>
            </div>
            <button className="secondary-button" type="button" onClick={handleAsk} disabled={loading || !query.trim()}>
              {loading ? 'Waiting for answer…' : 'Get Answer'}
            </button>
            {error && <div className="error-box">{error}</div>}
            {chatResult && (
              <div className="result-card">
                <h3>Answer</h3>
                <p>{chatResult.answer}</p>
                {chatResult.retrieved_documents.length > 0 && (
                  <div>
                    <h4>Retrieved Context</h4>
                    <ul>
                      {chatResult.retrieved_documents.map((doc, index) => (
                        <li key={index}>
                          <strong>Chunk {index + 1}:</strong> {doc}
                        </li>
                      ))}
                    </ul>
                  </div>
                )}
                {chatResult.steps_taken.length > 0 && (
                  <div>
                    <h4>Steps Taken</h4>
                    <ul>
                      {chatResult.steps_taken.map((step, index) => (
                        <li key={index}>{step}</li>
                      ))}
                    </ul>
                  </div>
                )}
              </div>
            )}
          </div>
        </section>
      </main>

      <footer className="footer-bar">
        <p>
          Backend API: <code>{apiBaseUrl}</code>
        </p>
      </footer>
    </div>
  );
}

export default App;
