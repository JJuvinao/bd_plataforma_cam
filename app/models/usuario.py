from sqlalchemy import Column, Integer, String, Boolean, Enum
from sqlalchemy.orm import relationship
import enum
from app.database import Base

class RolUsuario(str, enum.Enum):
    ADMIN = "ADMIN"
    CLIENTE = "CLIENTE"

class Usuario(Base):
    __tablename__ = 'usuarios'
    
    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    tipoDocumento = Column(String, nullable=False)
    numeroDocumento = Column(String, unique=True, index=True, nullable=False)
    nombres = Column(String, nullable=False)
    apellidos = Column(String, nullable=False)
    telefono = Column(String, nullable=False)
    correo = Column(String, unique=True, index=True, nullable=False)
    hashed_password = Column(String, nullable=False)
    roles = Column(Enum(RolUsuario), default=RolUsuario.CLIENTE)
    is_active = Column(Boolean, default=True)
    
    # Relación con exámenes médicos
    examenes = relationship("ExamenMedico", back_populates="usuario")