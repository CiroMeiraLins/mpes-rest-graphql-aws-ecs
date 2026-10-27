CREATE SCHEMA IF NOT EXISTS api_experimento;

CREATE TABLE api_experimento.registros (
	id uuid DEFAULT gen_random_uuid() NOT NULL,
	nome varchar(100) NULL,
	email varchar(150) NULL,
	idade int4 NULL,
	ativo bool NULL,
	criado_em timestamp DEFAULT now() NULL,
	atualizado_em timestamp NULL,
	salario numeric(10, 2) NULL,
	score_credito numeric(5, 2) NULL,
	endereco jsonb NULL,
	preferencias jsonb NULL,
	descricao text NULL,
	status varchar(20) NULL,
	tags _text NULL,
	empresa_id int4 NULL,
	latitude numeric(9, 6) NULL,
	longitude numeric(9, 6) NULL,
	CONSTRAINT registros_pkey PRIMARY KEY (id),
	CONSTRAINT registros_status_check CHECK (((status)::text = ANY ((ARRAY['ativo'::character varying, 'inativo'::character varying, 'pendente'::character varying])::text[])))
);
