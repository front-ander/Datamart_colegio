import React, { useState, useEffect } from 'react';
import axios from 'axios';

function RecentTable() {
  const [data, setData] = useState([]);

  useEffect(() => {
    axios.get('http://127.0.0.1:8000/api/table/recent')
      .then(res => setData(res.data))
      .catch(err => console.error("Error cargando tabla", err));
  }, []);

  return (
    <div className="table-card">
      <h3>Registros Recientes de Rendimiento</h3>
      <div className="table-container">
        <table>
          <thead>
            <tr>
              <th>ESTUDIANTE</th>
              <th>GRADO</th>
              <th>CURSO</th>
              <th>PROFESOR</th>
              <th>NOTA</th>
              <th>ESTADO</th>
            </tr>
          </thead>
          <tbody>
            {data.map((row, idx) => (
              <tr key={idx}>
                <td>{row.Estudiante}</td>
                <td>{row.Grado}</td>
                <td>{row.Curso}</td>
                <td>{row.Profesor}</td>
                <td><strong>{row.Nota}</strong></td>
                <td>
                  <span className={`badge ${row.Estado === 'APROBADO' ? 'badge-aprobado' : 'badge-desaprobado'}`}>
                    {row.Estado}
                  </span>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  );
}
export default RecentTable;
