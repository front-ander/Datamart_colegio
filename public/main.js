document.addEventListener('DOMContentLoaded', () => {
    // === UI Elements ===
    const navItems = document.querySelectorAll('.nav-item');
    const views = document.querySelectorAll('.view-section');
    const viewTitle = document.getElementById('view-title');
    const btnRefresh = document.getElementById('btn-refresh');
    const dbStatusDot = document.getElementById('db-status-dot');
    const dbStatusText = document.getElementById('db-status-text');
    
    // === Chart Instances ===
    let gradesChart = null;
    let attendanceChart = null;

    // === Navigation Logic ===
    navItems.forEach(item => {
        item.addEventListener('click', (e) => {
            e.preventDefault();
            const targetViewId = item.getAttribute('data-view');
            
            // Update active state in sidebar
            navItems.forEach(nav => nav.classList.remove('active'));
            item.classList.add('active');
            
            // Update title
            viewTitle.textContent = item.querySelector('span').textContent;
            
            // Switch views
            views.forEach(view => {
                if(view.id === targetViewId) {
                    view.classList.add('active-view');
                } else {
                    view.classList.remove('active-view');
                }
            });

            // If switching to dashboard, load data if empty
            if(targetViewId === 'dashboard-view') {
                loadDashboardData();
            }
        });
    });

    // === Dashboard Data Fetching ===
    btnRefresh.addEventListener('click', loadDashboardData);

    async function loadDashboardData() {
        try {
            setDbStatus('loading');
            
            // Fetch KPIs
            const kpiRes = await fetch('/api/kpis');
            if(!kpiRes.ok) throw new Error("Error al cargar KPIs");
            const kpiData = await kpiRes.json();
            
            document.getElementById('kpi-students').textContent = kpiData.total_estudiantes;
            document.getElementById('kpi-average').textContent = kpiData.promedio_general;
            document.getElementById('kpi-courses').textContent = kpiData.total_cursos;
            document.getElementById('kpi-attendance').textContent = kpiData.total_asistencias;

            // Fetch Table
            const tableRes = await fetch('/api/table/recent');
            if(tableRes.ok) {
                const tableData = await tableRes.json();
                renderTable(tableData);
            }

            // Fetch Charts
            const gradesRes = await fetch('/api/chart/grades');
            if(gradesRes.ok) {
                const gradesData = await gradesRes.json();
                renderGradesChart(gradesData);
            }

            const attendanceRes = await fetch('/api/chart/attendance');
            if(attendanceRes.ok) {
                const attendanceData = await attendanceRes.json();
                renderAttendanceChart(attendanceData);
            }

            setDbStatus('online');
            showToast('Datos del Dashboard actualizados', 'success');

        } catch (error) {
            console.error("Dashboard Fetch Error:", error);
            setDbStatus('offline');
            showToast('Error de conexión a la Base de Datos. Reintentando...', 'error');
        }
    }

    function setDbStatus(status) {
        dbStatusDot.className = 'status-dot ' + status;
        if(status === 'online') dbStatusText.textContent = 'Sistema Online';
        else if(status === 'loading') dbStatusText.textContent = 'Cargando...';
        else dbStatusText.textContent = 'Fallo de Conexión';
    }

    // === Render functions ===
    function renderTable(data) {
        const tbody = document.querySelector('#data-table tbody');
        tbody.innerHTML = '';
        data.forEach(row => {
            const tr = document.createElement('tr');
            const statusClass = row.Estado === 'APROBADO' ? 'badge-aprobado' : 'badge-desaprobado';
            tr.innerHTML = `
                <td>${row.Estudiante}</td>
                <td>${row.Grado}</td>
                <td>${row.Curso}</td>
                <td>${row.Profesor}</td>
                <td><strong>${row.Nota}</strong></td>
                <td><span class="badge ${statusClass}">${row.Estado}</span></td>
            `;
            tbody.appendChild(tr);
        });
    }

    function renderGradesChart(data) {
        const ctx = document.getElementById('gradesChart').getContext('2d');
        if(gradesChart) gradesChart.destroy();
        
        gradesChart = new Chart(ctx, {
            type: 'bar',
            data: {
                labels: data.labels,
                datasets: [{
                    label: 'Promedio de Nota',
                    data: data.data,
                    backgroundColor: 'rgba(67, 97, 238, 0.7)',
                    borderColor: '#4361ee',
                    borderWidth: 1,
                    borderRadius: 4
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                scales: { y: { beginAtZero: true, max: 20 } }
            }
        });
    }

    function renderAttendanceChart(data) {
        const ctx = document.getElementById('attendanceChart').getContext('2d');
        if(attendanceChart) attendanceChart.destroy();
        
        attendanceChart = new Chart(ctx, {
            type: 'doughnut',
            data: {
                labels: ['Asistencias', 'Ausencias'],
                datasets: [{
                    data: [
                        data.asistencias.reduce((a, b) => a + b, 0),
                        data.ausencias.reduce((a, b) => a + b, 0)
                    ],
                    backgroundColor: ['#10b981', '#ef4444'],
                    borderWidth: 0
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                cutout: '70%'
            }
        });
    }

    // === Toast Notifications ===
    function showToast(message, type) {
        const container = document.getElementById('toast-container');
        const toast = document.createElement('div');
        toast.className = `toast ${type}`;
        
        const icon = type === 'success' ? 'fa-check-circle' : 'fa-exclamation-circle';
        toast.innerHTML = `<i class="fa-solid ${icon}"></i> <span>${message}</span>`;
        
        container.appendChild(toast);
        
        setTimeout(() => {
            toast.style.animation = 'fadeOut 0.3s ease-in forwards';
            setTimeout(() => toast.remove(), 300);
        }, 4000);
    }

    // === ETL Logic ===
    const btnRunEtl = document.getElementById('btn-run-etl');
    const consoleOutput = document.getElementById('console-output');

    btnRunEtl.addEventListener('click', () => {
        // Reset Nodes
        document.querySelectorAll('.node').forEach(node => {
            node.className = 'node';
            const statusSpan = node.querySelector('.node-status');
            statusSpan.className = 'node-status text-pending';
            statusSpan.textContent = 'Pendiente';
            
            const badge = node.querySelector('.node-badge');
            if (badge) {
                badge.style.display = 'none';
                badge.textContent = '';
            }
        });

        // Clear console
        consoleOutput.innerHTML = '';
        btnRunEtl.disabled = true;
        btnRunEtl.innerHTML = '<i class="fa-solid fa-spinner fa-spin"></i> Procesando...';
        showToast('Iniciando extracción y transformación ETL...', 'info');

        const eventSource = new EventSource('/api/run-etl');

        eventSource.onmessage = function(event) {
            const data = JSON.parse(event.data);
            
            const p = document.createElement('p');
            p.className = `log-${data.status}`;
            p.textContent = `[${data.time}] [${data.node}] ${data.message}`;
            if (data.rows > 0) {
                p.textContent += ` (${data.rows} registros)`;
            }
            consoleOutput.appendChild(p);
            consoleOutput.scrollTop = consoleOutput.scrollHeight;

            if (data.node !== "System") {
                updateNodeStatus(data.node, data.status, data.rows);
            }

            if (data.status === "success" && data.node === "System") {
                eventSource.close();
                btnRunEtl.disabled = false;
                btnRunEtl.innerHTML = '<i class="fa-solid fa-play"></i> Ejecutar Proceso ETL';
                showToast('Proceso ETL Finalizado con Éxito', 'success');
                // Refresh dashboard data seamlessly
                loadDashboardData();
            }

            if (data.status === "error" && data.node === "System") {
                eventSource.close();
                btnRunEtl.disabled = false;
                btnRunEtl.innerHTML = '<i class="fa-solid fa-rotate-right"></i> Reintentar ETL';
                showToast('Error en proceso ETL. Revise la consola.', 'error');
            }
        };

        eventSource.onerror = function() {
            eventSource.close();
            const p = document.createElement('p');
            p.className = 'log-error';
            p.textContent = `[${new Date().toLocaleTimeString()}] Error de conexión con el servidor ETL. Posible caída del sistema.`;
            consoleOutput.appendChild(p);
            btnRunEtl.disabled = false;
            btnRunEtl.innerHTML = '<i class="fa-solid fa-rotate-right"></i> Reintentar';
            showToast('Conexión perdida con el Servidor.', 'error');
        };
    });

    function updateNodeStatus(nodeId, status, rows) {
        const node = document.getElementById(`node-${nodeId}`);
        if (!node) return;

        node.className = `node ${status}`;
        
        const statusSpan = node.querySelector('.node-status');
        statusSpan.className = `node-status text-${status}`;
        
        const statusTexts = {
            'running': 'En proceso...',
            'success': 'Completado',
            'error': 'Error',
            'warning': 'Advertencia'
        };
        statusSpan.textContent = statusTexts[status] || status;

        const badge = document.getElementById(`badge-${nodeId}`);
        if (badge && rows > 0) {
            badge.style.display = 'block';
            badge.textContent = rows;
        }
    }

    // Inicializar cargando el Dashboard
    loadDashboardData();
});
