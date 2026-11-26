from database import Base
from sqlalchemy import Column, Date, ForeignKey, Index, Integer, String, Table, Text, UniqueConstraint,Enum as SQLEnum
from enum import Enum as enum
from sqlalchemy.orm import relationship
from datetime import date

class EstadoMatricula(str,enum):
    PENDIENTE_DE_PAGO = "PENDIENTE_DE_PAGO"
    PAGADO = "PAGADO"
    ANULADA = "ANULADA"
    NO_MATRICULADO = "NO_MATRICULADO"

class EstadoSolicitud(str,enum):
    BORRADOR    = "BORRADOR"
    ENVIADA = "ENVIADA"
    EN_REVISION = "EN_REVISION"
    OBSERVADA = "OBSERVADA"


class Estudiante(Base):
    __tablename__="estudiantes"
    codigo_estudiante=Column(String,primary_key=True,index=True)
    dni = Column(String,nullable=False,unique=True)
    nombre = Column(String,nullable=False)
    apellidos = Column(String,nullable=False)
    telefono = Column(String(9),nullable=False)
    carrera = Column(String,nullable=False)
    correo = Column(String,nullable=False,unique=True)

    matriculas = relationship("Matriculas",back_populates="Estudiante",cascade="all,delete-orphan")
    solicitudes = relationship("Solicitudes",back_populates="Estudiante",cascade="all,delete-orphan")


class Matriculas(Base):
    __tablename__="matriculas"
    id_matricula = Column(Integer,primary_key=True,index=True)
    periodo = Column(String,nullable=False)
    estado = Column(SQLEnum(EstadoMatricula),nullable=False,default=EstadoMatricula.NO_MATRICULADO)
    total_creditos = Column(Integer,nullable=False)
    fecha = Column(Date,nullable=False,default=date.today)
    estudiante_id =Column(String,ForeignKey("estudiantes.codigo_estudiante",ondelete="CASCADE"),nullable=False)

    Estudiante = relationship("Estudiante",back_populates="matriculas")

class Solicitudes(Base):
    __tablename__="solicitudes"
    id_solicitudes  = Column(Integer,primary_key=True,index=True)
    estado = Column(SQLEnum(EstadoSolicitud),nullable=False,default=EstadoSolicitud.BORRADOR)
    fecha_creacion = Column(Date,nullable=False,default=date.today)
    estudiante_id = Column(String,ForeignKey("estudiantes.codigo_estudiante",ondelete="CASCADE"),nullable=False)

    Estudiante = relationship("Estudiante",back_populates="solicitudes")
