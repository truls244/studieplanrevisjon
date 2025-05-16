from app import db
from services.studyplan import StudyplanService
from services.studyprogram import StudyprogramService
from services.course import CourseService
from services.notifications import NotificationService
from services.user import UserService
from services.semester import SemesterService
from services.semestercourses import SemesterCoursesService


class ServiceFactory:
    _instances = {}
    
    @classmethod
    def get_course_service(cls):
        if 'course' not in cls._instances:
            
            cls._instances['course'] = CourseService(db_session=db.session)

        return cls._instances['course']
    
    @classmethod
    def get_studyprogram_service(cls):
        if 'studyprogram' not in cls._instances:
            cls._instances['studyprogram'] = StudyprogramService(db_session=db.session)
        return cls._instances['studyprogram']
    
    @classmethod
    def get_studyplan_service(cls):
        if 'studyplan' not in cls._instances:

            course_service = cls.get_course_service()
            studyprogram_service = cls.get_studyprogram_service()
            notification_service = cls.get_notification_service()
            semester_service = cls.get_semester_service()
            semesterCourses_service = cls.get_semesterCourses_service()
            

            cls._instances['studyplan'] = StudyplanService(
                db_session=db.session,
                course_service=course_service,
                studyprogram_service=studyprogram_service,
                notification_service=notification_service,
                semester_service=semester_service,
                semesterCourses_service=semesterCourses_service,
            )
        return cls._instances['studyplan']
    
    
    @classmethod
    def get_notification_service(cls):
        if 'notification' not in cls._instances:
            user_service = cls.get_user_service()
            studyprogram_service = cls.get_studyprogram_service()

            cls._instances['notification'] = NotificationService(
                db_session=db.session,
                user_service=user_service,
                studyprogram_service=studyprogram_service,
            )
        return cls._instances['notification']
    
    @classmethod
    def get_user_service(cls):
        if 'user' not in cls._instances:
            cls._instances['user'] = UserService(db_session=db.session)
        return cls._instances['user']

    @classmethod
    def get_semester_service(cls):
        if 'semester' not in cls._instances:
            cls._instances['semester'] = SemesterService(db_session=db.session)
        return cls._instances['semester']

    @classmethod
    def get_semesterCourses_service(cls):
        if 'semester_courses' not in cls._instances:
            cls._instances['semester_courses'] = SemesterCoursesService(db_session=db.session)
        return cls._instances['semester_courses']

    @classmethod
    def reset(cls):
        """Reset all service instances (useful for testing)"""
        cls._instances = {}