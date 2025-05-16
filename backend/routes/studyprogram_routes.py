from flask import Flask, jsonify, request, Blueprint
from app.models import Course, Studyprogram, Institute, Studyplan
from app import db
from services import ServiceFactory
from flask_jwt_extended import current_user, jwt_required

# http://localhost:5000/backend/studyprograms/
# LA LINJÅ OPPFOR STÅ - brukan te å lett henta URLen te POSTMAN. 

# Create a Blueprint
studyprogram_bp = Blueprint('studyprograms', __name__)

# Studyprogram
# Create
@studyprogram_bp.route("/create", methods=["POST"])
@jwt_required()
def create_studyprogram():
    try:
        data = request.json
        name = data.get("studyprogram_name")
        degree_type = data.get("degree")
        institute_id = data.get("institute")
        program_code = data.get("program_code")
        semester_number = data.get("semester_number")
        if not all([name, degree_type, institute_id, program_code, semester_number]):
            return jsonify({"error": "Missing required fields"}), 400

        studyprogram_service = ServiceFactory.get_studyprogram_service()
        studyprogram = studyprogram_service.add_studyprogram(
            name=name, 
            degree_type=degree_type, 
            institute_id=institute_id,
            semester_number=semester_number,
            program_code=program_code
            )
        return jsonify(studyprogram.serialize()), 201
    except ValueError as e:
        return jsonify({"error": str(e)}), 400
    except Exception as e:
        return jsonify({"error": str(e)}), 500


# Delete
@studyprogram_bp.route("/<int:studyprogram_id>", methods=["DELETE"])
@jwt_required()
def delete_studyprogram(studyprogram_id):
    try:
        studyprogram_service = ServiceFactory.get_studyprogram_service()
        result = studyprogram_service.delete_studyprogram(studyprogram_id)
        return jsonify(result), 200
    except ValueError as e:
        return jsonify({"error": str(e)}), 404
    except Exception as e:
        return jsonify({"error": str(e)}), 500

# Update
@studyprogram_bp.route("/<int:studyprogram_id>/update", methods=["PUT"])
@jwt_required()
def update_studyprogram(studyprogram_id):
    try:
        data = request.json
        name = data.get("name")
        degree_type = data.get("degree_type")
        institute = data.get("institute")
        program_code = data.get("program_code")

        studyprogram_service = ServiceFactory.get_studyprogram_service()
        studyprogram = studyprogram_service.update_studyprogram(
            studyprogram_id=studyprogram_id, 
            name=name, 
            degree_type=degree_type, 
            institute=institute,
            program_code=program_code
        )
        return jsonify(studyprogram.serialize()), 200
    except ValueError as e:
        return jsonify({"error": str(e)}), 404
    except Exception as e:
        return jsonify({"error": str(e)}), 500



# Get by id
@studyprogram_bp.route("/<int:studyprogram_id>", methods=["GET"])
def get_studyprogram_by_id(studyprogram_id):
    try:
        studyprogram_service = ServiceFactory.get_studyprogram_service()
        studyprogram = studyprogram_service.get_studyprogram_by_id(studyprogram_id)
        if not studyprogram:
            return jsonify({"error": "Study program not found"}), 404
        return jsonify(studyprogram.serialize()), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500

# get all
@studyprogram_bp.route("/getAllStudyPrograms", methods=["GET"])
def get_studyprograms():
    try:
        studyprogram_service = ServiceFactory.get_studyprogram_service()
        studyprograms = studyprogram_service.get_all_studyprograms()

        serialized_studyprograms = [studyprogram.serialize() for studyprogram in studyprograms]

        return jsonify(serialized_studyprograms), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500


# Søk etter studieprogram, enten på studieprogramnavn eller degree_type.
@studyprogram_bp.route('/search', methods=['GET'])
def search_program():
    query = request.args.get('query', '').lower()
    try:
        studyprogram_service = ServiceFactory.get_studyprogram_service()
        programs = studyprogram_service.search_studyprograms(query)
        programs_data = [program.serialize() for program in programs]

        return jsonify(programs_data), 200
    
    except Exception as e:
        return jsonify({"error": str(e)}), 500
    

# by insitute_id
@studyprogram_bp.route("/institute/<int:institute_id>", methods=["GET"])
def get_studyprograms_by_institute(institute_id):
    try:
        studyprogram_service = ServiceFactory.get_studyprogram_service()
        studyprograms = studyprogram_service.get_studyprograms_by_institute(institute_id)
        if not studyprograms:
            return jsonify({"error": "No study programs found for this institute"}), 404

        serialized_studyprograms = [studyprogram.serialize() for studyprogram in studyprograms]

        return jsonify(serialized_studyprograms), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500

# get institute by program id
@studyprogram_bp.route("/<int:studyprogram_id>/institute", methods=["GET"])
def get_institute_by_program_id(studyprogram_id):
    try:
        studyprogram_service = ServiceFactory.get_studyprogram_service()
        institute = studyprogram_service.get_institute_by_program_id(studyprogram_id)
        if not institute:
            return jsonify({"error": "Institute not found"}), 404

        return jsonify(institute.serialize()), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@studyprogram_bp.route("/<string:degree_type>/degree", methods=["GET"])
def get_studyprograms_by_degree_type(degree_type):
    try:
        studyprogram_service = ServiceFactory.get_studyprogram_service()
        studyprograms = studyprogram_service.get_studyprograms_by_degree_type(degree_type)
        if not studyprograms:
            return jsonify({"error": "No study programs found for this degree type"}), 404

        serialized_studyprograms = [studyprogram.serialize() for studyprogram in studyprograms]

        return jsonify(serialized_studyprograms), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@studyprogram_bp.route("/becomeincharge/<int:studyprogram_id>", methods=["POST"])
@jwt_required()
def become_in_charge(studyprogram_id):
    try:
        studyprogram_service = ServiceFactory.get_studyprogram_service()
        inCharge = studyprogram_service.become_in_charge_of_studyprogram(studyprogram_id,current_user.id)

        return jsonify(inCharge.serialize()), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@studyprogram_bp.route("/becomenotincharge/<int:studyprogram_id>", methods=["DELETE"])
@jwt_required()
def become_not_in_charge(studyprogram_id):
    try:
        studyprogram_service = ServiceFactory.get_studyprogram_service()
        inCharge = studyprogram_service.step_down_of_studyprogram(studyprogram_id,current_user.id)
        return jsonify(inCharge.serialize()), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500


# Henter "degree_type"/"semester_number" fra studyprogram og lager semestre. 
@studyprogram_bp.route('/<int:studyprogram_id>/semester-info', methods=['GET'])
def get_program_semester_info(studyprogram_id):
    try:
        studyprogram_service = ServiceFactory.get_studyprogram_service()
        semester_info = studyprogram_service.get_program_struct(studyprogram_id)
        print(semester_info)
        return jsonify(semester_info), 200
    except ValueError as e:
        return jsonify({"error": str(e)}), 404
    except Exception as e:
        return jsonify({"error": str(e)}), 500

##################### OPPE OK, NEDE DNO ########################



# get studyprogram
@studyprogram_bp.route("/<int:id>", methods=["GET"])
def get_studyprogram(id):
    studyprogram = Studyprogram.query.get(id)
    if not studyprogram:
        return jsonify({"error": "Studyprogram not found"}), 404
    
    # query institute (konvertera Id til navn)
    data = studyprogram.serialize()
    data["institute_name"] = studyprogram.institute.name
    return jsonify(data)

@studyprogram_bp.route("/<int:id>", methods=["GET"])
def getStudyprogramById(id):
    studyprogram = Studyprogram.query.get(id)
    if not studyprogram:
        return jsonify({"error": "Studyprogram not found"}), 404
    return jsonify(studyprogram.serialize()), 200



# update studyprograms
@studyprogram_bp.route("/<string:name>", methods=["PUT"])
def update_studyprogram_name(name):
    studyprogram = Studyprogram.query.get(name)
    if not studyprogram:
        return jsonify({"error": "Studyprogram not found"}), 404

    data = request.json
    studyprogram.name = data.get('name', studyprogram.name)
    studyprogram.degree_type = data.get('degree_type', studyprogram.degree_type)
    studyprogram.institute_id = data.get('institute_id', studyprogram.institute_id)
    studyprogram.semester_number = data.get('semester_number', studyprogram.semester_number)
    studyprogram.is_active = data.get('is_active', studyprogram.is_active)


    db.session.commit()
    return jsonify(studyprogram.serialize())

    

@studyprogram_bp.route('/<int:studyprogram_id>/sem', methods=['GET'])
def get_semester_structure(studyprogram_id):
    try:
        studyprogram_service = ServiceFactory.get_studyprogram_service()
        semester_info = studyprogram_service.get_semesterNumber(studyprogram_id)

        return jsonify(semester_info), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500
    
#få programmer som har semestere med over 30 poeng
@studyprogram_bp.get('/get_plans_with_too_many_credits')
def get_plans_too_many_credits():
    programservice = ServiceFactory.get_studyprogram_service()
    overloaded = programservice.get_study_programs_with_overloaded_semesters()
    return jsonify(overloaded)