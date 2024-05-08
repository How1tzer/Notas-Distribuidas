from flask import Flask, request, jsonify, render_template
from flask_socketio import SocketIO, emit
import sqlite3

app = Flask(__name__)
app.config['SECRET_KEY'] = 'clave-secreta'  # Clave secreta para la sesión
socketio = SocketIO(app)

# Función para realizar consultas a la base de datos SQLite
def query_database(sql_query, params=None):
    connection = sqlite3.connect('notas.db')
    cursor = connection.cursor()
    if params:
        cursor.execute(sql_query, params)
    else:
        cursor.execute(sql_query)
    results = cursor.fetchall()
    cursor.close()
    connection.close()
    return results

# Función para insertar datos en la base de datos SQLite
def insert_into_database(sql_query, params):
    connection = sqlite3.connect('notas.db')
    cursor = connection.cursor()
    cursor.execute(sql_query, params)
    connection.commit()
    cursor.close()
    connection.close()

# Función para obtener todas las notas de un usuario
def obtener_notas(usuario):
    return query_database("SELECT * FROM notas WHERE usuario=?", (usuario,))

# Función para crear una nueva nota
@socketio.on('crear_nota')
def crear_nota(data):
    usuario = data['usuario']
    titulo = data['titulo']
    contenido = data['contenido']
    insert_into_database("INSERT INTO notas (usuario, titulo, contenido) VALUES (?, ?, ?)", (usuario, titulo, contenido))
    notas = obtener_notas(usuario)
    emit('notas_actualizadas', {'notas': notas}, broadcast=True)

# Función para editar una nota existente
@socketio.on('editar_nota')
def editar_nota(data):
    id_nota = data['id']
    titulo = data['titulo']
    contenido = data['contenido']
    insert_into_database("UPDATE notas SET titulo=?, contenido=? WHERE id=?", (titulo, contenido, id_nota))
    usuario = data['usuario']
    notas = obtener_notas(usuario)
    emit('notas_actualizadas', {'notas': notas}, broadcast=True)

# Función para eliminar una nota
@socketio.on('eliminar_nota')
def eliminar_nota(data):
    id_nota = data['id']
    insert_into_database("DELETE FROM notas WHERE id=?", (id_nota,))
    usuario = data['usuario']
    notas = obtener_notas(usuario)
    emit('notas_actualizadas', {'notas': notas}, broadcast=True)

# Función para obtener todas las notas de un usuario
@socketio.on('obtener_notas')
def handle_obtener_notas(data):
    usuario = data['usuario']
    notas = obtener_notas(usuario)
    emit('notas_obtenidas', {'notas': notas})

# Ruta para la página de inicio
@app.route('/')
def index():
    return render_template('index.html')

if __name__ == '__main__':
    socketio.run(app, debug=True)
