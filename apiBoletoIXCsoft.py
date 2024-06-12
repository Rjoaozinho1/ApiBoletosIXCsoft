from flask import Flask, request, jsonify, json
from datetime import datetime
import json
import requests
import base64

busca_boleto = Flask(__name__)

# Função para criar um nome único para o boleto baseado no timestamp
def criar_nome_boleto(boleto):
    # Obter o timestamp atual
    timestamp = datetime.now().timestamp()
    
    # Converter o timestamp para uma string
    timestamp_str = str(int(timestamp))
    
    # Concatenar o ID do boleto com o timestamp
    resultado = f"{boleto}{timestamp_str}"
    
    return resultado

# Função para gerar o boleto
def gerar_boleto(boleto):
    # URL de consulta de boletos
    url = "https://dominio/webservice/v1/get_boleto"
    
    # Configurar o payload como JSON
    payload = json.dumps({
        "boletos": boleto,
        "juro": "N",
        "multa": "N",
        "atualiza_boleto": "N",
        "tipo_boleto": "arquivo",
        "base64": "S"
    })

    # Configurar os headers para a requisição
    headers = {
        'ixcsoft': 'listar',
        'Content-Type': 'application/json',
        'Authorization': 'Token IXC',
        'Cookie': 'IXC_Session=f1kcg4da63acg1l5je9l74729k'
    }
    
    # Enviar a requisição GET para obter o boleto
    response = requests.request("GET", url, headers=headers, data=payload)

    # Verificar se a resposta está vazia ou se houve um erro do lado do servidor
    if response.text is None or response.status_code == 500:
        return jsonify({'error': 'Serviço fora do ar'}), 500

    # Verificar se não houve resposta válida
    if not response.text:
        return jsonify({'error': 'Erro na geração do boleto'}), 404

    # Nome do arquivo onde o boleto será salvo
    fileName = f"PastaBoletos/{criar_nome_boleto(boleto)}.pdf"

    # Decodificar o conteúdo base64 do boleto
    conteudo_decodificado = base64.b64decode(response.text)

    # Salvar o boleto como um arquivo PDF
    with open("./" + fileName, 'wb') as file:
        file.write(conteudo_decodificado)

    # Retornar o link para o boleto gerado
    return jsonify({'linkBoleto': f'Url_Boleto{fileName}'}), 200

# Rota para buscar o boleto
@busca_boleto.route('/BuscarBoletoLoomy', methods=['POST'])
def puxar_boleto():
    # Obter o token de autenticação dos headers
    auth_token = request.headers.get('Authorization')
    
    # Verificar se o token é válido
    if not auth_token or not auth_token.startswith('Bearer '):
        return jsonify({'error': 'Token de autenticação inválido'}), 401

    # Remover o prefixo 'Bearer ' do token
    auth_token = auth_token.split(' ')[1]

    # Verificar se o token é válido (no caso, um token estático)
    if auth_token != 'Token estatico':
        return jsonify({'error': 'Token de autenticação inválido'}), 401

    # Obter os dados do JSON da requisição
    data = request.get_json()
    boleto = data.get('boleto')
    
    # Verificar se os dados são válidos
    if not data or not boleto:
        return jsonify({'error': 'Parâmetros inválidos'}), 404

    try:
        # Tentar gerar o boleto
        return gerar_boleto(boleto)

    except Exception as e:
        # Capturar e lidar com exceções
        print(e)
        return jsonify({'error': f'Erro no servidor: {e}'}), 500

# Iniciar o servidor Flask
if __name__ == '__main__':
    busca_boleto.run(host='0.0.0.0', port=5050, debug=True)
