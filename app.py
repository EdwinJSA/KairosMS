import os
from psycopg2 import *
from sqlalchemy import create_engine, text
from sqlalchemy.orm import scoped_session, sessionmaker
from flask import Flask, flash, redirect, render_template, request, session, url_for,jsonify
from dotenv import load_dotenv  

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

# LOGIN
@app.route("/login", methods=['POST'])
def login():
    correo = request.form.get('correo')
    contraseña = request.form.get('contraseña')

    if correo == adminUser and contraseña == adminPass:
        session["user_id"] = correo
        return redirect(url_for('home'))
    
    flash("Credenciales inválidas. Inténtalo de nuevo.", "error")
    return redirect(url_for('index'))

# CARGA LA VISTA DEL ADMINISTRADOR DE REGISTRO DE LOS PROFESORES
@app.route("/registro_profesores")
def profesores():
    if "user_id" in session:
        return render_template('profesores.html')
    
    return render_template('index.html')

# CARGA LA VISTA DEL ADMINISTRADOR DE REGISTRO DE LOS CURSOS
@app.route("/registro_cursos")
def cursos():
    if "user_id" in session:
        return render_template('cursos.html')
    
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
        return render_template('home.html')
    
    return render_template('index.html')

# Toma los valores del formulario y los almacena en la base de datos - tabla profesores
@app.route("/docentes_registro", methods=['POST'])
def registro_docentes():
    cedula = request.form.get('cedula')
    nombre = request.form.get('nombre')
    apellido = request.form.get('apellido')
    correo = request.form.get('correo')
    titulo = request.form.get('titulo')

    # Consulta
    query = text("INSERT INTO profesores (cedula_profesor, nombreprofesor, apellidoprofesor, correoelectronico, especializacion) VALUES (:cedula, :nombre, :apellido, :correo, :titulo)")

    # Inserción de datos en la base de datos
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
    query = text("INSERT INTO cursos (cursoid, nombrecurso, descripcioncurso, creditos, semestre) VALUES (:id, :nombre, :descripcion, :creditos, :semestre)")    
    
    db.execute(query, {'id': id, 'nombre': nombre, 'descripcion': descripcion, 'creditos': creditos, 'semestre':semestre})
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

    
    


if __name__ == '__main__':
    app.run()
