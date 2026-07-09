from flask import Flask, request, jsonify
from models import meal
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

@app.route('/add-meal', methods=["POST"])
@login_required
def add_meal():
    data = request.json
    user_id = current_user.id
    meal_name = data.get("meal_name")
    description = data.get("description")
    date_add = datetime.now().isoformat(timespec='minutes')
    within_diet = data.get("within_diet", True)

    if meal_name and description:
        meal = Meal(user_id=user_id, meal_name=meal_name, description=description, date_add=date_add, within_diet=within_diet)
        db.session.add(meal)
        db.session.commit()
        return jsonify({"message": f"Refeição {meal_name} cadastrada com sucesso"})
    
    return jsonify({"message": "Obrigatório informar todos os dados: meal_name & description"}), 400

@app.route('/meal/<int:meal_id>', methods=["GET"])
@login_required
def read_meal(meal_id):
    user_id = current_user.id
    meal = Meal.query.filter_by(id=meal_id).first()

    if not meal:
        return jsonify({"message": "Refeição não encontrada"}), 404

    if meal.user_id != user_id:
        return jsonify({"message": "Ação não autorizada"}), 403

    return jsonify({"meal": meal.to_dict()})

@app.route('/meal', methods=["GET"])
@login_required
def read_all_meals():
    user_id = current_user.id
    meals = Meal.query.filter_by(user_id=user_id).order_by(Meal.date_add.desc()).all()

    meals_data = [
        {
            "id": meal.id,
            "user_id": meal.user_id,
            "meal_name": meal.meal_name,
            "description": meal.description,
            "date_add": meal.date_add.isoformat() if meal.date_add else None,
            "within_diet": bool(meal.within_diet)
        }
        for meal in meals
    ]

    return jsonify({"refeições": meals_data, "total de refeições": len(meals_data)})

@app.route('/meal/<int:meal_id>', methods=["PUT"])
@login_required
def update_meal(meal_id):
    user_id = current_user.id
    meal = Meal.query.filter_by(id=meal_id).first()

    if not meal:
        return jsonify({"message": "Refeição não encontrada"}), 404

    if meal.user_id != user_id:
        return jsonify({"message": "Ação não autorizada"}), 403

    data = request.get_json(silent=True)
    if not data:
        return jsonify({"message": "Corpo da requisição inválido ou vazio"}), 400

    meal.meal_name = data.get('meal_name', meal.meal_name)
    meal.description = data.get('description', meal.description)

    if 'within_diet' in data:
        meal.within_diet = bool(data['within_diet'])

    db.session.commit()

    meal_data = {
        "id": meal.id,
        "user_id": meal.user_id,
        "meal_name": meal.meal_name,
        "description": meal.description,
        "date_add": meal.date_add.isoformat() if meal.date_add else None,
        "within_diet": bool(meal.within_diet)
    }

    return jsonify({"message": "Refeição atualizada com sucesso", "meal": meal_data})
    
@app.route('/meal/<int:meal_id>', methods=['DELETE'])
@login_required
def delete_meal(meal_id):
    user_id = current_user.id
    meal = Meal.query.filter_by(id=meal_id).first()

    if not meal:
        return jsonify({"message": "Refeição não encontrada"}), 404

    if meal.user_id != user_id:
        return jsonify({"message": "Ação não autorizada"}), 403

    db.session.delete(meal)
    db.session.commit()
    return jsonify({"message": "Refeição removida com sucesso"})

if __name__ == '__main__':
    app.run(debug=True)