"use client";

import { useState } from 'react';

export default function Home() {
  const [logs, setLogs] = useState([]);
  const [metrics, setMetrics] = useState(null);
  const [traceData, setTraceData] = useState(null);
  const [isRunning, setIsRunning] = useState(false);
  const [mode, setMode] = useState(''); // 'english' or 'nexus'
  const [inputText, setInputText] = useState("Hello Agent B, I have finished analyzing the quarterly revenue data. The total revenue is $4.2M. I need you to now generate a financial summary report for the board.");

  const runBenchmark = async (testMode) => {
    setIsRunning(true);
    setMode(testMode);
    setLogs([]);
    setMetrics(null);
    setTraceData(null);

    const taskText = inputText;

    // Simulate Agent A thinking
    setLogs([{ agent: 'A', text: 'Processing intent: Send revenue data to Agent B', type: 'info' }]);
    
    await new Promise(r => setTimeout(r, 800));

    try {
      // Call backend
      const res = await fetch('http://localhost:8000/api/benchmark', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ english_text: taskText })
      });
      const data = await res.json();

      if (testMode === 'english') {
        setLogs(prev => [...prev, { agent: 'A', text: `Sending via English: "${data.original_english}"`, type: 'payload_eng' }]);
        await new Promise(r => setTimeout(r, 1500)); // Simulate slow transmission
        setLogs(prev => [...prev, { agent: 'B', text: 'Received English paragraph. Parsing with LLM...', type: 'info' }]);
        await new Promise(r => setTimeout(r, 1000));
        setLogs(prev => [...prev, { agent: 'B', text: 'Task executing: Financial Summary Report generated.', type: 'success' }]);
      } else {
        setLogs(prev => [...prev, { agent: 'A', text: `Sending via Nexus Protocol (JSON): ${data.nexus_packet.substring(0, 150)}...`, type: 'payload_nxp' }]);
        await new Promise(r => setTimeout(r, 200)); // Simulate fast transmission
        setLogs(prev => [...prev, { agent: 'B', text: 'Received NXP JSON packet. Verifying HMAC signature and TTL...', type: 'info' }]);
        await new Promise(r => setTimeout(r, 200));
        setTraceData(data.llm_trace);
        
        const parsed = data.decoded_payload;
        if (parsed.error) {
            setLogs(prev => [...prev, { agent: 'B', text: `HMAC/TTL Validation Failed: ${parsed.error}. Falling back to LLM Decoder!`, type: 'error' }]);
        } else {
            setLogs(prev => [...prev, { agent: 'B', text: `HMAC Valid! Deterministically parsed dynamic params: ${JSON.stringify(parsed.params)}`, type: 'success' }]);
        }
        
        if (parsed.fetched_memory) {
            await new Promise(r => setTimeout(r, 400));
            setLogs(prev => [...prev, { agent: 'B', text: `Memory Payload detected in network stream. Decoded Base64 payload directly from packet:\n\n${parsed.fetched_memory}`, type: 'memory_fetch' }]);
        }
      }

      setMetrics(data.metrics);

    } catch (err) {
      setLogs(prev => [...prev, { agent: 'SYS', text: 'Connection to Nexus Router failed. Is backend running?', type: 'error' }]);
    }
    
    setIsRunning(false);
  };

  return (
    <main className="container">
      <header className="header">
        <h1>NEXUS PROTOCOL</h1>
        <p style={{ color: 'var(--text-muted)', fontSize: '1.2rem', marginTop: '1rem' }}>
          M2M Agentic Communication Engine
        </p>
      </header>

      <div style={{ marginBottom: '2rem', width: '100%', maxWidth: '800px', margin: '0 auto 2rem auto' }}>
        <h3 style={{ color: 'var(--text-main)', marginBottom: '0.5rem' }}>Input Task or Code Payload:</h3>
        <textarea
          value={inputText}
          onChange={(e) => setInputText(e.target.value)}
          disabled={isRunning}
          style={{
            width: '100%',
            height: '120px',
            padding: '1rem',
            backgroundColor: '#0d1117',
            color: 'var(--text-main)',
            border: '1px solid var(--accent-cyan)',
            borderRadius: '8px',
            fontFamily: 'monospace',
            resize: 'vertical'
          }}
          placeholder="Paste massive corpora of text or code here..."
        />
      </div>

      <div className="btn-group" style={{ marginBottom: '3rem' }}>
        <button 
          className="btn-english" 
          onClick={() => runBenchmark('english')}
          disabled={isRunning}
        >
          Run with English (Slow)
        </button>
        <button 
          className="btn-nexus" 
          onClick={() => runBenchmark('nexus')}
          disabled={isRunning}
        >
          Run with Nexus Protocol (Fast)
        </button>
      </div>

      <div className="dashboard-grid">
        {/* Left Panel: Agent Comm Feed */}
        <section className="panel">
          <h2 className="panel-title">Live Communication Feed</h2>
          <div className="agent-box" style={{ minHeight: '300px' }}>
            {logs.length === 0 && <p style={{ color: 'var(--text-muted)' }}>Waiting for transmission...</p>}
            {logs.map((log, i) => (
              <div key={i} style={{ marginBottom: '1rem', borderLeft: `3px solid ${log.agent === 'A' ? 'var(--accent-cyan)' : 'var(--accent-amber)'}`, paddingLeft: '1rem' }}>
                <strong style={{ color: log.agent === 'A' ? 'var(--accent-cyan)' : 'var(--accent-amber)' }}>
                  AGENT {log.agent}: 
                </strong> 
                <span className={log.type.startsWith('payload') ? 'packet-display' : ''} style={{ 
                  display: 'block', 
                  marginTop: '0.5rem', 
                  color: log.type === 'error' ? 'red' : (log.type === 'success' ? 'var(--accent-green)' : ''),
                  whiteSpace: log.type === 'memory_fetch' ? 'pre-wrap' : 'normal',
                  fontFamily: log.type === 'memory_fetch' ? 'monospace' : 'inherit',
                  background: log.type === 'memory_fetch' ? 'rgba(0, 255, 102, 0.05)' : 'none',
                  padding: log.type === 'memory_fetch' ? '1rem' : '0',
                  border: log.type === 'memory_fetch' ? '1px solid var(--accent-green)' : 'none',
                  borderRadius: log.type === 'memory_fetch' ? '8px' : '0'
                }}>
                  {log.text}
                </span>
              </div>
            ))}
          </div>
        </section>

        {/* Right Panel: Metrics */}
        <section className="panel">
          <h2 className="panel-title">Real-Time Metrics</h2>
          {metrics ? (
            <div className="metrics-grid">
              <div className="metric-card">
                <div>Tokens Used (English)</div>
                <div className="metric-value" style={{ color: 'var(--accent-amber)' }}>{metrics.english.tokens}</div>
              </div>
              <div className="metric-card">
                <div>Tokens Used (NXP)</div>
                <div className="metric-value" style={{ color: 'var(--accent-cyan)' }}>{metrics.nexus.tokens}</div>
              </div>
              <div className="metric-card">
                <div>Latency (English)</div>
                <div className="metric-value" style={{ color: 'var(--accent-amber)' }}>{metrics.english.latency}s</div>
              </div>
              <div className="metric-card">
                <div>Latency (NXP)</div>
                <div className="metric-value" style={{ color: 'var(--accent-cyan)' }}>{metrics.nexus.latency}s</div>
              </div>
              
              <div className="metric-card" style={{ gridColumn: 'span 2', background: 'rgba(0, 255, 102, 0.1)', border: '1px solid var(--accent-green)' }}>
                <div style={{ color: 'var(--text-main)' }}>Total Compute Savings (Scale: 50 Agent Hops)</div>
                <div className="metric-value" style={{ fontSize: '3rem', margin: '1rem 0' }}>{metrics.savings.tokens_percent}%</div>
                <div style={{ color: 'var(--accent-green)' }}>
                  Cost reduced from ${metrics.savings.swarm_english_cost.toFixed(4)} to ${metrics.savings.swarm_nxp_cost.toFixed(4)}
                </div>
              </div>
            </div>
          ) : (
             <div style={{ height: '300px', display: 'flex', alignItems: 'center', justifyContent: 'center', color: 'var(--text-muted)' }}>
               Run a benchmark to see metrics.
             </div>
          )}
        </section>
      </div>

      {traceData && mode === 'nexus' && (
        <section className="panel" style={{ marginTop: '2rem' }}>
          <h2 className="panel-title" style={{ color: 'var(--accent-purple, #b28dff)' }}>Agent A LLM Execution Trace (Groq Llama 3.3)</h2>
          <div className="agent-box" style={{ fontFamily: 'monospace', fontSize: '0.9rem', padding: '1.5rem', background: '#0d1117' }}>
            <div style={{ marginBottom: '1.5rem' }}>
              <strong style={{ color: 'var(--text-muted)' }}>--- SYSTEM PROMPT (INSTRUCTIONS) ---</strong>
              <pre style={{ color: '#8b949e', whiteSpace: 'pre-wrap', marginTop: '0.5rem' }}>{traceData.system_prompt}</pre>
            </div>
            <div style={{ marginBottom: '1.5rem' }}>
              <strong style={{ color: 'var(--text-muted)' }}>--- USER PROMPT (INPUT) ---</strong>
              <pre style={{ color: '#79c0ff', whiteSpace: 'pre-wrap', marginTop: '0.5rem' }}>{traceData.user_prompt}</pre>
            </div>
            <div>
              <strong style={{ color: 'var(--text-muted)' }}>--- RAW LLM OUTPUT ---</strong>
              <pre style={{ color: 'var(--accent-green)', whiteSpace: 'pre-wrap', marginTop: '0.5rem' }}>{traceData.raw_output}</pre>
            </div>
          </div>
        </section>
      )}
    </main>
  );
}
