#!/usr/bin/env python3
"""
Script para configurar el proyecto automaticamente
"""
import os
import subprocess
import sys

def check_dependencies():
    """Verificar que todas las dependencias estan instaladas"""
    try:
        import fastapi
        import sqlalchemy
        import uvicorn
        print("Todas las dependencias estan instaladas")
    except ImportError as e:
        print(f"Error: {e}")
        print("Instala las dependencias con: pip install -r requirements.txt")
        return False
    return True

def create_env_file():
    """Crear archivo .env de ejemplo si no existe"""
    if not os.path.exists('.env'):
        with open('.env', 'w') as f:
            f.write("""# Configuración de Supabase
SUPABASE_URL=db.rjkfsnlcvootsbnoycyg.supabase.co
SUPABASE_KEY=Mateo2025@2007@

# Entorno (cambiar a 'production' en Vercel)
VERCEL_ENV=production

# Configuración local
DATABASE_URL=sqlite:///./concesionario.db
""")
        print("Archivo .env creado - configura tus variables")
    else:
        print("Archivo .env ya existe")

def setup_database():
    """Configurar base de datos local"""
    try:
        from database.local_db import Base, engine
        Base.metadata.create_all(bind=engine)
        print("Base de datos local creada")
    except Exception as e:
        print(f"Error creando BD: {e}")

def main():
    print("Configurando API Concesionario")
    
    if check_dependencies():
        create_env_file()
        setup_database()
        print("\nConfiguración completada")
        print("\nPara ejecutar localmente:")
        print("  uvicorn main:app --reload --host 0.0.0.0 --port 8000")
        print("\nAbre http://localhost:8000/docs para ver la documentación")

if __name__ == "__main__":
    main()