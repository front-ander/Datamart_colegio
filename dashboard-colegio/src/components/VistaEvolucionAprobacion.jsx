import React, { useState, useEffect } from 'react';
import axios from 'axios';
import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, Legend } from 'recharts';

function VistaEvolucionAprobacion({ filters }) {
  const [data, setData] = useState([]);

  useEffect(() => {
    const params = new URLSearchParams();
    if (filters?.anio) params.append('anio', filters.anio);
    if (filters?.grado) params.append('grado', filters.grado);

    axios.get(`http://127.0.0.1:8000/api/rendimiento?${params.toString()}`)
      .then(res => {
        setData(res.data);
      })
      .catch(err => console.error(err));
  }, [filters]);

  return (
    <div className="card full-width">
      <h3><i className="fa-solid fa-chart-line"></i> Evolución Histórica de Aprobación</h3>
      <div className="chart-container">
        <ResponsiveContainer width="100%" height="100%">
          <LineChart data={data} margin={{ top: 20, right: 30, left: 20, bottom: 5 }}>
            <CartesianGrid strokeDasharray="3 3" stroke="rgba(0,0,0,0.1)" />
            <XAxis dataKey="Año" stroke="#5b2133" />
            <YAxis stroke="#5b2133" />
            <Tooltip contentStyle={{ backgroundColor: '#fff', borderRadius: '8px', color: '#3b1e27' }} />
            <Legend />
            <Line type="monotone" dataKey="aprobados" stroke="#2d8a56" strokeWidth={3} activeDot={{ r: 8 }} />
            <Line type="monotone" dataKey="desaprobados" stroke="#c23b3b" strokeWidth={3} />
          </LineChart>
        </ResponsiveContainer>
      </div>
    </div>
  );
}
export default VistaEvolucionAprobacion;
