from flask import Flask, session
from src.config.config import config


def create_app(config_name="development"):
    app = Flask(__name__, template_folder="templates", static_folder="static")
    app.config.from_object(config.get(config_name, config["default"]))

    from src.controllers.auth_controller import auth_bp
    from src.controllers.home_controller import home_bp
    from src.controllers.clientes_controller import clientes_bp
    from src.controllers.productos_controller import productos_bp
    from src.controllers.facturas_controller import facturas_bp
    from src.controllers.usuarios_controller import usuarios_bp

    app.register_blueprint(auth_bp, url_prefix="/auth")
    app.register_blueprint(home_bp)
    app.register_blueprint(clientes_bp)
    app.register_blueprint(productos_bp)
    app.register_blueprint(facturas_bp)
    app.register_blueprint(usuarios_bp)

    @app.context_processor
    def contexto_global():
        usuario = session.get("usuario") or {}
        return {
            "usuario_actual": usuario,
            "active_page": request_active_page(),
        }

    @app.errorhandler(404)
    def no_encontrado(error):
        return "Página no encontrada", 404

    @app.errorhandler(500)
    def error_interno(error):
        return "Ocurrió un error interno en el frontend.", 500

    return app


def request_active_page():
    from flask import request
    path = request.path
    if path.startswith("/dashboard") or path == "/":
        return "dashboard"
    for section in ("clientes", "productos", "facturas", "usuarios"):
        if path.startswith(f"/{section}"):
            return section
    return ""

