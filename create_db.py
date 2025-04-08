from database import Base, engine
from models import Personaje, Mision

print("Creando las tablas...")
Base.metadata.create_all(bind=engine)
print("¡Listo!")
