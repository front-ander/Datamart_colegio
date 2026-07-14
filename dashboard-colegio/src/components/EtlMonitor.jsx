import React, { useState, useRef, useEffect } from 'react';

function EtlMonitor() {
  const [logs, setLogs] = useState([]);
  const [isRunning, setIsRunning] = useState(false);
  const eventSourceRef = useRef(null);
  const consoleRef = useRef(null);

  const startETL = () => {
    if (isRunning) return;
    setLogs([]);
    setIsRunning(true);
    
    eventSourceRef.current = new EventSource('http://127.0.0.1:8000/api/run-etl');

    eventSourceRef.current.onmessage = (event) => {
      const data = JSON.parse(event.data);
      setLogs(prev => [...prev, data]);

      if (data.node === "System" && (data.status === "success" || data.status === "error")) {
        eventSourceRef.current.close();
        setIsRunning(false);
      }
    };

    eventSourceRef.current.onerror = () => {
      setLogs(prev => [...prev, { status: "error", time: new Date().toLocaleTimeString(), node: "System", message: "Conexión perdida con el servidor." }]);
      eventSourceRef.current.close();
      setIsRunning(false);
    };
  };

  useEffect(() => {
    if (consoleRef.current) {
      consoleRef.current.scrollTop = consoleRef.current.scrollHeight;
    }
  }, [logs]);

  return (
    <div className="etl-section">
      <div className="etl-header">
        <h2>Monitor de Pipeline ETL</h2>
        <button className="btn-primary" onClick={startETL} disabled={isRunning}>
          {isRunning ? "Procesando..." : "Ejecutar ETL"}
        </button>
      </div>
      <div className="console-box" ref={consoleRef}>
        {logs.length === 0 && <p style={{color: '#64748b'}}>Esperando ejecución del Pipeline...</p>}
        {logs.map((log, idx) => (
          <p key={idx} className={`log-${log.status}`}>
            <span className="log-time">[{log.time}]</span> 
            <strong>[{log.node}]</strong> {log.message} {log.rows ? `(${log.rows} registros)` : ''}
          </p>
        ))}
      </div>
    </div>
  );
}
export default EtlMonitor;
