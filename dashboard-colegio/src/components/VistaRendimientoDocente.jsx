import React, { useState, useEffect } from 'react';
import axios from 'axios';

function VistaRendimientoDocente({ filters }) {
  const [data, setData] = useState([]);

  useEffect(() => {
    const params = new URLSearchParams();
    if (filters?.anio) params.append('anio', filters.anio);
    if (filters?.grado) params.append('grado', filters.grado);

    axios.get(`http://127.0.0.1:8000/api/docentes?${params.toString()}`)
      .then(res => setData(res.data))
      .catch(err => console.error(err));
  }, [filters]);

  return (
    <div className="tab-content">
      <div className="table-card card full-width">
        <h3>Desempeño y Variabilidad por Docente (KPI 11 & 12)</h3>
        <div className="table-container">
          <table className="data-table">
            <thead>
            <tr>
              <th>Profesor</th>
              <th>Especialidad</th>
              <th>Total Notas (Muestra)</th>
              <th>Promedio Gral.</th>
              <th>Desviación Est.</th>
              <th>Nivel Variabilidad</th>
            </tr>
          </thead>
          <tbody>
            {data.map((row, i) => {
              const desv = row.desviacion;
              let variabilidad = 'BAJA';
              let badgeClass = 'status-good';
              if (desv > 5) {
                variabilidad = 'ALTA';
                badgeClass = 'status-danger';
              } else if (desv > 3) {
                variabilidad = 'MODERADA';
                badgeClass = 'status-warning';
              }

              return (
                <tr key={i}>
                  <td>{row.profesor}</td>
                  <td>{row.especialidad}</td>
                  <td>{row.total_Notas}</td>
                  <td>{row.promedio}</td>
                  <td>{desv}</td>
                  <td>
                    <span className={`status-badge ${badgeClass}`}>
                      {variabilidad}
                    </span>
                  </td>
                </tr>
              );
            })}
          </tbody>
          </table>
        </div>
      </div>
    </div>
  );
}

export default VistaRendimientoDocente;
