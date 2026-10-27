from ariadne import QueryType, make_executable_schema, gql, ScalarType
from graphql import GraphQLError
from sqlalchemy import func

from db import SessionLocal
from models import Registro

# Paginação do cenário COMPLEXO (mesmos limites da API REST)
LIMIT_PADRAO = 50
LIMIT_MAXIMO = 100

# Scalars
DateTime = ScalarType("DateTime")

@DateTime.serializer
def serialize_datetime(value):
    return value.isoformat() if value else None


JSON = ScalarType("JSON")

@JSON.serializer
def serialize_json(value):
    return value


type_defs = gql('''
    scalar DateTime
    scalar JSON

    type Registro {
        id: ID!
        nome: String
        email: String
        idade: Int
        ativo: Boolean
        criado_em: DateTime
        atualizado_em: DateTime
        salario: Float
        score_credito: Float
        endereco: JSON
        preferencias: JSON
        descricao: String
        status: String
        tags: [String]
        empresa_id: Int
        latitude: Float
        longitude: Float
    }

    "Página de registros do cenário COMPLEXO (coleção + agregação)"
    type RegistrosPagina {
        total: Int!
        limit: Int!
        offset: Int!
        items: [Registro!]!
    }

    type Query {
        "Cenários SIMPLES e COMPOSTO: a diferença está nos campos pedidos na query"
        registro(id: ID!): Registro

        "Cenário COMPLEXO"
        registros(limit: Int = 50, offset: Int = 0): RegistrosPagina!
    }
''')

query = QueryType()


@query.field("registro")
def resolve_registro(*_, id):
    session = SessionLocal()
    try:
        return session.get(Registro, id)
    finally:
        session.close()


@query.field("registros")
def resolve_registros(*_, limit=LIMIT_PADRAO, offset=0):
    if limit < 1 or limit > LIMIT_MAXIMO:
        raise GraphQLError(f"limit must be between 1 and {LIMIT_MAXIMO}")
    if offset < 0:
        raise GraphQLError("offset must be >= 0")

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
        return {"total": total, "limit": limit, "offset": offset, "items": itens}
    finally:
        session.close()


schema = make_executable_schema(type_defs, query, DateTime, JSON)
