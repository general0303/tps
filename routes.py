from init import app, db
from models import Workshop, Condition, OperatingMode, Resources, Energy
from flask import jsonify
import pytz
from datetime import datetime, timedelta


def refresh():
    record = Resources.query.all()[-1]
    delta = (datetime.now() - record.time_on_clock).seconds
    workshops = Workshop.query.all()[1:]
    resources = Resources(time_on_clock=datetime.now(pytz.timezone('Europe/Moscow')),
                          remains=record.remains - workshops[1].operating_mode.equipment_wear_and_tear_per_hour)
    energy = Energy(time_on_clock=datetime.now(pytz.timezone('Europe/Moscow')),
                    generated=workshops[2].operating_mode.generated_energy)
    for workshop in workshops:
        workshop.expenses = round(workshop.expenses + workshop.operating_mode.expenses_per_second * delta, 4)
        if workshop.expenses > 99:
            workshop.set_mode(OperatingMode.query.get(1))
        if workshop.expenses > 80 and workshop.condition != Condition.query.get(5):
            workshop.set_condition(Condition.query.get(4))
            repair = Workshop.query.first()
            if repair.condition == Condition.query.get(1):
                workshop.set_condition(Condition.query.get(5))
                repair.set_condition(Condition.query.get(2))
                workshop.set_mode(OperatingMode.query.get(1))
    db.session.add(resources)
    db.session.add(energy)
    db.session.commit()


@app.route('/finish_repair')
def finish_repair():
    workshop = Workshop.query.filter_by(condition=Condition.query.get(5)).first()
    workshop.set_condition(Condition.query.get(3))
    workshop.set_mode(OperatingMode.query.get(4))
    workshop.set_expenses(0)
    db.session.commit()
    Workshop.query.first().set_condition(Condition.query.get(1))
    db.session.commit()
    return "ok"


@app.route('/', methods=["GET"])
def index():
    refresh()
    workshops = Workshop.query.all()
    return jsonify({"energy": sum(energy.generated for energy in Energy.query.all()),
                    "resources": Resources.query.all()[-1].remains,
                    "workshops": [{"name": w.workshop_name, "expenses": w.expenses if w.workshop_number != 1 else "-",
                                   "condition": w.condition.description,
                                   "mode": w.operating_mode.description if w.workshop_number != 1 else "-",
                                   "lastRepair": (datetime.now() - timedelta(seconds=w.expenses /
                                                                                    w.operating_mode.expenses_per_second)
                                   if w.operating_mode.mode_number != 1 else "Is repairing now")
                                   if w.workshop_number != 1 else "-",
                                   "nextRepair": (datetime.now() + timedelta(seconds=(80 - w.expenses) /
                                                                                    w.operating_mode.expenses_per_second)
                                   if w.operating_mode.mode_number != 1 else "Is repairing now") if w.workshop_number != 1 else "-"}
                                  for w in (workshops[1:] + [workshops[0]])]})


@app.route('/change_mode')
def change_mode():
    return jsonify([{"description": m.description, "expenses_per_second": m.expenses_per_second,
                     "generated_energy_per_second": m.generated_energy,
                     "equipment_wear_and_tear_per_second": m.equipment_wear_and_tear_per_hour,
                     "mode": m.mode_number}
                    for m in OperatingMode.query.all()])


@app.route('/set_mode/<mode_number>')
def set_mode(mode_number):
    mode = OperatingMode.query.filter_by(mode_number=mode_number).first()
    condition = Condition.query.get(3)
    for workshop in Workshop.query.all():
        if workshop.condition == condition:
            workshop.set_mode(mode)
    db.session.commit()
    return "ok"
