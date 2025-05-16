from flask import Flask, jsonify, request, Blueprint
from app.models import db, Course
from flask_migrate import Migrate
from flask_jwt_extended import  jwt_required

prerequisites_bp = Blueprint('prerequisites', __name__)


# Legg til prerequisite
@prerequisites_bp.route("/add/<int:id>", methods=["POST"])
@jwt_required()
def add_prerequisites(id):
    prereqs = request.get_json()
    course = Course.query.get(id)
    for course in prereqs:
        prereq = Course.query.get(course['id'])
        course.prerequisites.append(prereq)
    db.session.commit()
    return jsonify({"message": "courses added successfully"}), 201

@prerequisites_bp.route("/remove/<int:id>/<int:preid>", methods=["DELETE"])
@jwt_required()
def remove_prerequisite(id,preid):
    course = Course.query.get(id)
    prereq = Course.query.get(preid)
    for i in course.prerequisites:
        if i.id == preid:
            course.prerequisites.remove(i)

    db.session.commit()
    return(jsonify({"message":"Removed"}))