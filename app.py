from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_marshmallow import Marshmallow
from password import my_password

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = f'mysql+mysqlconnector://root:{my_password}@localhost/fitness_center_db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)
ma = Marshmallow(app)

class Member(db.Model):
    __tablename__ = 'members'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(255), nullable=False)
    age = db.Column(db.Integer)

    def __repr__(self):
        return f'<Member {self.name}>'

class WorkoutSession(db.Model):
    __tablename__ = 'workoutsessions'
    
    session_id = db.Column(db.Integer, primary_key=True)
    member_id = db.Column(db.Integer, db.ForeignKey('members.id'), nullable=False)
    session_date = db.Column(db.Date, nullable=False)
    session_time = db.Column(db.String(50))
    activity = db.Column(db.String(255))

    member = db.relationship('Member', backref=db.backref('workouts', lazy=True))

    def __repr__(self):
        return f'<WorkoutSession {self.session_date} for member {self.member_id}>'

@app.route('/members', methods=['POST'])
def add_member():
    data = request.get_json()
    new_member = Member(name=data['name'], age=data['age'])
    db.session.add(new_member)
    db.session.commit()
    return jsonify({'message': 'Member added successfully'}), 201

@app.route('/members', methods=['GET'])
def get_members():
    members = Member.query.all()
    return jsonify([{'id': member.id, 'name': member.name, 'age': member.age} for member in members]), 200

@app.route('/members/<int:id>', methods=['PUT'])
def update_member(id):
    data = request.get_json()
    member = Member.query.get_or_404(id)
    member.name = data['name']
    member.age = data['age']
    db.session.commit()
    return jsonify({'message': 'Member updated successfully'}), 200

@app.route('/members/<int:id>', methods=['DELETE'])
def delete_member(id):
    member = Member.query.get_or_404(id)
    db.session.delete(member)
    db.session.commit()
    return jsonify({'message': 'Member deleted successfully'}), 200

@app.route('/workouts', methods=['POST'])
def schedule_workout():
    data = request.get_json()
    new_workout = WorkoutSession(member_id=data['member_id'], session_date=data['session_date'], session_time=data['session_time'], activity=data['activity'])
    db.session.add(new_workout)
    db.session.commit()
    return jsonify({'message': 'Workout session scheduled successfully'}), 201

@app.route('/workouts', methods=['GET'])
def get_workouts():
    workouts = WorkoutSession.query.all()
    return jsonify([{'session_id': workout.session_id, 'member_id': workout.member_id, 'session_date': workout.session_date, 'session_time': workout.session_time, 'activity': workout.activity} for workout in workouts]), 200

@app.route('/workouts/<int:session_id>', methods=['PUT'])
def update_workout(session_id):
    data = request.get_json()
    workout = WorkoutSession.query.get_or_404(session_id)
    workout.session_date = data['session_date']
    workout.session_time = data['session_time']
    workout.activity = data['activity']
    db.session.commit()
    return jsonify({'message': 'Workout session updated successfully'}), 200

@app.route('/workouts/<int:session_id>', methods=['DELETE'])
def delete_workout(session_id):
    workout = WorkoutSession.query.get_or_404(session_id)
    db.session.delete(workout)
    db.session.commit()
    return jsonify({'message': 'Workout session deleted successfully'}), 200

@app.route('/members/<int:member_id>/workouts', methods=['GET'])
def get_member_workouts(member_id):
    workouts = WorkoutSession.query.filter_by(member_id=member_id).all()
    return jsonify([{'session_id': workout.session_id, 'member_id': workout.member_id, 'session_date': workout.session_date, 'session_time': workout.session_time, 'activity': workout.activity} for workout in workouts]), 200

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True)
