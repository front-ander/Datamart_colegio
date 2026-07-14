import React from 'react';

function FilterPanel({ filters, setFilters }) {
  const handleChange = (e) => {
    const { name, value } = e.target;
    setFilters(prev => ({ ...prev, [name]: value }));
  };

  return (
    <div className="topbar-filters">
      <select name="anio" value={filters.anio} onChange={handleChange}>
        <option value="">Todos los Años</option>
        <option value="2026">2026</option>
        <option value="2025">2025</option>
        <option value="2024">2024</option>
      </select>
      
      <select name="grado" value={filters.grado} onChange={handleChange}>
        <option value="">Todos los Grados</option>
        <option value="1° PRIMARIA - PRIMARIA">1ro Primaria</option>
        <option value="2° PRIMARIA - PRIMARIA">2do Primaria</option>
        <option value="3° PRIMARIA - PRIMARIA">3ro Primaria</option>
        <option value="4° PRIMARIA - PRIMARIA">4to Primaria</option>
        <option value="5° PRIMARIA - PRIMARIA">5to Primaria</option>
        <option value="6° PRIMARIA - PRIMARIA">6to Primaria</option>
        <option value="1° SECUNDARIA - SECUNDARIA">1ro Secundaria</option>
        <option value="2° SECUNDARIA - SECUNDARIA">2do Secundaria</option>
        <option value="3° SECUNDARIA - SECUNDARIA">3ro Secundaria</option>
        <option value="4° SECUNDARIA - SECUNDARIA">4to Secundaria</option>
        <option value="5° SECUNDARIA - SECUNDARIA">5to Secundaria</option>
      </select>
    </div>
  );
}

export default FilterPanel;
