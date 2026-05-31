from sqlalchemy import Column, Integer, String, JSON, ForeignKey
from sqlalchemy.orm import relationship
from app.database import Base

class ExamenMedico(Base):
    __tablename__ = 'examenes_medicos'
    
    id = Column(Integer, primary_key=True, index=True)
    identificacion = Column(String, index=True)
    usuario_id = Column(Integer, ForeignKey('usuarios.id'), nullable=False)
    fecha_examen = Column(String, nullable=True)
    fecha_registro = Column(String, nullable=True)
    
    # Datos JSON para cada sección
    hemograma = Column(JSON, nullable=True)
    presionArterial = Column(JSON, nullable=True)
    glicemia = Column(JSON, nullable=True)
    coprologico = Column(JSON, nullable=True)
    uroanalisis = Column(JSON, nullable=True)
    perfilTiroideo = Column(JSON, nullable=True)
    perfilLipidico = Column(JSON, nullable=True)
    electrolitos = Column(JSON, nullable=True)
    
    # Relación con usuario
    usuario = relationship("Usuario", back_populates="examenes")