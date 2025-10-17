const API = "http://127.0.0.1:8000";

// ---------- Obras ----------
export async function getObras(q = "") {
  const url = q ? `${API}/obras?q=${encodeURIComponent(q)}` : `${API}/obras`;
  const r = await fetch(url);
  if (!r.ok) throw new Error(await r.text());
  return r.json();
}

export async function createObra(payload) {
  const r = await fetch(`${API}/obras`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(payload),
  });
  if (!r.ok) throw new Error(await r.text());
  return r.json();
}

export async function updateObra(id, payload) {
  const r = await fetch(`${API}/obras/${id}`, {
    method: "PUT",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(payload),
  });
  if (!r.ok) throw new Error(await r.text());
  return r.json();
}

export async function deleteObra(id) {
  const r = await fetch(`${API}/obras/${id}`, { method: "DELETE" });
  if (!r.ok && r.status !== 204) throw new Error(await r.text());
}

// ---------- Empleados ----------
export async function getEmpleados(q = "") {
  const url = q ? `${API}/empleados?q=${encodeURIComponent(q)}` : `${API}/empleados`;
  const r = await fetch(url);
  if (!r.ok) throw new Error(await r.text());
  return r.json();
}

// ---------- Materiales ----------
export async function getMateriales(q = "") {
  const url = q ? `${API}/materiales?q=${encodeURIComponent(q)}` : `${API}/materiales`;
  const r = await fetch(url);
  if (!r.ok) throw new Error(await r.text());
  return r.json();
}

// ---------- Proyectos ----------
export async function getProyectos(obraId = null) {
  const url = obraId != null ? `${API}/proyectos?obra_id=${obraId}` : `${API}/proyectos`;
  const r = await fetch(url);
  if (!r.ok) throw new Error(await r.text());
  return r.json();
}

// Ejemplo de arranque: llena contadores del dashboard
async function initDashboard() {
  try {
    const [obras, empleados, materiales] = await Promise.all([
      getObras(),
      getEmpleados(),
      getMateriales(),
    ]);
    document.getElementById("totalObras").textContent = obras.length;
    document.getElementById("totalEmpleados").textContent = empleados.length;
    document.getElementById("totalMateriales").textContent = materiales.length;
  } catch (e) {
    console.error(e);
  }
}
window.addEventListener("DOMContentLoaded", initDashboard);
