from flask import Blueprint, render_template, redirect, url_for, flash, session, request
from src.services.api_usuarios import ApiUsuarios, APIError
from src.controllers.auth_controller import login_required, rol_required, sesion_expirada
from src.utils.pagination import paginate

usuarios_bp = Blueprint("usuarios", __name__)


def _api():
    return ApiUsuarios(session["api_token"])


@usuarios_bp.route("/usuarios")
@login_required
@rol_required("Administrador")
def lista_usuarios():
    try:
        usuarios = _api().get_usuarios() or []

        pagination = paginate(
            usuarios,
            request.args.get("page", 1, type=int),
            request.args.get("per_page", 10, type=int),
        )

        return render_template(
            "usuarios/lista_usuarios.html",
            usuarios=pagination.items_page,
            pagination=pagination,
        )

    except APIError as error:
        if error.status_code == 401:
            return sesion_expirada()

        flash(error.message, "danger")
        return render_template(
            "usuarios/lista_usuarios.html",
            usuarios=[],
            pagination=paginate([]),
        )

@usuarios_bp.route("/usuarios/nuevo", methods=["GET", "POST"])
@login_required
@rol_required("Administrador")
def nuevo_usuario():
    usuario = {
        "nombre": request.form.get("nombre", "").strip(),
        "nombre_usuario": request.form.get("nombre_usuario", "").strip(),
        "email": request.form.get("email", "").strip(),
        "rol": request.form.get("rol", "Vendedor"),
        "activo": request.form.get("activo", "1"),
    }
    if request.method == "POST":
        password = request.form.get("password", "")
        if not all([usuario["nombre"], usuario["nombre_usuario"], usuario["email"], password]):
            flash("Nombre, usuario, correo y contraseña son obligatorios.", "danger")
            return render_template("usuarios/nuevo_usuario.html", usuario=usuario)
        try:
            data = {**usuario, "password": password, "activo": int(usuario["activo"])}
            _api().create_usuario(data)
            flash("Usuario creado exitosamente.", "success")
            return redirect(url_for("usuarios.lista_usuarios"))
        except ValueError:
            flash("El estado del usuario no es válido.", "danger")
        except APIError as error:
            if error.status_code == 401:
                return sesion_expirada()
            flash(error.message, "danger")
    return render_template("usuarios/nuevo_usuario.html", usuario=usuario)


@usuarios_bp.route("/usuarios/eliminar/<int:usuario_id>", methods=["POST"])
@login_required
@rol_required("Administrador")
def eliminar_usuario(usuario_id):
    if usuario_id == (session.get("usuario") or {}).get("id_usuario"):
        flash("No puedes eliminar el usuario con el que tienes la sesión activa.", "warning")
        return redirect(url_for("usuarios.lista_usuarios"))
    try:
        _api().delete_usuario(usuario_id)
        flash("Usuario eliminado exitosamente.", "success")
    except APIError as error:
        if error.status_code == 401:
            return sesion_expirada()
        flash(error.message, "danger")
    return redirect(url_for("usuarios.lista_usuarios"))