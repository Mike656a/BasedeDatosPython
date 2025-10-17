import os
from typing import List, Optional, Any, Dict
from datetime import date

import pyodbc
from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from fastapi.encoders import jsonable_encoder
from dotenv import load_dotenv

# =============================
# Config
# =============================
load_dotenv()

SERVER   = os.getenv("MSSQL_SERVER", r"(localdb)\MSSQLLocalDB")
DATABASE = os.getenv("MSSQL_DATABASE", "Constructora")
DRIVER   = os.getenv("MSSQL_DRIVER", "ODBC Driver 18 for SQL Server")
ENCRYPT  = os.getenv("MSSQL_ENCRYPT", "no")   # yes/no
TRUST    = os.getenv("MSSQL_TRUST_SERVER_CERTIFICATE", "yes")  # yes/no
UID      = os.getenv("MSSQL_USERNAME", "")
PWD      = os.getenv("MSSQL_PASSWORD", "")

# Cadena para LocalDB con autenticación integrada si no hay UID/PWD
if UID and PWD:
    CONN_STR = (
        f"DRIVER={{{DRIVER}}};SERVER={SERVER};DATABASE={DATABASE};UID={UID};PWD={PWD};"
        f"Encrypt={'Yes' if ENCRYPT.lower()=='yes' else 'No'};"
        f"TrustServerCertificate={'Yes' if TRUST.lower()=='yes' else 'No'};"
    ).replace("{DRIVER}", DRIVER)
else:
    CONN_STR = (
        f"DRIVER={{{DRIVER}}};SERVER={SERVER};DATABASE={DATABASE};Trusted_Connection=Yes;"
        f"Encrypt={'Yes' if ENCRYPT.lower()=='yes' else 'No'};"
        f"TrustServerCertificate={'Yes' if TRUST.lower()=='yes' else 'No'};"
    ).replace("{DRIVER}", DRIVER)

def get_conn():
    # Una conexión por request
    return pyodbc.connect(CONN_STR, autocommit=False)

def rows_to_dicts(cursor) -> List[Dict[str, Any]]:
    cols = [c[0] for c in cursor.description]
    return [dict(zip(cols, row)) for row in cursor.fetchall()]

# =============================
# FastAPI
# =============================
app = FastAPI(title="API Constructora", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],           # Permite abrir index.html directo (file://) o Live Server
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# =============================
# Schemas
# =============================
class ObraIn(BaseModel):
    nombre_obra: str
    tipo_obra: Optional[str] = None
    estado_obra: Optional[str] = None
    ubicacion_obra: Optional[str] = None

class ObraOut(ObraIn):
    id_obra: int

class EmpleadoIn(BaseModel):
    nombre_empleado: str
    tipo_empleado: Optional[str] = None
    salario_fijo_empleado: Optional[float] = None

class EmpleadoOut(EmpleadoIn):
    id_empleado: int

class MaterialIn(BaseModel):
    nombre_material: str
    unidad_material: Optional[str] = None
    precio_unitario_material: Optional[float] = None

class MaterialOut(MaterialIn):
    id_material: int

class ProyectoIn(BaseModel):
    id_obra: int
    nombre_proyecto: str
    fecha_inicio_proyecto: Optional[date] = None
    fecha_fin_proyecto: Optional[date] = None
    estado_proyecto: Optional[str] = None

class ProyectoOut(ProyectoIn):
    id_proyecto: int

# =============================
# Health
# =============================
@app.get("/health")
def health():
    return {"ok": True}

@app.get("/health/db")
def health_db():
    try:
        with get_conn() as conn:
            cur = conn.cursor()
            cur.execute("SELECT 1")
            _ = cur.fetchone()
        return {"ok": True}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"DB error: {e}")

# =============================
# OBRAS
# =============================
@app.get("/obras", response_model=List[ObraOut])
def list_obras(q: Optional[str] = Query(None, description="Filtro por nombre (contiene)")):
    try:
        with get_conn() as conn:
            cur = conn.cursor()
            if q:
                cur.execute("""
                    SELECT id_obra, nombre_obra, tipo_obra, estado_obra, ubicacion_obra
                    FROM dbo.OBRAS WHERE nombre_obra LIKE ? ORDER BY id_obra DESC
                """, f"%{q}%")
            else:
                cur.execute("""
                    SELECT id_obra, nombre_obra, tipo_obra, estado_obra, ubicacion_obra
                    FROM dbo.OBRAS ORDER BY id_obra DESC
                """)
            return jsonable_encoder(rows_to_dicts(cur))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/obras", response_model=ObraOut, status_code=201)
def create_obra(data: ObraIn):
    try:
        with get_conn() as conn:
            cur = conn.cursor()
            cur.execute("""
                INSERT INTO dbo.OBRAS (nombre_obra, tipo_obra, estado_obra, ubicacion_obra)
                VALUES (?, ?, ?, ?);
            """, data.nombre_obra, data.tipo_obra, data.estado_obra, data.ubicacion_obra)
            cur.execute("SELECT CAST(SCOPE_IDENTITY() AS INT)")
            new_id = cur.fetchone()[0]
            conn.commit()
            return {**data.dict(), "id_obra": new_id}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.put("/obras/{id_obra}", response_model=ObraOut)
def update_obra(id_obra: int, data: ObraIn):
    try:
        with get_conn() as conn:
            cur = conn.cursor()
            cur.execute("""
                UPDATE dbo.OBRAS
                SET nombre_obra=?, tipo_obra=?, estado_obra=?, ubicacion_obra=?
                WHERE id_obra=?;
            """, data.nombre_obra, data.tipo_obra, data.estado_obra, data.ubicacion_obra, id_obra)
            if cur.rowcount == 0:
                raise HTTPException(status_code=404, detail="Obra no encontrada")
            conn.commit()
            return {**data.dict(), "id_obra": id_obra}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.delete("/obras/{id_obra}", status_code=204)
def delete_obra(id_obra: int):
    try:
        with get_conn() as conn:
            cur = conn.cursor()
            # Si tienes tablas NO ACTION dependientes de OBRAS, elimínalas aquí antes del delete.
            cur.execute("DELETE FROM dbo.OBRAS WHERE id_obra=?;", id_obra)
            if cur.rowcount == 0:
                raise HTTPException(status_code=404, detail="Obra no encontrada")
            conn.commit()
            return
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# =============================
# EMPLEADOS
# =============================
@app.get("/empleados", response_model=List[EmpleadoOut])
def list_empleados(q: Optional[str] = Query(None, description="Filtro por nombre (contiene)")):
    try:
        with get_conn() as conn:
            cur = conn.cursor()
            if q:
                cur.execute("""
                    SELECT id_empleado, nombre_empleado, tipo_empleado, salario_fijo_empleado
                    FROM dbo.EMPLEADOS WHERE nombre_empleado LIKE ? ORDER BY id_empleado DESC
                """, f"%{q}%")
            else:
                cur.execute("""
                    SELECT id_empleado, nombre_empleado, tipo_empleado, salario_fijo_empleado
                    FROM dbo.EMPLEADOS ORDER BY id_empleado DESC
                """)
            return jsonable_encoder(rows_to_dicts(cur))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/empleados", response_model=EmpleadoOut, status_code=201)
def create_empleado(data: EmpleadoIn):
    try:
        with get_conn() as conn:
            cur = conn.cursor()
            cur.execute("""
                INSERT INTO dbo.EMPLEADOS (nombre_empleado, tipo_empleado, salario_fijo_empleado)
                VALUES (?, ?, ?);
            """, data.nombre_empleado, data.tipo_empleado, data.salario_fijo_empleado)
            cur.execute("SELECT CAST(SCOPE_IDENTITY() AS INT)")
            new_id = cur.fetchone()[0]
            conn.commit()
            return {**data.dict(), "id_empleado": new_id}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.put("/empleados/{id_empleado}", response_model=EmpleadoOut)
def update_empleado(id_empleado: int, data: EmpleadoIn):
    try:
        with get_conn() as conn:
            cur = conn.cursor()
            cur.execute("""
                UPDATE dbo.EMPLEADOS
                SET nombre_empleado=?, tipo_empleado=?, salario_fijo_empleado=?
                WHERE id_empleado=?;
            """, data.nombre_empleado, data.tipo_empleado, data.salario_fijo_empleado, id_empleado)
            if cur.rowcount == 0:
                raise HTTPException(status_code=404, detail="Empleado no encontrado")
            conn.commit()
            return {**data.dict(), "id_empleado": id_empleado}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.delete("/empleados/{id_empleado}", status_code=204)
def delete_empleado(id_empleado: int):
    try:
        with get_conn() as conn:
            cur = conn.cursor()
            # Limpieza previa de NO ACTION en INCIDENTES si aplica:
            cur.execute("""
                UPDATE dbo.INCIDENTES SET id_empleado_responsable = NULL
                WHERE id_empleado_responsable = ?;
            """, id_empleado)
            cur.execute("DELETE FROM dbo.EMPLEADOS WHERE id_empleado=?;", id_empleado)
            if cur.rowcount == 0:
                raise HTTPException(status_code=404, detail="Empleado no encontrado")
            conn.commit()
            return
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# =============================
# MATERIALES
# =============================
@app.get("/materiales", response_model=List[MaterialOut])
def list_materiales(q: Optional[str] = Query(None, description="Filtro por nombre (contiene)")):
    try:
        with get_conn() as conn:
            cur = conn.cursor()
            if q:
                cur.execute("""
                    SELECT id_material, nombre_material, unidad_material, precio_unitario_material
                    FROM dbo.MATERIALES WHERE nombre_material LIKE ? ORDER BY id_material DESC
                """, f"%{q}%")
            else:
                cur.execute("""
                    SELECT id_material, nombre_material, unidad_material, precio_unitario_material
                    FROM dbo.MATERIALES ORDER BY id_material DESC
                """)
            return jsonable_encoder(rows_to_dicts(cur))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/materiales", response_model=MaterialOut, status_code=201)
def create_material(data: MaterialIn):
    try:
        with get_conn() as conn:
            cur = conn.cursor()
            cur.execute("""
                INSERT INTO dbo.MATERIALES (nombre_material, unidad_material, precio_unitario_material)
                VALUES (?, ?, ?);
            """, data.nombre_material, data.unidad_material, data.precio_unitario_material)
            cur.execute("SELECT CAST(SCOPE_IDENTITY() AS INT)")
            new_id = cur.fetchone()[0]
            conn.commit()
            return {**data.dict(), "id_material": new_id}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.put("/materiales/{id_material}", response_model=MaterialOut)
def update_material(id_material: int, data: MaterialIn):
    try:
        with get_conn() as conn:
            cur = conn.cursor()
            cur.execute("""
                UPDATE dbo.MATERIALES
                SET nombre_material=?, unidad_material=?, precio_unitario_material=?
                WHERE id_material=?;
            """, data.nombre_material, data.unidad_material, data.precio_unitario_material, id_material)
            if cur.rowcount == 0:
                raise HTTPException(status_code=404, detail="Material no encontrado")
            conn.commit()
            return {**data.dict(), "id_material": id_material}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.delete("/materiales/{id_material}", status_code=204)
def delete_material(id_material: int):
    try:
        with get_conn() as conn:
            cur = conn.cursor()
            cur.execute("DELETE FROM dbo.MATERIALES WHERE id_material=?;", id_material)
            if cur.rowcount == 0:
                raise HTTPException(status_code=404, detail="Material no encontrado")
            conn.commit()
            return
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# =============================
# PROYECTOS
# =============================
@app.get("/proyectos", response_model=List[ProyectoOut])
def list_proyectos(obra_id: Optional[int] = Query(None, description="Filtra por id_obra")):
    try:
        with get_conn() as conn:
            cur = conn.cursor()
            if obra_id is not None:
                cur.execute("""
                    SELECT id_proyecto, id_obra, nombre_proyecto, fecha_inicio_proyecto,
                           fecha_fin_proyecto, estado_proyecto
                    FROM dbo.PROYECTOS WHERE id_obra=? ORDER BY id_proyecto DESC;
                """, obra_id)
            else:
                cur.execute("""
                    SELECT id_proyecto, id_obra, nombre_proyecto, fecha_inicio_proyecto,
                           fecha_fin_proyecto, estado_proyecto
                    FROM dbo.PROYECTOS ORDER BY id_proyecto DESC;
                """)
            return jsonable_encoder(rows_to_dicts(cur))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/proyectos", response_model=ProyectoOut, status_code=201)
def create_proyecto(data: ProyectoIn):
    try:
        with get_conn() as conn:
            cur = conn.cursor()
            cur.execute("""
                INSERT INTO dbo.PROYECTOS (id_obra, nombre_proyecto, fecha_inicio_proyecto,
                                           fecha_fin_proyecto, estado_proyecto)
                VALUES (?, ?, ?, ?, ?);
            """, data.id_obra, data.nombre_proyecto, data.fecha_inicio_proyecto,
                 data.fecha_fin_proyecto, data.estado_proyecto)
            cur.execute("SELECT CAST(SCOPE_IDENTITY() AS INT)")
            new_id = cur.fetchone()[0]
            conn.commit()
            return {**data.dict(), "id_proyecto": new_id}
    except pyodbc.IntegrityError as e:
        raise HTTPException(status_code=400, detail=f"Violación de FK/constraint: {e}")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.put("/proyectos/{id_proyecto}", response_model=ProyectoOut)
def update_proyecto(id_proyecto: int, data: ProyectoIn):
    try:
        with get_conn() as conn:
            cur = conn.cursor()
            cur.execute("""
                UPDATE dbo.PROYECTOS
                SET id_obra=?, nombre_proyecto=?, fecha_inicio_proyecto=?,
                    fecha_fin_proyecto=?, estado_proyecto=?
                WHERE id_proyecto=?;
            """, data.id_obra, data.nombre_proyecto, data.fecha_inicio_proyecto,
                 data.fecha_fin_proyecto, data.estado_proyecto, id_proyecto)
            if cur.rowcount == 0:
                raise HTTPException(status_code=404, detail="Proyecto no encontrado")
            conn.commit()
            return {**data.dict(), "id_proyecto": id_proyecto}
    except HTTPException:
        raise
    except pyodbc.IntegrityError as e:
        raise HTTPException(status_code=400, detail=f"Violación de FK/constraint: {e}")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.delete("/proyectos/{id_proyecto}", status_code=204)
def delete_proyecto(id_proyecto: int):
    try:
        with get_conn() as conn:
            cur = conn.cursor()
            cur.execute("DELETE FROM dbo.PROYECTOS WHERE id_proyecto=?;", id_proyecto)
            if cur.rowcount == 0:
                raise HTTPException(status_code=404, detail="Proyecto no encontrado")
            conn.commit()
            return
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# =============================
# PROVEEDORES (solo GET, opcional)
# =============================
@app.get("/proveedores")
def list_proveedores():
    try:
        with get_conn() as conn:
            cur = conn.cursor()
            cur.execute("""
                SELECT id_proveedor, nombre_proveedor, contacto_proveedor
                FROM dbo.PROVEEDORES ORDER BY id_proveedor DESC;
            """)
            return jsonable_encoder(rows_to_dicts(cur))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
