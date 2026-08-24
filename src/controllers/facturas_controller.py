from flask import Blueprint, render_template, redirect, url_for, flash, session, request
from src.services.api_facturas import ApiFacturas, ApiFacturaDetalle, APIError
from src.services.api_clientes import ApiClientes
from src.services.api_productos import ApiProductos
from src.controllers.auth_controller import login_required, sesion_expirada
from src.utils.pagination import paginate


facturas_bp = Blueprint("facturas", __name__)


def _cargar_catalogos(token):
    return ApiClientes(token).get_clientes() or [], ApiProductos(token).get_productos() or []


@facturas_bp.route("/facturas")
@login_required
def lista_facturas():
    try:
        facturas = ApiFacturas(
            session["api_token"]
        ).get_facturas() or []

        pagination = paginate(
            facturas,
            request.args.get("page", 1, type=int),
            request.args.get("per_page", 10, type=int),
        )

        return render_template(
            "facturas/lista_facturas.html",
            facturas=pagination.items_page,
            pagination=pagination,
        )

    except APIError as error:
        if error.status_code == 401:
            return sesion_expirada()

        flash(error.message, "danger")
        return render_template(
            "facturas/lista_facturas.html",
            facturas=[],
            pagination=paginate([]),
        )

@facturas_bp.route("/facturas/nueva", methods=["GET", "POST"])
@login_required
def nueva_factura():
    token = session["api_token"]
    api = ApiFacturas(token)
    detalle_api = ApiFacturaDetalle(token)
    try:
        clientes, productos = _cargar_catalogos(token)
    except APIError as error:
        if error.status_code == 401:
            return sesion_expirada()
        flash(error.message, "danger")
        clientes, productos = [], []

    datos = {
        "numero_factura": request.form.get("numero_factura", "").strip(),
        "id_cliente": request.form.get("id_cliente", ""),
        "id_producto": request.form.get("id_producto", ""),
        "cantidad": request.form.get("cantidad", "1"),
    }
    if request.method == "POST":
        if not all(datos.values()):
            flash("Todos los campos son obligatorios.", "danger")
            return render_template("facturas/nueva_factura.html", clientes=clientes, productos=productos, datos=datos)
        try:
            id_cliente = int(datos["id_cliente"])
            id_producto = int(datos["id_producto"])
            cantidad = int(datos["cantidad"])
            if cantidad <= 0:
                raise ValueError
        except (ValueError, TypeError):
            flash("Cliente, producto y cantidad deben tener valores válidos.", "danger")
            return render_template("facturas/nueva_factura.html", clientes=clientes, productos=productos, datos=datos)

        producto = next((p for p in productos if int(p["id_producto"]) == id_producto), None)
        if not producto:
            flash("El producto seleccionado no está disponible.", "danger")
            return render_template("facturas/nueva_factura.html", clientes=clientes, productos=productos, datos=datos)
        usuario = session.get("usuario") or {}
        factura = None
        try:
            factura = api.create_factura({
                "numero_factura": datos["numero_factura"],
                "id_cliente": id_cliente,
                "id_usuario": usuario.get("id_usuario"),
                "estado": "generada",
                "total": 0,
            })
            detalle_api.create_detalle({
                "id_factura": factura["id_factura"],
                "id_producto": id_producto,
                "cantidad": cantidad,
                "precio_unitario": float(producto["precio_venta"]),
            })
            flash("Factura registrada exitosamente.", "success")
            return redirect(url_for("facturas.lista_facturas"))
        except APIError as error:
            # Si el encabezado fue creado y falló el detalle, intentamos dejar la operación limpia.
            if factura and factura.get("id_factura"):
                try:
                    api.delete_factura(factura["id_factura"])
                except APIError:
                    pass
            if error.status_code == 401:
                return sesion_expirada()
            flash(error.message, "danger")
    return render_template("facturas/nueva_factura.html", clientes=clientes, productos=productos, datos=datos)


@facturas_bp.route("/facturas/<int:factura_id>")
@login_required
def detalle_factura(factura_id):
    token = session["api_token"]
    try:
        factura = ApiFacturas(token).get_factura(factura_id)
        detalles = ApiFacturaDetalle(token).get_detalles_por_factura(factura_id) or []
    except APIError as error:
        if error.status_code == 401:
            return sesion_expirada()
        flash(error.message, "danger")
        return redirect(url_for("facturas.lista_facturas"))

    cliente = None
    try:
        cliente = ApiClientes(token).get_cliente(factura["id_cliente"])
    except APIError:
        pass
    try:
        productos = ApiProductos(token).get_productos() or []
        mapa = {p["id_producto"]: p["nombre"] for p in productos}
    except APIError:
        mapa = {}
    for detalle in detalles:
        detalle["nombre_producto"] = mapa.get(detalle.get("id_producto"), f"Producto #{detalle.get('id_producto')}")
    return render_template("facturas/detalle_factura.html", factura=factura, cliente=cliente, detalles=detalles)


@facturas_bp.route("/facturas/eliminar/<int:factura_id>", methods=["POST"])
@login_required
def eliminar_factura(factura_id):
    try:
        ApiFacturas(session["api_token"]).delete_factura(factura_id)
        flash("Factura eliminada exitosamente.", "success")
    except APIError as error:
        if error.status_code == 401:
            return sesion_expirada()
        flash(error.message, "danger")
    return redirect(url_for("facturas.lista_facturas"))