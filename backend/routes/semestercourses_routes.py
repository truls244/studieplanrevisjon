from flask import Blueprint, request, jsonify
from app.models import SemesterCourses, ElectiveGroup
from app import db
from services import ServiceFactory
from flask_jwt_extended import  jwt_required

# http://localhost:5000/backend/semestercourses/


semestercourses_bp = Blueprint('/semestercourses', __name__)



@semestercourses_bp.route('/semestercourses/<int:studyplan_id>', methods=['GET'])
def get_semestercourses(studyplan_id):
    try:
        semesterCourses_service = ServiceFactory.get_semesterCourses_service()
        result = semesterCourses_service.get_all_courses_by_studyplan_id(studyplan_id)
        return jsonify([course.serialize() for course in result]), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@semestercourses_bp.route('/semestercourses/<int:semester_ids>', methods=['GET'])
def get_semestercourses_by_semesters(semester_ids):
    try:
        semesterCourses_service = ServiceFactory.get_semesterCourses_service()
        result = semesterCourses_service.get_all_courses_by_semester_ids(semester_ids)
        return jsonify([course.serialize() for course in result]), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500




# LOGIKK FOR VALGEMNER / ELECTIVE GROUPS / VALGEMNEGRUPPER / VALGEMNE KATEGORIER

@semestercourses_bp.route('/elective-groups', methods=['POST'])
@jwt_required()
def create_elective_group():
    data = request.json
    new_category = data.get('name')
    if not new_category:
        return jsonify({"error": "Category name cannot be empty."}), 400
    try:
        semesterCourses_service = ServiceFactory.get_semesterCourses_service()
        result = semesterCourses_service.create_elective_group(new_category)
        return jsonify(result), 201
    except ValueError as e:
        return jsonify({"error": str(e)}), 400
    except Exception as e:
        return jsonify({"error": str(e)}), 500
    except RuntimeError as e:
        return jsonify({"error": str(e)}), 400


@semestercourses_bp.route('/elective-groups', methods=['GET'])
def get_elective_group():
    try:
        semesterCourses_service = ServiceFactory.get_semesterCourses_service()
        result = semesterCourses_service.get_elective_group()
        return jsonify(result), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@semestercourses_bp.route('/elective-groups/<int:group_id>', methods=['DELETE'])
@jwt_required()
def delete_elective_group(group_id):
    try:
        semesterCourses_service = ServiceFactory.get_semesterCourses_service()
        result = semesterCourses_service.delete_elective_group(group_id)
        return jsonify(result), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500
    except RuntimeError as e:
        return jsonify({"error": str(e)}), 400


@semestercourses_bp.route('/elective-groups/<int:group_id>', methods=['PUT'])
@jwt_required()
def update_elective_group(group_id):
    data = request.json
    new_name = data.get('new_name')
    if not new_name:
        return jsonify({"error": "Category name cannot be empty."}), 400
    try:
        semesterCourses_service = ServiceFactory.get_semesterCourses_service()
        result = semesterCourses_service.update_elective_group(group_id, new_name)
        return jsonify(result), 200
    except ValueError as e:
        return jsonify({"error": str(e)}), 400
    except Exception as e:
        return jsonify({"error": str(e)}), 500
    except RuntimeError as e:
        return jsonify({"error": str(e)}), 400


