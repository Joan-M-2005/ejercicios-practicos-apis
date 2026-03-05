from flask import Blueprint, jsonify, request
from app import db
from app.models.estudiante import Estudiante

# Creamos un Blueprint (un grupo de rutas) para los estudiantes
estudiantes_bp = Blueprint('estudiantes', __name__, url_prefix='/api/estudiantes')

# 1. CREATE: POST /api/estudiantes
@estudiantes_bp.route("/", methods=["POST"])
def crear_estudiante():
    datos = request.get_json()
    if not datos:
        return jsonify({"error": "No se enviaron datos"}), 400
    
    campos_requeridos = ["matricula", "nombre", "apellido", "email", "carrera"]
    for campo in campos_requeridos:
        if campo not in datos:
            return jsonify({"error": f"El campo {campo} es requerido"}), 400
            
    if Estudiante.query.filter_by(matricula=datos["matricula"]).first():
        return jsonify({"error": "La matricula ya está registrada"}), 409
        
    nuevo = Estudiante(
        matricula=datos["matricula"],
        nombre=datos["nombre"],
        apellido=datos["apellido"],
        email=datos["email"],
        carrera=datos["carrera"],
        semestre=datos.get("semestre", 1)
    )
    
    db.session.add(nuevo)
    db.session.commit() # Guarda en la BD
    
    return jsonify({"mensaje": "Estudiante creado exitosamente", "estudiante": nuevo.to_dict()}), 201

# 2. READ ALL: GET /api/estudiantes
@estudiantes_bp.route("/", methods=["GET"])
def obtener_estudiantes():
    estudiantes = Estudiante.query.filter_by(activo=True).all()
    return jsonify({"estudiantes": [e.to_dict() for e in estudiantes]}), 200

# 3. READ ONE: GET /api/estudiantes/<id>
@estudiantes_bp.route("/<int:id>", methods=["GET"])
def obtener_estudiante(id):
    """
    Obtiene un estudiante por ID
    ---
    tags:
      - Estudiantes
    parameters:
      - name: id
        in: path
        type: integer
        required: true
        description: ID único del estudiante
    responses:
      200:
        description: Estudiante encontrado
        schema:
          properties:
            id: {type: integer}
            nombre: {type: string}
            matricula: {type: string}
      404:
        description: Estudiante no encontrado
    """
    estudiante = Estudiante.query.get_or_404(id, description="Estudiante no encontrado")
    return jsonify(estudiante.to_dict()), 200

# 4. UPDATE: PUT /api/estudiantes/<id>
@estudiantes_bp.route("/<int:id>", methods=["PUT"])
def actualizar_estudiante(id):
    estudiante = Estudiante.query.get_or_404(id)
    datos = request.get_json()
    
    if "nombre" in datos: estudiante.nombre = datos["nombre"]
    if "apellido" in datos: estudiante.apellido = datos["apellido"]
    if "email" in datos: estudiante.email = datos["email"]
    if "carrera" in datos: estudiante.carrera = datos["carrera"]
    if "semestre" in datos: estudiante.semestre = datos["semestre"]
    
    db.session.commit()
    return jsonify({"mensaje": "Actualizado", "estudiante": estudiante.to_dict()}), 200

# 5. DELETE: DELETE /api/estudiantes/<id>
@estudiantes_bp.route("/<int:id>", methods=["DELETE"])
def eliminar_estudiante(id):
    # Borrado lógico: no destruye el registro, solo lo marca inactivo
    estudiante = Estudiante.query.get_or_404(id)
    estudiante.activo = False
    db.session.commit()
    return jsonify({"mensaje": f"Estudiante {estudiante.matricula} desactivado"}), 200