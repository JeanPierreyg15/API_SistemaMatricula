from typing import Optional
from datetime import date
from pydantic import BaseModel, ConfigDict, EmailStr, Field, field_validator
from models import EstadoMatricula, EstadoSolicitud


class EstudianteBase(BaseModel):
    correo: EmailStr
    dni: str = Field(min_length=8, max_length=8, pattern=r"^\d{8}$")
    codigo_estudiante: str = Field(min_length=8, max_length=8, pattern=r"^\d{8}$")
    nombre: str
    apellidos: str
    carrera: str
    telefono: str = Field(min_length=9, max_length=9, pattern=r"^9\d{8}$")

    @field_validator("codigo_estudiante")
    @classmethod
    def validar_codigo(cls, valor: str):
        inicio_codigo = int(valor[:2])
        if 10 > inicio_codigo or inicio_codigo > 26:
            raise ValueError("El año de ingreso debe estar entre 10 y 26")
        return valor


class EstudianteCreate(EstudianteBase):
    pass


class EstudianteUpdate(BaseModel):
    correo: Optional[EmailStr] = None
    telefono: Optional[str] = Field(default=None, min_length=9, max_length=9, pattern=r"^9\d{8}$")
    nombre: Optional[str] = None
    apellidos: Optional[str] = None
    carrera: Optional[str] = None


class EstudianteResponse(EstudianteBase):
    model_config = ConfigDict(from_attributes=True)



class MatriculaBase(BaseModel):
    periodo: str
    total_creditos: int = Field(gt=0, le=30)
    estudiante_id: str = Field(min_length=8, max_length=8, pattern=r"^\d{8}$")


class MatriculaCreate(MatriculaBase):
    estado: EstadoMatricula = EstadoMatricula.NO_MATRICULADO


class MatriculaUpdate(BaseModel):
    periodo: Optional[str] = None
    total_creditos: Optional[int] = Field(default=None, gt=0, le=30)
    estado: Optional[EstadoMatricula] = None


class MatriculaResponse(MatriculaBase):
    id_matricula: int
    estado: EstadoMatricula
    fecha: date
    Estudiante: EstudianteResponse

    model_config = ConfigDict(from_attributes=True)


class SolicitudBase(BaseModel):
    estudiante_id: str = Field(min_length=8, max_length=8, pattern=r"^\d{8}$")


class SolicitudCreate(SolicitudBase):
    estado: EstadoSolicitud = EstadoSolicitud.BORRADOR


class SolicitudUpdate(BaseModel):
    estado: Optional[EstadoSolicitud] = None


class SolicitudResponse(SolicitudBase):
    id_solicitudes: int
    estado: EstadoSolicitud
    fecha_creacion: date
    Estudiante: EstudianteResponse

    model_config = ConfigDict(from_attributes=True)