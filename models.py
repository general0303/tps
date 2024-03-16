from init import db
from datetime import datetime
import pytz


class Workshop(db.Model):
    workshop_number = db.Column(db.Integer, primary_key=True)
    workshop_name = db.Column(db.String(30))
    expenses = db.Column(db.REAL)
    condition_number = db.Column(db.Integer, db.ForeignKey('condition.condition_number'))
    mode_number = db.Column(db.Integer, db.ForeignKey('operating_mode.mode_number'))

    def set_workshop_name(self, name):
        self.workshop_name = name

    def set_expenses(self, expenses):
        self.expenses = expenses

    def set_condition(self, condition):
        self.condition = condition

    def set_mode(self, mode):
        self.operating_mode = mode


class Condition(db.Model):
    condition_number = db.Column(db.Integer, primary_key=True)
    description = db.Column(db.String(50))
    workshops = db.relationship('Workshop', backref='condition', lazy='dynamic')


class OperatingMode(db.Model):
    mode_number = db.Column(db.Integer, primary_key=True)
    description = db.Column(db.String(50))
    expenses_per_second = db.Column(db.REAL)
    equipment_wear_and_tear_per_hour = db.Column(db.Integer)
    generated_energy = db.Column(db.Integer)
    workshops = db.relationship('Workshop', backref='operating_mode', lazy='dynamic')


class Resources(db.Model):
    time_on_clock = db.Column(db.DateTime, primary_key=True, default=datetime.now(pytz.timezone('Europe/Moscow')),
                              index=True)
    remains = db.Column(db.Integer)


class Energy(db.Model):
    time_on_clock = db.Column(db.DateTime, primary_key=True, default=datetime.now(pytz.timezone('Europe/Moscow')),
                              index=True)
    generated = db.Column(db.Integer)
