from flask import Blueprint, jsonify
from datetime import datetime

main_bp = Blueprint('main', __name__)

@main_bp.route("/", methods=["GET"])
def index():
    """Ruta raíz bienvenida."""
    return jsonify({
        "mensaje": "¡Bienvenido a mi primera API con Flask!",
        "version": "1.0.0",
        "tecnologias": ["Python", "Flask", "PostgreSQL"]
    })

@main_bp.route("/health", methods=["GET"])
def health_check():
    """Ruta de verificación de salud de la API."""
    return jsonify({
        "estado": "OK",
        "timestamp": datetime.now().isoformat(),
        "base_de_datos": "Conectada"
    }), 200