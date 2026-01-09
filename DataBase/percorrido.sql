select
	date(m.data) AS data,
    lag(m.carro, 1, 0) OVER (ORDER BY m.data, m.carro) AS carro,
        CASE
            WHEN lag(m.carro, 1, 0) OVER (ORDER BY m.data, m.carro) = m.carro THEN m.odometro - lag(m.odometro, 1, 0) OVER (ORDER BY m.data, m.carro)
            ELSE 0
        END AS percorrido_real
   FROM movimento m
WHERE m.odometro > 0
