from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

import models
import schemas
from database import get_db

router = APIRouter(
    prefix="/api/solicitudes",
    tags=["Solicitudes"]
)


@router.post("/", response_model=schemas.SolicitudResponse, status_code=status.HTTP_201_CREATED)
def crear_solicitud(solicitud: schemas.SolicitudCreate, db: Session = Depends(get_db)):
    estudiante = db.query(models.Estudiante).filter(
        models.Estudiante.codigo_estudiante == solicitud.estudiante_id
    ).first()

    if not estudiante:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="El estudiante especificado no existe"
        )

    nueva_solicitud = models.Solicitudes(**solicitud.model_dump())
    db.add(nueva_solicitud)
    db.commit()
    db.refresh(nueva_solicitud)
    return nueva_solicitud


@router.get("/", response_model=List[schemas.SolicitudResponse])
def listar_solicitudes(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    return db.query(models.Solicitudes).offset(skip).limit(limit).all()


@router.get("/{solicitud_id}", response_model=schemas.SolicitudResponse)
def obtener_solicitud(solicitud_id: int, db: Session = Depends(get_db)):
    solicitud = db.query(models.Solicitudes).filter(
        models.Solicitudes.id_solicitudes == solicitud_id
    ).first()

    if not solicitud:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="No se encontró ninguna solicitud con ese ID"
        )
    return solicitud


@router.patch("/{solicitud_id}", response_model=schemas.SolicitudResponse)
def actualizar_estado_solicitud(solicitud_id: int, datos: schemas.SolicitudUpdate, db: Session = Depends(get_db)):
    solicitud = db.query(models.Solicitudes).filter(
        models.Solicitudes.id_solicitudes == solicitud_id
    ).first()

    if not solicitud:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="No se encontró ninguna solicitud con ese ID"
        )

    datos_actualizados = datos.model_dump(exclude_unset=True)

    for clave, valor in datos_actualizados.items():
        setattr(solicitud, clave, valor)

    db.commit()
    db.refresh(solicitud)
    return solicitud


@router.delete("/{solicitud_id}", status_code=status.HTTP_200_OK)
def borrar_solicitud(solicitud_id: int, db: Session = Depends(get_db)):
    solicitud = db.query(models.Solicitudes).filter(
        models.Solicitudes.id_solicitudes == solicitud_id
    ).first()

    if not solicitud:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="No se encontró ninguna solicitud con ese ID"
        )

    if solicitud.estado is not models.EstadoSolicitud.BORRADOR:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Solo se pueden eliminar solicitudes en estado de BORRADOR"
        )

    db.delete(solicitud)
    db.commit()
    return {"mensaje": "Solicitud eliminada con éxito"}