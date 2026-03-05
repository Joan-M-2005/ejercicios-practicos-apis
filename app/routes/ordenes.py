from flask import Blueprint, jsonify, request
# Quitamos el jwt_required temporalmente para que sea más fácil probar
from app import db
from app.models.orden import Orden
from app.models.detalle_orden import DetalleOrden
from app.models.producto import Producto

ordenes_bp = Blueprint('ordenes', __name__, url_prefix='/api/ordenes')

@ordenes_bp.route("/", methods=["POST"])
def procesar_orden():
    datos = request.get_json()
    total = 0
    detalles = []
    errores = []

    # Validar inventario y precios
    for item in datos["productos"]:
        producto = Producto.query.get(item["producto_id"])
        if not producto:
            errores.append(f"Producto ID {item['producto_id']} no existe")
            continue
            
        if producto.stock < item["cantidad"]:
            errores.append(f"Stock insuficiente para {producto.nombre}. Disponible: {producto.stock}")
            continue
            
        subtotal = float(producto.precio) * item["cantidad"]
        total += subtotal
        detalles.append({
            "producto": producto,
            "cantidad": item["cantidad"],
            "precio_unitario": float(producto.precio)
        })

    if errores:
        return jsonify({"error": "No se pudo procesar la orden", "detalles": errores}), 400

    # Crear la transacción
    try:
        orden = Orden(cliente_id=datos["cliente_id"], total=total)
        db.session.add(orden)
        db.session.flush() # Obtener el ID de la orden nueva
        
        for d in detalles:
            detalle = DetalleOrden(
                orden_id=orden.id,
                producto_id=d["producto"].id,
                cantidad=d["cantidad"],
                precio_unitario=d["precio_unitario"]
            )
            db.session.add(detalle)
            d["producto"].stock -= d["cantidad"] # Descontar inventario
            
        db.session.commit() # Confirmar compra
        
        return jsonify({
            "mensaje": "Orden procesada exitosamente",
            "orden_id": orden.id,
            "total": total
        }), 201
        
    except Exception as e:
        db.session.rollback() # Si algo falla, cancelar la compra
        return jsonify({"error": "Error interno", "detalle": str(e)}), 500