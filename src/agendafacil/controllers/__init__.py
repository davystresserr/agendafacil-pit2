def registrar_blueprints(app):
    from .admin import bp as admin_bp
    from .agendamentos import bp as agendamentos_bp
    from .auth import bp as auth_bp
    from .main import bp as main_bp
    from .profissional import bp as profissional_bp

    for bp in (main_bp, auth_bp, agendamentos_bp, profissional_bp, admin_bp):
        app.register_blueprint(bp)
