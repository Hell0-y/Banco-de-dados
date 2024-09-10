from flask import Flask, request
from flask_restx import Api, Resource, fields
from datetime import datetime
import mysql.connector
from mysql.connector import Error
from datetime import datetime

app = Flask(__name__)
api = Api(app, version='1.0', title='API de Usuários', description='Uma API para gerenciar usuários')
ns = api.namespace('usuarios', description='Operações relacionadas a usuários')

usuario_model = api.model('Usuario', {
    'cpf': fields.Integer(required=True, description='O CPF do usuário'),
    'nome': fields.String(required=True, description='O nome do usuário'),
    'data_nascimento': fields.String(required=True, description='A data de nascimento do usuário (YYYY-MM-DD)')
})

def criar_conexao_bd():
    try:
        conexao = mysql.connector.connect(
            host='localhost',  
            port=3306,
            database='teste',  
            user='root',
            password='' 
        )
        if conexao.is_connected():
            return conexao
    except Error as e:
        print(f"Erro ao conectar ao banco de dados: {e}")
        return None

@ns.route('/users')
class UsuarioResource(Resource):
    @ns.doc('adicionar_usuario')
    @ns.expect(usuario_model)
    def post(self):
        dados = request.json
        cpf = dados.get('cpf')
        nome = dados.get('nome')
        data_nascimento_str = dados.get('data_nascimento')

        if not cpf or not nome or not data_nascimento_str:
            api.abort(400, "Dados insuficientes")

        try:
            data_nascimento = datetime.strptime(data_nascimento_str, '%Y-%m-%d')
        except ValueError:
            api.abort(400, "Formato de data inválido. Use YYYY-MM-DD")

        conexao = criar_conexao_bd()
        if not conexao:
            api.abort(500, "Falha ao conectar ao banco de dados")

        try:
            cursor = conexao.cursor()
            query = "INSERT INTO usuarios (cpf, nome, data_nascimento) VALUES (%s, %s, %s)"
            cursor.execute(query, (cpf, nome, data_nascimento))
            conexao.commit()
            return {'mensagem': 'Usuário adicionado com sucesso'}, 201
        except Error as e:
            print(f"Erro ao inserir dados: {e}")
            api.abort(500, "Erro ao salvar dados no banco de dados")
        finally:
            cursor.close()
            conexao.close()

    @ns.doc('obter_usuario')
    @ns.param('cpf', 'O CPF do usuário')
    def get(self):
        cpf = request.args.get('cpf')

        if not cpf:
            api.abort(400, "Parâmetro 'cpf' é necessário")

        conexao = criar_conexao_bd()
        if not conexao:
            api.abort(500, "Falha ao conectar ao banco de dados")

        try:
            cursor = conexao.cursor(dictionary=True)
            query = "SELECT * FROM usuarios WHERE cpf = %s"
            cursor.execute(query, (cpf,))
            usuario = cursor.fetchone()

            if not usuario:
                api.abort(404, "Usuário não encontrado")
            if 'data_nascimento' in usuario:
                usuario['data_nascimento'] = usuario['data_nascimento'].strftime('%Y-%m-%d')

            return usuario
        except Error as e:
            print(f"Erro ao buscar dados: {e}")
            api.abort(500, "Erro ao buscar dados no banco de dados")
        finally:
            cursor.close()
            conexao.close()

if __name__ == '__main__':
    app.run(debug=True)
