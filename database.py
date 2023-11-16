from flask import Flask
from sqlalchemy import create_engine, text
from sqlalchemy.orm import scoped_session, sessionmaker
from dotenv import load_dotenv
import os

load_dotenv(override=True)

DATABASE_URL = os.getenv("DATABASE_URL")

if not DATABASE_URL:
    raise Exception("DATABASE_URL environment variable is not set")

engine = create_engine(DATABASE_URL)
db = scoped_session(sessionmaker(bind=engine))

def create_tables():
    tabla_estudiantes = """
        CREATE TABLE Estudiantes (
            EstudianteID TEXT PRIMARY KEY,
            Nombre VARCHAR(50),
            Apellido VARCHAR(50),
            FechaNacimiento DATE,
            Telefono VARCHAR(15),
            CorreoElectronico VARCHAR(100),
            SEMESTRE INT UNIQUE
        )
    """
    tabla_profesores = """
        CREATE TABLE Profesores (
            cedula_profesor TEXT PRIMARY KEY,
            NombreProfesor VARCHAR(50),
            ApellidoProfesor VARCHAR(50),
            CorreoElectronico VARCHAR(100),
            Especializacion VARCHAR(100)
        )
    """
    
    
    tabla_cursos = """
        CREATE TABLE Cursos (
            CursoID INT PRIMARY KEY,
            NombreCurso VARCHAR(100),
            DescripcionCurso TEXT,
            creditos INT,
            SEMESTRE INT,
            FOREIGN KEY (ProfesorID) REFERENCES Profesores (cedula_profesor)
        )
    """


    tabla_matricula = """
        CREATE TABLE Matricula (
            MatriculaID INT PRIMARY KEY,
            EstudianteID TEXT,
            CursoID INT,
            AnoAcademico INT,
            estudianteSemestre INT,
            cursoSemestre INT,
            FOREIGN KEY (estudianteSemestre) REFERENCES Estudiantes (SEMESTRE),
            FOREIGN KEY (cursoSemestre) REFERENCES Estudiantes (SEMESTRE),
            FOREIGN KEY (EstudianteID) REFERENCES Estudiantes (EstudianteID),
            FOREIGN KEY (CursoID) REFERENCES Cursos (CursoID)
        )
    """

    tabla_calificaciones = """
        CREATE TABLE Calificaciones (
            CalificacionID INT PRIMARY KEY,
            EstudianteID TEXT,
            CursoID INT,
            Nota DECIMAL(3, 2),
            FOREIGN KEY (EstudianteID) REFERENCES Estudiantes (EstudianteID),
            FOREIGN KEY (CursoID) REFERENCES Cursos (CursoID)
        )
    """

    try:
        for tabla in [tabla_estudiantes, tabla_cursos, tabla_profesores, tabla_matricula, tabla_calificaciones]:
            db.execute(text(tabla))
        db.commit()
        print("La base de datos fue creada")
    except Exception as e:
        print(f"Error al crear la base de datos: {e}")
        db.rollback()

def main():
    print("Creando la base de datos")
    create_tables()

if __name__ == "__main__":
    main()
