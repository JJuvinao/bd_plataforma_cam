from pydantic import BaseModel
from typing import Optional

# ---------- Sub-esquemas para cada tipo de examen ----------
class Hemograma(BaseModel):
    hb: Optional[str] = ""
    hematocrito: Optional[str] = ""
    leucocitos: Optional[str] = ""
    neutrofilos: Optional[str] = ""
    plaquetas: Optional[str] = ""
    globulosRojos: Optional[str] = ""
    recomendaciones: Optional[str] = ""

class PresionArterial(BaseModel):
    sistolica: Optional[str] = ""
    diastolica: Optional[str] = ""
    recomendaciones: Optional[str] = ""

class Glicemia(BaseModel):
    ayuno: Optional[str] = ""
    postprandial: Optional[str] = ""
    hemoglobinaGlicosilada: Optional[str] = ""
    recomendaciones: Optional[str] = ""

class Coprologico(BaseModel):
    colorHeces: Optional[str] = ""
    consistencia: Optional[str] = ""
    ph: Optional[str] = ""
    sangreOculta: Optional[str] = ""
    parasitos: Optional[str] = ""
    leucocitos: Optional[str] = ""
    eritrocitos: Optional[str] = ""
    grasaFecal: Optional[str] = ""
    recomendaciones: Optional[str] = ""

class Uroanalisis(BaseModel):
    aspecto: Optional[str] = ""
    color: Optional[str] = ""
    densidad: Optional[str] = ""
    ph: Optional[str] = ""
    proteinas: Optional[str] = ""
    glucosa: Optional[str] = ""
    cetona: Optional[str] = ""
    bilirrubina: Optional[str] = ""
    urobilinogeno: Optional[str] = ""
    globulosRojos: Optional[str] = ""
    globulosBlancos: Optional[str] = ""
    cilindros: Optional[str] = ""
    recomendaciones: Optional[str] = ""

class PerfilTiroideo(BaseModel):
    tsh: Optional[str] = ""
    t3: Optional[str] = ""
    t4Libre: Optional[str] = ""
    recomendaciones: Optional[str] = ""

class PerfilLipidico(BaseModel):
    trigliceridos: Optional[str] = ""
    colesterol: Optional[str] = ""
    hdl: Optional[str] = ""
    ldl: Optional[str] = ""
    recomendacioneslipidico: Optional[str] = ""

class Electrolitos(BaseModel):
    sodio: Optional[str] = ""
    cloro: Optional[str] = ""
    recomendaciones: Optional[str] = ""

# ---------- Esquema principal de Examen Médico ----------
class ExamenMedicoCreate(BaseModel):
    identificacion: str
    hemograma: Optional[Hemograma] = Hemograma()
    presionArterial: Optional[PresionArterial] = PresionArterial()
    glicemia: Optional[Glicemia] = Glicemia()
    coprologico: Optional[Coprologico] = Coprologico()
    uroanalisis: Optional[Uroanalisis] = Uroanalisis()
    perfilTiroideo: Optional[PerfilTiroideo] = PerfilTiroideo()
    perfilLipidico: Optional[PerfilLipidico] = PerfilLipidico()
    electrolitos: Optional[Electrolitos] = Electrolitos()

class ExamenMedicoUpdate(BaseModel):
    identificacion: Optional[str] = None
    hemograma: Optional[Hemograma] = None
    presionArterial: Optional[PresionArterial] = None
    glicemia: Optional[Glicemia] = None
    coprologico: Optional[Coprologico] = None
    uroanalisis: Optional[Uroanalisis] = None
    perfilTiroideo: Optional[PerfilTiroideo] = None
    perfilLipidico: Optional[PerfilLipidico] = None
    electrolitos: Optional[Electrolitos] = None

class ExamenMedicoResponse(BaseModel):
    id: int
    identificacion: str
    usuario_id: int
    fecha_examen: Optional[str] = None
    fecha_registro: Optional[str] = None
    hemograma: Optional[Hemograma] = None
    presionArterial: Optional[PresionArterial] = None
    glicemia: Optional[Glicemia] = None
    coprologico: Optional[Coprologico] = None
    uroanalisis: Optional[Uroanalisis] = None
    perfilTiroideo: Optional[PerfilTiroideo] = None
    perfilLipidico: Optional[PerfilLipidico] = None
    electrolitos: Optional[Electrolitos] = None
    
    class Config:
        from_attributes = True

class ExamenMedicoSimpleResponse(BaseModel):
    id: int
    identificacion: str
    fecha_registro: Optional[str] = None
    
    class Config:
        from_attributes = True