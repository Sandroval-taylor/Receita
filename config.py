from werkzeug.utils import secure_filename
import psycopg2

# Configurações do banco de dados
DB_HOST = "localhost"
DB_PORT = "5432"
DB_NAME = "Negativo"
DB_USER = "postgres"
DB_PASSWORD = "sandro01"

# Variáveis globais para armazenar resultados das pesquisas
# Sócios
socios_Cnpj_Raiz, socios_identificador_socio, socios_nome, socios_cpf_cnpj, socios_qualificacao, socios_data_entrada_sociedade = [], [], [], [], [], []
socios_pais, socios_representante_legal, socios_nome_representante, socios_qualificacao_representante, socios_faixa_etaria = [], [], [], [], []

# Empresas
empresas_Cnpj_Raiz, empresas_nome, empresas_capital_social, empresas_ente_federativo = [], [], [], []
empresas_qualificacao_responsavel, empresas_natureza_juridica, empresas_porte = [], [], []

# Estabelecimentos
estabelecimentos_Cnpj_Raiz, estabelecimentos_cnpj_ordem, estabelecimentos_cnpj_dv = [], [], []
estabelecimentos_identificador_matriz_filial, estabelecimentos_nome_fantasia, estabelecimentos_situacao_cadastral = [], [], []
estabelecimentos_data_situacao_cadastral, estabelecimentos_motivo_situacao_cadastral, estabelecimentos_cidade_exterior = [], [], []
estabelecimentos_pais, estabelecimentos_data_inicio_atividade, estabelecimentos_cnae_principal, estabelecimentos_cnae_secundario = [], [], [], []
estabelecimentos_correio_eletronico, estabelecimentos_situacao_especial, estabelecimentos_data_situacao_especial = [], [], []
estabelecimentos_endereco, estabelecimentos_telefones = [], []

pesquisa_por_cnpj = False

# Funções utilitárias
def tratar_cnpj(cnpj_usuario):
    cnpj_limpo = cnpj_usuario.replace(".", "").replace("/", "").replace("-", "")# Remove caracteres indesejados e extrai o CNPJ Raiz
    if len(cnpj_limpo) != 14:
        raise ValueError("CNPJ inválido. O CNPJ deve conter 14 dígitos.")
    return cnpj_limpo[:8]  # Retorna apenas os 8 primeiros dígitos (CNPJ Raiz)

#Formata um CNPJ consolidado no formato XX.XXX.XXX/XXXX-XX.
def formatar_cnpj(cnpj): 
    if len(cnpj) != 14:
        return cnpj  # Retorna o valor original se não tiver o tamanho esperado
    return f"{cnpj[:2]}.{cnpj[2:5]}.{cnpj[5:8]}/{cnpj[8:12]}-{cnpj[12:]}"

def formatar_data(data): #Formata uma data no formato YYYYMMDD para DD/MM/YYYY.
    if len(data) != 8:
        return data  # Retorna o valor original se não tiver o tamanho esperado
    ano = data[:4]
    mes = data[4:6]
    dia = data[6:]
    return f"{dia}/{mes}/{ano}"


def tratar_cpf(cpf_usuario):
    cpf_limpo = cpf_usuario.replace(".", "").replace("-", "")
    return f"***{cpf_limpo[3:9]}**"

def tratar_coringa(coringa_usuario):
    return coringa_usuario.upper()

# Função para limpar variáveis globais
def limpar_variaveis_globais():
    global socios_Cnpj_Raiz, socios_identificador_socio, socios_nome, socios_cpf_cnpj, socios_qualificacao, socios_data_entrada_sociedade
    global socios_pais, socios_representante_legal, socios_nome_representante, socios_qualificacao_representante, socios_faixa_etaria

    global empresas_Cnpj_Raiz, empresas_nome, empresas_capital_social, empresas_ente_federativo
    global empresas_qualificacao_responsavel, empresas_natureza_juridica, empresas_porte

    global estabelecimentos_Cnpj_Raiz, estabelecimentos_cnpj_ordem, estabelecimentos_cnpj_dv
    global estabelecimentos_identificador_matriz_filial, estabelecimentos_nome_fantasia, estabelecimentos_situacao_cadastral
    global estabelecimentos_data_situacao_cadastral, estabelecimentos_motivo_situacao_cadastral, estabelecimentos_cidade_exterior
    global estabelecimentos_pais, estabelecimentos_data_inicio_atividade, estabelecimentos_cnae_principal, estabelecimentos_cnae_secundario
    global estabelecimentos_correio_eletronico, estabelecimentos_situacao_especial, estabelecimentos_data_situacao_especial
    global estabelecimentos_endereco, estabelecimentos_telefones, estabelecimentos_cnpj_consolidado

    socios_Cnpj_Raiz, socios_identificador_socio, socios_nome, socios_cpf_cnpj, socios_qualificacao, socios_data_entrada_sociedade = [], [], [], [], [], []
    socios_pais, socios_representante_legal, socios_nome_representante, socios_qualificacao_representante, socios_faixa_etaria = [], [], [], [], []

    empresas_Cnpj_Raiz, empresas_nome, empresas_capital_social, empresas_ente_federativo = [], [], [], []
    empresas_qualificacao_responsavel, empresas_natureza_juridica, empresas_porte = [], [], []

    estabelecimentos_Cnpj_Raiz, estabelecimentos_cnpj_ordem, estabelecimentos_cnpj_dv = [], [], []
    estabelecimentos_identificador_matriz_filial, estabelecimentos_nome_fantasia, estabelecimentos_situacao_cadastral = [], [], []
    estabelecimentos_data_situacao_cadastral, estabelecimentos_motivo_situacao_cadastral, estabelecimentos_cidade_exterior = [], [], []
    estabelecimentos_pais, estabelecimentos_data_inicio_atividade, estabelecimentos_cnae_principal, estabelecimentos_cnae_secundario = [], [], [], []
    estabelecimentos_correio_eletronico, estabelecimentos_situacao_especial, estabelecimentos_data_situacao_especial = [], [], []
    estabelecimentos_endereco, estabelecimentos_telefones, estabelecimentos_cnpj_consolidado = [], [], []

# Sincronização de dados por CNPJ Raiz
def sincronizar_tamanhos_por_cnpj_raiz():
    indices_por_cnpj = {}
    for idx, cnpj_raiz in enumerate(estabelecimentos_Cnpj_Raiz):
        if cnpj_raiz not in indices_por_cnpj:
            indices_por_cnpj[cnpj_raiz] = []
        indices_por_cnpj[cnpj_raiz].append(idx)

    novos_socios_Cnpj_Raiz, novos_socios_pais, novos_socios_representante_legal = [], [], []
    novos_socios_nome_representante, novos_socios_qualificacao_representante, novos_socios_nome = [], [], []
    novos_empresas_Cnpj_Raiz, novos_empresas_nome, novos_empresas_capital_social = [], [], []
    novos_empresas_ente_federativo, novos_empresas_qualificacao_responsavel = [], []
    novos_empresas_natureza_juridica, novos_empresas_porte = [], []

    for cnpj_raiz, indices in indices_por_cnpj.items():
        try:
            idx_socios = socios_Cnpj_Raiz.index(cnpj_raiz) if cnpj_raiz in socios_Cnpj_Raiz else None
            dados_socios = (
                socios_Cnpj_Raiz[idx_socios] if idx_socios is not None else None,
                socios_pais[idx_socios] if idx_socios is not None else None,
                socios_representante_legal[idx_socios] if idx_socios is not None else None,
                socios_nome_representante[idx_socios] if idx_socios is not None else None,
                socios_qualificacao_representante[idx_socios] if idx_socios is not None else None,
                socios_nome[idx_socios] if idx_socios is not None else None
            )
        except IndexError:
            dados_socios = (None, None, None, None, None, None)

        try:
            idx_empresas = empresas_Cnpj_Raiz.index(cnpj_raiz) if cnpj_raiz in empresas_Cnpj_Raiz else None
            dados_empresas = (
                empresas_Cnpj_Raiz[idx_empresas] if idx_empresas is not None else None,
                empresas_nome[idx_empresas] if idx_empresas is not None else None,
                empresas_capital_social[idx_empresas] if idx_empresas is not None else None,
                empresas_ente_federativo[idx_empresas] if idx_empresas is not None else None,
                empresas_qualificacao_responsavel[idx_empresas] if idx_empresas is not None else None,
                empresas_natureza_juridica[idx_empresas] if idx_empresas is not None else None,
                empresas_porte[idx_empresas] if idx_empresas is not None else None
            )
        except IndexError:
            dados_empresas = (None, None, None, None, None, None, None)

        for _ in indices:
            novos_socios_Cnpj_Raiz.append(dados_socios[0])
            novos_socios_pais.append(dados_socios[1])
            novos_socios_representante_legal.append(dados_socios[2])
            novos_socios_nome_representante.append(dados_socios[3])
            novos_socios_qualificacao_representante.append(dados_socios[4])
            novos_socios_nome.append(dados_socios[5])
            novos_empresas_Cnpj_Raiz.append(dados_empresas[0])
            novos_empresas_nome.append(dados_empresas[1])
            novos_empresas_capital_social.append(dados_empresas[2])
            novos_empresas_ente_federativo.append(dados_empresas[3])
            novos_empresas_qualificacao_responsavel.append(dados_empresas[4])
            novos_empresas_natureza_juridica.append(dados_empresas[5])
            novos_empresas_porte.append(dados_empresas[6])

    socios_Cnpj_Raiz[:] = novos_socios_Cnpj_Raiz
    socios_pais[:] = novos_socios_pais
    socios_representante_legal[:] = novos_socios_representante_legal
    socios_nome_representante[:] = novos_socios_nome_representante
    socios_qualificacao_representante[:] = novos_socios_qualificacao_representante
    socios_nome[:] = novos_socios_nome
    empresas_Cnpj_Raiz[:] = novos_empresas_Cnpj_Raiz
    empresas_nome[:] = novos_empresas_nome
    empresas_capital_social[:] = novos_empresas_capital_social
    empresas_ente_federativo[:] = novos_empresas_ente_federativo
    empresas_qualificacao_responsavel[:] = novos_empresas_qualificacao_responsavel
    empresas_natureza_juridica[:] = novos_empresas_natureza_juridica
    empresas_porte[:] = novos_empresas_porte


def connect_to_db():
    return psycopg2.connect(
        host=DB_HOST, 
        port=DB_PORT, 
        dbname=DB_NAME, 
        user=DB_USER, 
        password=DB_PASSWORD
    )

def template():
    return {
        "socios_Cnpj_Raiz": socios_Cnpj_Raiz,
        "socios_identificador_socio": socios_identificador_socio,
        "socios_nome": socios_nome,
        "socios_cpf_cnpj": socios_cpf_cnpj,
        "socios_qualificacao": socios_qualificacao,
        "socios_data_entrada_sociedade": socios_data_entrada_sociedade,
        "socios_pais": socios_pais,
        "socios_representante_legal": socios_representante_legal,
        "socios_nome_representante": socios_nome_representante,
        "socios_qualificacao_representante": socios_qualificacao_representante,
        "socios_faixa_etaria": socios_faixa_etaria,
        "empresas_Cnpj_Raiz": empresas_Cnpj_Raiz,
        "empresas_nome": empresas_nome,
        "empresas_capital_social": empresas_capital_social,
        "empresas_ente_federativo": empresas_ente_federativo,
        "empresas_qualificacao_responsavel": empresas_qualificacao_responsavel,
        "empresas_natureza_juridica": empresas_natureza_juridica,
        "empresas_porte": empresas_porte,
        "estabelecimentos_Cnpj_Raiz": estabelecimentos_Cnpj_Raiz,
        "estabelecimentos_cnpj_ordem": estabelecimentos_cnpj_ordem,
        "estabelecimentos_cnpj_dv": estabelecimentos_cnpj_dv,
        "estabelecimentos_identificador_matriz_filial": estabelecimentos_identificador_matriz_filial,
        "estabelecimentos_nome_fantasia": estabelecimentos_nome_fantasia,
        "estabelecimentos_situacao_cadastral": estabelecimentos_situacao_cadastral,
        "estabelecimentos_data_situacao_cadastral": estabelecimentos_data_situacao_cadastral,
        "estabelecimentos_motivo_situacao_cadastral": estabelecimentos_motivo_situacao_cadastral,
        "estabelecimentos_cidade_exterior": estabelecimentos_cidade_exterior,
        "estabelecimentos_pais": estabelecimentos_pais,
        "estabelecimentos_data_inicio_atividade": estabelecimentos_data_inicio_atividade,
        "estabelecimentos_cnae_principal": estabelecimentos_cnae_principal,
        "estabelecimentos_cnae_secundario": estabelecimentos_cnae_secundario,
        "estabelecimentos_correio_eletronico": estabelecimentos_correio_eletronico,
        "estabelecimentos_situacao_especial": estabelecimentos_situacao_especial,
        "estabelecimentos_data_situacao_especial": estabelecimentos_data_situacao_especial,
        "estabelecimentos_endereco": estabelecimentos_endereco,
        "estabelecimentos_telefones": estabelecimentos_telefones
    }
