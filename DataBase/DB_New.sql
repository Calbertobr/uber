create table public.estatistica_diaria(
	id integer not null,
	data as date,
	data_update timestamp without time zone DEFAULT CURRENT_TIMESTAMP NOT null
);
ALTER TABLE public.estatistica_diaria OWNER TO uber;

COMMENT ON TABLE public.estatistica_diaria IS 'tabela de estatistica diaria calculada';
COMMENT ON COLUMN public.estatistica_diaria.id IS 'id da estatistica';
COMMENT ON COLUMN public.estatistica_diaria.data IS 'data de referencia';
COMMENT ON COLUMN public.estatistica_diaria.data_update IS 'Data de Atualização';
COMMENT ON COLUMN public.estatistica_diaria.id IS 'id da estatistica';
CREATE SEQUENCE public.estatistica_diaria_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;

ALTER SEQUENCE public.estatistica_diaria_id_seq OWNER TO uber;
ALTER SEQUENCE public.estatistica_diaria_id_seq OWNED BY public.estatistica_diaria.id;
