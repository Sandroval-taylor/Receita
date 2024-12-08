from flask import Response
import xlsxwriter
import io
import config

def export_excel():
    """
    Exportar os resultados da pesquisa para um arquivo Excel formatado.
    ---
    tags:
      - Exportação
    produces:
      - application/vnd.openxmlformats-officedocument.spreadsheetml.sheet
    responses:
      200:
        description: "Arquivo Excel gerado com sucesso"
    """
    # Cria um arquivo Excel em memória
    output = io.BytesIO()
    workbook = xlsxwriter.Workbook(output, {'in_memory': True})
    worksheet = workbook.add_worksheet("Resultados")

    # Define os cabeçalhos na ordem especificada
    headers = [
        "Matriz/Filial", "CNPJ", "Nome da Empresa", "Início de Atividade", "Situação Cadastral",
        "Data Situação Cadastral", "Motivo Situação Cadastral", "Endereço", "Capital Social",
        "Sócios", "CNAE Principal", "CNAE Secundário", "Correio Eletrônico", "Telefones",
        "Situação Especial", "Data Situação Especial", "Nome Fantasia", "Porte da Empresa",
        "Ente Federativo", "Qualificação do Responsável", "Natureza Jurídica"
    ]

    # Define larguras das colunas
    column_widths = {
        "Matriz/Filial": 20, "CNPJ": 20, "Nome da Empresa": 30, "Início de Atividade": 20,
        "Situação Cadastral": 20, "Data Situação Cadastral": 20, "Motivo Situação Cadastral": 20,
        "Endereço": 50, "Capital Social": 20, "Sócios": 85, "CNAE Principal": 30,
        "CNAE Secundário": 30, "Correio Eletrônico": 30, "Telefones": 30, "Situação Especial": 20,
        "Data Situação Especial": 20, "Nome Fantasia": 20, "Porte da Empresa": 20,
        "Ente Federativo": 20, "Qualificação do Responsável": 20, "Natureza Jurídica": 20
    }

    # Estilos de formatação
    header_format = workbook.add_format({
        'bold': True,
        'font_name': 'Century Gothic',
        'font_size': 12,
        'align': 'center',
        'valign': 'vcenter',
        'text_wrap': True
    })

    cell_format_center = workbook.add_format({
        'font_name': 'Century Gothic',
        'font_size': 12,
        'text_wrap': True,
        'align': 'center',
        'valign': 'vcenter'
    })

    cell_format_left = workbook.add_format({
        'font_name': 'Century Gothic',
        'font_size': 12,
        'text_wrap': True,
        'align': 'left',
        'valign': 'vcenter'
    })

    currency_format = workbook.add_format({
        'font_name': 'Century Gothic',
        'font_size': 12,
        'num_format': 'R$ #,##0.00',
        'align': 'center',
        'valign': 'vcenter'
    })

    format_ativa = workbook.add_format({
        'bold': True,
        'font_color': 'green',
        'font_name': 'Century Gothic',
        'font_size': 12,
        'align': 'center',
        'valign': 'vcenter'
    })
    format_baixada = workbook.add_format({
        'bold': True,
        'font_color': 'red',
        'font_name': 'Century Gothic',
        'font_size': 12,
        'align': 'center',
        'valign': 'vcenter'
    })
    format_outros = workbook.add_format({
        'bold': True,
        'font_color': 'orange',
        'font_name': 'Century Gothic',
        'font_size': 12,
        'align': 'center',
        'valign': 'vcenter'
    })

    # Ajusta larguras das colunas
    for col_index, header in enumerate(headers):
        worksheet.set_column(col_index, col_index, column_widths[header])

    # Escreve os cabeçalhos
    for col_index, header in enumerate(headers):
        worksheet.write(0, col_index, header, header_format)

    def formatar_data(data): #Formata a data de aaaa-mm-dd para dd/mm/aaaa.
        if not data or len(data) != 8:
            return data
        return f"{data[6:8]}/{data[4:6]}/{data[0:4]}"

    def unificar_socios(index):
        return (
            f"{config.socios_identificador_socio[index]} - {config.socios_nome[index]}, {config.socios_cpf_cnpj[index]}, {config.socios_faixa_etaria[index]}, Entrada em: {config.socios_data_entrada_sociedade[index]} \n"
            f"- Representante: {config.socios_nome_representante[index]}, Qualificação Representante: {config.socios_qualificacao_representante[index]}\n"
            f"- País: {config.socios_pais[index]}, Qualificação Sócio: {config.socios_qualificacao[index]}\n"
            f"- Representante Legal: {config.socios_representante_legal[index]}"
        )
    row = 1
    for i in range(len(config.estabelecimentos_Cnpj_Raiz)):
        worksheet.write(row, 0, config.estabelecimentos_identificador_matriz_filial[i], cell_format_center)
        worksheet.write(row, 1, config.estabelecimentos_cnpj_consolidado[i], cell_format_center)
        worksheet.write(row, 2, config.empresas_nome[i], cell_format_center)
        worksheet.write(row, 3, config.estabelecimentos_data_inicio_atividade[i], cell_format_center)

        situacao = config.estabelecimentos_situacao_cadastral[i]
        if situacao == "Ativa":
            worksheet.write(row, 4, situacao, format_ativa)
        elif situacao == "Baixada":
            worksheet.write(row, 4, situacao, format_baixada)
        else:
            worksheet.write(row, 4, situacao, format_outros)

        worksheet.write(row, 5, formatar_data(config.estabelecimentos_data_situacao_cadastral[i]), cell_format_center)
        worksheet.write(row, 6, config.estabelecimentos_motivo_situacao_cadastral[i], cell_format_center)
        worksheet.write(row, 7, config.estabelecimentos_endereco[i], cell_format_left)
        worksheet.write(row, 8, config.empresas_capital_social[i], currency_format)
        worksheet.write(row, 9, unificar_socios(i), cell_format_left)
        worksheet.write(row, 10, config.estabelecimentos_cnae_principal[i], cell_format_center)
        worksheet.write(row, 11, config.estabelecimentos_cnae_secundario[i], cell_format_center)
        worksheet.write(row, 12, config.estabelecimentos_correio_eletronico[i], cell_format_center)
        worksheet.write(row, 13, config.estabelecimentos_telefones[i], cell_format_center)
        worksheet.write(row, 14, config.estabelecimentos_situacao_especial[i], cell_format_center)
        worksheet.write(row, 15, config.estabelecimentos_data_situacao_especial[i], cell_format_center)
        worksheet.write(row, 16, config.estabelecimentos_nome_fantasia[i], cell_format_center)
        worksheet.write(row, 17, config.empresas_porte[i], cell_format_center)
        worksheet.write(row, 18, config.empresas_ente_federativo[i], cell_format_center)
        worksheet.write(row, 19, config.empresas_qualificacao_responsavel[i], cell_format_center)
        worksheet.write(row, 20, config.empresas_natureza_juridica[i], cell_format_center)
        row += 1

    workbook.close()
    output.seek(0)

    response = Response(
        output,
        mimetype="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
    )
    response.headers["Content-Disposition"] = "attachment; filename=ResultadosPesquisa.xlsx"
    return response