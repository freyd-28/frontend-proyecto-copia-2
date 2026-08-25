from flask import Blueprint, render_template, redirect, url_for, flash, session, request
from src.services.api_productos import ApiProductos, APIError
from src.services.api_categorias import ApiCategorias
from src.controllers.auth_controller import login_required, sesion_expirada
from src.utils.pagination import paginate

productos_bp = Blueprint("productos", __name__)


def _apis():
    token = session.get("api_token")
    if not token:
        return None, None
    return ApiProductos(token), ApiCategorias(token)


def _categorias(api_cat):
    try:
        return api_cat.get_categorias() or []
    except APIError:
        return []


@productos_bp.route("/productos")
@login_required
def lista_productos():
    api, api_cat = _apis()

    try:
        productos = api.get_productos() or []
        categorias = _categorias(api_cat)

        nombres = {
            c["id_categoria"]: c["nombre"]
            for c in categorias
        }

        for producto in productos:
            producto["nombre_categoria"] = nombres.get(
                producto.get("id_categoria"),
                f"Categoría #{producto.get('id_categoria')}",
            )

        pagination = paginate(
            productos,
            request.args.get("page", 1, type=int),
            request.args.get("per_page", 10, type=int),
        )

        return render_template(
            "productos/lista_productos.html",
            productos=pagination.items_page,
            pagination=pagination,
        )

    except APIError as error:
        if error.status_code == 401:
            return sesion_expirada()

        flash(error.message, "danger")
        return render_template(
            "productos/lista_productos.html",
            productos=[],
            pagination=paginate([]),
        )

@productos_bp.route("/productos/nuevo", methods=["GET", "POST"])
@login_required
def nuevo_producto():
    api, api_cat = _apis()
    producto = {
        "nombre": request.form.get("nombre", "").strip(),
        "precio_venta": request.form.get("precio_venta", "").strip(),
        "id_categoria": request.form.get("id_categoria", "").strip(),
        "activo": request.form.get("activo", "1"),
    }
    categorias = _categorias(api_cat)

    if request.method == "POST":
        if not producto["nombre"] or not producto["precio_venta"] or not producto["id_categoria"]:
            flash("Nombre, precio y categoría son obligatorios.", "danger")
            return render_template("productos/nuevo_producto.html", producto=producto, categorias=categorias)
        try:
            producto["precio_venta"] = float(producto["precio_venta"])
            producto["id_categoria"] = int(producto["id_categoria"])
            producto["activo"] = int(producto["activo"])
            if producto["precio_venta"] <= 0 or producto["id_categoria"] <= 0 or producto["activo"] not in (0, 1):
                raise ValueError
        except (ValueError, TypeError):
            flash("Precio, categoría o estado no tienen un formato válido.", "danger")
            return render_template("productos/nuevo_producto.html", producto=producto, categorias=categorias)
        try:
            api.create_producto(producto)
            flash("Producto registrado exitosamente.", "success")
            return redirect(url_for("productos.lista_productos"))
        except APIError as error:
            if error.status_code == 401:
                return sesion_expirada()
            flash(error.message, "danger")

    return render_template("productos/nuevo_producto.html", producto=producto, categorias=categorias)


@productos_bp.route("/productos/editar/<int:producto_id>", methods=["GET", "POST"])
@login_required
def editar_producto(producto_id):
    api, api_cat = _apis()
    try:
        producto = api.get_producto(producto_id)
    except APIError as error:
        if error.status_code == 401:
            return sesion_expirada()
        flash(error.message, "danger")
        return redirect(url_for("productos.lista_productos"))

    categorias = _categorias(api_cat)
    if request.method == "POST":
        data = {
            "nombre": request.form.get("nombre", "").strip(),
            "precio_venta": request.form.get("precio_venta", "").strip(),
            "id_categoria": request.form.get("id_categoria", "").strip(),
            "activo": request.form.get("activo", "1"),
        }
        if not all(data.values()):
            flash("Todos los campos son obligatorios.", "danger")
            producto.update(data)
            return render_template("productos/editar_producto.html", producto=producto, categorias=categorias)
        try:
            data["precio_venta"] = float(data["precio_venta"])
            data["id_categoria"] = int(data["id_categoria"])
            data["activo"] = int(data["activo"])
            if data["precio_venta"] <= 0 or data["id_categoria"] <= 0 or data["activo"] not in (0, 1):
                raise ValueError
            api.update_producto(producto_id, data)
            flash("Producto actualizado exitosamente.", "success")
            return redirect(url_for("productos.lista_productos"))
        except (ValueError, TypeError):
            flash("Los datos ingresados no tienen un formato válido.", "danger")
        except APIError as error:
            if error.status_code == 401:
                return sesion_expirada()
            flash(error.message, "danger")
    return render_template("productos/editar_producto.html", producto=producto, categorias=categorias)


@productos_bp.route("/productos/eliminar/<int:producto_id>", methods=["POST"])
@login_required
def eliminar_producto(producto_id):
    api, _ = _apis()
    try:
        api.delete_producto(producto_id)
        flash("Producto eliminado exitosamente.", "success")
    except APIError as error:
        if error.status_code == 401:
            return sesion_expirada()
        flash(error.message, "danger")
    return redirect(url_for("productos.lista_productos"))