from flask import Flask
from sqlalchemy import create_engine, text
import os
from sqlalchemy import create_engine
from sqlalchemy.orm import scoped_session, sessionmaker
from dotenv import load_dotenv

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
            CorreoElectronico VARCHAR(100)
        )
    """

    tabla_cursos = """
        CREATE TABLE Cursos (
            CursoID INT PRIMARY KEY,
            NombreCurso VARCHAR(100),
            DescripcionCurso TEXT,
            creditos INT
        )
    """

    db.execute(text(tabla_estudiantes))
    db.execute(text(tabla_cursos))

    tabla_profesores = """
        CREATE TABLE Profesores (
            cedula_profesor TEXT PRIMARY KEY,
            NombreProfesor VARCHAR(50),
            ApellidoProfesor VARCHAR(50),
            CorreoElectronico VARCHAR(100),
            Especializacion VARCHAR(100)
        )
    """

    db.execute(text(tabla_profesores))

    tabla_matricula = """
        CREATE TABLE Matricula (
            MatriculaID INT PRIMARY KEY,
            EstudianteID TEXT,
            CursoID INT,
            ProfesorID TEXT,
            AnoAcademico INT,
            FOREIGN KEY (EstudianteID) REFERENCES Estudiantes (EstudianteID),
            FOREIGN KEY (CursoID) REFERENCES Cursos (CursoID),
            FOREIGN KEY (ProfesorID) REFERENCES Profesores (cedula_profesor)
        )
    """

    db.execute(text(tabla_matricula))

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

    db.execute(text(tabla_calificaciones))

    print("La base de datos fue creada")

def main():
    print("Creando la bases de datos")
    
    query = text("INSERT INTO Estudiantes (EstudianteID, Nombre, Apellido, FechaNacimiento, Telefono, CorreoElectronico) VALUES ('edwinjsa', 'Hello', 'World', '2000-07-10', '75342838', 'edwinjsa2021@gmail.com')")
    db.execute(query)
    print("Datos Insertados")
    db.commit()

if __name__ == "__main__":
    main()
