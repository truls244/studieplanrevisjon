from app import db
from app.models import Course, Studyprogram, Studyplan, Institute, Semester, SemesterCourses, Log
from sqlalchemy import func, and_, or_, union, literal, text, literal_column
from sqlalchemy.orm import joinedload
from flask import jsonify, request


class CourseService:
    def __init__(self, db_session=None):
        self.db = db_session or db.session

    # Hent emne basert på ID
    def get_course_by_id(self, course_id):
        if not course_id or not isinstance(course_id, int):
            raise ValueError("Invalid course ID")
        course = self.db.query(Course).get(course_id)
        if course is None:
            raise ValueError(f"Course with ID {course_id} not found")
        return course
    
    # Henter emner basert på IDer (flere emner)
    def get_courses_by_ids(self, course_ids):
        if not course_ids:
            return []
            
        return self.db.query(Course).filter(Course.id.in_(course_ids)).all()

    # Hent alle emner (serialisert) fra databasen
    def get_all_courses(self):
        return self.db.query(Course).all()
        # courses = self.db.query(Course).all()
        # return [course.serialize() for course in courses]

    def course_exists(self, name=None, course_code=None):
        try:
            query = self.db.query(Course)

            if name:
                query = query.filter(Course.name == name)
            if course_code:
                query = query.filter(Course.courseCode == course_code)

            return self.db.query(query.exists()).scalar()
        except Exception as e:
            print(f"Error checking course existence: {str(e)}")
            return False

    # Søk etter emne, enten på emnenavn eller emnekode. (evt term(semester))
    def search_courses(self, query, term=None):
        search = f"%{query}%"
        filters = [
            Course.name.ilike(search),
            Course.courseCode.ilike(search)
        ]
        
        if term:
            return self.db.query(Course).filter(db.or_(*filters), Course.semester == term).all()
        return self.db.query(Course).filter(db.or_(*filters)).all()
    
    # Legg til nytt emne
    def add_course(self, name, course_code, semester, credits, degree):
        course = Course(
            name=name,
            courseCode=course_code,
            semester=semester,
            credits=credits,
        )
        print(course)
        self.db.add(course)
        log = Log(f"Emne ble opprettet {course.name}")
        self.db.add(log)
        self.db.commit()
        return course
    
    # Oppdater eksisterende emne
    def update_course(self, course_id, name, courseCode, semester, credits, degree):
        course = self.get_course_by_id(course_id)
        if not course:
            raise ValueError(f"Course with ID {course_id} not found")
        if name is not None:
            course.name = name
        if courseCode is not None:
            course.courseCode = courseCode
        if semester is not None:
            course.semester = semester
        if credits is not None:
            course.credits = credits
        if degree is not None:
            course.degree = degree

        log = Log(f"Emne ble oppdatert {course.courseCode} {course.name}")
        self.db.add(log)
        self.db.commit()
        return course
    
    # Slett emne
    def delete_course(self, course_id):
        course = self.get_course_by_id(course_id)
        if not course:
            raise ValueError(f"Course with ID {course_id} not found")
        
        if self.is_course_in_use(course_id):
            raise ValueError(f"Course with ID {course_id} is in use and cannot be deleted") 
        

        self.db.delete(course)
        log = Log(f"Emne ble slettet {course.name}")
        self.db.add(log)
        self.db.commit()
        return {"message": f"Course with ID {course_id} deleted successfully"}
    

    def get_course_info(self, course_id):
        try:
            course = self.db.query(course).get(course_id)
            if not course:
                return None
            
            return {
                'id': course.id,
                'name': course.name,
                'courseCode': course.courseCode,
            }
        except Exception as e:
            print(f"Error getting course info: {str(e)}")
            return None

    def is_course_in_use(self, course_id):
        try:
            in_use = self.db.query(Studyplan).join(Semester).join(SemesterCourses).filter(
                SemesterCourses.course_id == course_id
            ).first()

            return in_use is not None  # True if in use
        except Exception as e:
            print(f"Error checking if course is in use: {str(e)}")
            return False
        
    def get_valgemne_course(self):
        try:
            valgemne_course = self.db.query(Course).filter(
                and_(Course.courseCode == 'VALGEMNE', Course.credits == 0)
            ).first()
            return valgemne_course if valgemne_course else None
        except Exception as e:
            print(f"Error getting VALGEMNE course: {str(e)}")
            return None
    def get_all_valgemner(self):
        try:
            valgemne_courses = self.db.query(Course).filter(Course.courseCode == 'VALGEMNE').all()
            if not valgemne_courses:
                return None
            return[valgemne.serialize() for valgemne in valgemne_courses]
            
        except Exception as e:
            print(f"Error getting VALGEMNE courses: {str(e)}")
            return None

    def get_course_usage(self):
        try:
            results = db.session.query(
                Course.id.label("course_id"),
                Course.name.label("course_name"),
                Studyprogram.id.label("studyprogram_id"),
                Studyprogram.name.label("studyprogram_name"),
                Studyplan.id.label("studyplan_id"),
                Studyplan.year.label("studyplan_year"),
                Semester.id.label("semester_id"),
                Semester.semester_number.label("semester_number"),
                Semester.term.label("term")
            ).join(SemesterCourses, SemesterCourses.course_id == Course.id) \
            .join(Semester, Semester.id == SemesterCourses.semester_id) \
            .join(Studyplan, Studyplan.id == Semester.studyplan_id) \
            .join(Studyprogram, Studyprogram.id == Studyplan.studyprogram_id) \
            .all()
            # Organize the results into a dictionary
            course_usage = {}
            for row in results:
                if row.course_id not in course_usage:
                    course_usage[row.course_id] = {
                        "course_id": row.course_id,
                        "course_name": row.course_name,
                        "usage": []
                    }

                course_usage[row.course_id]["usage"].append({
                    "studyprogram_id": row.studyprogram_id,
                    "studyprogram_name": row.studyprogram_name,
                    "studyplan_id": row.studyplan_id,
                    "studyplan_year": row.studyplan_year,
                    "semester_id": row.semester_id,
                    "semester_number": row.semester_number,
                    "term": row.term,
                })

            return list(course_usage.values())

        except Exception as e:
            print(f"Error fetching course usage: {str(e)}")
            return []
        

    def get_courses_overlapping_with_course(self,course_id):
        target_semesters = db.session.query(SemesterCourses.semester_id) \
                .filter(SemesterCourses.course_id == course_id).subquery()
        
        overlapping_courses = db.session.query(Course) \
        .join(SemesterCourses, Course.id == SemesterCourses.course_id) \
        .filter(Course.id != course_id,
                SemesterCourses.semester_id == target_semesters.c.semester_id
                ).all()
        
        return [course.serialize() for course in overlapping_courses]

    def get_studyprograms_using_course(self, course_id):
        study_plans = db.session.query(Studyplan).distinct() \
        .join(Semester, Studyplan.id == Semester.studyplan_id) \
        .join(SemesterCourses, Semester.id == SemesterCourses.semester_id) \
        .filter(SemesterCourses.course_id == course_id) \
        .order_by(Studyplan.id).subquery()

        study_programs = db.session.query(Studyprogram) \
        .join(Studyplan,Studyprogram.id == Studyplan.studyprogram_id) \
        .filter(Studyplan.studyprogram_id ==study_plans.c.studyprogram_id).all()



        return [program.serialize() for program in study_programs]

