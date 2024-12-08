from flask import send_file
import io
import xlsxwriter
import config

def export_excel():
    """
    Exportação de Resultados para Excel
    ---
    tags:
      - Exportação
    responses:
      200:
        description: "Arquivo Excel com os resultados exportados"
    """
    if not config.estabelecimentos_Cnpj_Raiz:
        return {"error": "Nenhum dado disponível para exportar. Realize uma pesquisa primeiro."}, 400

    output = io.BytesIO()
    workbook = xlsxwriter.Workbook(output, {'in_memory': True})
    worksheet = workbook.add_worksheet()

    # Cabeçalhos
    headers = [
        'CNPJ Raiz', 'Nome Fantasia', 'Sócios', 'País', 'CNAE Principal', 'Endereço', 'Telefones'
    ]

    # Escrever cabeçalhos
    for col_num, header in enumerate(headers):
        worksheet.write(0, col_num, header)

    # Determinar o número máximo de registros
    max_len = len(config.estabelecimentos_Cnpj_Raiz)
    row = 1

    # Escrever dados linha por linha
    for i in range(max_len):
        worksheet.write(row, 0, config.estabelecimentos_Cnpj_Raiz[i])
        worksheet.write(row, 1, config.estabelecimentos_cnpj_ordem[i])
        worksheet.write(row, 2, config.estabelecimentos_cnpj_dv[i])
        worksheet.write(row, 3, config.estabelecimentos_identificador_matriz_filial[i])  # Identificador Matriz/Filial   
        worksheet.write(row, 4, config.empresas_nome[i] if i < len(empresas_nome) else '')  # Nome da Empresa
        worksheet.write(row, 5, config.estabelecimentos_data_de_inicio_de_atividade[i])  # Data de Início de Atividade
        worksheet.write(row, 6, config.estabelecimentos_situacao_cadastral[i])  # Situação Cadastral
        worksheet.write(row, 7, config.estabelecimentos_data_situacao_cadastral[i])  # Data Situação Cadastral
        worksheet.write(row, 8, config.estabelecimentos_nome_fantasia[i])
        worksheet.write(row, 9, config.socios_identificador_socio[i])
        worksheet.write(row, 10, config.socios_nome[i])
        worksheet.write(row, 11, config.socios_cpf_cnpj[i])
        worksheet.write(row, 12, config.socios_qualificacao[i])
        worksheet.write(row, 13, config.socios_data_entrada_sociedade[i])
        worksheet.write(row, 14, config.worksheet.write(row, 3, config.socios_pais[i] if i < len(config.socios_pais) else '')
        worksheet.write(row, 15, config.estabelecimentos_cnae_principal[i] if i < len(config.estabelecimentos_cnae_principal) else '')
        worksheet.write(row, 16, config.estabelecimentos_cnae_secundario[i])  # CNAE Secundário
        worksheet.write(row, 17, config.estabelecimentos_endereco[i] if i < len(config.estabelecimentos_endereco) else '')
        worksheet.write(row, 18, config.estabelecimentos_telefones[i] if i < len(config.estabelecimentos_telefones) else '')
        worksheet.write(row, 19, config.estabelecimentos_correio_eletronico[i])  # Correio Eletrônico      
        worksheet.write(row, 20, config.empresas_natureza_juridica[i] if i < len(empresas_natureza_juridica) else '')  # Natureza Jurídica
        worksheet.write(row, 21, config.empresas_capital_social[i] if i < len(empresas_capital_social) else '')  # Capital Social
        worksheet.write(row, 22, config.empresas_porte[i] if i < len(empresas_porte) else '')  # Porte
        worksheet.write(row, 23, config.socios_repre_legal[i] if i < len(socios_repre_legal) else '')  # Representante Legal
        worksheet.write(row, 24, config.socios_nome_repre[i] if i < len(socios_nome_repre) else '')  # Nome do Representante
        worksheet.write(row, 25, config.socios_quali_repre[i] if i < len(socios_quali_repre) else '')  # Qualificação do Representante
        worksheet.write(row, 26, config.estabelecimentos_motivo_situacao_cadastral[i])  # Motivo Situação Cadastral
        worksheet.write(row, 27, config.estabelecimentos_cidade_exterior[i])  # Cidade no Exterior
        worksheet.write(row, 28, config.estabelecimentos_pais[i])  # País dos Estabelecimentos
        worksheet.write(row, 29, config.estabelecimentos_situacao_especial[i])  # Situação Especial
        worksheet.write(row, 30, config.estabelecimentos_data_situacao_especial[i])  # Data Situação Especial
        worksheet.write(row, 31, config.empresas_ente_federativo[i] if i < len(empresas_ente_federativo) else '')  # Ente Federativo
        worksheet.write(row, 32, config.empresas_quali_responsavel[i] if i < len(empresas_quali_responsavel) else '')  # Qualificação do Responsável
        row += 1

    workbook.close()
    output.seek(0)

    # Retornar o arquivo Excel para download
    return send_file(output, download_name='resultado.xlsx', as_attachment=True)
