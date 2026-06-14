import os

from dotenv import load_dotenv
from flask import Flask, redirect, url_for
from flask_login import LoginManager, current_user
from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()
login_manager = LoginManager()
login_manager.login_view = "auth.login"
login_manager.login_message = "Faça login para continuar."


def create_app():
    load_dotenv()

    app = Flask(__name__)
    app.config["SECRET_KEY"] = os.getenv("SECRET_KEY", "dev-secret-change-me")
    app.config["SQLALCHEMY_DATABASE_URI"] = os.getenv(
        "DATABASE_URL",
        "mysql+pymysql://root:senha@localhost:3306/receituario_digital",
    )
    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

    db.init_app(app)
    login_manager.init_app(app)

    from .models import User

    @login_manager.user_loader
    def load_user(user_id):
        return db.session.get(User, int(user_id))

    from .routes.auth import auth_bp
    from .routes.consultorio import consultorio_bp
    from .routes.funcionario import funcionario_bp
    from .routes.paciente import paciente_bp
    from .routes.shared import shared_bp

    app.register_blueprint(auth_bp)
    app.register_blueprint(consultorio_bp)
    app.register_blueprint(funcionario_bp)
    app.register_blueprint(paciente_bp)
    app.register_blueprint(shared_bp)

    @app.route("/")
    def index():
        if not current_user.is_authenticated:
            return redirect(url_for("auth.login"))
        return redirect(url_for("shared.dashboard"))

    @app.cli.command("init-db")
    def init_db_command():
        """Cria as tabelas no banco configurado."""
        db.create_all()
        print("Banco inicializado.")

    @app.cli.command("seed-admin")
    def seed_admin_command():
        """Cria um usuário inicial do consultório."""
        from werkzeug.security import generate_password_hash

        email = os.getenv("ADMIN_EMAIL", "admin@consultorio.local")
        password = os.getenv("ADMIN_PASSWORD", "admin123")
        if User.query.filter_by(email=email).first():
            print("Admin já existe.")
            return

        user = User(
            name="Administrador",
            email=email,
            password_hash=generate_password_hash(password),
            role="consultorio",
        )
        db.session.add(user)
        db.session.commit()
        print(f"Admin criado: {email} / {password}")

    return app
