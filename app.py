from flask import Flask
from flask_restful import Resource, Api, request, abort

import requests, json

app = Flask(__name__)
app.config.from_pyfile("local.cfg")

api = Api(app)

        
class AnaliseDeCredito(Resource):
    def post(self):
        
        try:
            cpf = request.json['cpf']
        except:
            abort(404, message="Parâmetros insuficientes.")
        
        url = f"{app.config['URL_PROCOB']}{cpf}"
        header = app.config['KEY_PROCOB']  
        
        r = requests.get(url, headers=header)
        response = r.json()
        
        content = response.get('content', {})

        if response.get('code') != '000':
            abort(404, message=f"{response.get('message', 'Error ao fazer a solicitação')}")

        # E: Negativado
        # D: <=0,3 Alto risco
        # C: <=0,5 Risco
        # B: <=0,7 Médio
        # A: >0,7 Baixo

        negativas = content.get('advertencias', {})
       
        grupo = ''
        for key, value in negativas.items():
            if value:
                grupo = 'E'
                break
        
        if not grupo:
            score = content.get('score_serasa', {}).get('conteudo', {}).get('score', 0)
            
            score = 0
            score = int(score)

            if score <= 300:
                grupo = 'D'
            elif score <= 500:
                grupo = 'C'
            elif score <= 700:
                grupo = 'B'
            else:
                grupo = 'A'
            
        return {'cpf': cpf, 'grupo': grupo}, 200

api.add_resource(AnaliseDeCredito, '/analisecredial/v1/')

if __name__ == '__main__':
    app.run(debug=app.config['DEBUG'])