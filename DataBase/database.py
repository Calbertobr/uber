
import psycopg2 as pgsql
from psycopg2.extras import RealDictCursor
import os
import socket
from time import sleep

######################################################################################################################3
def connection():   # Cria conexão do banco de dados Pgsql
    # Pgsql
    try:
        DbsHost = os.getenv('DB_HOST')
        DbsUser = os.getenv('DB_USER')
        DbsPass = os.getenv('DB_PASSWORD')
        DbsDbnm = os.getenv('DB_NAME')
        # print(f" \nHost: {DbsHost} \nUser: {DbsUser} \nPassword: {DbsPass} \nDatabase: {DbsDbnm} ")
        mydb = pgsql.connect( host = DbsHost, database = DbsDbnm, user = DbsUser, password = DbsPass, port=5432 )
        conn = mydb.cursor( cursor_factory= RealDictCursor  )

    except pgsql.Error as err :
        print(f"Erro na conexão com o banco de dados #conection#: {err}.")
    else:
        return mydb, conn

######################################################################################################################3
def data_tipo():    # Cria dados dos tipos cadastrados
    try:
        mydb, conn = connection()
        SqlString = """
            SELECT
                t.id,
                t.descricao,
                t.sigla,
                t.contabil,
                count(*) qtd,
                COALESCE(sum(t.contabil * m.valor),0) valor
            FROM
                tipo t
            LEFT JOIN
                movimento m on m.tipo = t.id
            group by
                t.id,
                t.descricao,
                t.sigla,
                t.contabil
        """
        conn.execute(SqlString)
        db_tipos = conn.fetchall()
    except pgsql.Error as err :
        print(f"Erro no banco de dados: {err}.")
    else:
        return db_tipos
    finally:
        if mydb:
            mydb.close()

######################################################################################################################3
def data_carro():   # Cria dados dos veiculos cadastrados
    try:
        mydb, conn = connection()
        SqlString = """
            SELECT 
                c.id,
                c.placa,
                c.fabricante,
                c.modelo,
                c.km_start,
                c.km_end,
                ( c.km_end - c.km_start ) km_rodado,
                c.data_start data_start,
                case
                	when c.data_stop is null
                	then now()::date
                	else c.data_stop
                end data_stop,
                case
                	when c.data_stop is NULL
                	then now()::date - c.data_start::date
                	else c.data_stop::date - c.data_start::date
                end
					dias, 
                count(m.valor) alugueis
            FROM
                carro c
            inner join
            	movimento m on ( c.id = m.carro and m.tipo = 1 )
            group by
            	c.id
            ORDER BY
                c.id desc
        """

        Old = """
            SELECT 
                c.id,
                c.placa,
                c.fabricante,
                c.modelo,
                c.km_start,
                c.km_end,
                ( c.km_end - c.km_start ) km_rodado,
                c.data_start data_start,
                c.data_stop data_stop,
                count(m.valor) alugueis
            FROM
                carro c
            inner join
            	movimento m on ( c.id = m.carro and m.tipo = 1 )
            group by
            	c.id
            ORDER BY
                c.id desc
        """
        conn.execute(SqlString)
        db_carro = conn.fetchall()
    except pgsql.Error as err :
        print(f"Erro no banco de dados: {err}.")
    else:
        return db_carro
    finally:
        if mydb:
            mydb.close()

######################################################################################################################3
def update_carro():    # Atualiza Kilometragem percorrida dos carros.
    mydb, conn = connection()
    SqlString = """
        UPDATE
            carro AS c
        SET
            km_end = m.max_odometro
        FROM (
            SELECT
                carro, MAX(odometro) AS max_odometro
            FROM
                movimento
            GROUP BY
                carro
        ) AS m
        WHERE
            c.id = m.carro;
    """
    try:
        conn.execute(SqlString)
    except pgsql.Error as err :
        print(f"Erro no banco de dados:\n\n {err}.")
    else:
        mydb.commit()
        print("Kilometragem atualizada com sucesso.")
        return True
    finally:
        if mydb:
            mydb.close()

######################################################################################################################3
def update_estat():
    mydb, conn = connection()
    SqlStringGrp =[ """
    insert into estat_diario (data_ref,carro) 
        select
	        date(data),(select max(c.id) from carro c)
        from
	        generate_series(( select max(data_ref)+1  from estat_diario )::date, (select current_date)::date, '1 day'::interval) as data
    ""","""
    select public.ajusta_carros() 
    """]
    for SqlString in SqlStringGrp:
        try:
            conn.execute(SqlString)
        except pgsql.Error as err :
            print(f"Erro no banco de dados:\n\n {err}.")
        else:
            mydb.commit()
            print("Estatistica atualizada com sucesso.")
            return True
        finally:
            if mydb:
                mydb.close()



######################################################################################################################3
def verify_dbs(host, porta):
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.settimeout(1)
    while not sock.connect_ex((host, porta)) == 0:
        sleep(1)
    update_carro()
    update_estat()
    return True

######################################################################################################################3

# connection()