from pydantic import BaseModel, EmailStr, Field
from typing import Optional
from app.models.usuario import RolUsuario

# ---------- Esquemas de Usuario ----------
class UsuarioCreate(BaseModel):
    tipoDocumento: str = Field(..., description="Tipo de documento: CC, CE, NIT, etc.")
    numeroDocumento: str = Field(..., description="Número de documento")
    nombres: str = Field(..., min_length=2, max_length=100)
    apellidos: str = Field(..., min_length=2, max_length=100)
    telefono: str = Field(..., description="Número de teléfono")
    correo: EmailStr = Field(..., description="Correo electrónico")
    password: str = Field(..., min_length=6, description="Contraseña (mínimo 6 caracteres)")
    roles: RolUsuario = Field(default=RolUsuario.CLIENTE)

class UsuarioResponse(BaseModel):
    id: int
    tipoDocumento: str
    numeroDocumento: str
    nombres: str
    apellidos: str
    telefono: str
    correo: str
    roles: RolUsuario
    is_active: bool
    
    class Config:
        from_attributes = True

class UsuarioUpdate(BaseModel):
    tipoDocumento: Optional[str] = None
    nombres: Optional[str] = None
    apellidos: Optional[str] = None
    telefono: Optional[str] = None
    correo: Optional[EmailStr] = None
    roles: Optional[RolUsuario] = None

class LoginRequest(BaseModel):
    numeroDocumento: str
    password: str

class TokenResponse(BaseModel):
    access_token: str
    token_type: str
    usuario: UsuarioResponse
    roles: str