from app import db
from datetime import timezone
import datetime
import bcrypt
import pytz
prerequisites = db.Table(
    'prerequisites',
    db.Column('course_id', db.Integer, db.ForeignKey('course.id'), primary_key=True),
    db.Column('prerequisite_id', db.Integer, db.ForeignKey('course.id'), primary_key=True)
)
# Model for Emne
class Course(db.Model):
    __tablename__ = 'course'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(80), nullable=False)
    courseCode = db.Column(db.String(80), nullable=False)
    semester = db.Column(db.Enum('H', 'V', name='semester_type'), nullable=False)
    credits = db.Column(db.Integer, nullable=False)
    is_active = db.Column(db.Boolean, default=False)  #nullable=False
    degree = db.Column(db.String(80), nullable=True)
    semester_courses = db.relationship('SemesterCourses', back_populates='course')
    prerequisites = db.relationship('Course',secondary=prerequisites,
                                    primaryjoin=(id == prerequisites.c.course_id),
                                    secondaryjoin=(id == prerequisites.c.prerequisite_id))

    def serialize(self):
        prereqs = []
        for courses in self.prerequisites:
            prereqs.append({ "id": courses.id, "name": courses.name, "code": courses.courseCode })
        return {"id": self.id, "name": self.name, "courseCode": self.courseCode, "semester": self.semester, "credits": self.credits, "is_active": self.is_active, "degree" : self.degree, "prereqs" : prereqs}
    
    def __repr__(self):
        return f'<course {self.name}>'
    
    def __init__(self, name, courseCode, semester, credits):
        self.name = name
        self.courseCode = courseCode
        self.semester = semester
        self.credits = credits

# Model for studieprogram
class Studyprogram(db.Model):
    __tablename__ = 'studyprogram'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(80), nullable=False)
    degree_type = db.Column(db.Enum('Bachelor', 'Master', name='degree_type'), nullable=False)
    institute_id = db.Column(db.Integer, db.ForeignKey('institute.id'), nullable=False)
    semester_number = db.Column(db.Integer, nullable=False) # Antall semestre studieprogrammet går over
    is_active = db.Column(db.Boolean, default=True)
    program_code = db.Column(db.String(80), nullable=False)
    program_ansvarlig_id = db.Column(db.Integer, db.ForeignKey('user.id', ondelete='SET NULL'), nullable=True )
    # Relationship 
    program_ansvarlig = db.relationship('User', back_populates='studyprograms',lazy='joined')
    institute = db.relationship('Institute', back_populates='studyprograms', lazy='joined')
    studyplans = db.relationship('Studyplan', back_populates='studyprogram', cascade='all, delete-orphan')

    def serialize(self):
        return {
            "id": self.id, 
            "name": self.name,
            "degree_type": self.degree_type, 
            "institute": self.institute.serialize(), 
            "semester_number": self.semester_number, 
            "is_active": self.is_active,
            "program_code": self.program_code,
            "program_ansvarlig": {
                "id":self.program_ansvarlig.id,
                "name" : self.program_ansvarlig.name,
                "email" : self.program_ansvarlig.email
            } if self.program_ansvarlig else None
        }
    
    def __repr__(self):
        return f'<Studyprogram {self.name}>'
    
    def __init__(self, name, degree_type, institute_id,semester_number, program_code):
        self.name = name
        self.degree_type = degree_type
        self.institute_id = institute_id
        self.semester_number = semester_number
        self.program_code = program_code

# Model for institutt
class Institute(db.Model):
    __tablename__ = 'institute'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(80), nullable=False)
    ansvarlig = db.Column(db.String(80), nullable=True)

    studyprograms = db.relationship('Studyprogram', back_populates='institute', cascade='all, delete-orphan')

    def serialize(self):
        return {
            "id": self.id, 
            "name": self.name, 
            "ansvarlig": self.ansvarlig
        }
    
    def __repr__(self):
        return f'<Institute {self.name}>'
    
    def __init__(self,id, name):
        self.id = id
        self.name = name


# Model for studyplan
class Studyplan(db.Model):
    __tablename__ = 'studyplan'
    id = db.Column(db.Integer, primary_key=True)
    year = db.Column(db.Integer, nullable=False) # årskull
    studyprogram_id = db.Column(db.Integer, db.ForeignKey('studyprogram.id'), nullable=False) # foreign key

    semesters = db.relationship('Semester', back_populates='studyplan', cascade='all, delete-orphan', lazy='joined')
    studyprogram = db.relationship('Studyprogram', back_populates='studyplans', lazy='joined')
    
    __table_args__ = (
        db.UniqueConstraint('year', 'studyprogram_id', name='unique_year_studyprogram'),
    )

    def serialize(self):
        return {
            "id": self.id, 
            "year": self.year, 
            "studyprogram_id": self.studyprogram_id, 
            "semesters": [semester.serialize() for semester in self.semesters],

        }
    
    def __repr__(self):
        return f'<Studyplan {self.id}: {self.year} - Program {self.studyprogram_id}>'
    
    def __init__(self, year, studyprogram_id):
        self.year = year
        self.studyprogram_id = studyprogram_id



# Model for bruker
class User(db.Model):
    __tablename__ = 'user'
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(80), nullable=False)
    name = db.Column(db.String(80), nullable=False)
    password = db.Column(db.String(80), nullable=False)
    role = db.Column(db.Enum('user', 'admin', 'ansvarlig', name='role_type'), nullable=False)
    verified = db.Column(db.Boolean, default=False)
    studyprograms = db.relationship('Studyprogram', back_populates='program_ansvarlig')

    def check_password(self, password):
        if not bcrypt.checkpw(password, self.password):
            return False
        return True

    def serialize(self):
        return {
            "id": self.id, 
            "email": self.email, 
            "role": self.role, 
            "name": self.name, 
            "verified":self.verified}
    
    def __repr__(self):
        return f'<User {self.email}>'
    
    def __init__(self, email, password, name, role):
        self.email = email
        self.password = password
        self.name = name
        self.role = role


class Verificationtokens(db.Model):
    __tablename__ = 'verificationtokens'
    token = db.Column(db.String(36), nullable=False, primary_key=True)
    expiration_time = db.Column(db.DateTime, default=datetime.timezone.utc, nullable=False)
    email = db.Column(db.String(80),nullable=False)

    def __init__(self, token, email):
        self.token = token
        self.email = email
        self.expiration_time = datetime.datetime.now(datetime.timezone.utc) + datetime.timedelta(hours=1)


class Notifications(db.Model):
    __tablename__ = 'notifications'
    id = db.Column(db.Integer, primary_key=True)
    program_id = db.Column(db.Integer, db.ForeignKey('studyprogram.id'), nullable=True)
    source_program_id = db.Column(db.Integer, db.ForeignKey('studyprogram.id'), nullable=True)
    recipient_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=True)
    sender_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=True)
    message = db.Column(db.String(200), nullable=False)
    # reason = db.Column(db.String(200), nullable=True)
    is_acknowledged = db.Column(db.Boolean, default=False)
    is_solved = db.Column(db.Boolean, default=False, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.datetime.utcnow)
    email_sent = db.Column(db.Boolean, default=False)
    noti_type = db.Column(db.Enum('studyprogram', 'studyplan', 'course', 'user', 'institute', name='noti_type'), nullable=False)
    noti_id = db.Column(db.Integer, nullable=False)
    notification_group_id = db.Column(db.String(100), nullable=True)
    target_term = db.Column(db.Enum('H', 'V', name='semester_type'), nullable=True)

    program = db.relationship('Studyprogram', foreign_keys=[program_id], backref='notifications')
    source_program = db.relationship('Studyprogram', foreign_keys=[source_program_id])
    recipient = db.relationship('User', foreign_keys=[recipient_id], backref='notifications')
    sender = db.relationship('User', foreign_keys=[sender_id])


    def serialize(self):
        result = {
            "id": self.id, 
            "message": self.message,
            "notification_group_id": self.notification_group_id,
            "created_at": self.created_at.isoformat(),
            "noti_type": self.noti_type,
            "noti_id": self.noti_id,
            "is_solved": self.is_solved,
            "target_term": self.target_term,
        }
        
        # program fields
        if self.program_id:
            result.update({
                "program_id": self.program_id,
                "source_program_id": self.source_program_id,
                "is_acknowledged": self.is_acknowledged
            })
        
        # user fields
        if self.recipient_id:
            result.update({
                "recipient_id": self.recipient_id,
                "sender_id": self.sender_id,
                "is_read": self.is_read
            })
            
        return result
    
    def __repr__(self):
        if self.program_id:
            return f'<Program Notification {self.id}>'
        else:
            return f'<User Notification {self.id}>'
    
    def __init__(self, message, noti_type, noti_id, is_acknowledged=False, is_solved=False, program_id=None, source_program_id=None, recipient_id=None, sender_id=None, notification_group_id=None, target_term=None):
        self.notification_group_id = notification_group_id
        self.message = message
        self.noti_type = noti_type
        self.noti_id = noti_id
        self.is_acknowledged = is_acknowledged
        self.is_solved = is_solved
        self.target_term = target_term
        # self.created_at = datetime.utcnow()
        
        if program_id is not None:
            self.program_id = program_id
        
        if source_program_id is not None:
            self.source_program_id = source_program_id
        
        if recipient_id is not None:
            self.recipient_id = recipient_id
            
        if sender_id is not None:
            self.sender_id = sender_id

        # self.created_at = datetime.now


class SemesterCourses(db.Model):
    __tablename__ = 'semester_courses'
    id = db.Column(db.Integer, primary_key=True)
    semester_id = db.Column(db.Integer, db.ForeignKey('semester.id'), nullable=False)
    course_id = db.Column(db.Integer, db.ForeignKey('course.id'), nullable=False)
    is_elective = db.Column(db.Boolean, default=False)
    category_id = db.Column(db.Integer, db.ForeignKey('elective_groups.id'), nullable=True)

    semester = db.relationship('Semester', back_populates='semester_courses')
    course = db.relationship('Course', back_populates='semester_courses', lazy='joined')
    category = db.relationship('ElectiveGroup', backref='semester_courses', lazy='joined')


    __table_args__ = (
        db.UniqueConstraint('semester_id', 'course_id', name='uix_semester_course'),
    )

    def serialize(self):
        return {
            "id": self.id, 
            "semester_id": self.semester_id, 
            "course_id": self.course.serialize(), 
            "is_elective": self.is_elective,
            "category": {
                "id": self.category.id,
                "name": self.category.name
            } if self.is_elective and self.category else None
        }
    
    def __repr__(self):
        course_type = "Elective" if self.is_elective else "Mandatory"
        category_info = f", Category: {self.category}" if self.is_elective else ""
        return f'<{course_type} Course {self.course.courseCode} in Semester {self.semester_id}{category_info}>'
    
    def __init__(self, semester_id=None, course_id=None, is_elective=False, category_id=None):
        self.semester_id = semester_id
        self.course_id = course_id
        self.is_elective = is_elective

        
        if is_elective:
            if not category_id:
                raise ValueError("Category must be provided for elective courses.")
            self.category_id = category_id
        else:
            self.category_id = None

class ElectiveGroup(db.Model):
    __tablename__ = 'elective_groups'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), unique=True, nullable=False)

    def serialize(self):
        return {"id": self.id, "name": self.name}

    def __repr__(self):
        return f'<ElectiveGroup {self.name}>'
    
    def __init__(self, category):
        self.name = category
        
        


class Semester(db.Model):
    __tablename__ = 'semester'
    id = db.Column(db.Integer, primary_key=True)
    semester_number = db.Column(db.Integer, nullable=False)
    studyplan_id = db.Column(db.Integer, db.ForeignKey('studyplan.id'), nullable=False)
    term = db.Column(db.Enum('H', 'V', name='semester_type'), nullable=False)

    studyplan = db.relationship('Studyplan', back_populates='semesters')
    semester_courses = db.relationship('SemesterCourses', back_populates='semester', cascade='all, delete-orphan', lazy='joined')

    def serialize(self):
        return {
            "id": self.id,
            "semester_number": self.semester_number,
            "term": self.term,
            "semester_courses": [
                {
                    "course_id": sc.course.id,
                    "is_elective": sc.is_elective,
                    "category": {
                        "category_id": sc.category.id,
                        "name": sc.category.name
                    } if sc.is_elective and sc.category else None
                } 
                for sc in self.semester_courses
            ],
        }
    
    def __repr__(self):
        return f'<Semester {self.semester_number} ({self.term}) - Studyplan {self.studyplan_id}>'


    def __init__(self, semester_number, studyplan_id, term=None):
        self.semester_number = semester_number
        self.studyplan_id = studyplan_id
        self.term = term or ('H' if semester_number % 2 == 1 else 'V')

class Log(db.Model):
    __tablename__ = 'log'
    id = db.Column(db.Integer, primary_key=True)
    time = db.Column(db.DateTime, default=datetime.timezone.utc, nullable=False)
    message = db.Column(db.String(100), nullable=False)

    
    def serialize(self):

        self.time = pytz.UTC.localize(self.time)
        self.time = self.time.astimezone(pytz.timezone('Europe/Oslo'))
        print(self)
        return{
            "id":self.id,
            "time" : self.time.strftime('%Y-%m-%d %H:%M:%S %Z'),
            "message" : self.message
        }
    def __repr__(self):
        return f'<Log at {self.time}>'

    def __init__(self, message):
        self.time = datetime.datetime.now(datetime.timezone.utc)
        self.message = message
        


