from flask import Blueprint, render_template, redirect, url_for, flash, session, request
from src.services.api_clientes import ApiClientes, APIError
from src.controllers.auth_controller import login_required, sesion_expirada
from src.utils.pagination import paginate

clientes_bp = Blueprint("clientes", __name__)


def _api():
    return ApiClientes(session["api_token"])


@clientes_bp.route("/clientes")
@login_required
def lista_clientes():
    try:
        clientes = _api().get_clientes() or []

        pagination = paginate(
            clientes,
            request.args.get("page", 1, type=int),
            request.args.get("per_page", 10, type=int),
        )

        return render_template(
            "clientes/lista_clientes.html",
            clientes=pagination.items_page,
            pagination=pagination,
        )
    except APIError as error:
        if error.status_code == 401:
            return sesion_expirada()

        flash(error.message, "danger")
        return render_template(
            "clientes/lista_clientes.html",
            clientes=[],
            pagination=paginate([]),
        )

@clientes_bp.route("/clientes/nuevo", methods=["GET", "POST"])
@login_required
def nuevo_cliente():
    cliente = {
        "nombre": request.form.get("nombre", "").strip(),
        "documento": request.form.get("documento", "").strip(),
        "telefono": request.form.get("telefono", "").strip(),
        "direccion": request.form.get("direccion", "").strip(),
    }
    if request.method == "POST":
        if not cliente["nombre"] or not cliente["documento"]:
            flash("Nombre y documento son obligatorios.", "danger")
            return render_template("clientes/nuevo_cliente.html", cliente=cliente)
        try:
            _api().create_cliente(cliente)
            flash("Cliente registrado exitosamente.", "success")
            return redirect(url_for("clientes.lista_clientes"))
        except APIError as error:
            if error.status_code == 401:
                return sesion_expirada()
            flash(error.message, "danger")
    return render_template("clientes/nuevo_cliente.html", cliente=cliente)


@clientes_bp.route("/clientes/editar/<int:cliente_id>", methods=["GET", "POST"])
@login_required
def editar_cliente(cliente_id):
    try:
        cliente = _api().get_cliente(cliente_id)
    except APIError as error:
        if error.status_code == 401:
            return sesion_expirada()
        flash(error.message, "danger")
        return redirect(url_for("clientes.lista_clientes"))

    if request.method == "POST":
        data = {
            "nombre": request.form.get("nombre", "").strip(),
            "documento": request.form.get("documento", "").strip(),
            "telefono": request.form.get("telefono", "").strip(),
            "direccion": request.form.get("direccion", "").strip(),
        }
        if not data["nombre"] or not data["documento"]:
            flash("Nombre y documento son obligatorios.", "danger")
            cliente.update(data)
            return render_template("clientes/editar_cliente.html", cliente=cliente)
        try:
            _api().update_cliente(cliente_id, data)
            flash("Cliente actualizado exitosamente.", "success")
            return redirect(url_for("clientes.lista_clientes"))
        except APIError as error:
            if error.status_code == 401:
                return sesion_expirada()
            flash(error.message, "danger")
            cliente.update(data)
    return render_template("clientes/editar_cliente.html", cliente=cliente)


@clientes_bp.route("/clientes/eliminar/<int:cliente_id>", methods=["POST"])
@login_required
def eliminar_cliente(cliente_id):
    try:
        _api().delete_cliente(cliente_id)
        flash("Cliente eliminado exitosamente.", "success")
    except APIError as error:
        if error.status_code == 401:
            return sesion_expirada()
        flash(error.message, "danger")
    return redirect(url_for("clientes.lista_clientes"))

