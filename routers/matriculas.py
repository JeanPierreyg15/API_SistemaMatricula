from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import and_
from sqlalchemy.orm import Session

import models
import schemas
from database import get_db

router = APIRouter(
    prefix="/api/matriculas",
    tags=["Matrículas"]
)


@router.post("/", response_model=schemas.MatriculaResponse, status_code=status.HTTP_201_CREATED)
def registrar_matricula(matricula: schemas.MatriculaCreate, db: Session = Depends(get_db)):
    estudiante = db.query(models.Estudiante).filter(
        models.Estudiante.codigo_estudiante == matricula.estudiante_id
    ).first()

    if not estudiante:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="El estudiante especificado no existe"
        )

    matricula_duplicada = db.query(models.Matriculas).filter(
        and_(
            models.Matriculas.estudiante_id == matricula.estudiante_id,
            models.Matriculas.periodo == matricula.periodo
        )
    ).first()

    if matricula_duplicada:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"El estudiante ya tiene una matrícula registrada en el periodo {matricula.periodo}"
        )

    nueva_matricula = models.Matriculas(**matricula.model_dump())
    db.add(nueva_matricula)
    db.commit()
    db.refresh(nueva_matricula)
    return nueva_matricula


@router.get("/", response_model=List[schemas.MatriculaResponse])
def listar_matriculas(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    return db.query(models.Matriculas).offset(skip).limit(limit).all()


@router.get("/{matricula_id}", response_model=schemas.MatriculaResponse)
def consultar_matricula(matricula_id: int, db: Session = Depends(get_db)):
    matricula = db.query(models.Matriculas).filter(
        models.Matriculas.id_matricula == matricula_id
    ).first()

    if not matricula:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="No hay una matrícula asignada a ese ID"
        )
    return matricula


@router.patch("/{matricula_id}", response_model=schemas.MatriculaResponse)
def editar_matricula(matricula_id: int, datos: schemas.MatriculaUpdate, db: Session = Depends(get_db)):
    matricula = db.query(models.Matriculas).filter(
        models.Matriculas.id_matricula == matricula_id
    ).first()

    if not matricula:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="No hay una matrícula asignada a ese ID"
        )

    datos_actualizados = datos.model_dump(exclude_unset=True)

    for clave, valor in datos_actualizados.items():
        setattr(matricula, clave, valor)

    db.commit()
    db.refresh(matricula)
    return matricula


@router.delete("/{matricula_id}", status_code=status.HTTP_200_OK)
def eliminar_matricula(matricula_id: int, db: Session = Depends(get_db)):
    matricula = db.query(models.Matriculas).filter(
        models.Matriculas.id_matricula == matricula_id
    ).first()

    if not matricula:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="No hay una matrícula asignada a ese ID"
        )

    db.delete(matricula)
    db.commit()
    return {"mensaje": "Matrícula eliminada con éxito"}