import config

def pesquisar_cnpj_raiz(cursor, cnpj_r):
    # Função principal para chamar as pesquisas nas tabelas
    pesquisar_cnpj_raiz_socios(cursor, cnpj_r)
    pesquisar_cnpj_raiz_empresas(cursor, cnpj_r)
    pesquisar_cnpj_raiz_estabelecimentos(cursor, cnpj_r)

def pesquisar_cnpj_raiz_socios(cursor, cnpj_r):
    try:
        # Consulta na tabela de Sócios
        for i in range(10):  # Executa a consulta na tabela de sócios
            tabela_socios = f"socios{i}"
            query_socios = f"SELECT * FROM \"public\".\"{tabela_socios}\" WHERE \"Cnpj Raiz\" = %s"
            cursor.execute(query_socios, (cnpj_r,))
            resultados = cursor.fetchall()
            if resultados:
                for linha in resultados:
                    config.socios_Cnpj_Raiz.append(linha[0])
                    config.socios_identificador_socio.append(linha[1])
                    config.socios_nome.append(linha[2])
                    config.socios_cpf_cnpj.append(linha[3])
                    config.socios_qualificacao.append(linha[4])
                    config.socios_data_entrada_sociedade.append(linha[5])
                    config.socios_pais.append(linha[6])
                    config.socios_representante_legal.append(linha[7])
                    config.socios_nome_representante.append(linha[8])
                    config.socios_qualificacao_representante.append(linha[9])
                    config.socios_faixa_etaria.append(linha[10])
    except Exception as e:
        print(f"Erro durante a consulta de sócios: {e}")

def pesquisar_cnpj_raiz_empresas(cursor, cnpj_r):
    try:
        # Consulta na tabela de Empresas
        for i in range(10):  # Executa a consulta na tabela de empresas
            tabela_empresas = f"empresas{i}"
            query_empresas = f"SELECT * FROM \"public\".\"{tabela_empresas}\" WHERE \"Cnpj Raiz\" = %s"
            cursor.execute(query_empresas, (cnpj_r,))
            resultados = cursor.fetchall()
            if resultados:
                for linha in resultados:
                    config.empresas_Cnpj_Raiz.append(linha[0])
                    config.empresas_nome.append(linha[1])
                    config.empresas_capital_social.append(linha[2])
                    config.empresas_ente_federativo.append(linha[3])
                    config.empresas_qualificacao_responsavel.append(linha[4])
                    config.empresas_natureza_juridica.append(linha[5])
                    config.empresas_porte.append(linha[6])
    except Exception as e:
        print(f"Erro durante a consulta de empresas: {e}")

def pesquisar_cnpj_raiz_estabelecimentos(cursor, cnpj_r):
    try:
        # Consulta na tabela de Estabelecimentos
        for i in range(10):  # Executa a consulta na tabela de estabelecimentos
            tabela_estabelecimentos = f"estabelecimentos{i}"
            query_estabelecimentos = f"""
            SELECT * FROM \"public\".\"{tabela_estabelecimentos}\" WHERE \"Cnpj Raiz\" = %s
            """
            cursor.execute(query_estabelecimentos, (cnpj_r,))
            resultados = cursor.fetchall()
            if resultados:
                for linha in resultados:
                    # Garantir que CNPJ Raiz, Ordem e DV sejam formatados corretamente
                    cnpj_raiz = str(linha[0]).zfill(8)  # CNPJ Raiz
                    cnpj_ordem = str(linha[1]).zfill(4)  # CNPJ Ordem
                    cnpj_dv = str(linha[2]).zfill(2)  # CNPJ DV

                    # Criar o CNPJ consolidado
                    cnpj_completo = f"{cnpj_raiz}{cnpj_ordem}{cnpj_dv}"
                    cnpj_formatado = config.formatar_cnpj(cnpj_completo)  # Formatar o CNPJ
                    config.estabelecimentos_Cnpj_Raiz.append(linha[0])  # Apenas o CNPJ Raiz
                    config.estabelecimentos_cnpj_consolidado.append(cnpj_formatado)  # Unificação

                    # Adicionar outros campos necessários
                    config.estabelecimentos_identificador_matriz_filial.append(linha[3])
                    config.estabelecimentos_nome_fantasia.append(linha[4])
                    config.estabelecimentos_situacao_cadastral.append(linha[5])
                    config.estabelecimentos_data_situacao_cadastral.append(linha[6])
                    config.estabelecimentos_motivo_situacao_cadastral.append(linha[7])
                    config.estabelecimentos_cidade_exterior.append(linha[8])
                    config.estabelecimentos_pais.append(linha[9])
                    
                    # Adicionar a data formatada
                    data_inicio = config.formatar_data(str(linha[10]))  # Formatar a data
                    config.estabelecimentos_data_inicio_atividade.append(data_inicio)

                    config.estabelecimentos_cnae_principal.append(linha[11])
                    config.estabelecimentos_cnae_secundario.append(linha[12])
                    config.estabelecimentos_correio_eletronico.append(linha[13])
                    config.estabelecimentos_situacao_especial.append(linha[14])
                    config.estabelecimentos_data_situacao_especial.append(linha[15])
                    config.estabelecimentos_endereco.append(linha[16])
                    config.estabelecimentos_telefones.append(linha[17])

                    # Verificar se é pesquisa por CNPJ e replicar dados
                    if config.pesquisa_por_cnpj:
                        # Replicar dados de sócios
                        config.socios_Cnpj_Raiz.append(config.socios_Cnpj_Raiz[-1] if config.socios_Cnpj_Raiz else None)
                        config.socios_pais.append(config.socios_pais[-1] if config.socios_pais else None)
                        config.socios_representante_legal.append(config.socios_representante_legal[-1] if config.socios_representante_legal else None)
                        config.socios_nome_representante.append(config.socios_nome_representante[-1] if config.socios_nome_representante else None)
                        config.socios_qualificacao_representante.append(config.socios_qualificacao_representante[-1] if config.socios_qualificacao_representante else None)
                        config.socios_nome.append(config.socios_nome[-1] if config.socios_nome else None)

                        # Replicar dados de empresas
                        config.empresas_Cnpj_Raiz.append(config.empresas_Cnpj_Raiz[-1] if config.empresas_Cnpj_Raiz else None)
                        config.empresas_nome.append(config.empresas_nome[-1] if config.empresas_nome else None)
                        config.empresas_capital_social.append(config.empresas_capital_social[-1] if config.empresas_capital_social else None)
                        config.empresas_ente_federativo.append(config.empresas_ente_federativo[-1] if config.empresas_ente_federativo else None)
                        config.empresas_qualificacao_responsavel.append(config.empresas_qualificacao_responsavel[-1] if config.empresas_qualificacao_responsavel else None)
                        config.empresas_natureza_juridica.append(config.empresas_natureza_juridica[-1] if config.empresas_natureza_juridica else None)
                        config.empresas_porte.append(config.empresas_porte[-1] if config.empresas_porte else None)
        ordenar_dados()  # Ordenar os dados pela lista de CNPJ
    except Exception as e:
        print(f"Erro durante a consulta de estabelecimentos: {e}")

def ordenar_dados():
    # Função para ordenar todas as listas com base na lista de estabelecimentos_cnpj
    dados_completos = list(zip(
        config.estabelecimentos_Cnpj_Raiz, config.estabelecimentos_cnpj_ordem, config.estabelecimentos_cnpj_dv,
        config.estabelecimentos_identificador_matriz_filial, config.estabelecimentos_nome_fantasia,
        config.estabelecimentos_situacao_cadastral, config.estabelecimentos_data_situacao_cadastral,
        config.estabelecimentos_motivo_situacao_cadastral, config.estabelecimentos_cidade_exterior,
        config.estabelecimentos_pais, config.estabelecimentos_data_inicio_atividade,
        config.estabelecimentos_cnae_principal, config.estabelecimentos_cnae_secundario,
        config.estabelecimentos_correio_eletronico, config.estabelecimentos_situacao_especial,
        config.estabelecimentos_data_situacao_especial, config.estabelecimentos_endereco,
        config.estabelecimentos_telefones
    ))
    # Ordenar os dados com base no CNPJ Raiz (primeiro campo)
    dados_completos.sort(key=lambda x: x[0])
    # Desempacotar os dados de volta para as listas globais, agora ordenados
    (
        config.estabelecimentos_Cnpj_Raiz, config.estabelecimentos_cnpj_ordem, config.estabelecimentos_cnpj_dv,
        config.estabelecimentos_identificador_matriz_filial, config.estabelecimentos_nome_fantasia,
        config.estabelecimentos_situacao_cadastral, config.estabelecimentos_data_situacao_cadastral,
        config.estabelecimentos_motivo_situacao_cadastral, config.estabelecimentos_cidade_exterior,
        config.estabelecimentos_pais, config.estabelecimentos_data_inicio_atividade,
        config.estabelecimentos_cnae_principal, config.estabelecimentos_cnae_secundario,
        config.estabelecimentos_correio_eletronico, config.estabelecimentos_situacao_especial,
        config.estabelecimentos_data_situacao_especial, config.estabelecimentos_endereco,
        config.estabelecimentos_telefones
    ) = map(list, zip(*dados_completos))
