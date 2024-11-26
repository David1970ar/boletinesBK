from flask import Flask, request
from flask import jsonify
from flask_cors import CORS
from flask_cors import cross_origin
import pymysql
import os
# from werkzeug.security import generate_password_hash, check_password_hash

app = Flask(__name__)
cors = CORS(app)
app.config['CORS_HEADERS'] = 'Content-Type'

db = pymysql.connect(host="localhost", user="root",
                     passwd="3107", db="boletines")

# busqueda de alumnos por DNI


@app.route('/api/alumnos/<DNIAlu>', methods=['GET'])
@cross_origin()
def buscarAlumno(DNIAlu):
    if (DNIAlu != ""):

        sql = '''select * from alumnos where DNIAlu = %s'''

        cursor = db.cursor(pymysql.cursors.DictCursor)
        cursor.execute(sql, (DNIAlu))

        respuesta = cursor.fetchall()
        codRetorno = 200

    else:
        respuesta = {"message": "Falta Informacion"}
        codRetorno = 400

    return jsonify(respuesta), codRetorno

# carga de un alumno nuevo


@app.route('/api/nuevoAlumno', methods=['POST'])
@cross_origin()
def nuevoAlumno():
    nuevoAlumno = request.get_json()  # informacion en el JSON

    print(nuevoAlumno)

    DNIAlu = nuevoAlumno['DNIAlu']
    nomApeAlu = nuevoAlumno['nomApeAlu']
    mailAlu = nuevoAlumno['mailAlu']
    telefonoAlu = nuevoAlumno['telefonoAlu']
    nomApeResp = nuevoAlumno['nomApeResp']
    mailResp = nuevoAlumno['mailResp']
    telefonoResp = nuevoAlumno['telefonoResp']
    añoIngreso = nuevoAlumno['añoIngreso']
    cursoActual = nuevoAlumno['cursoActual']

    if (DNIAlu != "" and nomApeAlu != "" and nomApeResp != "" and mailResp != ""):

        sql = f'insert into alumnos (DNIAlu, nomApeAlu, mailAlu, telefonoAlu, nomApeResp, mailResp, telefonoResp, añoIngreso, cursoActual) values (%s, %s, %s, %s, %s, %s, %s, %s, %s)'

        print(sql)

        try:
            cursor = db.cursor()
            cursor.execute(sql, (DNIAlu, nomApeAlu, mailAlu, telefonoAlu,
                           nomApeResp, mailResp, telefonoResp, añoIngreso, cursoActual))
            db.commit()
            respuesta = {"message": "Alumno creado con exito"}
            codRetorno = 200
        except:
            respuesta = {"message": "ocurrio un problema al crear el Alumno"}
            codRetorno = 500

    else:
        respuesta = {"message": "Falta Informacion"}
        codRetorno = 400

    return respuesta, codRetorno


# despues de buscar datos y mostrar en pantalla, se hace un update para modificar datos en la base.
@app.route('/api/alumnoModif/', methods=['PUT'])
@cross_origin()
def alumnoModif():

    alumnoActualizar = request.get_json()
    print(type(alumnoActualizar))
    print("Datos recibidos:", alumnoActualizar)

    # Verificamos que sea un diccionario, si es una lista, accedemos al primer elemento
    if isinstance(alumnoActualizar, list):
        alumnoActualizar = alumnoActualizar[0]

    # Asegurarse de que es un diccionario
    if not isinstance(alumnoActualizar, dict):
        return {"message": "Formato de datos incorrecto"}, 400

    sql = f'''
        UPDATE alumnos
        SET
            nomApeAlu = %s,
            mailAlu = %s,
            telefonoAlu = %s,
            nomApeResp = %s,
            mailResp = %s,
            telefonoResp = %s,
            añoIngreso = %s,
            cursoActual = %s
        WHERE DNIAlu = %s
    '''

    valores = (
        alumnoActualizar["nomApeAlu"],
        alumnoActualizar["mailAlu"],
        alumnoActualizar["telefonoAlu"],
        alumnoActualizar["nomApeResp"],
        alumnoActualizar["mailResp"],
        alumnoActualizar["telefonoResp"],
        alumnoActualizar["añoIngreso"],
        alumnoActualizar["cursoActual"],
        alumnoActualizar["DNIAlu"]

    )
    print(valores)
    try:
        cursor = db.cursor()
        cursor.execute(sql, valores)
        db.commit()
        respuesta = {"message": "Alumno actualizado con éxito"}
        codRetorno = 200
    except Exception as e:
        print(f"Error al actualizar alumno: {e}")
        respuesta = {"message": "Ocurrió un problema al actualizar el alumno"}
        codRetorno = 500

    return respuesta, codRetorno

# busca notas del alumno por DNI y año de cursada


@app.route('/api/notas/<DNIAlu>/<year>', methods=['GET'])
@cross_origin()
def buscarNotasAlumno(DNIAlu, year):
    if (DNIAlu != ""):

        sql = f'''SELECT
                        a.nomApeAlu AS "Nombre del Alumno",
                    a.cursoActual AS "Curso Actual",
                    asig.cargos_materias_materia AS "Asignatura",
                    p.periodo AS "Periodo",
                    c.calificacion AS "Calificación",
                    asig.periodos_añoCursada AS "Año de Cursada"
                FROM
                    alumnos a
                JOIN
                    calificaciones c ON a.DNIAlu = c.alumnos_DNIAlu
                JOIN
                    asignaturas asig ON c.asignaturas_cargos_profesores_DNIProf = asig.cargos_profesores_DNIProf
                                    AND c.asignaturas_cargos_materias_materia = asig.cargos_materias_materia
                                    AND c.asignaturas_cargos_cursos_IDcurso = asig.cargos_cursos_IDcurso
                                    AND c.asignaturas_periodos_añoCursada = asig.periodos_añoCursada
                JOIN
                    periodos p ON c.periodos_periodo = p.periodo AND c.asignaturas_periodos_añoCursada = p.añoCursada
                WHERE
                    a.DNIAlu = %s AND asig.periodos_añoCursada = %s
                ORDER BY
                    asig.cargos_materias_materia, p.fechaCierre;'''

        cursor = db.cursor(pymysql.cursors.DictCursor)
        cursor.execute(sql, (DNIAlu, year))

        respuesta = cursor.fetchall()
        codRetorno = 200

    else:
        respuesta = {"message": "Falta Informacion"}
        codRetorno = 400

    return jsonify(respuesta), codRetorno

# Validacion del profesor para ingresar notas


@app.route('/api/validarProfesor', methods=['POST'])
@cross_origin()
def validarProfesor():
    valProf = request.get_json()  # Información en el JSON

    # Verificamos que valProf es un diccionario
    if not isinstance(valProf, dict):
        return jsonify({"success": False, "message": "Formato de datos incorrecto"}), 400

    print(valProf)

    email = valProf.get('mailProf')
    password = valProf.get('password')

    # Asegurarse de que email y password existen
    if not email or not password:
        return jsonify({"success": False, "message": "Faltan el correo o la contraseña"}), 400

    sql = "SELECT pass FROM profesores WHERE mailProf = %s"
    try:
        # Realizamos la conexión y ejecutamos la consulta
        cursor = db.cursor(pymysql.cursors.DictCursor)
        cursor.execute(sql, (email,))
        respuesta = cursor.fetchone()  # Usamos fetchone ya que esperamos un solo resultado

        print(respuesta)

        # Comprobamos si se encontró el profesor y si la contraseña coincide
        if respuesta and password == respuesta['pass']:
            return jsonify({"success": True}), 200
        else:
            return jsonify({"success": False, "message": "Email o contraseña incorrectos"}), 401

    except Exception as e:
        print("Error al validar el profesor:", e)
        return jsonify({"success": False, "message": "Error en el servidor"}), 500

    finally:
        cursor.close()


# busca notas del curso para crear lista de todos los alumnos.
@app.route('/api/alumnos_calificaciones', methods=['GET'])
@cross_origin()
def obtener_alumnos_calificaciones():
    # Obtiene los parámetros desde la URL en lugar de esperar un JSON en un GET.
    curso = request.args.get('cursoActual')
    materia = request.args.get('materia')

    print("Curso:", curso, "Materia:", materia)  # Depuración

    # Verifica que ambos parámetros estén presentes
    if not curso or not materia:
        return jsonify({"success": False, "message": "Faltan parámetros 'cursoActual' o 'materia'"}), 400

    sql = '''
    SELECT
        alumnos.DNIAlu AS "DNI Alumno",
        alumnos.nomApeAlu AS "Nombre del Alumno",
        MAX(calificaciones.asignaturas_cargos_profesores_DNIProf) AS "DNI Profesor",
        MAX(calificaciones.asignaturas_cargos_materias_materia) AS "Materia",
        alumnos.cursoActual AS "Curso Actual",
        MAX(calificaciones.asignaturas_periodos_añoCursada) AS "Año",
        MAX(calificaciones.calificacion) AS "Calificación",
        MAX(calificaciones.periodos_periodo) AS "Periodo"
    FROM
        alumnos
    LEFT JOIN
        calificaciones ON alumnos.DNIAlu = calificaciones.alumnos_DNIAlu
        AND calificaciones.asignaturas_cargos_materias_materia = %s
    WHERE
        alumnos.cursoActual = %s
    GROUP BY
        alumnos.DNIAlu, alumnos.nomApeAlu, alumnos.cursoActual;
        '''

    try:
        # Ejecuta la consulta con parámetros seguros
        cursor = db.cursor(pymysql.cursors.DictCursor)
        cursor.execute(sql, (materia, curso))
        respuesta = cursor.fetchall()

        # Verifica si hay resultados
        if not respuesta:
            return jsonify({"success": False, "message": "No se encontraron alumnos para los parámetros dados"}), 404

        # Retorna la lista de alumnos y sus calificaciones
        return jsonify(respuesta), 200

    except Exception as e:
        print("Error al obtener alumnos y calificaciones:", e)
        return jsonify({"success": False, "message": "Error en el servidor"}), 500

    finally:
        cursor.close()


@app.route('/api/cargarCalificaciones', methods=['POST'])
@cross_origin()
def cargar_calificaciones():
    data = request.get_json()
    calificaciones = data.get("calificaciones", [])
    cursor = db.cursor(pymysql.cursors.DictCursor)
    print(calificaciones)
    for calificacion in calificaciones:
        carga = '''
        INSERT INTO calificaciones (alumnos_DNIAlu, asignaturas_cargos_profesores_DNIProf, asignaturas_cargos_materias_materia, asignaturas_cargos_cursos_IDcurso, asignaturas_periodos_añoCursada, calificacion, periodos_periodo)
        VALUES (%s, %s, %s, %s, %s, %s, %s)
        '''
        datos = {
            calificacion["DNI Alumno"],
            calificacion["DNI Profesor"],
            calificacion["Materia"],
            calificacion["Curso Actual"],
            calificacion["Año"],
            calificacion["Calificacion"],
            calificacion["Periodo"]
        }
        cursor.execute(carga, datos)

    db.commit()
    cursor.close()
    db.close()
    return jsonify({"success": True})


if __name__ == '__main__':
    app.run(debug=True)
