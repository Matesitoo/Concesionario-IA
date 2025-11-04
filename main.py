from fastapi import FastAPI, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
from typing import List, Optional
import os
from dotenv import load_dotenv

# Cargar variables de entorno
load_dotenv()

# Importar configuraciones de base de datos
if os.getenv("VERCEL_ENV"):
    from database.supabase_db import get_db, Cliente, Auto, Pedido, EstadoPedido, TipoCombustible
else:
    from database.local_db import get_db, Cliente, Auto, Pedido, EstadoPedido, TipoCombustible

# Modelos Pydantic
from pydantic import BaseModel
from datetime import datetime
from enum import Enum as PyEnum

app = FastAPI(title="Concesionario API", version="1.0.0")

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Enums para estados (usando PyEnum para Pydantic)
class EstadoPedidoStr(str, PyEnum):
    PENDIENTE = "pendiente"
    APROBADO = "aprobado"
    ENTREGADO = "entregado"
    CANCELADO = "cancelado"

class TipoCombustibleStr(str, PyEnum):
    GASOLINA = "gasolina"
    DIESEL = "diesel"
    ELECTRICO = "eléctrico"
    HIBRIDO = "híbrido"

# Modelos Pydantic
class ClienteBase(BaseModel):
    nombre: str
    email: str
    telefono: str
    direccion: str

class ClienteCreate(ClienteBase):
    pass

class ClienteResponse(ClienteBase):
    id: int
    
    class Config:
        from_attributes = True

class AutoBase(BaseModel):
    marca: str
    modelo: str
    año: int
    precio: float
    color: str
    combustible: TipoCombustibleStr
    disponible: bool = True

class AutoCreate(AutoBase):
    pass

class AutoResponse(AutoBase):
    id: int
    
    class Config:
        from_attributes = True

class PedidoBase(BaseModel):
    cliente_id: int
    auto_id: int
    estado: EstadoPedidoStr = EstadoPedidoStr.PENDIENTE
    total: float

class PedidoCreate(PedidoBase):
    pass

class PedidoResponse(PedidoBase):
    id: int
    fecha_pedido: datetime
    cliente: ClienteResponse
    auto: AutoResponse
    
    class Config:
        from_attributes = True

# Endpoints de Clientes
@app.post("/clientes/", response_model=ClienteResponse)
def crear_cliente(cliente: ClienteCreate, db=Depends(get_db)):
    try:
        db_cliente = Cliente(**cliente.dict())
        db.add(db_cliente)
        db.commit()
        db.refresh(db_cliente)
        return db_cliente
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=400, detail=f"Error creando cliente: {str(e)}")

@app.get("/clientes/", response_model=List[ClienteResponse])
def listar_clientes(skip: int = 0, limit: int = 100, db=Depends(get_db)):
    clientes = db.query(Cliente).offset(skip).limit(limit).all()
    return clientes

@app.get("/clientes/{cliente_id}", response_model=ClienteResponse)
def obtener_cliente(cliente_id: int, db=Depends(get_db)):
    cliente = db.query(Cliente).filter(Cliente.id == cliente_id).first()
    if cliente is None:
        raise HTTPException(status_code=404, detail="Cliente no encontrado")
    return cliente

@app.put("/clientes/{cliente_id}", response_model=ClienteResponse)
def actualizar_cliente(cliente_id: int, cliente: ClienteCreate, db=Depends(get_db)):
    db_cliente = db.query(Cliente).filter(Cliente.id == cliente_id).first()
    if db_cliente is None:
        raise HTTPException(status_code=404, detail="Cliente no encontrado")
    
    try:
        for key, value in cliente.dict().items():
            setattr(db_cliente, key, value)
        
        db.commit()
        db.refresh(db_cliente)
        return db_cliente
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=400, detail=f"Error actualizando cliente: {str(e)}")

@app.delete("/clientes/{cliente_id}")
def eliminar_cliente(cliente_id: int, db=Depends(get_db)):
    cliente = db.query(Cliente).filter(Cliente.id == cliente_id).first()
    if cliente is None:
        raise HTTPException(status_code=404, detail="Cliente no encontrado")
    
    try:
        db.delete(cliente)
        db.commit()
        return {"message": "Cliente eliminado correctamente"}
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=400, detail=f"Error eliminando cliente: {str(e)}")

@app.get("/clientes/buscar/{nombre}", response_model=List[ClienteResponse])
def buscar_clientes_por_nombre(nombre: str, db=Depends(get_db)):
    clientes = db.query(Cliente).filter(Cliente.nombre.ilike(f"%{nombre}%")).all()
    return clientes

# Endpoints de Autos
@app.post("/autos/", response_model=AutoResponse)
def crear_auto(auto: AutoCreate, db=Depends(get_db)):
    try:
        # Convertir el enum de string a el enum de SQLAlchemy
        auto_data = auto.dict()
        auto_data['combustible'] = getattr(TipoCombustible, auto_data['combustible'].upper())
        
        db_auto = Auto(**auto_data)
        db.add(db_auto)
        db.commit()
        db.refresh(db_auto)
        
        # Convertir de vuelta para la respuesta
        response_auto = AutoResponse.from_orm(db_auto)
        return response_auto
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=400, detail=f"Error creando auto: {str(e)}")

@app.get("/autos/", response_model=List[AutoResponse])
def listar_autos(
    skip: int = 0, 
    limit: int = 100, 
    marca: Optional[str] = None,
    disponible: Optional[bool] = None,
    db=Depends(get_db)
):
    try:
        query = db.query(Auto)
        
        if marca:
            query = query.filter(Auto.marca.ilike(f"%{marca}%"))
        if disponible is not None:
            query = query.filter(Auto.disponible == disponible)
        
        autos = query.offset(skip).limit(limit).all()
        return autos
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error listando autos: {str(e)}")

@app.get("/autos/{auto_id}", response_model=AutoResponse)
def obtener_auto(auto_id: int, db=Depends(get_db)):
    try:
        auto = db.query(Auto).filter(Auto.id == auto_id).first()
        if auto is None:
            raise HTTPException(status_code=404, detail="Auto no encontrado")
        return auto
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error obteniendo auto: {str(e)}")

@app.put("/autos/{auto_id}", response_model=AutoResponse)
def actualizar_auto(auto_id: int, auto: AutoCreate, db=Depends(get_db)):
    db_auto = db.query(Auto).filter(Auto.id == auto_id).first()
    if db_auto is None:
        raise HTTPException(status_code=404, detail="Auto no encontrado")
    
    try:
        auto_data = auto.dict()
        auto_data['combustible'] = getattr(TipoCombustible, auto_data['combustible'].upper())
        
        for key, value in auto_data.items():
            setattr(db_auto, key, value)
        
        db.commit()
        db.refresh(db_auto)
        return db_auto
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=400, detail=f"Error actualizando auto: {str(e)}")

@app.delete("/autos/{auto_id}")
def eliminar_auto(auto_id: int, db=Depends(get_db)):
    auto = db.query(Auto).filter(Auto.id == auto_id).first()
    if auto is None:
        raise HTTPException(status_code=404, detail="Auto no encontrado")
    
    try:
        db.delete(auto)
        db.commit()
        return {"message": "Auto eliminado correctamente"}
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=400, detail=f"Error eliminando auto: {str(e)}")

@app.get("/autos/buscar/{modelo}", response_model=List[AutoResponse])
def buscar_autos_por_modelo(modelo: str, db=Depends(get_db)):
    try:
        autos = db.query(Auto).filter(Auto.modelo.ilike(f"%{modelo}%")).all()
        return autos
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error buscando autos: {str(e)}")

# Endpoints de Pedidos
@app.post("/pedidos/", response_model=PedidoResponse)
def crear_pedido(pedido: PedidoCreate, db=Depends(get_db)):
    try:
        # Verificar que el cliente existe
        cliente = db.query(Cliente).filter(Cliente.id == pedido.cliente_id).first()
        if not cliente:
            raise HTTPException(status_code=404, detail="Cliente no encontrado")
        
        # Verificar que el auto existe
        auto = db.query(Auto).filter(Auto.id == pedido.auto_id).first()
        if not auto:
            raise HTTPException(status_code=404, detail="Auto no encontrado")
        
        # Convertir el enum de string a el enum de SQLAlchemy
        pedido_data = pedido.dict()
        pedido_data['estado'] = getattr(EstadoPedido, pedido_data['estado'].upper())
        
        # Crear pedido
        db_pedido = Pedido(**pedido_data)
        db.add(db_pedido)
        db.commit()
        db.refresh(db_pedido)
        
        # Las relaciones se cargan automaticamente gracias a SQLAlchemy
        return db_pedido
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=400, detail=f"Error creando pedido: {str(e)}")

@app.get("/pedidos/", response_model=List[PedidoResponse])
def listar_pedidos(
    skip: int = 0, 
    limit: int = 100, 
    estado: Optional[EstadoPedidoStr] = None,
    db=Depends(get_db)
):
    try:
        query = db.query(Pedido)
        
        if estado:
            # Convertir el enum de string a el enum de SQLAlchemy
            estado_db = getattr(EstadoPedido, estado.upper())
            query = query.filter(Pedido.estado == estado_db)
        
        pedidos = query.offset(skip).limit(limit).all()
        return pedidos
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error listando pedidos: {str(e)}")

@app.get("/pedidos/{pedido_id}", response_model=PedidoResponse)
def obtener_pedido(pedido_id: int, db=Depends(get_db)):
    try:
        pedido = db.query(Pedido).filter(Pedido.id == pedido_id).first()
        if pedido is None:
            raise HTTPException(status_code=404, detail="Pedido no encontrado")
        return pedido
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error obteniendo pedido: {str(e)}")

@app.put("/pedidos/{pedido_id}", response_model=PedidoResponse)
def actualizar_pedido(pedido_id: int, pedido: PedidoCreate, db=Depends(get_db)):
    db_pedido = db.query(Pedido).filter(Pedido.id == pedido_id).first()
    if db_pedido is None:
        raise HTTPException(status_code=404, detail="Pedido no encontrado")
    
    try:
        pedido_data = pedido.dict()
        pedido_data['estado'] = getattr(EstadoPedido, pedido_data['estado'].upper())
        
        for key, value in pedido_data.items():
            setattr(db_pedido, key, value)
        
        db.commit()
        db.refresh(db_pedido)
        return db_pedido
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=400, detail=f"Error actualizando pedido: {str(e)}")

@app.delete("/pedidos/{pedido_id}")
def eliminar_pedido(pedido_id: int, db=Depends(get_db)):
    pedido = db.query(Pedido).filter(Pedido.id == pedido_id).first()
    if pedido is None:
        raise HTTPException(status_code=404, detail="Pedido no encontrado")
    
    try:
        db.delete(pedido)
        db.commit()
        return {"message": "Pedido eliminado correctamente"}
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=400, detail=f"Error eliminando pedido: {str(e)}")

@app.get("/pedidos/cliente/{cliente_id}", response_model=List[PedidoResponse])
def obtener_pedidos_por_cliente(cliente_id: int, db=Depends(get_db)):
    try:
        pedidos = db.query(Pedido).filter(Pedido.cliente_id == cliente_id).all()
        return pedidos
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error obteniendo pedidos del cliente: {str(e)}")

@app.put("/pedidos/{pedido_id}/estado")
def actualizar_estado_pedido(pedido_id: int, estado: EstadoPedidoStr, db=Depends(get_db)):
    pedido = db.query(Pedido).filter(Pedido.id == pedido_id).first()
    if pedido is None:
        raise HTTPException(status_code=404, detail="Pedido no encontrado")
    
    try:
        pedido.estado = getattr(EstadoPedido, estado.upper())
        db.commit()
        
        return {"message": f"Estado del pedido actualizado a {estado}"}
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=400, detail=f"Error actualizando estado: {str(e)}")

# Para mirar
@app.get("/")
def read_root():
    return {"message": "API Concesionario funcionando correctamente"}

@app.get("/docs")
def read_docs():
    return {"message": "Documentacion disponible en /docs"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)