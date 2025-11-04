from sqlalchemy import create_engine, Column, Integer, String, Float, Boolean, DateTime, ForeignKey, Enum
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, relationship
import datetime
import enum

# Base de datos SQLite
SQLALCHEMY_DATABASE_URL = "sqlite:///./concesionario.db"

engine = create_engine(SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()

# Enums
class EstadoPedido(enum.Enum):
    PENDIENTE = "pendiente"
    APROBADO = "aprobado"
    ENTREGADO = "entregado"
    CANCELADO = "cancelado"

class TipoCombustible(enum.Enum):
    GASOLINA = "gasolina"
    DIESEL = "diesel"
    ELECTRICO = "eléctrico"
    HIBRIDO = "híbrido"

# Modelos de base de datos
class Cliente(Base):
    __tablename__ = "clientes"
    
    id = Column(Integer, primary_key=True, index=True)
    nombre = Column(String, index=True)
    email = Column(String, unique=True, index=True)
    telefono = Column(String)
    direccion = Column(String)
    
    # Relacion con pedidos
    pedidos = relationship("Pedido", back_populates="cliente")

class Auto(Base):
    __tablename__ = "autos"
    
    id = Column(Integer, primary_key=True, index=True)
    marca = Column(String, index=True)
    modelo = Column(String, index=True)
    año = Column(Integer)
    precio = Column(Float)
    color = Column(String)
    combustible = Column(Enum(TipoCombustible))
    disponible = Column(Boolean, default=True)
    
    # Relacion con pedidos
    pedidos = relationship("Pedido", back_populates="auto")

class Pedido(Base):
    __tablename__ = "pedidos"
    
    id = Column(Integer, primary_key=True, index=True)
    cliente_id = Column(Integer, ForeignKey("clientes.id"))
    auto_id = Column(Integer, ForeignKey("autos.id"))
    fecha_pedido = Column(DateTime, default=datetime.datetime.utcnow)
    estado = Column(Enum(EstadoPedido), default=EstadoPedido.PENDIENTE)
    total = Column(Float)
    
    # Relaciones
    cliente = relationship("Cliente", back_populates="pedidos")
    auto = relationship("Auto", back_populates="pedidos")

# Crear tablas
Base.metadata.create_all(bind=engine)

# Dependencia de base de datos
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()