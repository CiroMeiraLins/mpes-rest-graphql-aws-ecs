from flask import Flask, jsonify, request
from dotenv import load_dotenv
from sqlalchemy import func

from models import Registro
from db import engine, SessionLocal, Base

# Paginação do cenário COMPLEXO
LIMIT_PADRAO = 50
LIMIT_MAXIMO = 100


def _num(valor):
    """Converte Decimal em float sem transformar 0 em None."""
    return float(valor) if valor is not None else None


def _data(valor):
    return valor.isoformat() if valor is not None else None


# Dados cadastrais (escalares) do registro.
# Usado no cenário SIMPLES.
def serialize_cadastro(obj: Registro) -> dict:
    return {
        "id": str(obj.id),
        "nome": obj.nome,
        "email": obj.email,
        "idade": obj.idade,
        "ativo": obj.ativo,
        "criado_em": _data(obj.criado_em),
        "atualizado_em": _data(obj.atualizado_em),
        "salario": _num(obj.salario),
        "score_credito": _num(obj.score_credito),
        "descricao": obj.descricao,
        "status": obj.status,
        "tags": obj.tags,
        "empresa_id": obj.empresa_id,
        "latitude": _num(obj.latitude),
        "longitude": _num(obj.longitude),
    }


# Registro completo, com os documentos aninhados (JSONB).
# Usado nos cenários COMPOSTO e COMPLEXO.
def serialize_completo(obj: Registro) -> dict:
    dados = serialize_cadastro(obj)
    dados["endereco"] = obj.endereco
    dados["preferencias"] = obj.preferencias
    return dados


def create_app() -> Flask:
    load_dotenv()
    app = Flask(__name__)

    # DEV ONLY: cria a tabela caso não exista
    with engine.begin() as conn:
        Base.metadata.create_all(bind=conn)

    @app.get("/health")
    def health():
        return jsonify(status="ok"), 200

    # ------------------------------------------------------------------
    # CENÁRIO SIMPLES — uma entidade por chave primária (1 requisição)
    # ------------------------------------------------------------------
    @app.get("/registros/<id>")
    def get_registro(id: str):
        session = SessionLocal()
        try:
            obj = session.get(Registro, id)
            if not obj:
                return jsonify(error="not found"), 404
            return jsonify(serialize_cadastro(obj)), 200
        finally:
            session.close()

    # ------------------------------------------------------------------
    # CENÁRIO COMPOSTO — objeto principal + documentos aninhados
    # (endereco e preferencias) em uma única requisição
    # ------------------------------------------------------------------
    @app.get("/registros/<id>/detalhes")
    def get_registro_detalhes(id: str):
        session = SessionLocal()
        try:
            obj = session.get(Registro, id)
            if not obj:
                return jsonify(error="not found"), 404
            return jsonify(serialize_completo(obj)), 200
        finally:
            session.close()

    # Sub-recursos individuais (não usados pelo teste de carga atual)
    @app.get("/registros/<id>/endereco")
    def get_endereco(id: str):
        session = SessionLocal()
        try:
            row = (
                session.query(Registro.id, Registro.endereco)
                .filter(Registro.id == id)
                .one_or_none()
            )
            if not row:
                return jsonify(error="not found"), 404
            return jsonify(id=str(row.id), endereco=row.endereco), 200
        finally:
            session.close()

    @app.get("/registros/<id>/preferencias")
    def get_preferencias(id: str):
        session = SessionLocal()
        try:
            row = (
                session.query(Registro.id, Registro.preferencias)
                .filter(Registro.id == id)
                .one_or_none()
            )
            if not row:
                return jsonify(error="not found"), 404
            return jsonify(id=str(row.id), preferencias=row.preferencias), 200
        finally:
            session.close()

    # ------------------------------------------------------------------
    # CENÁRIO COMPLEXO — coleção paginada, registros completos com
    # estruturas aninhadas (JSONB/arrays) + agregação (total de registros)
    # ------------------------------------------------------------------
    @app.get("/registros")
    def list_registros():
        try:
            limit = int(request.args.get("limit", LIMIT_PADRAO))
            offset = int(request.args.get("offset", 0))
        except ValueError:
            return jsonify(error="invalid pagination parameters"), 400

        if limit < 1 or limit > LIMIT_MAXIMO:
            return jsonify(error=f"limit must be between 1 and {LIMIT_MAXIMO}"), 400
        if offset < 0:
            return jsonify(error="offset must be >= 0"), 400

        session = SessionLocal()
        try:
            total = session.query(func.count(Registro.id)).scalar()
            itens = (
                session.query(Registro)
                .order_by(Registro.id)
                .offset(offset)
                .limit(limit)
                .all()
            )
            return jsonify(
                total=total,
                limit=limit,
                offset=offset,
                items=[serialize_completo(x) for x in itens],
            ), 200
        finally:
            session.close()

    return app


# Ponto de entrada do gunicorn
app = create_app()