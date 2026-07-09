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

    def to_dict(self):
        return {
            "id": self.id,
            "user_id": self.user_id,
            "meal_name": self.meal_name,
            "description": self.description,
            "date_add": self.date_add.isoformat() if self.date_add else None,
            "within_diet": bool(self.within_diet)
        }