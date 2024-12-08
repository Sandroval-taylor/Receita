from werkzeug.utils import secure_filename
import psycopg2

# Configurações do banco de dados
DB_HOST = "postgresql-188561-0.cloudclusters.net"
DB_PORT = "10029"
DB_NAME = "Negativo"
DB_USER = "sandro"
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
def sincronizar_tamanhos_por_cnpj_raiz(): #Sincroniza o tamanho das listas globais de empresas, sócios e estabelecimentos com base no CNPJ Raiz. Garante que os índices correspondem às mesmas entidades.
    # Mapeia todos os índices de CNPJ Raiz para os estabelecimentos
    indices_por_cnpj = {}
    for idx, cnpj_raiz in enumerate(estabelecimentos_Cnpj_Raiz):
        if cnpj_raiz not in indices_por_cnpj:
            indices_por_cnpj[cnpj_raiz] = []
        indices_por_cnpj[cnpj_raiz].append(idx)

    # Função auxiliar para buscar dados por índice ou retornar valores padrão
    def buscar_dados(lista, idx):
        return lista[idx] if idx is not None and idx < len(lista) else None

    # Função auxiliar para preencher listas com valores sincronizados
    def preencher_lista(dados, indices):
        return [dados for _ in indices]

    # Variáveis para armazenar as listas sincronizadas
    novos_socios = {k: [] for k in ["Cnpj_Raiz", "pais", "representante_legal", "nome_representante", "qualificacao_representante", "nome"]}
    novos_empresas = {k: [] for k in ["Cnpj_Raiz", "nome", "capital_social", "ente_federativo", "qualificacao_responsavel", "natureza_juridica", "porte"]}

    # Sincronizar dados por CNPJ Raiz
    for cnpj_raiz, indices in indices_por_cnpj.items():
        # Buscar dados dos sócios
        idx_socios = socios_Cnpj_Raiz.index(cnpj_raiz) if cnpj_raiz in socios_Cnpj_Raiz else None
        dados_socios = {
            "Cnpj_Raiz": buscar_dados(socios_Cnpj_Raiz, idx_socios),
            "pais": buscar_dados(socios_pais, idx_socios),
            "representante_legal": buscar_dados(socios_representante_legal, idx_socios),
            "nome_representante": buscar_dados(socios_nome_representante, idx_socios),
            "qualificacao_representante": buscar_dados(socios_qualificacao_representante, idx_socios),
            "nome": buscar_dados(socios_nome, idx_socios),
        }

        # Buscar dados das empresas
        idx_empresas = empresas_Cnpj_Raiz.index(cnpj_raiz) if cnpj_raiz in empresas_Cnpj_Raiz else None
        dados_empresas = {
            "Cnpj_Raiz": buscar_dados(empresas_Cnpj_Raiz, idx_empresas),
            "nome": buscar_dados(empresas_nome, idx_empresas),
            "capital_social": buscar_dados(empresas_capital_social, idx_empresas),
            "ente_federativo": buscar_dados(empresas_ente_federativo, idx_empresas),
            "qualificacao_responsavel": buscar_dados(empresas_qualificacao_responsavel, idx_empresas),
            "natureza_juridica": buscar_dados(empresas_natureza_juridica, idx_empresas),
            "porte": buscar_dados(empresas_porte, idx_empresas),
        }

        # Preencher as listas sincronizadas
        for key, value in dados_socios.items():
            novos_socios[key].extend(preencher_lista(value, indices))
        for key, value in dados_empresas.items():
            novos_empresas[key].extend(preencher_lista(value, indices))

    # Substituir as listas globais pelas listas sincronizadas
    socios_Cnpj_Raiz[:] = novos_socios["Cnpj_Raiz"]
    socios_pais[:] = novos_socios["pais"]
    socios_representante_legal[:] = novos_socios["representante_legal"]
    socios_nome_representante[:] = novos_socios["nome_representante"]
    socios_qualificacao_representante[:] = novos_socios["qualificacao_representante"]
    socios_nome[:] = novos_socios["nome"]

    empresas_Cnpj_Raiz[:] = novos_empresas["Cnpj_Raiz"]
    empresas_nome[:] = novos_empresas["nome"]
    empresas_capital_social[:] = novos_empresas["capital_social"]
    empresas_ente_federativo[:] = novos_empresas["ente_federativo"]
    empresas_qualificacao_responsavel[:] = novos_empresas["qualificacao_responsavel"]
    empresas_natureza_juridica[:] = novos_empresas["natureza_juridica"]
    empresas_porte[:] = novos_empresas["porte"]



def connect_to_db():
    return psycopg2.connect(
        host=DB_HOST, 
        port=DB_PORT, 
        dbname=DB_NAME, 
        user=DB_USER, 
        password=DB_PASSWORD
    )
