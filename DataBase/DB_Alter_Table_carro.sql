
ALTER TABLE carro ADD COLUMN data_start date;
ALTER TABLE carro ADD COLUMN data_stop date;

COMMENT ON COLUMN public.carro.data_start IS 'Data Inicio do Aluguel';
COMMENT ON COLUMN public.carro.data_stop IS 'Data Final do Aluguel';

