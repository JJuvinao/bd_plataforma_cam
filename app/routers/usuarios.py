from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from typing import List
from datetime import timedelta
from app.database import get_db
from app.models.usuario import Usuario, RolUsuario
from app.schemas.usuario_schemas import (
    UsuarioCreate, UsuarioResponse, UsuarioUpdate,
    LoginRequest, TokenResponse
)
from app.auth import (
    authenticate_user, create_access_token, get_current_user,
    get_password_hash, verificar_roles, ACCESS_TOKEN_EXPIRE_MINUTES
)

router = APIRouter(prefix="/usuarios", tags=["Usuarios"])

# ---------- Endpoints ----------
@router.post("/registro", response_model=UsuarioResponse, status_code=status.HTTP_201_CREATED)
def registrar_usuario(usuario: UsuarioCreate, db: Session = Depends(get_db)):
    try:
        # Verificar si el número de documento ya existe
        db_user_by_doc = db.query(Usuario).filter(Usuario.numeroDocumento == usuario.numeroDocumento).first()
        if db_user_by_doc:
            raise HTTPException(status_code=400, detail="Ya existe un usuario con este número de documento")
        
        # Verificar si el correo ya existe
        db_user_by_email = db.query(Usuario).filter(Usuario.correo == usuario.correo).first()
        if db_user_by_email:
            raise HTTPException(status_code=400, detail="Ya existe un usuario con este correo electrónico")
        
        # Crear nuevo usuario
        hashed_password = get_password_hash(usuario.password)
        nuevo_usuario = Usuario(
            tipoDocumento=usuario.tipoDocumento,
            numeroDocumento=usuario.numeroDocumento,
            nombres=usuario.nombres,
            apellidos=usuario.apellidos,
            telefono=usuario.telefono,
            correo=usuario.correo,
            hashed_password=hashed_password,
            roles=usuario.roles
        )
        
        db.add(nuevo_usuario)
        db.commit()
        db.refresh(nuevo_usuario)
        return nuevo_usuario
    
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Error interno: {str(e)}")

@router.post("/login", response_model=TokenResponse)
def login(login_data: LoginRequest, db: Session = Depends(get_db)):
    user = authenticate_user(db, login_data.numeroDocumento, login_data.password)
    
    if not user:
        raise HTTPException(status_code=401, detail="Número de documento o contraseña incorrectos")
    
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={
            "sub": user.numeroDocumento,
            "id": user.id,
            "nombres": user.nombres,
            "apellidos": user.apellidos,
            "correo": user.correo,
            "roles": user.roles.value
        },
        expires_delta=access_token_expires
    )
    
    usuario_response = UsuarioResponse.model_validate(user)
    
    return {
        "access_token": access_token,
        "token_type": "bearer",
        "usuario": usuario_response,
        "roles": user.roles.value
    }

@router.post("/login-form", response_model=TokenResponse)
def login_form_swagger(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    user = authenticate_user(db, form_data.username, form_data.password)
    
    if not user:
        raise HTTPException(status_code=401, detail="Número de documento o contraseña incorrectos")
    
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={
            "sub": user.numeroDocumento,
            "id": user.id,
            "nombres": user.nombres,
            "apellidos": user.apellidos,
            "correo": user.correo,
            "roles": user.roles.value
        },
        expires_delta=access_token_expires
    )
    
    usuario_response = UsuarioResponse.model_validate(user)
    
    return {
        "access_token": access_token,
        "token_type": "bearer",
        "usuario": usuario_response,
        "roles": user.roles.value
    }

@router.get("/perfil", response_model=UsuarioResponse)
def obtener_perfil(current_user: Usuario = Depends(get_current_user)):
    return current_user

@router.put("/perfil", response_model=UsuarioResponse)
def actualizar_perfil(
    usuario_update: UsuarioUpdate,
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(get_current_user)
):
    try:
        if usuario_update.tipoDocumento:
            current_user.tipoDocumento = usuario_update.tipoDocumento
        if usuario_update.nombres:
            current_user.nombres = usuario_update.nombres
        if usuario_update.apellidos:
            current_user.apellidos = usuario_update.apellidos
        if usuario_update.telefono:
            current_user.telefono = usuario_update.telefono
        if usuario_update.correo:
            existing_user = db.query(Usuario).filter(Usuario.correo == usuario_update.correo).first()
            if existing_user and existing_user.id != current_user.id:
                raise HTTPException(status_code=400, detail="El correo ya está en uso")
            current_user.correo = usuario_update.correo
        if usuario_update.roles:
            if current_user.roles != RolUsuario.ADMIN:
                raise HTTPException(status_code=403, detail="No tienes permiso para cambiar roles")
            current_user.roles = usuario_update.roles
        
        db.commit()
        db.refresh(current_user)
        return current_user
    
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Error al actualizar: {str(e)}")

@router.get("/", response_model=List[UsuarioResponse])
def listar_usuarios(
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(verificar_roles([RolUsuario.ADMIN]))
):
    return db.query(Usuario).all()

@router.get("/{usuario_id}", response_model=UsuarioResponse)
def obtener_usuario_por_id(
    usuario_id: int,
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(verificar_roles([RolUsuario.ADMIN]))
):
    usuario = db.query(Usuario).filter(Usuario.id == usuario_id).first()
    if not usuario:
        raise HTTPException(status_code=404, detail="Usuario no encontrado")
    return usuario

@router.delete("/{usuario_id}")
def eliminar_usuario(
    usuario_id: int,
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(verificar_roles([RolUsuario.ADMIN]))
):
    usuario = db.query(Usuario).filter(Usuario.id == usuario_id).first()
    if not usuario:
        raise HTTPException(status_code=404, detail="Usuario no encontrado")
    
    if usuario.id == current_user.id:
        raise HTTPException(status_code=400, detail="No puedes eliminarte a ti mismo")
    
    db.delete(usuario)
    db.commit()
    return {"mensaje": f"Usuario {usuario.nombres} {usuario.apellidos} eliminado exitosamente"}