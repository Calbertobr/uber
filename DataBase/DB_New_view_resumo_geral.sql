CREATE OR REPLACE VIEW view_resumo_geral
as
select
	s.ref,
	s.data,
	s.tempo,
	s.litros,
	s.ponto,
	s.distancia,
	t.contabil,
	t.descricao,
	s.registros,
	s.valor * t.contabil valor,
	p.percorrido ,
	case
		when t.contabil = 1 and s.valor > 0 and p.percorrido > 0 		then s.valor / p.percorrido  
	else 
		0
	end valorkm,
	case
		when t.id = 3 and s.litros  > 0 and p.percorrido  > 0 			then p.percorrido  / s.litros 
	else 
		0
	end kmlitros
from (
	select
		to_char(m.data, 'YYYYMM') ref ,
		max(m.data) data,
		sum(m.valor) valor,
		sum(m.tempo) tempo,
		sum(m.litros) litros,
		sum(m.ponto) ponto,
		sum(m.distancia ) distancia,
		tipo,
		count(*) registros
	from
		movimento m
	group by
		to_char(m.data, 'YYYYMM'),
		m.tipo
	) s
inner join
	tipo t on s.tipo = t.id
inner join
	(
		select
			to_char(data, 'YYYYMM') ref,
			sum(percorrido ) percorrido
		from
			view_percurso_diario
		group by 
			to_char(data, 'YYYYMM')	
	) p on p.ref = s.ref 	
order by
	s.data,
	t.id

	
	
