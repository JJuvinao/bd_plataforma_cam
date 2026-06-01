from datetime import datetime, timedelta
from typing import Optional, Dict, Any
from jose import JWTError, jwt
from passlib.context import CryptContext
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session
from app.database import get_db
from app.models.usuario import Usuario, RolUsuario

# Configuración JWT
SECRET_KEY = "Legos-Juvinao-tu-clave-secreta-muy-segura-Plataforma-Examenes-Medicos-2026"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 3000

# Configuración de hashing
pwd_context = CryptContext(schemes=["pbkdf2_sha256"], deprecated="auto")

# Cambiar a HTTPBearer (más simple para Swagger)
security = HTTPBearer(auto_error=False)

# ---------- Funciones de Hashing ----------
def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)

def get_password_hash(password: str) -> str:
    return pwd_context.hash(password)

# ---------- Funciones de JWT ----------
def create_access_token(data: Dict[str, Any], expires_delta: Optional[timedelta] = None) -> str:
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=15)
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)

def decode_access_token(token: str) -> Dict[str, Any]:
    try:
        return jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
    except JWTError as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=f"Token inválido o expirado: {str(e)}",
            headers={"WWW-Authenticate": "Bearer"},
        )

# ---------- Funciones de Autenticación ----------
def authenticate_user(db: Session, correo: str, password: str):
    user = db.query(Usuario).filter(Usuario.correo == correo).first()
    if not user or not verify_password(password, user.hashed_password):
        return False
    return user

async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: Session = Depends(get_db)
):
    """
    Obtiene el usuario actual a partir del token Bearer
    En Swagger: Solo pega el token en el campo "Value" y haz clic en Authorize
    """
    # Si no hay credenciales
    if not credentials:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="No se proporcionó token. Ve a Authorize y pega tu token",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    # Obtener el token (ya viene sin "Bearer " automáticamente)
    token = credentials.credentials
    
    try:
        # Decodificar token
        payload = decode_access_token(token)
        correo: str = payload.get("sub")

        if correo is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Token no contiene información de usuario",
            )

        # Buscar usuario en la base de datos
        user = db.query(Usuario).filter(Usuario.correo == correo).first()

        if user is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Usuario no encontrado",
            )

        return user
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=f"Error de autenticación: {str(e)}",
        )

def verificar_roles(roles_permitidos: list[RolUsuario]):
    async def role_checker(current_user: Usuario = Depends(get_current_user)):
        if current_user.roles not in roles_permitidos:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Acceso denegado. Se requiere: {[r.value for r in roles_permitidos]}"
            )
        return current_user
    return role_checker