# Programa: KairosMS

import os
from psycopg2 import *
from sqlalchemy import create_engine, text
from sqlalchemy.orm import scoped_session, sessionmaker
from flask import Flask, flash, redirect, render_template, request, session, url_for,jsonify
from dotenv import load_dotenv  
import random

app = Flask(__name__)

load_dotenv(override=True)

engine = create_engine(os.getenv("DATABASE_URL"))
db = scoped_session(sessionmaker(bind=engine))

adminUser = os.getenv('ADMIN_USER')
adminPass = os.getenv('ADMIN_PASS')

# Configuración de la sesión
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
app.secret_key = os.urandom(24)

# RUTA PRINCIPAL AL CARGAR LA PAGINA
@app.route("/")
def index():
    return render_template('index.html')

@app.route("/busqueda_actualizar")
def busqueda_actualizar():
    return render_template('busqueda.html')

@app.route("/matricula")
def matricula():
    return render_template('matricula.html')

# LOGIN
@app.route("/login", methods=['POST'])
def login():
    correo = request.form.get('correo')
    contraseña = request.form.get('contraseña')
    tipo = request.form.get('tipoUsuario')
    
    alumnos = db.execute(text("SELECT COUNT (nombre) FROM estudiantes")).fetchone()[0]
    docentes = db.execute(text("SELECT COUNT (nombreprofesor) FROM profesores")).fetchone()[0]
    matriculados = db.execute(text("SELECT COUNT(DISTINCT estudianteid) FROM matricula")).fetchone()[0]

    if tipo == "estudiante":
        
        try:
            if correo and contraseña:
                query = text("SELECT * FROM estudiantes WHERE correoelectronico = :correo")
                result = db.execute(query, {"correo": correo})
                datos = result.fetchall()
                print(datos)
                if contraseña == datos[0][0]:
                    session['user_id'] = datos[0][0]
                    return render_template("alumnoVista.html")
            else:
                flash("Por favor, introduce tus datos")
        except:
            return render_template("index.html")
        
    elif tipo == "profesor":
        try:
            if correo and contraseña:
                query = text("SELECT * FROM profesores WHERE correoelectronico = :correo")
                result = db.execute(query, {"correo": correo})
                datos = result.fetchall()
                print(datos)
                if datos and contraseña == datos[0][0]:
                    session['user_id'] = datos[0][0]
                    return render_template("docenteVista.html")
            else:
                flash("Por favor, introduce tus datos")
        except:
            return render_template("index.html")
    
    elif tipo == "administrador":
        if correo == adminUser and contraseña == adminPass:
            session["user_id"] = correo
            return render_template('home.html',alumnos=alumnos,docentes=docentes, matriculados=matriculados)
    
    flash("Credenciales inválidas. Inténtalo de nuevo.", "error")
    return redirect(url_for('index'))

@app.route("/logout")
def logout():
    # Elimina la información de la sesión
    session.pop("user_id", None)
    flash("Has cerrado sesión exitosamente.", "info")
    return redirect(url_for('index'))


# CARGA LA VISTA DEL ADMINISTRADOR DE REGISTRO DE LOS PROFESORES
@app.route("/registro_profesores")
def profesores():
    if "user_id" in session:
        query = text("SELECT nombrecurso FROM cursos")
        return render_template('profesores.html', cursos = db.execute(query).fetchall())
    
    return render_template('index.html')

# CARGA LA VISTA DEL ADMINISTRADOR DE REGISTRO DE LOS CURSOS
@app.route("/registro_cursos")
def cursos():
    if "user_id" in session:
        query = text("SELECT nombreprofesor FROM profesores")
        return render_template('cursos.html', profesores = db.execute(query).fetchall())
    
    return render_template('index.html')

# CARGA LA VISTA DEL ADMINISTRADOR DE REGISTRO DE LOS ESTUDIANTES
@app.route("/registro_estudiantes")
def estudiantes():
    if "user_id" in session:
        return render_template('estudiantes.html')
    
    return render_template('index.html')

# CARGA LA PAGINA PRINCIPAL DEL ADMINISTRADOR
@app.route("/home")
def home():
    if "user_id" in session:
        
        alumnos = db.execute(text("SELECT COUNT (nombre) FROM estudiantes")).fetchone()[0]
        docentes = db.execute(text("SELECT COUNT (nombreprofesor) FROM profesores")).fetchone()[0]
        matricula = db.execute(text("SELECT COUNT(DISTINCT estudianteid) FROM matricula")).fetchone()[0]
        print(matricula)
        
        return render_template('home.html', alumnos=alumnos, docentes=docentes, matriculados = matricula)
    
    return render_template('index.html')

# Toma los valores del formulario y los almacena en la base de datos - tabla profesores
@app.route("/docentes_registro", methods=['POST'])
def registro_docentes():
    cedula = request.form.get('cedula')
    nombre = request.form.get('nombre')
    apellido = request.form.get('apellido')
    correo = request.form.get('correo')
    titulo = request.form.get('titulo')

    query = text("INSERT INTO profesores (cedula_profesor, nombreprofesor, apellidoprofesor, correoelectronico, especializacion) VALUES (:cedula, :nombre, :apellido, :correo, :titulo)")

    db.execute(query, {'cedula': cedula, 'nombre': nombre, 'apellido': apellido, 'correo': correo, 'titulo': titulo})
    db.commit()

    return render_template('profesores.html')

# Toma los valores del formulario y los almacena en la base de datos - tabla cursos
@app.route("/cursos_registro", methods=['POST'])
def registro_cursos():
    id = request.form.get('idcurso')
    nombre = request.form.get('nombrecurso')
    descripcion = request.form.get('descripcioncurso')
    creditos = request.form.get('creditos')
    semestre= request.form.get('semestre')
    profesor = request.form.get('profesor')
    print(profesor)
    
    query = text("INSERT INTO cursos (cursoid, nombrecurso, descripcioncurso, creditos, semestre, profesor) VALUES (:id, :nombre, :descripcion, :creditos, :semestre, :profesor)")    
    
    db.execute(query, {'id': id, 'nombre': nombre, 'descripcion': descripcion, 'creditos': creditos, 'semestre':semestre, 'profesor':profesor})
    db.commit()
    
    return render_template('cursos.html')

#toma los valores del formulario y los almacena en la base de datos - tabla estudiantes
@app.route("/estudiantes_registro", methods=['POST'])
def registro_estudiantes():
    carnet = request.form.get('carnet')
    nombre = request.form.get('nombre')
    apellido = request.form.get('apellido')
    fecha = request.form.get('fecha_nacimiento')
    telefono = request.form.get('telefono')
    correo = request.form.get('correo')
    semestre= request.form.get('semestre')
    query = text("INSERT INTO estudiantes (estudianteid, nombre, apellido, fechanacimiento, telefono, correoelectronico,semestre) VALUES (:carnet, :nombre, :apellido, :fecha, :telefono, :correo, :semestre)")
    
    db.execute(query, {'carnet': carnet, 'nombre': nombre, 'apellido': apellido, 'telefono': telefono, 'fecha': fecha, 'correo': correo, 'semestre': semestre})
    
    db.commit()
    
    return render_template('estudiantes.html')



#TOMA LOS DATOS DE LA DB Y LOS MUESTRA EN LA TABLA PROFESORES
@app.route("/ver_docentes", methods=['GET'])
def ver_docentes():
    query = text("SELECT * FROM profesores")
    datos = db.execute(query).fetchall()
    print(datos)  
    return render_template('profesores.html',datos=datos)

#TOMA LOS DATOS DE LA DB Y LOS MUESTRA EN LA TABLA CURSOS
@app.route("/ver_cursos", methods=['GET'])
def ver_cursos():
    query = text("SELECT * FROM cursos")
    datos = db.execute(query).fetchall()
    print(datos)  
    return render_template('cursos.html',datos=datos)

#TOMA LOS DATOS DE LA DB Y LOS MUESTRA EN LA TABLA ESTUDIANTES
@app.route("/ver_estudiantes", methods=['GET'])
def ver_estudiantes():
    query = text("SELECT * FROM estudiantes")
    datos = db.execute(query).fetchall()
    return render_template('estudiantes.html', datos=datos)

@app.route("/actualizar", methods=['GET', 'POST'])
def actualizar():
    if request.method == 'POST':
        carnet = request.form.get('carnet')
        nombre = request.form.get('nombre')
        apellido = request.form.get('apellido')
        fecha = request.form.get('fecha_nacimiento')
        telefono = request.form.get('telefono')
        correo = request.form.get('correo')
        
        query = text("UPDATE estudiantes SET nombre = :nombre, apellido = :apellido, fechanacimiento = :fecha, telefono = :telefono, correoelectronico = :correo WHERE estudianteid = :estudianteid")
                
        db.execute(query, {'nombre': nombre, 'apellido': apellido, 'fecha': fecha, 'telefono': telefono, 'correo': correo, 'estudianteid': carnet})
        db.commit()
        
        return render_template('estudiantes.html')

    identificador = request.args.get('carnet')
    datos = None

    if identificador:
        query = text("SELECT * FROM estudiantes WHERE estudianteid = :identificador")
        datos = db.execute(query, {'identificador': identificador}).fetchone()

    return render_template('busqueda.html', datos=datos)

@app.route("/eliminarDocente", methods=['POST'])
def eliminar():
    if request.method == 'POST':
        cedula = request.form.get('cedula')
        query = text("DELETE FROM profesores WHERE cedula_profesor = :cedula")
        db.execute(query, {'cedula': cedula})
        db.commit()
        return render_template('profesores.html')
    
@app.route("/eliminarCurso", methods=['POST'])
def eliminarCurso():
    if request.method == 'POST':
        id = request.form.get('idcurso')
        query = text("DELETE FROM cursos WHERE cursoid = :id")
        db.execute(query, {'id': id})
        db.commit()
        return render_template('cursos.html')
    
@app.route("/eliminarEstudiante", methods=['POST'])
def eliminarEstudiante():
    if request.method == 'POST':
        carnet = request.form.get('carnet')
        query = text("DELETE FROM estudiantes WHERE estudianteid = :carnet")
        db.execute(query, {'carnet': carnet})
        db.commit()
        return render_template('estudiantes.html')
    
@app.route('/guardar_elementos', methods=['POST'])
def guardar_elementos():
    data = request.get_json()
    lista = data.get('lista', [])
    print(lista)
    return 'Elementos recibidos con éxito'

@app.route('/matriculaEstudiante', methods=['GET'])
def matriculaget():
    query = text("SELECT * FROM estudiantes WHERE estudianteid = :carnet")
    datos = db.execute(query, {'carnet': request.args.get("carnet")}).fetchone()
    
    semestre = datos[6]
    query_cursos = text("SELECT * FROM cursos WHERE semestre = :semestre")
    cursos = db.execute(query_cursos, {'semestre': semestre}).fetchall()
    
    print(cursos)

    return render_template('matricula.html', estudiante=datos, cursos=cursos)

@app.route('/matricularAlumno', methods=['POST'])
def matricularEstudiante():
    print(request.form.get('carnet'))
    print(request.form.getlist('cursos'))
    
    for curso in request.form.getlist('cursos'):
        query = text("INSERT INTO matricula (MatriculaID, EstudianteID, CursoID, AnoAcademico, estudianteSemestre, cursoSemestre) VALUES (:MatriculaID, :EstudianteID, :CursoID, :AnoAcademico, :estudianteSemestre, :cursoSemestre)")
        db.execute(query, {
            'MatriculaID': random.randint(1, 100000),
            'EstudianteID': request.form.get('carnet'),
            'CursoID': int(curso),
            'AnoAcademico': 2023,
            'estudianteSemestre': 1,
            'cursoSemestre': 1
        })
        db.commit()

    return render_template('matricula.html')
    

if __name__ == '__main__':
    app.run()
