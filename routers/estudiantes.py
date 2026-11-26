from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import and_, or_
from sqlalchemy.orm import Session

import models
import schemas
from database import get_db

router = APIRouter(
    prefix="/api/estudiantes",
    tags=["Estudiantes"]
)


@router.post("/", response_model=schemas.EstudianteResponse, status_code=status.HTTP_201_CREATED)
def registrar_estudiante(estudiante: schemas.EstudianteCreate, db: Session = Depends(get_db)):
    existe = db.query(models.Estudiante).filter(
        or_(
            models.Estudiante.codigo_estudiante == estudiante.codigo_estudiante,
            models.Estudiante.dni == estudiante.dni,
            models.Estudiante.correo == estudiante.correo
        )
    ).first()

    if existe:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="El código, DNI o correo ya está registrado"
        )

    nuevo_estudiante = models.Estudiante(**estudiante.model_dump())
    db.add(nuevo_estudiante)
    db.commit()
    db.refresh(nuevo_estudiante)
    return nuevo_estudiante


@router.get("/", response_model=List[schemas.EstudianteResponse])
def listar_estudiantes(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    return db.query(models.Estudiante).offset(skip).limit(limit).all()


@router.get("/{codigo_estudiante}", response_model=schemas.EstudianteResponse)
def obtener_estudiante(codigo_estudiante: str, db: Session = Depends(get_db)):
    estudiante = db.query(models.Estudiante).filter(
        models.Estudiante.codigo_estudiante == codigo_estudiante
    ).first()

    if not estudiante:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="No se encontró un estudiante con ese código"
        )
    return estudiante


@router.patch("/{codigo_estudiante}", response_model=schemas.EstudianteResponse)
def editar_estudiante(codigo_estudiante: str, datos: schemas.EstudianteUpdate, db: Session = Depends(get_db)):
    estudiante = db.query(models.Estudiante).filter(
        models.Estudiante.codigo_estudiante == codigo_estudiante
    ).first()

    if not estudiante:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="No se encontró un alumno con ese código de estudiante"
        )

    datos_actualizados = datos.model_dump(exclude_unset=True)

    if "correo" in datos_actualizados:
        correo_en_uso = db.query(models.Estudiante).filter(
            and_(
                models.Estudiante.correo == datos_actualizados["correo"],
                models.Estudiante.codigo_estudiante != codigo_estudiante
            )
        ).first()
        if correo_en_uso:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Ese correo ya está registrado por otro estudiante"
            )

    for clave, valor in datos_actualizados.items():
        setattr(estudiante, clave, valor)

    db.commit()
    db.refresh(estudiante)
    return estudiante


@router.delete("/{codigo_estudiante}", status_code=status.HTTP_200_OK)
def eliminar_estudiante(codigo_estudiante: str, db: Session = Depends(get_db)):
    estudiante = db.query(models.Estudiante).filter(
        models.Estudiante.codigo_estudiante == codigo_estudiante
    ).first()

    if not estudiante:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="No se encontró un estudiante con ese código"
        )

    tiene_matriculas = db.query(models.Matriculas).filter(
        models.Matriculas.estudiante_id == codigo_estudiante
    ).first()
    tiene_solicitudes = db.query(models.Solicitudes).filter(
        models.Solicitudes.estudiante_id == codigo_estudiante
    ).first()

    if tiene_matriculas or tiene_solicitudes:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="No se puede eliminar un estudiante con matrículas o solicitudes asociadas"
        )

    db.delete(estudiante)
    db.commit()
    return {"mensaje": "Estudiante eliminado con éxito"}