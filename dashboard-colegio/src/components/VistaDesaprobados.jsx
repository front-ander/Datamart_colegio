import React, { useState, useEffect } from 'react';
import axios from 'axios';
import { PieChart, Pie, Cell, Tooltip, ResponsiveContainer, Legend } from 'recharts';

function VistaDesaprobados({ filters }) {
  const [data, setData] = useState([]);

  useEffect(() => {
    const params = new URLSearchParams();
    if (filters?.anio) params.append('anio', filters.anio);
    if (filters?.grado) params.append('grado', filters.grado);

    axios.get(`http://127.0.0.1:8000/api/rendimiento?${params.toString()}`)
      .then(res => {
        let aprobados = 0;
        let desaprobados = 0;
        res.data.forEach(d => { aprobados += d.aprobados; desaprobados += d.desaprobados; });
        setData([
          { name: 'Aprobados', value: aprobados },
          { name: 'Desaprobados', value: desaprobados }
        ]);
      })
      .catch(err => console.error(err));
  }, [filters]);

  const COLORS = ['#2d8a56', '#c23b3b'];

  return (
    <div className="card full-width">
      <h3><i className="fa-solid fa-user-xmark"></i> Análisis de Desaprobados</h3>
      <div className="chart-container" style={{ height: 400 }}>
        <ResponsiveContainer width="100%" height="100%">
          <PieChart>
            <Pie data={data} innerRadius={80} outerRadius={120} paddingAngle={5} dataKey="value">
              {data.map((entry, index) => <Cell key={`cell-${index}`} fill={COLORS[index % COLORS.length]} />)}
            </Pie>
            <Tooltip contentStyle={{ backgroundColor: '#fff', borderRadius: '8px', color: '#3b1e27' }} />
            <Legend verticalAlign="bottom" height={36}/>
          </PieChart>
        </ResponsiveContainer>
      </div>
    </div>
  );
}
export default VistaDesaprobados;
