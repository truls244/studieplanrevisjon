from flask import Flask, jsonify, request, Blueprint
from app.models import Course, Studyprogram, Institute, Studyplan
from app import db
from services import ServiceFactory
from flask_jwt_extended import  jwt_required


# http://localhost:5000/backend/courses/
# LA LINJÅ OPPFOR STÅ - brukan te å lett henta URLen te POSTMAN. 

# Create a Blueprint
courses_bp = Blueprint('courses', __name__)


# Subject
# get courses
@courses_bp.route("/", methods=["GET"])
@jwt_required()
def get_courses():
    try:
        course_service = ServiceFactory.get_course_service()
        courses = course_service.get_all_courses()
        return jsonify([course.serialize() for course in courses]), 200
    except ValueError as e:
        return jsonify({"error": str(e)}), 404
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@courses_bp.route("/<int:course_id>", methods=["GET"])
def get_course_by_id(course_id):
    try:
        course_service = ServiceFactory.get_course_service()
        course = course_service.get_course_by_id(course_id)
        return jsonify(course.serialize()), 200
    except ValueError as e:
        return jsonify({"error": str(e)}), 404
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@courses_bp.route("/create", methods=["POST"])
@jwt_required()
def create_course():
    try:
        data = request.json
        name = data.get("name")
        course_code = data.get("code")
        semester = data.get("semester")
        credits = data.get("credits")
        degree = data.get("degree")


        course_service = ServiceFactory.get_course_service()
        course = course_service.add_course(
            name=name,
            course_code=course_code,
            semester=semester,
            credits=credits,
            degree=degree
        )
        return jsonify(course.serialize()), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@courses_bp.route("/<int:course_id>", methods=["DELETE"])
@jwt_required()
def delete_course(course_id):
    try:
        course_service = ServiceFactory.get_course_service()
        result = course_service.delete_course(course_id)
        return jsonify(result), 200
    except ValueError as e:
        return jsonify({"error": str(e)}), 404
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@courses_bp.route("/<int:course_id>", methods=["PUT"])
@jwt_required()
def update_course(course_id):
    try:
        data = request.json
        name = data.get("name")
        course_code = data.get("courseCode")
        semester = data.get("semester")
        credits = data.get("credits")
        degree = data.get("degree")

        course_service = ServiceFactory.get_course_service()
        course = course_service.update_course(
            course_id=course_id,
            name=name,
            courseCode=course_code,
            semester=semester,
            credits=credits,
            degree=degree
        )
        return jsonify(course.serialize()), 200
    except ValueError as e:
        return jsonify({"error": str(e)}), 404
    except Exception as e:
        return jsonify({"error": str(e)}), 500
    

# search courses
@courses_bp.route('/search', methods=['GET'])
@jwt_required()
def search_courses():
    query = request.args.get('query', '')
    term = request.args.get('term')


    course_service = ServiceFactory.get_course_service()
    
    if query:
        courses = course_service.search_courses(query, term)
    else:
        courses = course_service.get_all_courses()
    
    return jsonify([course.serialize() for course in courses])




@courses_bp.route('/valgemne', methods=['GET'])
@jwt_required()
def get_valgemne_courses():
    try:
        course_service = ServiceFactory.get_course_service()
        valgemne_course = course_service.get_valgemne_course()

        return jsonify(valgemne_course.serialize()), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500
    
@courses_bp.route('/all_valgemne', methods=['GET'])
@jwt_required()
def get_all_valgemne_courses():
    try:
        course_service = ServiceFactory.get_course_service()
        valgemne_courses = course_service.get_all_valgemner()
        return jsonify(valgemne_courses), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@courses_bp.route('/overlapping_courses/<int:course_id>' , methods=['GET'])
@jwt_required()
def get_overlapping_courses(course_id):
    try:
        course_service = ServiceFactory.get_course_service()
        overlappingcourses = course_service.get_courses_overlapping_with_course(course_id)
        return jsonify(overlappingcourses)
    except ValueError as e:
        return jsonify({"error": str(e)}), 404
    except Exception as e:
        return jsonify({"error": str(e)}), 500
    
@courses_bp.route('/course_usage/<int:course_id>' , methods=['GET'])
@jwt_required()
def course_usage123(course_id):
    try:
        course_service = ServiceFactory.get_course_service()
        course_usage = course_service.get_studyprograms_using_course(course_id)
        return jsonify(course_usage)
    except ValueError as e:
        return jsonify({"error": str(e)}), 404
    except Exception as e:
        return jsonify({"error": str(e)}), 500



##################### OPPE OK, NEDE DNO ########################




















# update courses 
@courses_bp.route("/<int:course_id>/gammel", methods=["PUT"])
def update_subject(course_id):
    course = Course.query.get(course_id)
    if not course:
        return jsonify({"error": "Subject not found"}), 404
    print(course.subjectCode)
    data = request.json
    course.name = data.get("name", course.name)
    course.subjectCode = data.get("subjectCode", course.subjectCode)
    course.semester = data.get("semester", course.semester)
    course.credits = data.get("credits", course.credits)
    course.is_active = data.get("is_active", course.is_active)


    db.session.commit()
    return jsonify({"message": "Subject edited successfully"})

@courses_bp.route("/<int:course_id>/gammel", methods=["GET"])
def get_course_by_idz(course_id):
    course = Course.query.get(course_id)
    if not course:
        return jsonify({"error": "Subject not found"}), 404
    return jsonify(course.serialize()), 200

# delete courses by id.
@courses_bp.route("/<int:course_id>/gammel", methods=["DELETE"])
def delete_subject(course_id):
    course = Course.query.get(course_id)
    if not course:
        return jsonify({"error": "Subject not found"}), 404

    db.session.delete(course)
    db.session.commit()
    return jsonify({"message": "Subject deleted successfully"})



@courses_bp.route("/<int:course_id>/details", methods=["GET"])
def course_details(course_id):
    course = Course.query.get(course_id)
    ser_subject = course.serialize()
    
    if not course:
        return jsonify({"error": "Subject not found"}), 404
    return jsonify(ser_subject)

@courses_bp.route("/<int:course_id>/studyprograms", methods=["GET"])
def get_studyprograms_by_course(course_id):
    course_service = ServiceFactory.get_course_service()
    studyprograms = course_service.get_studyprograms_by_course(course_id)
    result = jsonify([studyprogram.serialize() for studyprogram in studyprograms])
    return result
    #eturn jsonify([studyprogram.serialize() for studyprogram in studyprograms])

@courses_bp.route("/<int:course_id>/studyprograms/latest", methods=["GET"])
def get_programs_with_course_in_latest_plans(course_id):
    try:
        course_service = ServiceFactory.get_course_service()
        programs = course_service.get_studyprograms_with_course_in_latest_plans(course_id)
        return jsonify(programs), 200
    except ValueError as e:
        return jsonify({"error": str(e)}), 404
    except Exception as e:
        return jsonify({"error": str(e)}), 500
    
@courses_bp.route('/<int:course_id>/study-plans', methods=['GET'])
def get_studyplans_using_course(course_id):
    try:
        course_service = ServiceFactory.get_course_service()
        study_plans = course_service.get_studyplans_used_by_course(course_id)
        return jsonify(study_plans), 200
    except ValueError as e:
        return jsonify({"error": str(e)}), 404
    except Exception as e:
        return jsonify({"error": str(e)}), 500
    
@courses_bp.route('/<int:course_id>/usage-in-latest-plans', methods=['GET'])
def get_course_usage_in_latest_plans(course_id):
    try:
        course_service = ServiceFactory.get_course_service()
        usage_data = course_service.get_studyplans_used_by_course(course_id)
        return jsonify(usage_data), 200
    except ValueError as e:
        return jsonify({"error": str(e)}), 404
    except Exception as e:
        return jsonify({"error": str(e)}), 500
    
    
@courses_bp.route('/course-usage/<int:course_id>', methods=['GET'])
def get_course_usage(course_id):
    try:
        course_service = ServiceFactory.get_course_service()
        course_usage = course_service.get_course_usage()
        return jsonify(course_usage), 200
    except ValueError as e:
        return jsonify({"error": str(e)}), 404
    except Exception as e:
        return jsonify({"error": str(e)}), 500
    

@courses_bp.route('/courseusage/<int:course_id>', methods=['GET'])
def course_usage(course_id):
    try:
        studyplan_service = ServiceFactory.get_studyplan_service()
        course_usage = studyplan_service.course_usage(course_id)
        return jsonify(course_usage), 200
    except ValueError as e:
        return jsonify({"error": str(e)}), 404
    except Exception as e:
        return jsonify({"error": str(e)}), 500
    
