from flask import Blueprint, jsonify, request
from flask_jwt_extended import create_access_token, jwt_required, get_jwt_identity
from app import db
from app.models.usuario import Usuario
from datetime import timedelta
from flask_jwt_extended import get_jwt
auth_bp = Blueprint('auth', __name__, url_prefix='/api/auth')

@auth_bp.route("/registro", methods=["POST"])
def registro():
    """Registra un nuevo usuario en el sistema."""
    datos = request.get_json()
    
    if Usuario.query.filter_by(username=datos["username"]).first():
        return jsonify({"error": "El username ya está en uso"}), 409
        
    usuario = Usuario(
        username=datos["username"],
        email=datos["email"],
        rol=datos.get("rol", "docente")
    )
    usuario.set_password(datos["password"]) # Hashea la contraseña
    
    db.session.add(usuario)
    db.session.commit()
    return jsonify({"mensaje": "Usuario creado", "id": usuario.id}), 201

@auth_bp.route("/login", methods=["POST"])
def login():
    """Autentica al usuario y devuelve un token JWT."""
    datos = request.get_json()
    usuario = Usuario.query.filter_by(username=datos["username"]).first()
    
    # Verificar credenciales
    if not usuario or not usuario.check_password(datos["password"]):
        return jsonify({"error": "Credenciales inválidas"}), 401
        
    # Crear token (VERSIÓN ACTUALIZADA PARA JWT v4)
    token = create_access_token(
        identity=str(usuario.id), # Ahora exige que sea estrictamente un string
        additional_claims={"rol": usuario.rol}, # Los datos extra (diccionario) van aquí
        expires_delta=timedelta(hours=24)
    )
    
    return jsonify({
        "token": token,
        "tipo": "Bearer",
        "expira_en": "24 horas",
        "usuario": {"id": usuario.id, "username": usuario.username, "rol": usuario.rol}
    }), 200

@auth_bp.route("/perfil", methods=["GET"])
@jwt_required() 
def perfil():
    """Ruta protegida: solo accesible con token JWT válido."""
    identidad = get_jwt_identity() # Ahora esto nos devuelve únicamente el ID en texto
    claims = get_jwt() # Extraemos los datos adicionales (el rol)
    
    usuario = Usuario.query.get(identidad)
    return jsonify({"usuario": usuario.username, "rol": claims["rol"]}), 200