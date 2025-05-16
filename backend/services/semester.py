from app import db
from app.models import Course, Studyprogram, Studyplan, Institute, Notifications, Semester, SemesterCourses
from sqlalchemy import func, and_, or_, literal_column
from sqlalchemy.orm import joinedload


class SemesterService:
    def __init__(self, db_session=None):
        self.db = db_session or db.session


    # map id to semester number
    def get_semester_mapping(self, semesters):
        return {semester.semester_number: semester.id for semester in semesters}
    
    # serialize semesters
    def serialize_semesters(self, semesters):
        return [semester.serialize() for semester in semesters]



    # Create
    def create_semesters(self, studyplan_id, studyprogram_id):
        try:
            studyprogram = self.db.query(Studyprogram).get(studyprogram_id)
            if not studyprogram:
                raise ValueError(f"Studyprogram with id {studyprogram_id} does not exist.")
            semesters = []
            for i in range(1, studyprogram.semester_number + 1):
                semester = Semester(
                    semester_number=i,
                    studyplan_id=studyplan_id,
                )
                self.db.add(semester)
                semesters.append(semester)
            self.db.flush()
            return semesters
        except Exception as e:
            raise RuntimeError(f"Failed to create semesters for studyplan {studyplan_id}: {str(e)}")


    def get_all_semesters_by_studyplan_id(self, studyplan_id):
        try:
            semesters = self.db.query(Semester).filter_by(studyplan_id=studyplan_id).order_by(Semester.semester_number).all()
            
            return semesters
        except Exception as e:
            raise RuntimeError(f"Failed to fetch semesters for studyplan {studyplan_id}: {str(e)}")


    def get_semester_by_id(self, semester_id):
        semester = self.db.query(Semester).filter(Semester.id == semester_id).first()
        return semester

    def get_semesters_by_term(self, studyplan_id, term):
        try:
            semesters = (
                self.db.query(Semester)
                .filter(Semester.studyplan_id == studyplan_id, Semester.term == term)
                .all()
            )
            print(f"Fetched {len(semesters)} semesters with term '{term}' for studyplan {studyplan_id}.")
            return semesters
        except Exception as e:
            raise RuntimeError(f"Failed to fetch semesters by term for studyplan {studyplan_id}: {str(e)}")

    def get_semesters_with_courses_by_studyplan_id(self, studyplan_id):
        try:
            semesters = (
                self.db.query(Semester)
                .filter(Semester.studyplan_id == studyplan_id)
                .options(joinedload(Semester.semester_courses).joinedload(SemesterCourses.course))
                .all()
            )
            print(f"Fetched {len(semesters)} semesters with courses for studyplan {studyplan_id}.")
            return semesters
        except Exception as e:
            raise RuntimeError(f"Failed to fetch semesters with courses for studyplan {studyplan_id}: {str(e)}")


    def get_all_semesters_by_studyprogram_id(self, studyprogram_id):
        try:
            semesters = (
                self.db.query(Semester)
                .join(Studyplan, Semester.studyplan_id == Studyplan.id)
                .filter(Studyplan.studyprogram_id == studyprogram_id)
                .all()
            )
            print(f"Fetched {len(semesters)} semesters for studyprogram {studyprogram_id}.")
            return semesters
        except Exception as e:
            raise RuntimeError(f"Failed to fetch semesters for studyprogram {studyprogram_id}: {str(e)}")

    def get_semester_info_by_prog(self, studyprogram_id):
        return None


    
    
    