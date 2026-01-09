#!./.venv/bin/python3

# app.py

import database as dbm
from os import getenv
from time import sleep
from flask import Flask, render_template, request, redirect, url_for
from datetime import date, timedelta, datetime
import psycopg2 as pgsql
import psycopg2.extras
import statistics as stat

DbsHost = getenv('DB_HOST')
dbm.verify_dbs( DbsHost, 5432)
app = Flask(__name__)


######################################################################################################################3
@app.route('/')
def index():
    """Rota da página inicial com o menu."""
    return render_template('index.html')
######################################################################################################################3
@app.route('/cadastro_movimento', methods=['GET', 'POST'])
def cadastro_movimento():
    """Rota para o formulário de cadastro de Movimentos."""
    tipos = dbm.data_tipo()
    carros = dbm.data_carro()
    mydb, conn = dbm.connection()
    if request.method == 'POST':
        data = str.replace( request.form['data'], 'T', ' ')
        SqlString = 'INSERT INTO movimento (tipo, carro, data, odometro, tempo, distancia, ponto, valor, litros) VALUES ( %s, %s, %s, %s, %s, %s, %s, %s, %s)'
        Dados =  ( request.form['tipo'], request.form['carro'], data, request.form['odometro'], request.form['tempo'], request.form['distancia'], request.form['ponto'], request.form['valor'], request.form['litros'])
        try:
            conn.execute(SqlString, Dados)
            mydb.commit()
        except pgsql.Error as err :
            print(f"Erro no banco de dados: {err}.")
        finally:
            if mydb:
                mydb.close()
        return redirect(url_for('index'))
    return render_template('cadastro_movimento.html', tipos=tipos, carros=carros )
######################################################################################################################3
@app.route('/cadastro_tipo', methods=['GET', 'POST'])
def cadastro_tipo():
    """Rota para o formulário de cadastro de Tipos."""
    mydb, conn = dbm.connection()
    if request.method == 'POST':
        SqlString = 'INSERT INTO tipo (sigla, descricao, contabil) VALUES (%s, %s, %s)'
        Dados =  ( request.form['sigla'], request.form['descript'], request.form['contabil'] )
        conn.execute(SqlString , Dados)
        mydb.commit()
        mydb.close()
        return redirect(url_for('index'))
    return render_template('cadastro_tipo.html')
######################################################################################################################3
@app.route('/cadastro_carro', methods=['GET', 'POST'])
def cadastro_carro():
    """Rota para o formulário de cadastro de Carros."""
    mydb, conn = dbm.connection()
    if request.method == 'POST':
        SqlString = 'INSERT INTO carro (placa, fabricante, modelo, km_start, km_end) VALUES (%s, %s, %s, %s, %s)'
        Dados = ( request.form['placa'], request.form['fabricante'], request.form['modelo'], request.form['km_start'], request.form['km_end'] )
        conn.execute(SqlString , Dados)
        mydb.commit()
        mydb.close()
        return redirect(url_for('index'))
    return render_template('cadastro_carro.html')
######################################################################################################################3
#
#   #   #   #   #   #   #   #              C   O   N   S   U   L   T   A   S              #   #   #   #   #   #   #   #
#
######################################################################################################################3

######################################################################################################################3
##@@ Resumo Geral
@app.route('/consulta_resumo_geral')
def consulta_resumo_geral():
    """Rota de resultado Geral."""
    mydb, conn = dbm.connection()
    release = 2
    resumo = []
    total = { 
        'id': '00',
        'descricao': 'Todos',
        'qtd': 0.0,
        'percorrido': 0,
        'valortotal': 0.0,
        'litros': 0.0
    }
    if request.method == 'GET':
        release = 2
        try:
            sql_query_resumo = f"""
				select
					vo.id, 
                    vo.descricao, 
                    sum(vo.qtd) qtd, 
                    sum(vo.percorrido) percorrido, 
                    sum(vo.valortotal) valortotal,
                    sum(vo.litros) litros
				from
					(
	                SELECT 
	                    t.id,
	                    t.descricao, 
	                    count(*) qtd,
                        COALESCE(max(v.percorrido),0) percorrido,
	                    sum(m.valor * t.contabil) valortotal,
                        sum(m.litros) litros
	                FROM
	                    movimento m
	                JOIN
	                    tipo t ON m.tipo = t.id
	                JOIN
	                    carro c ON m.carro = c.id
	                left JOIN
	                        view_percurso_diario v on v.data = date(m.data)  and t.id = 8
	                GROUP BY
	                        date(m.data), t.id 
	                ORDER BY
	                        date(m.data), t.id
					) vo
				group by
					vo.id,
					vo.descricao
            """
            sql_query_resumo_mes = """
                select
                    to_char(vo.data, 'YYYY-MM') Mes,
                    sum(vo.qtd) qtd,
                    sum(vo.litros) litros,
                    sum(vo.percorrido) percorrido, 
                    sum(vo.percorrido) / sum(vo.litros) lpk,
                    sum(vo.valortotal) valortotal 
                from
                    (
                    select
                        date(m.data) data,
                        t.id,
                        t.descricao, 
                        count(*) qtd, 
                        COALESCE(max(v.percorrido),0) percorrido, 
                        sum(m.valor * t.contabil) valortotal,
                        sum(m.litros) litros
                    FROM
                        movimento m
                    JOIN
                        tipo t ON m.tipo = t.id
                    JOIN
                        carro c ON m.carro = c.id
                    left JOIN
                            view_percurso_diario v on v.data = date(m.data)  and t.id = 8
                    GROUP BY
                            date(m.data), t.id 
                    ORDER BY
                            date(m.data), t.id
                    ) vo
                group by
                    to_char(vo.data, 'YYYY-MM')
                order by
                    to_char(vo.data, 'YYYY-MM')
            """
            conn.execute(sql_query_resumo)
            resumo = conn.fetchall()

            conn.execute(sql_query_resumo_mes)
            resumo_mes = conn.fetchall()
            conn.close()
        except pgsql.Error as err :
            print(f"Erro no banco de dados: \n{err}.\n")
        finally:
            if mydb:
                mydb.close()
        sum_total = 0
        sum_litros = 0
        sum_percorido = 0
        sum_qtd = 0
        # percorrido, valortol, litros = 0.0, 0.0, 0.0, 0.0
        lpk_med = []
        for resu in resumo_mes:
            sum_total += resu['valortotal']
            sum_qtd += resu['qtd']
            sum_litros += resu['litros']
            sum_percorido += float(resu['percorrido'])
            lpk_med.append(resu['lpk'])
        total['valortotal'] = sum_total
        total['litros'] = sum_litros
        total['percorrido'] = sum_percorido
        total['qtd'] = sum_qtd
        total['lpk'] = sum(lpk_med) / len(lpk_med)

        

    return render_template('consulta_resumo_geral.html', resumo=resumo, total=total, resumo_mes=resumo_mes , release=release )
###@@
@app.route('/consulta_resultado_mes', methods=['GET', 'POST'])
def consulta_resultado_mes():
    """Rota para a consulta de movimentos."""
    mydb, conn = dbm.connection()
    movimentos = []
    resumo = []
    estatistica = []
    total = { 'resultado': 0.0 }
    if request.method == 'POST':
        release = 2
        data_mes = request.form['data_mes']
        if data_mes == '' :
            data_inicio = date.today()
            data_fim    = date.today()
        else:
            data_inicio = f'{data_mes[:8]}01'
            data_fim    = data_mes
        try:
            sql_query = f"""
                SELECT 
                    date(m.data) data,
                    t.id,
                    t.descricao,
                    c.placa,
                    count(*) qtd,
                    max(m.odometro) odometro,
                    sum(m.tempo) tempo,
                    sum(m.distancia) distancia,
                    case when p.percorrido > 1 then p.percorrido else 0 end distancia_real,
                    CASE when sum(m.distancia) > 0 and p.percorrido > 0 then (( 1 - sum(m.distancia) / p.percorrido )* 100 ) else 0 END perda,
                    sum(m.ponto) ponto,
                    sum(m.valor * t.contabil ) valor
                FROM
                    movimento m
                JOIN
                    tipo t ON m.tipo = t.id
                JOIN
                    carro c ON m.carro = c.id
                LEFT JOIN
                	view_percurso_diario p on p.data = date(m.data) and t.id in (2,8)
                WHERE
                    DATE(m.data) BETWEEN '{data_inicio}' AND
                    (DATE_TRUNC('month', '{data_fim}'::DATE) + INTERVAL '1 month - 1 day')::DATE
                group by
                	date(m.data),
                	t.id,
                    t.descricao, 
                    c.placa,
                    p.percorrido
                ORDER BY
                    date(m.data)
            """
            print(sql_query)
            conn.execute(sql_query )
            movimentos = conn.fetchall()

            sql_query_resumo = f"""
				select
					vo.id, vo.descricao, sum(vo.qtd) qtd, sum(vo.litros) litros,
                    sum(vo.percorrido) percorrido, sum(vo.valortotal) valortotal 
				from
					(
	                SELECT 
	                    t.id,
	                    t.descricao, 
	                    count(*) qtd,
                        sum(m.litros) litros,
	                    max(v.percorrido) percorrido, 
	                    sum(m.valor * t.contabil) valortotal
	                FROM
	                    movimento m
	                JOIN
	                    tipo t ON m.tipo = t.id
	                JOIN
	                    carro c ON m.carro = c.id
	                left JOIN
	                        view_percurso_diario v on v.data = date(m.data)  and t.id = 8
	                WHERE
	                    DATE(m.data) BETWEEN '{data_inicio}' AND 
                        (DATE_TRUNC('month', '{data_fim}'::DATE) + INTERVAL '1 month - 1 day')::DATE
	                GROUP BY
	                        date(m.data), t.id 
	                ORDER BY
	                        date(m.data), t.id
					) vo
				group by
					vo.id,
					vo.descricao
                order by
					vo.id
            """
            conn.execute(sql_query_resumo)
            resumo = conn.fetchall()
            conn.close()
        except pgsql.Error as err :
            print(f"Erro no banco de dados: \n{err}.\n")
        finally:
            if mydb:
                mydb.close()
        for resu in resumo:
            total['resultado'] += resu['valortotal']

            
    return render_template('consulta_resultado_mes.html', movimentos=movimentos, resumo=resumo, total=total, estatistica=estatistica )
# , release=release
######################################################################################################################3
###@@
@app.route('/consulta_resultado_dia', methods=['GET', 'POST'])
def consulta_resultado_dia():
    """Rota para a consulta de resultados."""
    mydb, conn = dbm.connection()
    movimento_dia = [] 
    movimento_soma = []
    resumo = []
    if request.method == 'POST':
        data_ref = request.form['data_ref']
        if data_ref == '' :
            data_ref = date.today()
        try:
            # data_ref = f"{data_ref[-2:]}-{data_ref[5:7]}-{data_ref[:4]}"
            sql_query = f"""
                SELECT 
                    t.id, m.data, t.descricao, c.placa, m.odometro, 
                    m.tempo, m.distancia, m.ponto, m.valor, t.contabil AS tipo_contabil,
                    case
                    	when m.valor > 0 and m.distancia > 0 then m.valor / m.distancia
                    else
                    	0
                    end valor_km
                FROM
                    movimento m
                JOIN
                    tipo t ON m.tipo = t.id
                JOIN
                    carro c ON m.carro = c.id
                WHERE
                    DATE(m.data) = '{data_ref}'
                ORDER BY
                    m.data
                """
            conn.execute(sql_query)
            movimento_dia = conn.fetchall()
            sql_query_soma = f"""
                SELECT 
                    t.id, date(m.data) data, t.descricao, c.placa, k.percorrido percurso, sum(m.tempo) tempo_total,
                    sum(m.distancia) distancia_total, sum(m.ponto) pontos, sum( m.valor * t.contabil ) valor_total,
                    case
                    	when sum( m.valor * t.contabil ) > 0 and sum(m.distancia) > 0 
                        then sum( m.valor * t.contabil ) / sum(m.distancia)
                    else
                    	0
                    end valor_km
                FROM
                    movimento m
                JOIN
                    tipo t ON m.tipo = t.id
                JOIN
                    carro c ON m.carro = c.id
                JOIN 
                	view_percurso_diario k on date(m.data) = k.data and c.id = k.carro 
                WHERE
                    DATE(m.data) = '{data_ref}'
                GROUP BY
                    t.id, date(m.data), t.descricao, c.placa, k.percorrido
                ORDER BY
                    date(m.data)
                """
            conn.execute(sql_query_soma)
            movimento_soma = conn.fetchall()
            sql_query_resumo = f"""
                SELECT 
                    k.percorrido,
                    sum(m.distancia) distancia,
                    sum(m.valor) valor,
                    sum(m.valor) / sum(m.distancia) valor_km,
                    sum(m.valor) / k.percorrido valor_km_total,
                    sum(m.distancia) / k.percorrido * 100  servico
                FROM
                    movimento m
                JOIN
                    tipo t ON m.tipo = t.id
                JOIN 
                        view_percurso_diario k on date(m.data) = k.data 
                WHERE
                    t.id in (2,8,9) and DATE(m.data) = '{data_ref}'
                group by
                    k.percorrido
                having
                    sum(m.valor) >0 and sum(m.distancia) > 0 and k.percorrido > 0
                """
            conn.execute(sql_query_resumo)
            resumo = conn.fetchall()  
            conn.close()
        except pgsql.Error as err :
            print(f"Erro no banco de dados: {err}.")
        finally:
            if mydb:
                mydb.close()
    return render_template('consulta_resultado_dia.html', 
                            movimento_dia = movimento_dia,
                            movimento_soma = movimento_soma,
                            resumo = resumo )
######################################################################################################################3
##@@ Cunsulta Movimento do periodo selecionado
@app.route('/consulta_movimentos', methods=['GET', 'POST'])
def consulta_movimentos():
    """Rota para a consulta de movimentos."""
    mydb, conn = dbm.connection()
    movimentos = []
    resumo = []
    bare = []
    total = { 'resultado': 0.0 }
    if request.method == 'POST':
        release = 2
        data_inicio = request.form['data_inicio']
        data_fim = request.form['data_fim']
        if data_inicio == '' or data_fim == '' :
            data_inicio = date.today()
            data_fim    = date.today()
        try:
            sql_query = f"""
                SELECT 
                    t.id, m.data, t.descricao, c.placa, m.odometro, m.tempo, m.distancia,
                    m.ponto, m.valor, t.contabil AS tipo_contabil,
                    case
                    	when t.contabil = 1 and m.valor >0 and m.distancia > 0 
                        then m.valor / m.distancia
                    else
                    	0	
                    end AS valorkm
                FROM
                    movimento m
                JOIN
                    tipo t ON m.tipo = t.id
                JOIN
                    carro c ON m.carro = c.id
                WHERE
                    DATE(m.data) BETWEEN '{data_inicio}' AND '{data_fim}'
                ORDER BY
                    m.data
            """
            sql_query_bare = f"""
				SELECT 
					mo.id,
					mo.data data,
	                '' tipo,
	                mo.placa,  
	                pe.percorrido,
	                mo.tempo,
	                mo.distancia,
	                mo.ponto,
					mo.valor,
                        case
	                        when mo.valor > 0 and pe.percorrido > 0 
	                        then mo.valor / pe.percorrido
                        else
                            0	
                        end AS valorkm
				from
					(
	                SELECT 
	                	count(*) id,
	                    sum(m.tempo) tempo,
                        c.placa,
	                    sum(m.distancia) distancia,
	                    sum(m.ponto) ponto, 
	                    sum(m.valor * t.contabil) valor, 
	                    0 tipo_contabil,
	                    date(m.data) data
	                FROM
	                    movimento m
	                JOIN
	                    tipo t ON m.tipo = t.id
	                JOIN
	                    carro c ON m.carro = c.id
	                WHERE
	                    DATE(m.data) BETWEEN '{data_inicio}' AND '{data_fim}'
	                GROUP BY
	                    date(m.data), c.placa
	                ORDER BY
	                    date(m.data)
                   	) mo
				join
					view_percurso_diario pe on pe.data = mo.data
            """
            sql_query_resumo = f"""
				select
					vo.id, 
                    vo.descricao, 
                    sum(vo.qtd) qtd, 
                    sum(vo.percorrido) percorrido, 
                    sum(vo.valortotal) valortotal 
				from
					(
	                SELECT 
	                    t.id,
	                    t.descricao, 
	                    count(*) qtd, 
	                    max(v.percorrido) percorrido, 
	                    sum(m.valor * t.contabil) valortotal
	                FROM
	                    movimento m
	                JOIN
	                    tipo t ON m.tipo = t.id
	                JOIN
	                    carro c ON m.carro = c.id
	                left JOIN
	                        view_percurso_diario v on v.data = date(m.data)  and t.id = 8
	                WHERE
	                    DATE(m.data) BETWEEN '{data_inicio}' AND '{data_fim}'
	                GROUP BY
	                        date(m.data), t.id 
	                ORDER BY
	                        date(m.data), t.id
					) vo
				group by
					vo.id,
					vo.descricao


            """
            conn.execute(sql_query )
            movimentos = conn.fetchall()
            conn.execute(sql_query_bare)
            bare = conn.fetchall()
            conn.execute(sql_query_resumo)
            resumo = conn.fetchall()
            conn.close()
        except pgsql.Error as err :
            print(f"Erro no banco de dados: \n{err}.\n")
        finally:
            if mydb:
                mydb.close()
        for resu in resumo:
            total['resultado'] += resu['valortotal']
    return render_template('consulta_movimentos.html', movimentos=movimentos, resumo=resumo, bare=bare, total=total )
# , release=release
######################################################################################################################3
###@@ Consulta Tipos - OK MY
@app.route('/consulta_tipos')
def consulta_tipos():
    """Rota para a consulta de tipos."""
    release = 2
    total = { 'resultado': 0.0, 'eventos': 0.0 }
    tipos = dbm.data_tipo()
    for resu in tipos:
        total['resultado'] += resu['valor']
        total['eventos']   += resu['qtd']
    return render_template('consulta_tipos.html', tipos=tipos, total=total, release=release )
######################################################################################################################
###@@ Consulta Veiculos - OK MY
@app.route('/consulta_veiculos')
def consulta_veiculos():
    dbm.update_carro()
    # dbs.update_kilometragem()
    """Rota para a consulta de veiculos."""
    release = 2
    total = { 
        'Kilometragem': 0.0,
        'Alugueis': 0,
        'InicioContrato': datetime.now().date(),
        'DiasUso': 0,
        'DiasContrato': 0
    }
    veiculos = dbm.data_carro()
    for veiculo in veiculos:
        total['Kilometragem'] += veiculo['km_rodado']
        total['Alugueis'] += veiculo['alugueis']
        if total['InicioContrato'] > veiculo['data_start'] :
            total['InicioContrato'] = veiculo['data_start']
            total['DiasUso'] += veiculo['dias']
    total['DiasContrato'] = total['Alugueis'] * 30        
    total['Alugueis'] = total['Alugueis'] * 5000
    print(total)
    return render_template('consulta_veiculos.html', veiculos=veiculos , total=total , release=release )
######################################################################################################################3
###@@
if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000 ) # O '0.0.0.0' torna o servidor acessível a partir de outros dispositivos da rede
 