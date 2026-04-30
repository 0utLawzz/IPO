import React, { useEffect, useMemo, useRef, useState } from 'react';

const TM_FORMS = [
  'TM-01',
  'TM-02',
  'TM-05',
  'TM-06',
  'TM-07',
  'TM-11',
  'TM-12',
  'TM-13',
  'TM-15',
  'TM-16',
  'TM-24',
  'TM-33',
  'TM-34',
  'TM-46',
  'TM-55',
  'TM-56',
  'TM-57',
];

function Card({ title, children }) {
  return (
    <div style={{
      background: 'linear-gradient(180deg, rgba(255,255,255,0.06), rgba(255,255,255,0.03))',
      border: '1px solid rgba(255,255,255,0.10)',
      borderRadius: 14,
      padding: 16,
      boxShadow: '0 10px 40px rgba(0,0,0,0.35)'
    }}>
      <div style={{
        fontSize: 12,
        letterSpacing: '0.14em',
        textTransform: 'uppercase',
        opacity: 0.85,
        marginBottom: 10
      }}>{title}</div>
      {children}
    </div>
  );
}

function Button({ variant = 'primary', ...props }) {
  const base = {
    borderRadius: 12,
    padding: '10px 14px',
    fontSize: 13,
    border: '1px solid rgba(255,255,255,0.14)',
    cursor: 'pointer',
    userSelect: 'none'
  };
  const styles = {
    primary: {
      background: 'linear-gradient(90deg, #3b82f6, #22c55e)',
      color: '#071018',
      border: '1px solid rgba(255,255,255,0.08)'
    },
    ghost: {
      background: 'rgba(255,255,255,0.04)',
      color: 'rgba(255,255,255,0.92)'
    },
    danger: {
      background: 'rgba(239,68,68,0.18)',
      color: 'rgba(255,255,255,0.92)',
      border: '1px solid rgba(239,68,68,0.35)'
    }
  };
  return <button {...props} style={{ ...base, ...styles[variant], ...(props.style || {}) }} />;
}

function Metric({ label, value }) {
  return (
    <div style={{ padding: '10px 12px', borderRadius: 12, background: 'rgba(255,255,255,0.04)', border: '1px solid rgba(255,255,255,0.08)' }}>
      <div style={{ fontSize: 11, opacity: 0.75, marginBottom: 6 }}>{label}</div>
      <div style={{ fontSize: 22, fontWeight: 650, letterSpacing: '-0.02em' }}>{value}</div>
    </div>
  );
}

export default function App() {
  const [screen, setScreen] = useState('welcome'); // welcome | submission
  const [tm, setTm] = useState('TM-01');
  const [status, setStatus] = useState({ state: 'idle' });
  const [logs, setLogs] = useState('');
  const [sessions, setSessions] = useState([]);
  const logRef = useRef(null);

  const canUseBridge = typeof window !== 'undefined' && window.ipo;

  useEffect(() => {
    if (!canUseBridge) return;
    const offLog = window.ipo.onLog((msg) => setLogs((prev) => (prev + msg)));
    const offStatus = window.ipo.onStatus((s) => setStatus(s));
    return () => {
      offLog?.();
      offStatus?.();
    };
  }, [canUseBridge]);

  useEffect(() => {
    if (!logRef.current) return;
    logRef.current.scrollTop = logRef.current.scrollHeight;
  }, [logs]);

  async function refreshSessions() {
    if (!canUseBridge) return;
    const res = await window.ipo.listSessions({ tm });
    if (res?.ok) setSessions(res.sessions);
  }

  useEffect(() => {
    refreshSessions();
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [tm]);

  async function run() {
    if (!canUseBridge) return;
    setLogs('');
    await window.ipo.runScraper({ tm, python: 'python' });
    await refreshSessions();
  }

  async function stop() {
    if (!canUseBridge) return;
    await window.ipo.stopScraper();
  }

  const latestSummary = useMemo(() => {
    const first = sessions?.[0];
    return first?.summary || null;
  }, [sessions]);

  const shellBg = {
    minHeight: '100vh',
    background: 'radial-gradient(1200px 900px at 25% 15%, rgba(59,130,246,0.22), transparent 55%), radial-gradient(900px 800px at 85% 25%, rgba(34,197,94,0.16), transparent 60%), #0b0d12',
    color: 'rgba(255,255,255,0.92)',
    fontFamily: 'ui-sans-serif, system-ui, -apple-system, Segoe UI, Roboto, Arial',
  };

  return (
    <div style={shellBg}>
      <div style={{ maxWidth: 1180, margin: '0 auto', padding: 22 }}>
        <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: 18 }}>
          <div>
            <div style={{ fontSize: 12, letterSpacing: '0.16em', textTransform: 'uppercase', opacity: 0.8 }}>IPO Pakistan</div>
            <div style={{ fontSize: 28, fontWeight: 700, letterSpacing: '-0.03em' }}>Trademark Scraper</div>
          </div>
          <div style={{ display: 'flex', gap: 10 }}>
            <Button variant="ghost" onClick={() => window.ipo?.openExports?.()}>Open Export Folder</Button>
            <Button variant="ghost" onClick={refreshSessions}>Refresh</Button>
          </div>
        </div>

        {screen === 'welcome' && (
          <Card title="Welcome">
            <div style={{
              borderRadius: 16,
              padding: 14,
              background: 'rgba(0,0,0,0.22)',
              border: '1px solid rgba(255,255,255,0.10)'
            }}>
              <div style={{
                height: 1,
                background: 'linear-gradient(90deg, rgba(255,255,255,0.22), rgba(255,255,255,0.06))',
                marginBottom: 12
              }} />

              <div style={{
                display: 'flex',
                alignItems: 'center',
                justifyContent: 'space-between',
                gap: 12,
                marginBottom: 12
              }}>
                <div style={{
                  fontSize: 18,
                  fontWeight: 750,
                  letterSpacing: '0.06em',
                  textTransform: 'uppercase'
                }}>
                  IPO Trademark Scraper
                </div>
                <div style={{
                  fontFamily: 'ui-monospace, SFMono-Regular, Menlo, Consolas, monospace',
                  fontSize: 12,
                  opacity: 0.75
                }}>
                  Main Menu
                </div>
              </div>

              <div style={{
                display: 'grid',
                gap: 10,
                gridTemplateColumns: '1fr',
              }}>
                <div style={{
                  display: 'grid',
                  gridTemplateColumns: '54px 1fr 120px',
                  gap: 10,
                  padding: '10px 12px',
                  borderRadius: 14,
                  background: 'rgba(255,255,255,0.03)',
                  border: '1px solid rgba(255,255,255,0.08)',
                  alignItems: 'center'
                }}>
                  <div style={{ fontFamily: 'ui-monospace, SFMono-Regular, Menlo, Consolas, monospace', opacity: 0.9 }}>1.</div>
                  <div style={{ fontSize: 14, fontWeight: 650 }}>Number Check</div>
                  <div style={{
                    justifySelf: 'end',
                    fontSize: 11,
                    padding: '4px 10px',
                    borderRadius: 999,
                    background: 'rgba(255,255,255,0.06)',
                    border: '1px solid rgba(255,255,255,0.10)',
                    opacity: 0.7
                  }}>PENDING</div>
                </div>

                <div style={{
                  display: 'grid',
                  gridTemplateColumns: '54px 1fr 120px',
                  gap: 10,
                  padding: '10px 12px',
                  borderRadius: 14,
                  background: 'rgba(255,255,255,0.03)',
                  border: '1px solid rgba(255,255,255,0.08)',
                  alignItems: 'center'
                }}>
                  <div style={{ fontFamily: 'ui-monospace, SFMono-Regular, Menlo, Consolas, monospace', opacity: 0.9 }}>2.</div>
                  <div style={{ fontSize: 14, fontWeight: 650 }}>Acknowledgements</div>
                  <div style={{
                    justifySelf: 'end',
                    fontSize: 11,
                    padding: '4px 10px',
                    borderRadius: 999,
                    background: 'rgba(255,255,255,0.06)',
                    border: '1px solid rgba(255,255,255,0.10)',
                    opacity: 0.7
                  }}>PENDING</div>
                </div>

                <div style={{
                  display: 'grid',
                  gridTemplateColumns: '54px 1fr 120px',
                  gap: 10,
                  padding: '10px 12px',
                  borderRadius: 14,
                  background: 'linear-gradient(90deg, rgba(59,130,246,0.16), rgba(34,197,94,0.10))',
                  border: '1px solid rgba(255,255,255,0.10)',
                  alignItems: 'center'
                }}>
                  <div style={{ fontFamily: 'ui-monospace, SFMono-Regular, Menlo, Consolas, monospace', opacity: 0.9 }}>3.</div>
                  <div style={{ fontSize: 14, fontWeight: 650 }}>Submission</div>
                  <div style={{ justifySelf: 'end' }}>
                    <Button onClick={() => setScreen('submission')} style={{ padding: '8px 12px', borderRadius: 12 }}>Open</Button>
                  </div>
                </div>
              </div>

              <div style={{ display: 'flex', justifyContent: 'space-between', gap: 10, marginTop: 14, flexWrap: 'wrap' }}>
                <Button variant="ghost" onClick={() => setScreen('submission')}>Go to Submission</Button>
                <Button variant="danger" onClick={() => window.close?.()}>Exit</Button>
              </div>

              <div style={{
                height: 1,
                background: 'linear-gradient(90deg, rgba(255,255,255,0.06), rgba(255,255,255,0.22))',
                marginTop: 12
              }} />
            </div>
          </Card>
        )}

        {screen === 'submission' && (
          <div style={{ display: 'grid', gridTemplateColumns: '420px 1fr', gap: 16 }}>
            <div style={{ display: 'grid', gap: 16 }}>
              <Card title="Submission">
                <div style={{ display: 'grid', gap: 10 }}>
                  <div style={{ display: 'grid', gap: 6 }}>
                    <div style={{ fontSize: 12, opacity: 0.75 }}>TM Form</div>
                    <select
                      value={tm}
                      onChange={(e) => setTm(e.target.value)}
                      style={{
                        borderRadius: 12,
                        padding: '10px 12px',
                        background: 'rgba(255,255,255,0.04)',
                        border: '1px solid rgba(255,255,255,0.10)',
                        color: 'rgba(255,255,255,0.92)'
                      }}
                    >
                      {TM_FORMS.map((f) => <option key={f} value={f}>{f}</option>)}
                    </select>
                  </div>

                  <div style={{ display: 'flex', gap: 10, flexWrap: 'wrap' }}>
                    <Button onClick={run} disabled={status?.state === 'running'}>Run</Button>
                    <Button variant="danger" onClick={stop} disabled={status?.state !== 'running'}>Stop</Button>
                    <Button variant="ghost" onClick={() => setScreen('welcome')}>Back</Button>
                  </div>

                  <div style={{ fontSize: 12, opacity: 0.8 }}>
                    Status: <span style={{ opacity: 1 }}>{status?.state || 'idle'}</span>
                    {status?.exitCode !== undefined && status?.exitCode !== null ? ` (exit ${status.exitCode})` : ''}
                  </div>
                </div>
              </Card>

              <Card title="This Session">
                <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: 10 }}>
                  <Metric label="Scraped" value={latestSummary?.scraped_total ?? '—'} />
                  <Metric label="New Written" value={latestSummary?.new_rows_written ?? '—'} />
                  <Metric label="Duplicates" value={latestSummary?.duplicates_skipped ?? '—'} />
                  <Metric label="Timestamp" value={latestSummary?.session_timestamp ?? '—'} />
                </div>
              </Card>

              <Card title="Sessions">
                <div style={{ display: 'grid', gap: 10, maxHeight: 240, overflow: 'auto' }}>
                  {sessions.length === 0 && (
                    <div style={{ fontSize: 12, opacity: 0.75 }}>No sessions found for {tm} yet.</div>
                  )}
                  {sessions.map((s) => (
                    <div key={s.timestamp} style={{ padding: 10, borderRadius: 12, background: 'rgba(255,255,255,0.035)', border: '1px solid rgba(255,255,255,0.08)' }}>
                      <div style={{ display: 'flex', justifyContent: 'space-between', gap: 10 }}>
                        <div style={{ fontSize: 12, opacity: 0.85 }}>{s.timestamp}</div>
                        <div style={{ fontSize: 12, opacity: 0.7 }}>{(s.files || []).filter((f) => f.endsWith('.csv')).length} CSV</div>
                      </div>
                      {s.summary && (
                        <div style={{ marginTop: 8, display: 'grid', gridTemplateColumns: '1fr 1fr 1fr', gap: 8 }}>
                          <div style={{ fontSize: 11, opacity: 0.75 }}>Scraped: <span style={{ opacity: 1 }}>{s.summary.scraped_total}</span></div>
                          <div style={{ fontSize: 11, opacity: 0.75 }}>New: <span style={{ opacity: 1 }}>{s.summary.new_rows_written}</span></div>
                          <div style={{ fontSize: 11, opacity: 0.75 }}>Dup: <span style={{ opacity: 1 }}>{s.summary.duplicates_skipped}</span></div>
                        </div>
                      )}
                    </div>
                  ))}
                </div>
              </Card>
            </div>

            <Card title="Live Logs">
              <div
                ref={logRef}
                style={{
                  height: 560,
                  overflow: 'auto',
                  fontFamily: 'ui-monospace, SFMono-Regular, Menlo, Consolas, monospace',
                  fontSize: 12,
                  whiteSpace: 'pre-wrap',
                  lineHeight: 1.25,
                  padding: 12,
                  borderRadius: 12,
                  background: 'rgba(0,0,0,0.28)',
                  border: '1px solid rgba(255,255,255,0.08)'
                }}
              >
                {logs || 'Logs will appear here...'}
              </div>
            </Card>
          </div>
        )}

        {!canUseBridge && (
          <div style={{ marginTop: 18, fontSize: 12, opacity: 0.7 }}>
            Electron bridge not available. Run this UI through Electron (not just in the browser).
          </div>
        )}
      </div>
    </div>
  );
}
