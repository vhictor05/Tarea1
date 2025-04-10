from fastapi import FastAPI, Depends, HTTPException
from sqlalchemy.orm import Session
import models, schemas
from database import SessionLocal, engine
from fastapi import status

# Crear las tablas en la base de datos
models.Base.metadata.create_all(bind=engine)

# Inicializar FastAPI
app = FastAPI()

# Dependencia para obtener la sesión de base de datos por cada request
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# Endpoint para crear un personaje
@app.post("/personajes", response_model=schemas.Personaje)
def crear_personaje(personaje: schemas.PersonajeCreate, db: Session = Depends(get_db)):
    nuevo = models.Personaje(nombre=personaje.nombre)
    db.add(nuevo)
    db.commit()
    db.refresh(nuevo)
    return nuevo

@app.post("/misiones", response_model=schemas.Mision)
def crear_mision(mision: schemas.MisionCreate, db: Session = Depends(get_db)):
    nueva_mision = models.Mision(
        descripcion=mision.descripcion,
        recompensa_xp=mision.recompensa_xp
    )
    db.add(nueva_mision)
    db.commit()
    db.refresh(nueva_mision)
    return nueva_mision

@app.post("/personajes/{personaje_id}/misiones/{mision_id}", response_model=schemas.Personaje)
def aceptar_mision(personaje_id: int, mision_id: int, db: Session = Depends(get_db)):
    personaje = db.query(models.Personaje).filter(models.Personaje.id == personaje_id).first()
    if not personaje:
        raise HTTPException(status_code=404, detail="Personaje no encontrado")

    mision = db.query(models.Mision).filter(models.Mision.id == mision_id).first()
    if not mision:
        raise HTTPException(status_code=404, detail="Misión no encontrada")

    if mision not in personaje.misiones:
        personaje.misiones.append(mision)
        db.commit()
        db.refresh(personaje)

    return personaje

@app.post("/personajes/{id}/completar", response_model=schemas.Personaje)
def completar_mision(id: int, db: Session = Depends(get_db)):
    personaje = db.query(models.Personaje).filter(models.Personaje.id == id).first()

    if not personaje:
        raise HTTPException(status_code=404, detail="Personaje no encontrado")

    if not personaje.misiones:
        raise HTTPException(status_code=400, detail="No hay misiones para completar")

    # FIFO: la primera misión agregada es la primera que se completa
    mision = personaje.misiones[0]

    # Sumar XP
    personaje.experiencia += mision.recompensa_xp

    # Eliminar misión de la lista (desencolar)
    personaje.misiones.remove(mision)

    db.commit()
    db.refresh(personaje)
    return personaje

@app.get("/personajes/{personaje_id}/misiones", response_model=list[schemas.Mision])
def listar_misiones_personaje(
    personaje_id: int,
    db: Session = Depends(get_db)
):
    personaje = db.query(models.Personaje).filter(models.Personaje.id == personaje_id).first()
    if not personaje:
        raise HTTPException(status_code=404, detail="Personaje no encontrado")
    
    return personaje.misiones  # Como es una lista, ya respeta el orden de inserción



@app.delete("/misiones/{id}", status_code=status.HTTP_204_NO_CONTENT)
def eliminar_mision(id: int, db: Session = Depends(get_db)):
    mision = db.query(models.Mision).filter(models.Mision.id == id).first()

    if not mision:
        raise HTTPException(status_code=404, detail="Misión no encontrada")

    # Eliminar relaciones en la tabla intermedia antes de borrar
    for personaje in mision.personajes:
        personaje.misiones.remove(mision)

    db.delete(mision)
    db.commit()
    return



@app.delete("/personajes/{id}", status_code=status.HTTP_204_NO_CONTENT)
def eliminar_personaje(id: int, db: Session = Depends(get_db)):
    personaje = db.query(models.Personaje).filter(models.Personaje.id == id).first()

    if not personaje:
        raise HTTPException(status_code=404, detail="Personaje no encontrado")

    # Eliminar relaciones en la tabla intermedia antes de borrar
    for mision in personaje.misiones:
        personaje.misiones.remove(mision)

    db.delete(personaje)
    db.commit()
    return





#uvicorn main:app --reload
