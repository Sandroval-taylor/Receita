from flask import request, jsonify
import config
from tabelas import pesquisar_cnpj_raiz
import psycopg2

# Função para conexão com o banco de dados
def connect_to_db():
    return psycopg2.connect(
        host=config.DB_HOST,
        port=config.DB_PORT,
        dbname=config.DB_NAME,
        user=config.DB_USER,
        password=config.DB_PASSWORD
    )

# Função principal consolidada de pesquisa para o Swagger
def api_pesquisa():
    """
    Pesquisas por CNPJ, NOME & CPF, CORINGA
    ---
    tags:
      - Pesquisas
    consumes:
      - application/json
    produces:
      - application/json
    parameters:
      - in: body
        name: body
        required: true
        schema:
          type: object
          properties:
            cnpj:
              type: string
              description: "CNPJ para realizar a pesquisa"
              example: "52.035.849/0001-02"
            nome:
              type: string
              description: "Nome para realizar a pesquisa"
              example: "Rommel"
            cpf:
              type: string
              description: "CPF para realizar a pesquisa junto com o nome"
              example: "410.040.918-42"
            coringa:
              type: string
              description: "Palavra-chave para realizar uma pesquisa coringa"
              example: "palavra-chave"
    responses:
      200:
        description: "Resultados da pesquisa em JSON"
        schema:
          type: object
    """
    try:
        data = request.get_json()

        if not data:
            return jsonify({"error": "Nenhum dado fornecido"}), 400

        cnpj = data.get("cnpj")
        nome = data.get("nome")
        cpf = data.get("cpf")
        coringa = data.get("coringa")

        if not (cnpj or nome or cpf or coringa):
            return jsonify({"error": "Nenhum parâmetro de pesquisa fornecido"}), 400

        config.limpar_variaveis_globais()

        conn = connect_to_db()
        cursor = conn.cursor()

        if cnpj:
            cnpj_raiz = config.tratar_cnpj(cnpj)  # Extrai apenas o CNPJ Raiz
            for i in range(10):
                tabela_estabelecimentos = f"estabelecimentos{i}"
                query = f"SELECT \"Cnpj Raiz\" FROM \"public\".\"{tabela_estabelecimentos}\" WHERE \"Cnpj Raiz\" = %s"
                cursor.execute(query, (cnpj_raiz,))  # Busca diretamente pelo CNPJ Raiz
                resultados = cursor.fetchall()
                for resultado in resultados:
                    pesquisar_cnpj_raiz(cursor, resultado[0])


        elif nome and cpf:
            cpf_tratado = config.tratar_cpf(cpf)
            nome_upper = nome.upper()
            for i in range(10):
                tabela_socios = f"socios{i}"
                query = f"SELECT \"Cnpj Raiz\" FROM \"public\".\"{tabela_socios}\" WHERE UPPER(\"Nome do Socio\") LIKE %s AND \"Cpf/Cnpj do Socio\" LIKE %s"
                cursor.execute(query, (f"%{nome_upper}%", f"%{cpf_tratado}%"))
                for resultado in cursor.fetchall():
                    pesquisar_cnpj_raiz(cursor, resultado[0])

        elif coringa:
            coringa_formatado = config.tratar_coringa(coringa)
            for i in range(10):
                tabela_estabelecimentos = f"estabelecimentos{i}"
                query = f"""
                    SELECT "Cnpj Raiz" 
                    FROM "public"."{tabela_estabelecimentos}" 
                    WHERE UPPER("Nome Fantasia") LIKE %s
                    OR UPPER("Correio Eletronico") LIKE %s
                    OR UPPER("Telefones") LIKE %s
                """
                try:
                    cursor.execute(query, (f"%{coringa_formatado}%", f"%{coringa_formatado}%", f"%{coringa_formatado}%"))
                    resultados = cursor.fetchall()
                    for resultado in resultados:
                        if resultado and len(resultado) > 0:  # Certifica-se de que o resultado é válido
                            pesquisar_cnpj_raiz(cursor, resultado[0])
                except Exception as e:
                    print(f"Erro ao executar a consulta na tabela {tabela_estabelecimentos}: {e}")

            for i in range(10):
                tabela_socios = f"socios{i}"
                query = f"""
                    SELECT "Cnpj Raiz" 
                    FROM "public"."{tabela_socios}" 
                    WHERE UPPER("Nome do Socio") LIKE %s
                """
                try:
                    cursor.execute(query, (f"%{coringa_formatado}%",))
                    resultados = cursor.fetchall()
                    for resultado in resultados:
                        if resultado and len(resultado) > 0:  # Certifica-se de que o resultado é válido
                            pesquisar_cnpj_raiz(cursor, resultado[0])
                except Exception as e:
                    print(f"Erro ao executar a consulta na tabela {tabela_socios}: {e}")


        config.sincronizar_tamanhos_por_cnpj_raiz()
        print("socios_nome:", config.socios_nome)
        print("empresas_capital_social:", config.empresas_capital_social)
        print("empresas_qualificacao_responsavel:", config.empresas_qualificacao_responsavel)

        resultado_json = {
            "sócios": {
                "Cnpj Raiz": config.socios_Cnpj_Raiz,
                "Socios": [
                    f"{identificador} - {nome} {cpf} - {faixa_etaria} - Entrada em: {data_entrada}"
                    for identificador, nome, cpf, faixa_etaria, data_entrada in zip(
                        config.socios_identificador_socio,
                        config.socios_nome,
                        config.socios_cpf_cnpj,
                        config.socios_faixa_etaria,
                        config.socios_data_entrada_sociedade,
                    )
                ],
                "Nome do Representante": config.socios_nome_representante,
                "País": config.socios_pais,
                "Qualificação do Representante": config.socios_qualificacao_representante,
                "Qualificação do Socio": config.socios_qualificacao,
                "Representante Legal": config.socios_representante_legal,
            },
            "empresas": {
                "Cnpj Raiz": config.empresas_Cnpj_Raiz,
                "Nome da Empresa": config.empresas_nome,
                "Capital Social": config.empresas_capital_social,
                "Ente Federativo": config.empresas_ente_federativo,
                "Qualificação do Responsável": config.empresas_qualificacao_responsavel,
                "Natureza Jurídica": config.empresas_natureza_juridica,
                "Porte da Empresa": config.empresas_porte,
            },
            "estabelecimentos": {
                "Cnpj Raiz": config.estabelecimentos_Cnpj_Raiz,
                "Cnpj": config.estabelecimentos_cnpj_consolidado,
                "Identificador Matriz/Filial": config.estabelecimentos_identificador_matriz_filial,
                "Nome Fantasia": config.estabelecimentos_nome_fantasia,
                "Situação Cadastral": config.estabelecimentos_situacao_cadastral,
                "Data Situação Cadastral": config.estabelecimentos_data_situacao_cadastral,
                "Motivo Situação Cadastral": config.estabelecimentos_motivo_situacao_cadastral,
                "Nome da Cidade no Exterior": config.estabelecimentos_cidade_exterior,
                "País": config.estabelecimentos_pais,
                "Data de Início de Atividade": config.estabelecimentos_data_inicio_atividade,
                "Cnae Principal": config.estabelecimentos_cnae_principal,
                "Cnae Secundário": config.estabelecimentos_cnae_secundario,
                "Correio Eletrônico": config.estabelecimentos_correio_eletronico,
                "Situação Especial": config.estabelecimentos_situacao_especial,
                "Data Situação Especial": config.estabelecimentos_data_situacao_especial,
                "Endereço": config.estabelecimentos_endereco,
                "Telefones": config.estabelecimentos_telefones,
            }
        }

        # Salvar os resultados para exportação
        config.socios_Cnpj_Raiz = resultado_json["sócios"]["Cnpj Raiz"]
        config.empresas_Cnpj_Raiz = resultado_json["empresas"]["Cnpj Raiz"]
        config.estabelecimentos_Cnpj_Raiz = resultado_json["estabelecimentos"]["Cnpj Raiz"]

        return jsonify(resultado_json)

    except psycopg2.Error as e:
        return jsonify({"error": str(e)}), 500

    finally:
        cursor.close()
        conn.close()
