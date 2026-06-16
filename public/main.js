document.addEventListener('DOMContentLoaded', () => {
    const btnRun = document.getElementById('btn-run');
    const consoleOutput = document.getElementById('console-output');

    // Mapeo de iconos originales por defecto para restaurarlos
    const defaultIcons = {
        'Extract_MySQL': 'fa-server',
        'Transform_Data': 'fa-filter',
        'Clean_Dest': 'fa-broom',
        'Load_DimEstudiante': 'fa-users',
        'Load_DimCurso': 'fa-book',
        'Load_DimProfesor': 'fa-chalkboard-user',
        'Load_DimGrado': 'fa-layer-group',
        'Load_DimTiempo': 'fa-calendar-days',
        'Mapping_Facts': 'fa-key',
        'Load_Hecho': 'fa-chart-line'
    };

    function appendLog(time, level, message) {
        const p = document.createElement('p');
        p.className = `log-${level}`;
        p.innerHTML = `<span class="log-time">[${time}]</span> ${message}`;
        consoleOutput.appendChild(p);
        consoleOutput.scrollTop = consoleOutput.scrollHeight;
    }

    function resetNodes() {
        Object.keys(defaultIcons).forEach(nodeId => {
            const nodeEl = document.getElementById(`node-${nodeId}`);
            if (!nodeEl) return;
            
            nodeEl.className = 'node';
            
            const iconEl = nodeEl.querySelector('.node-icon i');
            iconEl.className = `fa-solid ${defaultIcons[nodeId]}`;
            
            const statusEl = nodeEl.querySelector('.node-status');
            statusEl.className = 'node-status text-pending';
            statusEl.textContent = 'Pendiente';
            
            const badgeEl = document.getElementById(`badge-${nodeId}`);
            if (badgeEl) {
                badgeEl.className = 'node-badge';
                badgeEl.textContent = '';
            }
        });
        
        consoleOutput.innerHTML = '';
        appendLog(new Date().toLocaleTimeString('es-ES', {hour12:false}), 'info', 'Iniciando nuevo proceso ETL...');
    }

    function updateNode(nodeId, status, message, rows) {
        const nodeEl = document.getElementById(`node-${nodeId}`);
        if (!nodeEl) return;

        // Limpiar clases
        nodeEl.classList.remove('status-running', 'status-success', 'status-error');
        const iconEl = nodeEl.querySelector('.node-icon i');
        const statusEl = nodeEl.querySelector('.node-status');

        if (status === 'running') {
            nodeEl.classList.add('status-running');
            iconEl.className = 'fa-solid fa-spinner';
            statusEl.className = 'node-status text-running';
            statusEl.textContent = 'Procesando...';
        } 
        else if (status === 'success') {
            nodeEl.classList.add('status-success');
            iconEl.className = 'fa-solid fa-check-circle';
            statusEl.className = 'node-status text-success';
            statusEl.textContent = 'Completado';
            
            // Mostrar contador de filas estilo SSIS
            const badgeEl = document.getElementById(`badge-${nodeId}`);
            if (badgeEl && rows > 0) {
                badgeEl.textContent = `${rows} filas`;
                badgeEl.classList.add('show');
            }
        }
        else if (status === 'error') {
            nodeEl.classList.add('status-error');
            iconEl.className = 'fa-solid fa-circle-xmark';
            statusEl.className = 'node-status text-error';
            statusEl.textContent = 'Error';
        }
    }

    btnRun.addEventListener('click', () => {
        btnRun.disabled = true;
        btnRun.innerHTML = '<i class="fa-solid fa-spinner fa-spin"></i> Ejecutando...';
        
        resetNodes();

        // Conectar al backend usando Server-Sent Events
        const eventSource = new EventSource('/api/run-etl');

        eventSource.onmessage = (event) => {
            const data = JSON.parse(event.data);
            
            // Log en consola web
            appendLog(data.time, data.status, data.message);
            
            // Actualizar UI Visual (Data Flow)
            if (data.node !== 'System') {
                updateNode(data.node, data.status, data.message, data.rows);
            }

            // Cerrar conexión si terminó (éxito o error fatal)
            if (data.node === 'System' && (data.status === 'success' || data.status === 'error')) {
                eventSource.close();
                btnRun.disabled = false;
                btnRun.innerHTML = '<i class="fa-solid fa-play"></i> Ejecutar ETL';
            }
        };

        eventSource.onerror = (error) => {
            appendLog(new Date().toLocaleTimeString('es-ES', {hour12:false}), 'error', 'Error de conexión con el servidor.');
            eventSource.close();
            btnRun.disabled = false;
            btnRun.innerHTML = '<i class="fa-solid fa-play"></i> Ejecutar ETL';
        };
    });
});
