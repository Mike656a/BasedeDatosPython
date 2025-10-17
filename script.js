// script.js — Frontend puro para FastAPI (sin Node)
const API_BASE = 'http://127.0.0.1:8000';

// Helpers simples
const $  = (sel, ctx=document) => ctx.querySelector(sel);
const $$ = (sel, ctx=document) => Array.from(ctx.querySelectorAll(sel));

async function apiGet(path) {
  const r = await fetch(`${API_BASE}${path}`, { cache: 'no-store' });
  if (!r.ok) throw new Error(`${path} -> ${r.status}`);
  return r.json();
}

// ====== Navegación lateral (mostrar/ocultar secciones) ======
function initMenu() {
  $$('.menu-item').forEach(a => {
    a.addEventListener('click', (e) => {
      e.preventDefault();
      const sectionId = a.dataset.section;

      // activar item
      $$('.menu-item').forEach(x => x.classList.remove('active'));
      a.classList.add('active');

      // activar sección
      $$('.content-section').forEach(s => s.classList.remove('active'));
      const sec = document.getElementById(sectionId);
      if (sec) sec.classList.add('active');

      // cargar datos de la sección
      switch (sectionId) {
        case 'dashboard':  loadDashboard();  break;
        case 'obras':      loadObras();      break;
        case 'empleados':  loadEmpleados();  break;
        case 'materiales': loadMateriales(); break;
        case 'proyectos':  loadProyectos();  break;
        // puedes añadir más: proveedores, inventario, etc.
      }
    });
  });
}

// ====== Cargas de datos ======
async function loadDashboard() {
  try {
    const [obras, empleados, materiales/*, proveedores*/] = await Promise.all([
      apiGet('/obras'),
      apiGet('/empleados'),
      apiGet('/materiales'),
      // apiGet('/proveedores'),
    ]);
    $('#totalObras').textContent = obras.length;
    $('#totalEmpleados').textContent = empleados.length;
    $('#totalMateriales').textContent = materiales.length;
    // $('#totalProveedores').textContent = proveedores.length;

    // Obras recientes
    const cont = $('#obrasRecientes');
    cont.innerHTML = '';
    obras.slice(0,5).forEach(o => {
      const div = document.createElement('div');
      div.className = 'recent-item';
      div.innerHTML = `<h4>${o.nombre_obra}</h4>
        <p><strong>Tipo:</strong> ${o.tipo_obra ?? '-'} |
        <strong>Estado:</strong> ${o.estado_obra ?? '-'}</p>`;
      cont.appendChild(div);
    });

    // Actividad reciente: ejemplo simple
    const act = $('#actividadReciente');
    act.innerHTML = '';
    empleados.slice(0,5).forEach(emp => {
      const div = document.createElement('div');
      div.className = 'recent-item';
      div.innerHTML = `<h4>${emp.nombre_empleado}</h4>
        <p><strong>Tipo:</strong> ${emp.tipo_empleado ?? '-'} |
        <strong>Salario:</strong> ${emp.salario_fijo_empleado ?? '-'}</p>`;
      act.appendChild(div);
    });
  } catch (e) {
    console.error(e);
  }
}

async function loadObras() {
  const tbody = $('#tablaObras tbody');
  tbody.innerHTML = '<tr><td colspan="9" class="text-center">Cargando…</td></tr>';
  try {
    const data = await apiGet('/obras');
    tbody.innerHTML = '';
    data.forEach(o => {
      const tr = document.createElement('tr');
      tr.innerHTML = `
        <td>${o.id_obra}</td>
        <td>${o.nombre_obra}</td>
        <td>${o.ubicacion_obra ?? '-'}</td>
        <td>${o.tipo_obra ?? '-'}</td>
        <td><span class="status-badge ${statusClass(o.estado_obra)}">${o.estado_obra ?? '-'}</span></td>
        <td>-</td>
        <td>-</td>
        <td>
          <div class="progress-bar"><div class="progress" style="width:0%"></div><span>0%</span></div>
        </td>
        <td>
          <button class="action-btn btn-view" data-id="${o.id_obra}">Ver</button>
          <button class="action-btn btn-edit" data-id="${o.id_obra}">Editar</button>
          <button class="action-btn btn-delete" data-id="${o.id_obra}">Eliminar</button>
        </td>
      `;
      tbody.appendChild(tr);
    });
  } catch (e) {
    console.error(e);
    tbody.innerHTML = '<tr><td colspan="9" class="text-center">Error cargando obras</td></tr>';
  }
}

async function loadEmpleados() {
  const tbody = $('#tablaEmpleados tbody');
  tbody.innerHTML = '<tr><td colspan="8" class="text-center">Cargando…</td></tr>';
  try {
    const data = await apiGet('/empleados');
    tbody.innerHTML = '';
    data.forEach(x => {
      const tr = document.createElement('tr');
      tr.innerHTML = `
        <td>${x.id_empleado}</td>
        <td>${x.nombre_empleado}</td>
        <td>${x.tipo_empleado ?? '-'}</td>
        <td class="text-right">${fmtMoney(x.salario_fijo_empleado)}</td>
        <td><span class="status-badge status-activo">Activo</span></td>
        <td>0</td>
        <td>-</td>
        <td>
          <button class="action-btn btn-view" data-id="${x.id_empleado}">Ver</button>
          <button class="action-btn btn-edit" data-id="${x.id_empleado}">Editar</button>
          <button class="action-btn btn-delete" data-id="${x.id_empleado}">Eliminar</button>
        </td>
      `;
      tbody.appendChild(tr);
    });
  } catch (e) {
    console.error(e);
    tbody.innerHTML = '<tr><td colspan="8" class="text-center">Error cargando empleados</td></tr>';
  }
}

async function loadMateriales() {
  const tbody = $('#tablaMateriales tbody');
  tbody.innerHTML = '<tr><td colspan="9" class="text-center">Cargando…</td></tr>';
  try {
    const data = await apiGet('/materiales');
    tbody.innerHTML = '';
    data.forEach(m => {
      const tr = document.createElement('tr');
      tr.innerHTML = `
        <td>${m.id_material}</td>
        <td>${m.nombre_material}</td>
        <td>${m.unidad_material ?? '-'}</td>
        <td class="text-right">${fmtMoney(m.precio_unitario_material)}</td>
        <td>-</td>
        <td><span class="status-badge status-activo">Disponible</span></td>
        <td>-</td>
        <td class="text-right">-</td>
        <td>
          <button class="action-btn btn-view" data-id="${m.id_material}">Ver</button>
          <button class="action-btn btn-edit" data-id="${m.id_material}">Editar</button>
          <button class="action-btn btn-delete" data-id="${m.id_material}">Eliminar</button>
        </td>
      `;
      tbody.appendChild(tr);
    });
  } catch (e) {
    console.error(e);
    tbody.innerHTML = '<tr><td colspan="9" class="text-center">Error cargando materiales</td></tr>';
  }
}

async function loadProyectos() {
  const tbody = $('#tablaProyectos tbody');
  tbody.innerHTML = '<tr><td colspan="9" class="text-center">Cargando…</td></tr>';
  try {
    const data = await apiGet('/proyectos');
    tbody.innerHTML = '';
    data.forEach(p => {
      const tr = document.createElement('tr');
      tr.innerHTML = `
        <td>${p.id_proyecto}</td>
        <td>${p.nombre_proyecto}</td>
        <td>${p.id_obra}</td>
        <td>${p.fecha_inicio_proyecto ?? '-'}</td>
        <td>${p.fecha_fin_proyecto ?? '-'}</td>
        <td><span class="status-badge ${statusClass(p.estado_proyecto)}">${p.estado_proyecto ?? '-'}</span></td>
        <td>
          <div class="progress-bar"><div class="progress" style="width:0%"></div><span>0%</span></div>
        </td>
        <td>0</td>
        <td>
          <button class="action-btn btn-view" data-id="${p.id_proyecto}">Ver</button>
          <button class="action-btn btn-edit" data-id="${p.id_proyecto}">Editar</button>
          <button class="action-btn btn-delete" data-id="${p.id_proyecto}">Eliminar</button>
        </td>
      `;
      tbody.appendChild(tr);
    });
  } catch (e) {
    console.error(e);
    tbody.innerHTML = '<tr><td colspan="9" class="text-center">Error cargando proyectos</td></tr>';
  }
}

// ====== Utilidades de formato/estado ======
function fmtMoney(v) {
  if (v === null || v === undefined) return 'Q. 0.00';
  const n = Number(v);
  if (Number.isNaN(n)) return 'Q. 0.00';
  return new Intl.NumberFormat('es-GT', { style: 'currency', currency: 'GTQ' }).format(n);
}
function statusClass(estado) {
  if (!estado) return 'status-proceso';
  const e = estado.toLowerCase();
  if (e.includes('activo') || e.includes('complet')) return 'status-completado';
  if (e.includes('suspend')) return 'status-suspendido';
  if (e.includes('proceso') || e.includes('plan')) return 'status-proceso';
  return 'status-activo';
}

// ====== Inicio ======
document.addEventListener('DOMContentLoaded', () => {
  initMenu();
  // carga inicial (dashboard)
  loadDashboard();
});
