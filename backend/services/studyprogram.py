from app import db
from sqlalchemy import func, and_, or_
from app.models import Studyprogram, Studyplan, Institute, User, Log, Semester, SemesterCourses, Course


class StudyprogramService:
    def __init__(self, db_session=None):
        self.db = db_session or db.session

    # Legg til nytt studieprogram
    def add_studyprogram(self, name, degree_type, institute_id,semester_number,program_code):
        studyprogram = Studyprogram(
            name=name,
            degree_type=degree_type,
            institute_id=institute_id,
            semester_number=semester_number,
            program_code=program_code
        )
        
        self.db.add(studyprogram)
        log = Log(f"Studieprogram ble opprettet {studyprogram.name}")
        self.db.add(log)
        self.db.commit()
        return studyprogram

    # Slett studieprogram
    def delete_studyprogram(self, studyprogram_id):
        studyprogram = self.get_studyprogram_by_id(studyprogram_id)
        if not studyprogram:
            raise ValueError(f"Studyprogram with ID {studyprogram_id} not found")

        self.db.delete(studyprogram)
        log = Log(f"Studieprogram ble slettet {studyprogram.name}")
        self.db.add(log)
        self.db.commit()
        return {"message": f"Studyprogram with ID {studyprogram_id} deleted successfully"}


    # Oppdater eksisterende studieprogram (navn, degree_type, institutt)
    def update_studyprogram(self, studyprogram_id, name=None, degree_type=None, institute=None,program_code=None):
        studyprogram = self.get_studyprogram_by_id(studyprogram_id)
        inst = self.db.query(Institute).get(institute["id"])
        if not studyprogram:
            raise ValueError(f"Studyprogram with ID {studyprogram_id} not found")
        
        if name:
            studyprogram.name = name
        
        if degree_type:
            studyprogram.degree_type = degree_type
            studyprogram.semester_number = 6 if degree_type == 'bachelor' else 4
        
        if inst:
            studyprogram.institute = inst
        if program_code:
            studyprogram.program_code= program_code
        log = Log(f"Studieprogram ble endret {studyprogram.name}")
        self.db.add(log)

        self.db.commit()
        return studyprogram

    # Hent studieprogram basert på ID
    def get_studyprogram_by_id(self, studyprogram_id):
        try:
            if not studyprogram_id or not isinstance(studyprogram_id, int):
                raise ValueError("Invalid studyprogram ID")
            studyprogram = self.db.query(Studyprogram).get(studyprogram_id)
            if studyprogram is None:
                raise ValueError(f"Studyprogram with ID {studyprogram_id} not found")
            return studyprogram
        except Exception as e:
            raise RuntimeError(f"Failed to fetch studyprogram with ID {studyprogram_id}: {str(e)}")
    
    # Hent alle studieprogram
    def get_all_studyprograms(self):
        return self.db.query(Studyprogram).all()
    
    # Søk etter studieprogram, enten på studieprogramnavn eller degree_type. 
    def search_studyprograms(self, query):
        if not query:
            return []
            
        search = f"%{query}%"
        return self.db.query(Studyprogram).filter(
            or_(
                Studyprogram.name.ilike(search),
                Studyprogram.degree_type.ilike(search)
            )
        ).all()
    
    # Hent alle studieprogram basert på degree_type
    def get_studyprograms_by_degree_type(self, degree_type):
        return self.db.query(Studyprogram).filter_by(
            degree_type=degree_type
        ).all()

    def get_program_struct(self, studyprogram_id):
        studyprogram = self.get_studyprogram_by_id(studyprogram_id)
        if not studyprogram:
            raise ValueError(f"Studyprogram with ID {studyprogram_id} not found")
        
        semesterNumber = self.get_semesterNumber(studyprogram.id)
        total_semesters = list(range(1, semesterNumber + 1))
        print(f"Total semesters for studyprogram {studyprogram_id}: {total_semesters}")
        return total_semesters
        



    def get_institute_by_program_id(self, studyprogram_id):
        studyprogram = self.get_studyprogram_by_id(studyprogram_id)
        if studyprogram is None:
            raise ValueError("Studyprogram not found")
        return studyprogram.institute
    
    # Hent alle studieprogram basert på institute_id
    def get_studyprograms_by_institute(self, institute_id):
        return self.db.query(Studyprogram).filter_by(
            institute_id=institute_id
        ).all()
    
    # Hent institutt ansvarlig basert på studieprogram ID
    def get_instituteAnsvarlig_by_studyprogramId(self, studyprogram_id):
        studyprogram = self.get_studyprogram_by_id(studyprogram_id)
        if studyprogram is None:
            raise ValueError("Studyprogram not found")
        return studyprogram.institute.ansvarlig
    
    def become_in_charge_of_studyprogram(self, studyprogram_id, user_id):
        studyprogram = self.get_studyprogram_by_id(studyprogram_id)
        user = db.session.query(User).get(user_id)
        studyprogram.program_ansvarlig_id = user.id
        db.session.commit()
        return user
    
    def step_down_of_studyprogram(self, studyprogram_id, user_id):
        studyprogram = self.get_studyprogram_by_id(studyprogram_id)
        user = db.session.query(User).get(user_id)
        if studyprogram.program_ansvarlig_id == user.id:
            studyprogram.program_ansvarlig_id = None
        db.session.commit()
        return user

    def get_program_by_studyplan(self, studyplan_id):
        try:
            studyplan = self.db.query(Studyplan).get(studyplan_id)
            if not studyplan:
                raise ValueError(f"Studyplan with id {studyplan_id} does not exist.")
            studyprogram = self.db.query(Studyprogram).get(studyplan.studyprogram_id)
            return studyprogram.serialize()
        except ValueError as ve:
            raise ve
        except Exception as e:
            raise RuntimeError(f"Failed to fetch studyprogram for studyplan {studyplan_id}: {str(e)}")

    def get_studyprogram_detail(self, studyprogram_id):
        try:
            studyprogram = self.get_studyprogram_by_id(studyprogram_id)
            if not studyprogram:
                raise ValueError(f"Studyprogram with id {studyprogram_id} does not exist.")
            
            # Fetch the institute details
            institute = self.db.query(Institute).get(studyprogram.institute_id)
            if not institute:
                raise ValueError(f"Institute with id {studyprogram.institute_id} does not exist.")
            print(studyprogram)
            result = {
                "id": studyprogram.id,
                "name": studyprogram.name,
                "degree_type": studyprogram.degree_type,
                "semester_number": studyprogram.semester_number,
                "institute_id": institute.id,
                "institute_ansvarlig": institute.ansvarlig,
                "institute_name": institute.name,
                "program_ansvarlig": {
                    "id":studyprogram.program_ansvarlig.id,
                    "name" : studyprogram.program_ansvarlig.name,
                    "email" : studyprogram.program_ansvarlig.email
                    }if studyprogram.program_ansvarlig else None
                }
            return result
        except Exception as e:
            raise RuntimeError(f"Failed to fetch studyprogram details: {str(e)}")


    ##################### OPPE OK, NEDE DNO ########################









    
    # Hent antall semestre for et studieprogram basert på ID
    def get_semesterNumber(self, studyprogram_id):
        studyprogram = self.get_studyprogram_by_id(studyprogram_id)
        if studyprogram is None:
            raise ValueError("Studyprogram not found")
        
        semesterNumber = getattr(studyprogram, 'semester_number', None)
        if semesterNumber is None:
            degree_type = getattr(studyprogram, 'degree_type', None).lower()
            if degree_type == 'bachelor':
                semesterNumber = 6
            elif degree_type == 'master':
                semesterNumber = 4
            else:
                raise ValueError("Invalid degree type or semester number")
        # total_semesters = list(range(1, semesterNumber + 1))
        # print(f"Total semesters for studyprogram {studyprogram_id}: {total_semesters}")

        return semesterNumber
    

    # Hent alle studieplaner basert på studieprogram ID
    def get_studyplans_by_studyprogramId(self, studyprogram_id):
        return self.db.query(Studyplan).filter_by(
            studyprogram_id=studyprogram_id
        ).all()
    
    # Hent den siste studieplanen for et studieprogram basert på ID (Siste året)
    def get_latest_studyplan(self, studyprogram_id):
        return self.db.query(Studyplan).filter_by(
            studyprogram_id=studyprogram_id
        ).order_by(Studyplan.year.desc()).first()
    

    # Hent den siste studieplanen for alle studieprogrammer
    def get_all_latest_studyplans(self):
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

    

    def get_study_programs_with_overloaded_semesters(session, credit_threshold=30):
    
    # Use a subquery to calculate the total credits per semester
        subquery = db.session.query(
        Semester.id.label('semester_id'),
        Semester.semester_number.label('semester_number'),
        Semester.studyplan_id.label('studyplan_id'),
        func.sum(Course.credits).label('total_credits'))\
            .join(SemesterCourses, Semester.id == SemesterCourses.semester_id)\
            .join(Course, SemesterCourses.course_id == Course.id)\
            .filter((SemesterCourses.is_elective.is_(False)) | (SemesterCourses.is_elective.is_(None)))\
            .group_by(Semester.id, Semester.semester_number, Semester.studyplan_id)\
            .having(func.sum(Course.credits) > credit_threshold).subquery()
        
        # Get the study plans and their overloaded semesters
        results = db.session.query(Studyplan,subquery.c.semester_number, subquery.c.total_credits) \
            .join(subquery, Studyplan.id == subquery.c.studyplan_id) \
            .order_by(subquery.c.semester_number).where(Studyplan.year > 2024).subquery()
        final = db.session.query(Studyprogram)\
        .join(Studyplan, Studyprogram.id == Studyplan.studyprogram_id) \
        .filter(Studyplan.studyprogram_id ==results.c.studyprogram_id).all()
        
        # Group results by study program
       
        
        return [program.serialize() for program in final]




    


    
    
    
    
    