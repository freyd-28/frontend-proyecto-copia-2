from flask import Blueprint, render_template, redirect, url_for, session, flash
from src.controllers.auth_controller import login_required, sesion_expirada
from src.services.api_clientes import ApiClientes, APIError
from src.services.api_productos import ApiProductos
from src.services.api_facturas import ApiFacturas

home_bp = Blueprint("home", __name__)


@home_bp.route("/")
def index():
    if session.get("api_token"):
        return redirect(url_for("home.dashboard"))
    return redirect(url_for("auth.login"))


@home_bp.route("/dashboard")
@login_required
def dashboard():
    token = session["api_token"]
    clientes, productos, facturas = [], [], []
    error = None
    try:
        clientes = ApiClientes(token).get_clientes() or []
        productos = ApiProductos(token).get_productos() or []
        facturas = ApiFacturas(token).get_facturas() or []
    except APIError as exc:
        if exc.status_code == 401:
            return sesion_expirada()
        error = exc.message
        flash(error, "warning")

    total_facturacion = sum(float(f.get("total") or 0) for f in facturas if str(f.get("estado", "")).lower() != "anulada")
    stock_alertas = 0  
    return render_template(
        "dashboard/dashboard.html",
        total_clientes=len(clientes),
        total_productos=len(productos),
        total_facturas=len(facturas),
        total_facturacion=total_facturacion,
        stock_alertas=stock_alertas,
        api_error=error,
    )

