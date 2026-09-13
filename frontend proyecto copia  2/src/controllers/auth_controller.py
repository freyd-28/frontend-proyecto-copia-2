from functools import wraps
from flask import Blueprint, render_template, redirect, url_for, flash, request, session
from src.clients.api_client import APIClient, APIError

auth_bp = Blueprint("auth", __name__)


def login_required(view):
    @wraps(view)
    def wrapper(*args, **kwargs):
        if not session.get("api_token"):
            session["next_url"] = request.full_path.rstrip("?")
            flash("Debes iniciar sesión para continuar.", "warning")
            return redirect(url_for("auth.login"))
        return view(*args, **kwargs)
    return wrapper


def rol_required(*roles):
    def decorator(view):
        @wraps(view)
        def wrapper(*args, **kwargs):
            usuario = session.get("usuario") or {}
            if usuario.get("rol") not in roles:
                flash("No tienes permisos para acceder a esa sección.", "danger")
                return redirect(url_for("home.dashboard"))
            return view(*args, **kwargs)
        return wrapper
    return decorator


def cerrar_sesion(mensaje=None, categoria="info"):
    session.clear()
    if mensaje:
        flash(mensaje, categoria)
    return redirect(url_for("auth.login"))


def sesion_expirada():
    return cerrar_sesion("Tu sesión expiró. Ingresa de nuevo.", "warning")


@auth_bp.route("/login", methods=["GET", "POST"])
def login():
    if session.get("api_token"):
        return redirect(url_for("home.dashboard"))

    email = request.form.get("email", "").strip()
    if request.method == "POST":
        password = request.form.get("password", "")
        if not email or not password:
            flash("Correo y contraseña son obligatorios.", "danger")
            return render_template("auth/login.html", email=email)

        try:
            data = APIClient().post("/auth/login", json={"email": email, "password": password})
            token = data.get("access_token")
            usuario = data.get("usuario")
            if not token or not usuario:
                raise APIError("El backend no devolvió una sesión válida.")
            session["api_token"] = token
            session["usuario"] = usuario
            session.permanent = True
            flash(f"Bienvenido, {usuario.get('nombre', 'usuario')}.", "success")
            destino = session.pop("next_url", None)
            return redirect(destino or url_for("home.dashboard"))
        except APIError as error:
            flash(error.message, "danger")

    return render_template("auth/login.html", email=email)


@auth_bp.route("/logout", methods=["POST"])
def logout():
    return cerrar_sesion("Sesión cerrada correctamente.", "success")


@auth_bp.route("/registro", methods=["GET", "POST"])
def registro():
    if session.get("api_token"):
        return redirect(url_for("home.dashboard"))

    datos = {
        "nombre": request.form.get("nombre", "").strip(),
        "email": request.form.get("email", "").strip(),
    }
    if request.method == "POST":
        password = request.form.get("password", "")
        confirmacion = request.form.get("password_confirmacion", "")
        if not all(datos.values()) or not password:
            flash("Todos los campos son obligatorios.", "danger")
            return render_template("auth/registro.html", datos=datos)
        if password != confirmacion:
            flash("Las contraseñas no coinciden.", "danger")
            return render_template("auth/registro.html", datos=datos)
        try:
            APIClient().post("/auth/register", json={**datos, "password": password})
            flash("Cuenta creada. Ya puedes iniciar sesión.", "success")
            return redirect(url_for("auth.login"))
        except APIError as error:
            flash(error.message, "danger")
    return render_template("auth/registro.html", datos=datos)


@auth_bp.route("/perfil")
@login_required
def perfil():
    usuario = session.get("usuario", {})
    try:
        actualizado = APIClient(session["api_token"]).get("/auth/me")
        if isinstance(actualizado, dict):
            usuario = actualizado
            session["usuario"] = actualizado
    except APIError as error:
        if error.status_code == 401:
            return sesion_expirada()
        flash(error.message, "danger")
    return render_template("auth/perfil.html", usuario=usuario)
