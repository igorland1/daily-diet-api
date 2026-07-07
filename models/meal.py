from database import db
from flask_login import UserMixin

class Meal(db.Model, UserMixin):
    __tablename__ = 'meals'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    meal_name = db.Column(db.String(80), nullable=False)
    description = db.Column(db.String(200), nullable=False)
    date_add = db.Column(db.Date, nullable=False)
    within_diet = db.Column(db.Boolean, default=False)