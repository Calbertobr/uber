DROP TABLE public.estat_diario CASCADE;

create table estat_diario (
	id serial primary key ,
	data_write timestamp without time zone DEFAULT CURRENT_TIMESTAMP NOT NULL,
	data_ref date not null,
	carro int DEFAULT 1 NOT NULL, 
	consumo_litros double precision DEFAULT 0 NOT NULL,
	valor_km       double precision DEFAULT 0 NOT NULL,
	Valor_aluguel  double precision DEFAULT 0 NOT NULL,
	total_km_pago  double precision DEFAULT 0 NOT NULL,
	total_km_real  double precision DEFAULT 0 NOT NULL
);
ALTER TABLE public.estat_diario OWNER TO uber;
COMMENT ON TABLE public.estat_diario IS 'tabela de estatistica de dados';
COMMENT ON COLUMN public.estat_diario.id IS 'Id do Calculo';
COMMENT ON COLUMN public.estat_diario.data_write IS 'Data da Atualização';
COMMENT ON COLUMN public.estat_diario.data_ref IS 'Data de referencia dos dados';
COMMENT ON COLUMN public.estat_diario.carro IS 'ID do Carro';
COMMENT ON COLUMN public.estat_diario.consumo_litros IS 'Consumo de Litros';
COMMENT ON COLUMN public.estat_diario.valor_km IS 'Valor por Km';
COMMENT ON COLUMN public.estat_diario.Valor_aluguel IS 'Valor do Aluguel';
COMMENT ON COLUMN public.estat_diario.total_km_pago IS 'Total de Km Pago';
COMMENT ON COLUMN public.estat_diario.total_km_real IS 'Total de Km Real';

ALTER SEQUENCE public.estat_diario_id_seq OWNER TO uber;
ALTER SEQUENCE public.estat_diario_id_seq OWNED BY public.estat_diario.id;

ALTER TABLE ONLY public.estat_diario
    ADD CONSTRAINT estat_diario_carro_fkey FOREIGN KEY (carro) REFERENCES public.carro(id);



insert into estat_diario (data_ref,carro) values ( to_date('01/07/2025','DD/MM/YYYY'), 1 )


