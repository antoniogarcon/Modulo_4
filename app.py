from flask import Flask, jsonify, request
from models.user import User
from database import db
from flask_login import LoginManager, login_user, current_user, logout_user, login_required

# Configura a conexão com o banco de dados
app = Flask(__name__)
app.config['SECRET_KEY'] = "your_secret_key"
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///database.db'
login_manager = LoginManager()

#Iniciando Banco de Dados e o Login Manager
db.init_app(app)
login_manager.init_app(app)

#view login
login_manager.login_view = 'login'

#Session <- conexao ativa
#MFunção usada para recuperar user <SELECT>
@login_manager.user_loader
def load_user(user_id):
  return User.query.get(user_id)

#Rota utilizada para efetuar login
@app.route('/login', methods=['POST'])
def login():
    data = request.get_json()
    username = data.get('username')
    password = data.get('password')

    if username and password:
        #Login, recuperando um registro do banco
        user = User.query.filter_by(username=username).first()
        
        if user and user.password == password:
            # Autenticado
            login_user(user)
            print(current_user.is_authenticated)
            return jsonify({"message": "Autenticação realizada com sucesso!"})
    
        return jsonify({"message": "Autenticação realizada com sucesso!"})
    
    #Falha no login
    return jsonify({'message': 'Credenciais inválidas!'}),400

#Rota utilizada para fazer Logout
@app.route('/logout',methods=['GET'])
#Decorated do Flask para verificar se existe um user logado
@login_required
def logout():
    logout_user()
    return jsonify({"message": "Logout realizado com sucesso!"})

#Rota utilizada para Cadastrar um novo user
@app.route('/user', methods=['POST'])
def create_user():
    data = request.get_json()
    username = data.get('username')
    password = data.get('password')

    if username and password:
        # Cria um novo registro no banco
        new_user = User(username=username, password=password)
        db.session.add(new_user)
        db.session.commit()
        return jsonify({"message": "Usuário criado com sucesso!"}), 400
    
    # Falha na criação do usuário
    return jsonify({"message": "Dados inválidos!"})

#Rota utilizada para recuperar um user pelo id
@app.route('/user/<int:user_id>', methods=['GET'])
@login_required
def read_user(user_id):
    user = User.query.get(user_id)

    if user:
        return jsonify({"username": user.username})
    
    return jsonify({"message": "Usuário não encontrado!"}), 404

#Rota utilizada para atualizar um user
@app.route('/user/<int:user_id>', methods=['PUT'])
@login_required
def update_user(user_id):
    data = request.get_json()
    user = User.query.get(user_id)
    
    if user and data.get('password'):
        user.password = data.get('password')
        db.session.commit()
        return jsonify({"message": f"Senha do usuario{user_id} atualizada com sucesso!"})
    
    return jsonify({"message": "Usuário não encontrado!"}), 404

#Rota utilizada para deletar um user
@app.route('/user/<int:user_id>',methods=['DELETE'])
@login_required
def delete_user(user_id):
    user = User.query.get(user_id)

    if user_id == current_user.id:
        return jsonify({"message": "Deleção não permitida"}), 403

    if user:
        db.session.delete(user)
        db.session.commit()
        return jsonify({"message": f"Usuário {user_id} deletado com sucesso!"})
    
    return jsonify({"message": "Usuário não encontrado!"}), 404

if __name__ == '__main__':
    # Inicia o servidor, com debug ativado para depuração
    app.run(debug=True) 