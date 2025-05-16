from flask import Flask, jsonify, request, Blueprint
from app.models import Course, Studyprogram, Institute, Studyplan, Semester, SemesterCourses, Log
from app import db
from services import ServiceFactory
from flask_jwt_extended import  jwt_required


# http://localhost:5000/backend/studyplans/
# LA LINJÅ OPPFOR STÅ - brukan te å lett henta URLen te POSTMAN. 

## Create a Blueprint
studyplan_bp = Blueprint('studyplans', __name__)

# Create
@studyplan_bp.route('/create/sp', methods=['POST'])
@jwt_required()
def create_studyplan():
    try:
        data = request.json
        print("Received data:", data)


        if not data.get('year') or not data.get('studyprogram_id'):
            return jsonify({"error": "Missing required fields: year and studyprogram_id"}), 400


        studyplan_service = ServiceFactory.get_studyplan_service()


        if studyplan_service.check_studyplan_exists(data['year'], data['studyprogram_id']):
            return jsonify({
                "error": f"A study plan for program ID {data['studyprogram_id']} and year {data['year']} already exists"
            }), 409


        studyplan, semesters = studyplan_service.create_complete_studyplan(
            year=data['year'],
            studyprogram_id=data['studyprogram_id'],
            semester_courses=data.get('semester_courses', {})
        )
        db.session.commit()
        return jsonify(studyplan.serialize()), 201

    except ValueError as e:
        db.session.rollback()
        return jsonify({"error": str(e)}), 400
    except Exception as e:
        db.session.rollback()
        print(f"Error creating complete studyplan: {str(e)}")
        return jsonify({"error": str(e)}), 500



# get by id
@studyplan_bp.route('/<int:studyplan_id>', methods=['GET'])
@jwt_required()
def get_studyplanById(studyplan_id):
    try:
        studyplan_service = ServiceFactory.get_studyplan_service()
        studyplan = studyplan_service.get_studyplan(studyplan_id)

        if not studyplan:
            return jsonify({"error": "Study plan not found"}), 404

        return jsonify(studyplan.serialize()), 200

    except ValueError as e:
        return jsonify({"error": str(e)}), 404
    except Exception as e:
        return jsonify({"error": str(e)}), 500


# Delete
@studyplan_bp.route('/<int:studyplan_id>', methods=['DELETE'])
@jwt_required()
def delete_studyplan(studyplan_id):
    try:
        studyplan_service = ServiceFactory.get_studyplan_service()
        studyplan_service.delete_studyplan(studyplan_id)
        return jsonify({"message": "Study plan deleted successfully"}), 200
    except ValueError as e:
        return jsonify({"error": str(e)}), 404
    except Exception as e:
        return jsonify({"error": str(e)}), 500



# update courses in studyplan
@studyplan_bp.route('/<int:studyplan_id>/updatecourses', methods=['PUT'])
@jwt_required()
def update_studyplan_courses(studyplan_id):
    try:
        data = request.get_json()
        print("Received data:", data)
        studyplan_service = ServiceFactory.get_studyplan_service()
        if not data.get('semester_courses'):
            return jsonify({"error": "Missing required field: semester_courses"}), 400
        semester_courses = data.get('semester_courses', {})
        # studyplan_service = ServiceFactory.get_studyplan_service()
        result = studyplan_service.update_semesters_courses(studyplan_id, semester_courses)
        # db.session.commit()
        print("Updated study plan courses:", result)
        return jsonify(result), 200

    except ValueError as e:
        db.session.rollback()
        return jsonify({"error": str(e)}), 400
    except Exception as e:
        db.session.rollback()
        print(f"Error updating study plan courses: {str(e)}")
        return jsonify({"error": str(e)}), 500



# Henter all informasjon om emner, semestre, valgemner, etc. med studieplanID
@studyplan_bp.route('/<int:studyplan_id>/full', methods=['GET'])
def get_full_studyplan(studyplan_id):
    try:
        studyplan_service = ServiceFactory.get_studyplan_service()
        full_plan = studyplan_service.get_full_studyplan(studyplan_id)
        return jsonify(full_plan), 200
    except ValueError as e:
        return jsonify({"error": str(e)}), 404
    except Exception as e:
        return jsonify({"error": str(e)}), 500

 

# Sjekk for om en studieplan eksisterer for et studieprogram og et år
@studyplan_bp.route('/check', methods=['GET'])
def check_studyplan():
    studyprogram_id = request.args.get('studyprogram_id')
    year = request.args.get('year')

    if not studyprogram_id or not year:
        return jsonify({"error": "Missing studyprogram_id or year"}), 400
    
    try:
        studyplan_service = ServiceFactory.get_studyplan_service()
        exists = studyplan_service.check_studyplan_exists(int(studyprogram_id), int(year))

        return jsonify({"exists": exists})
    
    except ValueError:
        return jsonify({"error": "Invalid studyprogram_id or year format"}), 400
    except Exception as e:
        return jsonify({"error": str(e)}), 500



# Henter ALLE studieplaner for ett gitt studieprogram 
@studyplan_bp.route('/studyprograms/<int:studyprogram_id>', methods=['GET'])
def get_studyplans_for_studyprogram(studyprogram_id):
    try:
        studyplan_service = ServiceFactory.get_studyplan_service()
        studyplans = studyplan_service.get_studyplans_for_program(studyprogram_id)
        if not studyplans:
            return jsonify({"message": "No study plans found for this study program"}), 404

        return jsonify(studyplans), 200 #Serialized i service
    
    except ValueError as e:
        return jsonify({"error": str(e)}), 400
    except Exception as e:
        return jsonify({"error": str(e)}), 500
    

# Henter studieplan for en gitt studieplanID
@studyplan_bp.route('/<int:studyplan_id>', methods=['GET'])
def get_studyplan_by_id(studyplan_id):
    try:
        studyplan_service = ServiceFactory.get_studyplan_service()
        studyplan = studyplan_service.get_studyplan_by_id(studyplan_id)
        
        if not studyplan:
            return jsonify({"error": "Study plan not found"}), 404
        
        return jsonify(studyplan.serialize()), 200 
        
    except ValueError as e:
        return jsonify({"error": str(e)}), 400
    except Exception as e:
        return jsonify({"error": str(e)}), 500



@studyplan_bp.route('/<int:studyplan_id>/basic', methods=['GET'])
def get_studyplan_basic(studyplan_id):
    try:
        studyplan_service = ServiceFactory.get_studyplan_service()
        studyplan_data = studyplan_service.get_sp_basic(studyplan_id)
        return jsonify(studyplan_data), 200
    except ValueError as e:
        return jsonify({"error": str(e)}), 404
    except Exception as e:
        return jsonify({"error": str(e)}), 500



# Hente semestre med emner (inkl all info), i en studieplan.
@studyplan_bp.route('/<int:studyplan_id>/with-courses', methods=['GET'])
def get_studyplan_with_courses(studyplan_id):
    try:
        studyplan_service = ServiceFactory.get_studyplan_service()
        studyplan_data = studyplan_service.get_studyplan_with_courses(studyplan_id)
        
        return jsonify(studyplan_data), 200
        
    except ValueError as e:
        return jsonify({'error': str(e)}), 404
    except Exception as e:
        return jsonify({'error': str(e)}), 500
    

# sjekke term conflict.
@studyplan_bp.route('/courses/<int:course_id>/term-conflicts', methods=['GET'])
def detect_term_conflicts(course_id):
    try:
        new_term = request.args.get('new_term')
        studyprogram_id = request.args.get('studyprogram_id', type=int)

        print(f"Received new_term: {new_term}")  # Debug log
        print(f"Received studyprogram_id: {studyprogram_id}")  # Debug log

        if not new_term:
            return jsonify({"error": "Missing new_term"}), 400

        studyplan_service = ServiceFactory.get_studyplan_service()
        termConflicts = studyplan_service.detect_term_conflicts_for_course_by_program(
            course_id, new_term, studyprogram_id
        )

        return jsonify({
            'course_id': course_id,
            # 'semester_number': semester_number,
            'has_conflicts': len(termConflicts) > 0,
            'termConflicts': termConflicts
        })
    except Exception as e:
        print(f"Error detecting term conflicts: {str(e)}")
        return jsonify({"error": str(e)}), 500
    
# Endepunkt for å finne semesterene for en studieplan (inkl. litt info om emnene)   
@studyplan_bp.route('/<int:studyplan_id>/semesters', methods=['GET'])
def get_studyplan_semesters(studyplan_id):
    try:
        studyplan = Studyplan.query.get_or_404(studyplan_id)
        return jsonify([semester.serialize() for semester in studyplan.semesters]), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500



# Endepunkt for å hente den siste SP'en for et studieprogram
@studyplan_bp.route('/<int:studyprogram_id>/latestplan', methods=['GET'])
def get_latest_sp(studyprogram_id):
    try:
        studyplan_service = ServiceFactory.get_studyplan_service()
        latest_studyplan = studyplan_service.get_latest_sp(studyprogram_id)
        
        if not latest_studyplan:
            return jsonify({"message": "No study plan found for this study program"}), 404
        
        return jsonify(latest_studyplan), 200
    except ValueError as e:
        return jsonify({"error": str(e)}), 404
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@studyplan_bp.route('/<int:studyplan_id>/courszez', methods=['GET'])
def get_courses_by_studyplan(studyplan_id):
    try: 
        studyplan_service = ServiceFactory.get_studyplan_service()
        studyplan = studyplan_service.get_studyplan(studyplan_id)
        if not studyplan:
            return jsonify({"error": "Study plan not found"}), 404
        studyplan_courses = studyplan_service.get_studyplan_with_courses(studyplan_id)
        if not studyplan_courses:
            return jsonify({"error": "No courses found for this study plan"}), 404
        
        return jsonify(studyplan_courses), 200
    except ValueError as e:
        return jsonify({"error": str(e)}), 404
    
    
# brukes til å hente alle studieplaner for et studieprogram (nyeste først) og den nyeste studieplanen med detaljer
@studyplan_bp.route('/studyprograms/<int:studyprogram_id>/fullsp', methods=['GET'])
def get_full_sp(studyprogram_id):
    try:

        studyplan_service = ServiceFactory.get_studyplan_service()
        studyprogram_service = ServiceFactory.get_studyprogram_service()

        program = studyprogram_service.get_studyprogram_by_id(studyprogram_id)
        if not program:
            return jsonify({"error": f"Study program with ID {studyprogram_id} not found"}), 404
        program = studyprogram_service.get_studyprogram_detail(program.id)
        all_studyplans = studyplan_service.get_all_studyplans(studyprogram_id)
        if not all_studyplans:
            return jsonify({
                "error": f"No study plans found for program {studyprogram_id}",
                "all_plans": [],
                "latest_plan": None,
                "program": program
            }), 200


        latest_studyplan = all_studyplans[0]  
        serialized_latest_studyplan = studyplan_service.get_full_studyplan(latest_studyplan.id)

        result = {
            "all_plans": [
                {
                    "id": plan.id,
                    "year": plan.year,
                    "studyprogram_id": plan.studyprogram_id
                } for plan in all_studyplans
            ],
            "latest_plan": {
                **serialized_latest_studyplan,
                "program": program
            }
        }
        return jsonify(result), 200
    except ValueError as e:
        return jsonify({"error": str(e)}), 404
    except Exception as e:
        return jsonify({"error": str(e)}), 500






@studyplan_bp.route('/<int:studyplan_id>/sem', methods=['GET'])
def get_sem(studyplan_id):
    try:
        semester_service = ServiceFactory.get_semester_service()
        semesters = semester_service.get_all_semesters_by_studyplan_id(studyplan_id)
        return jsonify(semester_service.serialize_semesters(semesters)), 200
    except ValueError as e:
        return jsonify({"error": str(e)}), 404
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@studyplan_bp.route('/<int:studyplan_id>/fullsem', methods=['GET'])
def get_full_semesters(studyplan_id):
    try:
        studyplan_service = ServiceFactory.get_studyplan_service()
        semesterCourses_service = ServiceFactory.get_semesterCourses_service()
        courses = semesterCourses_service.get_all_courses_by_studyplan_id(studyplan_id)

        return jsonify([course.serialize() for course in courses]), 200
    except ValueError as e:
        return jsonify({"error": str(e)}), 404
    except Exception as e:
        return jsonify({"error": str(e)}), 500

#brukes i hook (studyplandata)
@studyplan_bp.route('/<int:studyplan_id>/completesp', methods=['GET'])
def get_complete_sp(studyplan_id):
    try:
        studyplan_service = ServiceFactory.get_studyplan_service()
        complete_studyplan = studyplan_service.get_full_studyplan(studyplan_id)
        
        if not complete_studyplan:
            return jsonify({"error": "Study plan not found"}), 404
        

        return jsonify(complete_studyplan), 200
    except ValueError as e:
        return jsonify({"error": str(e)}), 404
    except Exception as e:
        return jsonify({"error": str(e)}), 500


    
# endepunkt for å få semesterstruktur for et studieprogram
@studyplan_bp.route('/studyprograms/<int:studyprogram_id>/semesterinfo', methods=['GET'])
def get_program_semester_structure(studyprogram_id):
    try:
        studyprogram_service = ServiceFactory.get_studyprogram_service()
        program = studyprogram_service.get_studyprogram_by_id(studyprogram_id)
        
        if not program:
            return jsonify({"error": f"Study program with ID {studyprogram_id} not found"}), 404
        

        semester_count = program.semester_number
        
        if not semester_count or semester_count <= 0:
            return jsonify({"error": "Program has invalid semester count"}), 400
        
        semester_terms = {}
        semester_list = []
        
        for i in range(1, semester_count + 1):
            term = 'H' if i % 2 == 1 else 'V'
            semester_terms[i] = term
            
            semester_list.append({
                'semester_number': i,
                'term': term
            })
        

        response = {
            'program': {
                'id': program.id,
                'name': program.name,
                'degree_type': program.degree_type,
                'institute': program.institute.serialize(),
                'semester_count': semester_count
            },
            'semesters': semester_list,
            'terms_by_semester': semester_terms
        }
        
        return jsonify(response), 200
        
    except ValueError as e:
        return jsonify({"error": str(e)}), 404
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@studyplan_bp.route('/export/<int:studyprogram_id>', methods=['GET'])
def get_plans_for_export(studyprogram_id):
    try:
        studyplan_service = ServiceFactory.get_studyplan_service()
        data = studyplan_service.get_plans_for_export(studyprogram_id)
        return jsonify(data), 200
    except ValueError as e:
        return jsonify({"error": str(e)}), 404
    except Exception as e:
        return jsonify({"error": str(e)}), 500
    
