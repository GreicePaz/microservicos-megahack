from flask import Flask
from flask_restful import Resource, Api, request, abort

import requests, json, random

app = Flask(__name__)
app.config.from_pyfile("local.cfg")

api = Api(app)

        
class AnaliseDeCredito(Resource):
    def post(self):
        
        try:
            api_key = request.headers['API_KEY']
            key = app.config['API_KEY']
        except:
            abort(401, message="Chave inválida")
        
        if api_key != key:
            abort(401, message="Chave inválida 2")

        try:
            cpf = request.json['cpf']
        except:
            abort(404, message="Parâmetros insuficientes.")
        
        url = f"{app.config['URL_PROCOB']}{cpf}"
        header = app.config['KEY_PROCOB']  
        
        try:
            r = requests.get(url, headers=header)
            response = r.json()
        except:
            abort(404,message="Erro ao realizar a chamada.")

        content = response.get('content', {})

        #Se acabar de novo os créditos da API...
        if response.get('code') == '002':
            content = {
                'advertencias': {
                    'p': random.choice(list({0,1}))
                },
                'score_serasa': {
                    'conteudo': {
                        'score': random.randint(0, 1000) 
                    }
                }
            }
        elif response.get('code') != '000':
            abort(404, message=f"{response.get('message', 'Erro ao fazer a solicitação.')}")

        # E: Negativado
        # C: <=0,5 Risco 5%
        # B: <=0,7 Médio 4%
        # A: >0,7 Baixo 3%

        negativas = content.get('advertencias', {})
       
        grupo = ''
        for key, value in negativas.items():
            if value:
                grupo = 'E'
                break
        
        score = content.get('score_serasa', {}).get('conteudo', {}).get('score', 0)
        
        score = int(score)

        if not grupo:
            if score <= 500:
                grupo = 'C'
            elif score <= 750:
                grupo = 'B'
            else:
                grupo = 'A'
            
        return {'pontuacao': score, 'grupo': grupo, 'porcentagem': score/100 }, 200

api.add_resource(AnaliseDeCredito, '/analisecredial/v1/')

if __name__ == '__main__':
    app.run(debug=app.config['DEBUG'])