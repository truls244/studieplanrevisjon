from app import db
from app.models import Studyplan, Semester, SemesterCourses, Log
from sqlalchemy import func, and_
from flask_jwt_extended import current_user


class StudyplanService:
    def __init__(self, db_session=None, course_service=None, 
                studyprogram_service=None, valgemne_service=None, 
                notification_service=None, semester_service=None, semesterCourses_service=None):
        self.db = db_session or db.session
        self.course_service = course_service
        self.studyprogram_service = studyprogram_service
        self.valgemne_service = valgemne_service
        self.notification_service = notification_service
        self.semester_service = semester_service
        self.semesterCourses_service = semesterCourses_service


    # Create (med flush)
    def add_studyplan(self, year, studyprogram_id):
        existing_studyplan = self.db.query(Studyplan).filter_by(year=year, studyprogram_id=studyprogram_id).first()
        if existing_studyplan:
            raise ValueError(f"A studyplan already exists for the year {year} and program ID {studyprogram_id}")
        try:
            studyplan = Studyplan(year=year, studyprogram_id=studyprogram_id)
            self.db.add(studyplan)
            self.db.flush()
            return studyplan
        except Exception as e:
            self.db.rollback()
            raise RuntimeError(f"Failed to add studyplan: {str(e)}")

    # Delete
    def delete_studyplan(self, studyplan_id):
        try:
            studyplan = self.get_studyplan(studyplan_id)
            if not studyplan:
                raise ValueError(f"Studyplan with ID {studyplan_id} not found")
            
            self.db.delete(studyplan)
            self.db.commit()
            return {"message": f"Studyplan with ID {studyplan_id} deleted successfully"}
        except ValueError as e:
            raise e
        except Exception as e:
            self.db.rollback()
            raise RuntimeError(f"Failed to delete studyplan: {str(e)}")


    # update
    def update_semesters_courses(self, studyplan_id, semester_courses):
        try:
            semesters = self.semester_service.get_all_semesters_by_studyplan_id(studyplan_id)
            print(f"semesters: {semesters}")
            semester_mapping = self.semester_service.get_semester_mapping(semesters)
            print(f"semester_mapping: {semester_mapping}")
            formatted_courses = self.semesterCourses_service.format_courses_for_semesters(semester_courses, semester_mapping)
            print(f"formatted_courses: {formatted_courses}")
            result = self.semesterCourses_service.update_courses(formatted_courses)
            print(f"Updated courses for studyplan {studyplan_id}: {result}")
            # db.session.commit()
            log = Log(f"{current_user.name} har redigert studieplanen med id {studyplan_id}")
            self.db.add(log)
            return result
        except Exception as e:
            raise RuntimeError(f"Failed to update semester courses for studyplan {studyplan_id}: {str(e)}")


    # get by id
    def get_studyplan(self, studyplan_id):
        try:
            studyplan = self.db.query(Studyplan).get(studyplan_id)
            if not studyplan:
                raise ValueError(f"Studyplan with ID {studyplan_id} not found")
            return studyplan
        except Exception as e:
            raise RuntimeError(f"Failed to get studyplan: {str(e)}")

    # check if studyplan exists
    def check_studyplan_exists(self, studyprogram_id, year):

        return self.db.query(Studyplan).filter_by(
            studyprogram_id=studyprogram_id,
            year=year
        ).first() is not None

    # get all plans by progID (not serialized)
    def get_all_studyplans(self, studyprogram_id):
        try:
            studyplans = self.db.query(Studyplan).filter_by(studyprogram_id=studyprogram_id).order_by(Studyplan.year.desc()).all()
            return studyplans
        except Exception as e:
            raise RuntimeError(f"Failed to get all studyplans: {str(e)}")
            return []

    #create new studyplan with semesters and courses(createSP)
    def create_complete_studyplan(self, year, studyprogram_id, semester_courses):
        if self.check_studyplan_exists(year, studyprogram_id):
            raise ValueError("A studyplan already exists for this year and program")
        try:
            studyplan = self.add_studyplan(year, studyprogram_id)

            semesters = self.semester_service.create_semesters(studyplan.id, studyprogram_id)
            semester_mapping = self.semester_service.get_semester_mapping(semesters)

            if semester_courses:
                formatted_courses = self.semesterCourses_service.format_courses_for_semesters(semester_courses, semester_mapping)
                self.semesterCourses_service.batch_add_all_courses(studyplan.id, formatted_courses)
            log = Log(f"{current_user.name} har laget en ny studieplan for studieprogram med id: {studyprogram_id}")
            self.db.add(log)
            return studyplan, semesters
        except Exception as e:
            raise RuntimeError(f"Failed to create complete studyplan: {str(e)}")



    def get_latest_studyplan(self, studyprogram_id):
        try:
            latest_studyplan = (
                self.db.query(Studyplan)
                .filter_by(studyprogram_id=studyprogram_id)
                .order_by(Studyplan.year.desc())
                .first()
            )

            if not latest_studyplan:
                raise ValueError(f"No studyplan found for program ID {studyprogram_id}")
            return latest_studyplan
        except Exception as e:
            raise RuntimeError(f"Failed to get latest studyplan: {str(e)}")



    # get all studyplans
    def get_studyplans(self):
        try:
            studyplan = self.db.query(Studyplan).all()
            return studyplan
        except Exception as e:
            raise RuntimeError(f"Failed to get studyplan: {str(e)}")

    # get latest studyplan per program
    def get_all_latest_studyplans(self):
        try:
            latest_years_subquery = self.db.query(
                Studyplan.studyprogram_id,
                func.max(Studyplan.year).label('max_year')
            ).group_by(Studyplan.studyprogram_id).subquery()
            
            latest_plans = self.db.query(Studyplan).join(
                latest_years_subquery,
                and_(
                    Studyplan.studyprogram_id == latest_years_subquery.c.studyprogram_id,
                    Studyplan.year == latest_years_subquery.c.max_year
                )
            ).all()
        
            return latest_plans
        
        except Exception as e:
            print(f"Error getting latest studyplans: {str(e)}")
            return []



    def get_studyplan_by_programId(self, studyprogram_id):
        try:
            studyplan = self.db.query(Studyplan).filter_by(studyprogram_id=studyprogram_id).first()
            if not studyplan:
                raise ValueError(f"Studyplan with program ID {studyprogram_id} not found")
            return studyplan
        except Exception as e:
            raise RuntimeError(f"Failed to get studyplan: {str(e)}")


    def get_sp_basic(self, studyplan_id):
        try:
            studyplan = self.get_studyplan(studyplan_id)
            if not studyplan:
                raise ValueError(f"Studyplan with ID {studyplan_id} not found")

            studyplan_data = studyplan.serialize()

            program = self.studyprogram_service.get_studyprogram_by_id(studyplan.studyprogram_id)
            if program:
                studyplan_data["program"] = program.serialize()

            semesters = self.semester_service.get_all_semesters_by_studyplan_id(studyplan_id)
            semester_data = [semester.serialize() for semester in semesters]
            studyplan_data["semesters"] = semester_data

            return studyplan_data
        except Exception as e:
            raise RuntimeError(f"Failed to get studyplan basic: {str(e)}")


    def get_full_studyplan(self, studyplan_id):
        try:

            studyplan = self.get_studyplan(studyplan_id)
            if not studyplan:
                raise ValueError(f"Studyplan with ID {studyplan_id} not found")


            serialized_studyplan = studyplan.serialize()


            program = self.studyprogram_service.get_studyprogram_by_id(studyplan.studyprogram_id)
            if program:
                serialized_studyplan["program"] = program.serialize()
            semesters = self.semester_service.get_all_semesters_by_studyplan_id(studyplan_id)
            serialized_semesters = []
            for semester in semesters:
                semester_courses = self.semesterCourses_service.get_courses_by_semester_id(semester.id)
                serialized_semester = semester.serialize()
                serialized_semester["semester_courses"] = self.semesterCourses_service.serialize_courses(semester_courses)
                serialized_semesters.append(serialized_semester)

            serialized_studyplan["semesters"] = serialized_semesters
            return serialized_studyplan
        except Exception as e:
            raise RuntimeError(f"Failed to get full studyplan: {str(e)}")

    def get_studyplan_with_courses(self, studyplan_id):
        try:
            # Fetch the basic studyplan data
            studyplan_data = self.get_sp_basic(studyplan_id)

            for semester in studyplan_data.get('semesters', []):
                semester_id = semester.get('id')
                if not semester_id:
                    continue
                semester_courses_objs = self.semesterCourses_service.get_courses_by_semester_id(semester_id)
                serialized_courses = self.semesterCourses_service.serialize_courses(semester_courses_objs)

                semester['semester_courses'] = serialized_courses
            

            return studyplan_data
        except Exception as e:
            raise RuntimeError(f"Failed to get studyplan with courses: {str(e)}")


    def detect_term_conflicts_for_course_by_program(self, course_id, new_term, source_program_id=None):
        try:
            latest_studyplans = self.get_all_latest_studyplans()

            termConflicts = []
            for studyplan in latest_studyplans:
                if source_program_id and studyplan.studyprogram_id == source_program_id:
                    continue

                semester = self.db.query(Semester).join(SemesterCourses).filter(
                    Semester.studyplan_id == studyplan.id,
                    SemesterCourses.course_id == course_id
                ).first()

                if not semester:
                    continue  

                if semester.term != new_term:
                    termConflicts.append({
                        "program_id": studyplan.studyprogram_id,
                        "program_name": studyplan.studyprogram.name,
                        "semester_number": semester.semester_number,
                        "current_term": semester.term,
                        "new_term": new_term,
                    })

                print(f"Found term conflict for course {course_id} in program {studyplan.studyprogram_id} (current term: {semester.term}, new term: {new_term})")
                print(f"Program name: {studyplan.studyprogram.name}")
                print(f"Semester number: {semester.semester_number}")

            print(f"Term conflicts for course {course_id}: {termConflicts}")
            return termConflicts

        except Exception as e:
            print(f"Error detecting term conflicts for course {course_id}: {str(e)}")
            return {
                "message": f"Failed to detect term conflicts for course {course_id}.",
                "error": str(e)
            }

    def get_plans_for_export(self, studyprogram_id):
        try:
            studyplans = (
                self.db.query(Studyplan)
                .filter_by(studyprogram_id=studyprogram_id)
                .order_by(Studyplan.year.desc())
                .limit(3)
                .all()
            )

            if not studyplans:
                raise ValueError(f"No study plans found for program ID {studyprogram_id}")

            serialized_studyplans = []
            for studyplan in studyplans:
                full_studyplan = self.get_full_studyplan(studyplan.id)
                serialized_studyplans.append(full_studyplan)
            
            return serialized_studyplans
        except Exception as e:
            print(f"Error fetching study plans for export: {str(e)}")
            return {
                "message": f"Failed to fetch study plans for program ID {studyprogram_id}.",
                "error": str(e)
            }

