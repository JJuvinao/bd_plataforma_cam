from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from datetime import datetime
from app.database import get_db
from app.models.usuario import Usuario, RolUsuario
from app.models.examen import ExamenMedico
from app.schemas.examen_schemas import (
    ExamenMedicoCreate, ExamenMedicoUpdate, ExamenMedicoResponse
)
from app.auth import get_current_user, verificar_roles

router = APIRouter(prefix="/examenes", tags=["Exámenes Médicos"])

# Funciones auxiliares
def convertir_a_response(examen: ExamenMedico) -> ExamenMedicoResponse:
    from app.schemas.examen_schemas import (
        Hemograma, PresionArterial, Glicemia, Coprologico,
        Uroanalisis, PerfilTiroideo, PerfilLipidico, Electrolitos
    )
    
    return ExamenMedicoResponse(
        id=examen.id,
        identificacion=examen.identificacion,
        usuario_id=examen.usuario_id,
        fecha_examen=examen.fecha_examen,
        fecha_registro=examen.fecha_registro,
        hemograma=Hemograma(**examen.hemograma) if examen.hemograma else None,
        presionArterial=PresionArterial(**examen.presionArterial) if examen.presionArterial else None,
        glicemia=Glicemia(**examen.glicemia) if examen.glicemia else None,
        coprologico=Coprologico(**examen.coprologico) if examen.coprologico else None,
        uroanalisis=Uroanalisis(**examen.uroanalisis) if examen.uroanalisis else None,
        perfilTiroideo=PerfilTiroideo(**examen.perfilTiroideo) if examen.perfilTiroideo else None,
        perfilLipidico=PerfilLipidico(**examen.perfilLipidico) if examen.perfilLipidico else None,
        electrolitos=Electrolitos(**examen.electrolitos) if examen.electrolitos else None
    )

@router.post("/", response_model=ExamenMedicoResponse, status_code=status.HTTP_201_CREATED)
def crear_examen(
    examen: ExamenMedicoCreate,
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(get_current_user)
):
    try:        
        # Validar que el paciente exista
        paciente = db.query(Usuario).filter(Usuario.numeroDocumento == examen.identificacion).first()
        
        if not paciente:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"No existe un paciente con la identificación: {examen.identificacion}"
            )
        
        # Crear el examen
        nuevo_examen = ExamenMedico(
            identificacion=examen.identificacion,
            usuario_id=current_user.id,
            fecha_registro=datetime.now().isoformat(),
            hemograma=examen.hemograma.dict() if examen.hemograma else None,
            presionArterial=examen.presionArterial.dict() if examen.presionArterial else None,
            glicemia=examen.glicemia.dict() if examen.glicemia else None,
            coprologico=examen.coprologico.dict() if examen.coprologico else None,
            uroanalisis=examen.uroanalisis.dict() if examen.uroanalisis else None,
            perfilTiroideo=examen.perfilTiroideo.dict() if examen.perfilTiroideo else None,
            perfilLipidico=examen.perfilLipidico.dict() if examen.perfilLipidico else None,
            electrolitos=examen.electrolitos.dict() if examen.electrolitos else None
        )
        
        db.add(nuevo_examen)
        db.commit()
        db.refresh(nuevo_examen)
        return convertir_a_response(nuevo_examen)
    
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        print(f"❌ Error al crear examen: {str(e)}")
        import traceback
        traceback.print_exc()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error al crear examen: {str(e)}"
        )

@router.get("/", response_model=List[ExamenMedicoResponse])
def listar_mis_examenes(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(get_current_user)
):
    examenes = db.query(ExamenMedico).filter(
        ExamenMedico.usuario_id == current_user.id
    ).offset(skip).limit(limit).all()
    return [convertir_a_response(examen) for examen in examenes]

@router.get("/todos", response_model=List[ExamenMedicoResponse])
def listar_todos_examenes(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(verificar_roles([RolUsuario.ADMIN]))
):
    examenes = db.query(ExamenMedico).offset(skip).limit(limit).all()
    return [convertir_a_response(examen) for examen in examenes]

@router.get("/{examen_id}", response_model=ExamenMedicoResponse)
def obtener_examen(
    examen_id: int,
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(get_current_user)
):
    query = db.query(ExamenMedico).filter(ExamenMedico.id == examen_id)
    
    if current_user.roles == RolUsuario.CLIENTE:
        query = query.filter(ExamenMedico.usuario_id == current_user.id)
    
    examen = query.first()
    if not examen:
        raise HTTPException(status_code=404, detail="Examen no encontrado")
    
    return convertir_a_response(examen)

@router.get("/paciente/{identificacion}", response_model=List[ExamenMedicoResponse])
def buscar_examenes_por_identificacion(
    identificacion: str,
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(get_current_user)
):
    """
    Busca exámenes por número de identificación del paciente
    - CLIENTE: puede ver exámenes de cualquier paciente (sin filtrar por owner)
    - ADMIN: puede ver todos
    """
    query = db.query(ExamenMedico).filter(ExamenMedico.identificacion == identificacion)
    
    examenes = query.all()
    return [convertir_a_response(examen) for examen in examenes]

@router.put("/{examen_id}", response_model=ExamenMedicoResponse)
def actualizar_examen(
    examen_id: int,
    examen_update: ExamenMedicoUpdate,
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(get_current_user)
):
    query = db.query(ExamenMedico).filter(ExamenMedico.id == examen_id)
    
    if current_user.roles == RolUsuario.CLIENTE:
        query = query.filter(ExamenMedico.usuario_id == current_user.id)
    
    db_examen = query.first()
    if not db_examen:
        raise HTTPException(status_code=404, detail="Examen no encontrado o no tienes permiso")
    
    if examen_update.identificacion is not None:
        db_examen.identificacion = examen_update.identificacion
    if examen_update.hemograma is not None:
        db_examen.hemograma = examen_update.hemograma.dict()
    if examen_update.presionArterial is not None:
        db_examen.presionArterial = examen_update.presionArterial.dict()
    if examen_update.glicemia is not None:
        db_examen.glicemia = examen_update.glicemia.dict()
    if examen_update.coprologico is not None:
        db_examen.coprologico = examen_update.coprologico.dict()
    if examen_update.uroanalisis is not None:
        db_examen.uroanalisis = examen_update.uroanalisis.dict()
    if examen_update.perfilTiroideo is not None:
        db_examen.perfilTiroideo = examen_update.perfilTiroideo.dict()
    if examen_update.perfilLipidico is not None:
        db_examen.perfilLipidico = examen_update.perfilLipidico.dict()
    if examen_update.electrolitos is not None:
        db_examen.electrolitos = examen_update.electrolitos.dict()
    
    db_examen.fecha_registro = datetime.now().isoformat()
    
    db.commit()
    db.refresh(db_examen)
    return convertir_a_response(db_examen)

@router.delete("/{examen_id}")
def eliminar_examen(
    examen_id: int,
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(get_current_user)
):
    query = db.query(ExamenMedico).filter(ExamenMedico.id == examen_id)
    
    if current_user.roles == RolUsuario.CLIENTE:
        query = query.filter(ExamenMedico.usuario_id == current_user.id)
    
    examen = query.first()
    if not examen:
        raise HTTPException(status_code=404, detail="Examen no encontrado o no tienes permiso")
    
    db.delete(examen)
    db.commit()
    return {"mensaje": f"Examen {examen.id} eliminado exitosamente"}