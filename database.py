from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

db = SQLAlchemy()

# Table 1: Users
class User(db.Model):
    __tablename__ = 'users'

    id = db.Column(db.Integer, primary_key=True)
    full_name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password = db.Column(db.String(200), nullable=False)
    role = db.Column(db.String(20), nullable=False)  # 'patient' or 'caregiver'
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    # Relationship — one user has many medicines
    medicines = db.relationship('Medicine', backref='owner', lazy=True)

# Table 2: Medicines
class Medicine(db.Model):
    __tablename__ = 'medicines'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    name = db.Column(db.String(100), nullable=False)
    dosage = db.Column(db.String(50), nullable=False)
    frequency = db.Column(db.String(50), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    # Relationships — one medicine has many schedules, doses, and one stock
    schedules = db.relationship('Schedule', backref='medicine', lazy=True)
    doses = db.relationship('Dose', backref='medicine', lazy=True)
    stock = db.relationship('Stock', backref='medicine', uselist=False)

# Table 3: Schedules
class Schedule(db.Model):
    __tablename__ = 'schedules'

    id = db.Column(db.Integer, primary_key=True)
    medicine_id = db.Column(db.Integer, db.ForeignKey('medicines.id'), nullable=False)
    scheduled_time = db.Column(db.String(20), nullable=False)  # e.g. "08:00 AM"
    days = db.Column(db.String(50), nullable=False, default='daily')

    # Relationship — one schedule slot has many dose logs
    doses = db.relationship('Dose', backref='schedule', lazy=True)

# Table 4: Doses
class Dose(db.Model):
    __tablename__ = 'doses'

    id = db.Column(db.Integer, primary_key=True)
    medicine_id = db.Column(db.Integer, db.ForeignKey('medicines.id'), nullable=False)
    schedule_id = db.Column(db.Integer, db.ForeignKey('schedules.id'), nullable=False)
    status = db.Column(db.String(10), nullable=False)  # 'taken' or 'missed'
    logged_at = db.Column(db.DateTime, default=datetime.utcnow)

# Table 5: Stock
class Stock(db.Model):
    __tablename__ = 'stock'

    id = db.Column(db.Integer, primary_key=True)
    medicine_id = db.Column(db.Integer, db.ForeignKey('medicines.id'), unique=True, nullable=False)
    quantity = db.Column(db.Integer, nullable=False, default=0)
    low_stock_threshold = db.Column(db.Integer, nullable=False, default=5)
    last_updated = db.Column(db.DateTime, default=datetime.utcnow)