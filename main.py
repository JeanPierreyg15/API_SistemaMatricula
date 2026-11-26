from fastapi import FastAPI
import models
from database import engine
from routers import estudiantes, matriculas, solicitudes

models.Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="API Sistema de Matrícula Universitaria",
    description="API RESTful para la gestión de estudiantes, matrículas y solicitudes académicas.",
)

app.include_router(estudiantes.router)
app.include_router(matriculas.router)
app.include_router(solicitudes.router)


@app.get("/", tags=["Inicio"])
def root():
    return {"mensaje": "API Sistema de Matrícula Universitaria operativa. Visita /docs para la documentación."}