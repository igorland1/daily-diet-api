from flask import Flask, request, jsonify
from models.user import User
from models.meal import Meal
from database import db
from flask_login import LoginManager, login_user, current_user, logout_user, login_required
import bcrypt
from datetime import datetime

app = Flask(__name__)
app.config['SECRET_KEY'] = "your_secret_key"
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://admin:admin123@127.0.0.1:3306/daily-diet-api'

login_manager = LoginManager()
db.init_app(app)
login_manager.init_app(app)
login_manager.login_view = 'login'

@login_manager.user_loader
def load(user_id):
    return User.query.get (user_id)

@app.route('/login', methods=["POST"])
def login():
    data = request.json
    username = data.get("username")
    password = data.get("password")

    if username and password:
        user = User.query.filter_by(username=username).first()

        if user and bcrypt.checkpw(str.encode(password), str.encode(user.password)):
            login_user(user)
            print(current_user.is_authenticated)
            return jsonify({"message": f"Seja bem vindo(a) {username}"})
        
        return jsonify({"message": "Credenciais inválidas"}), 400

@app.route('/logout', methods=["GET"])
@login_required
def logout():
    logout_user()
    return jsonify({"message": "Logout realizada com sucesso"})

@app.route('/register-user', methods=["POST"])
def create_user():
    data = request.json
    username = data.get("username")
    password = data.get("password")

    if username and password:
        hashed_password = bcrypt.hashpw(str.encode(password), bcrypt.gensalt())
        user = User(username=username, password=hashed_password)
        db.session.add(user)
        db.session.commit()
        return jsonify({"message": f"Usuário {username} registrado com sucesso"})
    
    return jsonify({"message": "Dados inválidos"}), 400

@app.route('/add-meal', methods=["POST"])
@login_required
def add_meal():
    data = request.json
    user_name = current_user.username
    meal_name = data.get("meal_name")
    description = data.get("description")
    date_add = datetime.now().isoformat(timespec='minutes')
    within_diet = data.get("within_diet", True)

    if meal_name and description:
        meal = Meal(user_name=user_name, meal_name=meal_name, description=description, date_add=date_add, within_diet=within_diet)
        db.session.add(meal)
        db.session.commit()
        return jsonify({"message": f"Refeição {meal_name} cadastrada com sucesso"})
    
    return jsonify({"message": "Obrigatório informar todos os dados: meal_name & description"}), 400

@app.route('/')
def hello_world():
    return 'Hello World'

if __name__ == '__main__':
    app.run(debug=True)