import React, { useState, useEffect } from 'react';
import axios from 'axios';

function VistaRiesgoCritico({ filters }) {
  const [data, setData] = useState([]);

  useEffect(() => {
    const params = new URLSearchParams();
    if (filters?.anio) params.append('anio', filters.anio);
    if (filters?.grado) params.append('grado', filters.grado);

    axios.get(`http://127.0.0.1:8000/api/riesgo?${params.toString()}`)
      .then(res => setData(res.data))
      .catch(err => console.error(err));
  }, [filters]);

  return (
    <div className="tab-content">
      <div className="table-card card full-width">
        <h3>Top 10 Estudiantes en Riesgo Crítico (KPI 10)</h3>
        <div className="table-container">
          <table className="data-table">
            <thead>
            <tr>
              <th>Estudiante</th>
              <th>Grado</th>
              <th>Año</th>
              <th>Prom. Notas</th>
              <th>Total Ausencias</th>
              <th>Índice Riesgo Global</th>
            </tr>
          </thead>
          <tbody>
            {data.map((row, i) => (
              <tr key={i}>
                <td>{row.estudiante}</td>
                <td>{row.grado}</td>
                <td>{row.Año}</td>
                <td>{row.promedio_notas}</td>
                <td>{row.total_Ausencias}</td>
                <td>
                  <span className="status-badge status-danger">
                    {row.indice_riesgo} pts
                  </span>
                </td>
              </tr>
            ))}
          </tbody>
          </table>
        </div>
      </div>
    </div>
  );
}

export default VistaRiesgoCritico;
