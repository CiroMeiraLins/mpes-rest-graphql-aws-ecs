# app.py (trecho relevante)
import os
from flask import Flask, jsonify
from dotenv import load_dotenv
from ariadne.wsgi import GraphQL
from werkzeug.middleware.dispatcher import DispatcherMiddleware  # << aqui
from schema import schema
from models import Base
from db import engine

def create_app() -> Flask:
    load_dotenv()
    app = Flask(__name__)

    # DEV ONLY: cria tabelas; em PROD use Alembic/migrations
    with engine.begin() as conn:
        Base.metadata.create_all(bind=conn)

    graphql_wsgi = GraphQL(schema, debug=(os.getenv("FLASK_ENV") != "production"))

    # ✅ monta o WSGI do GraphQL em /graphql
    app.wsgi_app = DispatcherMiddleware(app.wsgi_app, {
        "/graphql": graphql_wsgi
    })

    @app.get("/health")
    def health():
        return jsonify(status="ok"), 200

    return app

app = create_app()