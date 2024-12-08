from flask import Flask, render_template
from flasgger import Swagger
from flask_cors import CORS
from API import api_pesquisa
#from export_excel import export_excel
from unificar_escrituras import process_excel
import config

# Inicialização da aplicação Flask
app = Flask(__name__)

# Configuração de CORS e Swagger
CORS(app)  # Ativa o CORS para todas as rotas

# Template personalizado para o Swagger
swagger_template = {
    "swagger": "2.0",
    "info": {
        "title": "API Receita",  # Nome personalizado
        "version": "1.0.0",      # Versão da API
        "description": "Descrição personalizada da sua API.",  # Descrição opcional
    },
    "host": "localhost:5001",  # Altere conforme necessário
    "basePath": "/",
}

swagger = Swagger(app)

# Rota principal para carregar a página HTML
@app.route("/")
def index():
    # Limpa variáveis globais ao carregar a página principal
    config.limpar_variaveis_globais()
    # Renderiza a página com variáveis zeradas
    return render_template("index.html", **config.template())

# Rotas da API
app.add_url_rule("/API", "API", api_pesquisa, methods=["POST"])

# Rotas de exportação e processamento
#app.add_url_rule("/export_excel", "export_excel", export_excel, methods=["GET"])
#app.add_url_rule("/process_excel", "process_excel", process_excel, methods=["POST"])

# Inicialização do servidor
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5001)