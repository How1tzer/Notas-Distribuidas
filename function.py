from flask import Flask, request, jsonify, render_template
from flask_socketio import SocketIO, emit
import sqlite3

app = Flask(__name__)
app.config['SECRET_KEY'] = 'clave-secreta'  # Clave secreta para la sesión
socketio = SocketIO(app)

# Conexión a la base de datos SQLite
conn = sqlite3.connect('notas.db')
c = conn.cursor()

# Crear tabla de notas si no existe
c.execute('''CREATE TABLE IF NOT EXISTS notas
             (id INTEGER PRIMARY KEY AUTOINCREMENT, usuario TEXT, titulo TEXT, contenido TEXT)''')
conn.commit()

# Función para obtener todas las notas de un usuario
def obtener_notas(usuario):
    c.execute("SELECT * FROM notas WHERE usuario=?", (usuario,))
    return c.fetchall()

# Función para crear una nueva nota
@socketio.on('crear_nota')
def crear_nota(data):
    usuario = data['usuario']
    titulo = data['titulo']
    contenido = data['contenido']
    c.execute("INSERT INTO notas (usuario, titulo, contenido) VALUES (?, ?, ?)", (usuario, titulo, contenido))
    conn.commit()
    notas = obtener_notas(usuario)
    emit('notas_actualizadas', {'notas': notas}, broadcast=True)

# Función para editar una nota existente
@socketio.on('editar_nota')
def editar_nota(data):
    id_nota = data['id']
    titulo = data['titulo']
    contenido = data['contenido']
    c.execute("UPDATE notas SET titulo=?, contenido=? WHERE id=?", (titulo, contenido, id_nota))
    conn.commit()
    usuario = data['usuario']
    notas = obtener_notas(usuario)
    emit('notas_actualizadas', {'notas': notas}, broadcast=True)

# Función para eliminar una nota
@socketio.on('eliminar_nota')
def eliminar_nota(data):
    id_nota = data['id']
    c.execute("DELETE FROM notas WHERE id=?", (id_nota,))
    conn.commit()
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
