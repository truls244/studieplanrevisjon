from app import db
from app.models import Course, Studyprogram, Studyplan, Institute, Notifications, Semester, SemesterCourses, ElectiveGroup
from sqlalchemy import func, and_, or_, literal_column
from sqlalchemy.orm import joinedload


class SemesterCoursesService:
    def __init__(self, db_session=None):
        self.db = db_session or db.session

    # create
    def create_semester_course(self, semester_id, course_id, is_elective=False, category_id=None):
        semester_course = SemesterCourses(
            semester_id=semester_id,
            course_id=course_id,
            is_elective=is_elective,
            category_id=category_id
        )
        self.db.add(semester_course)
        self.db.commit()
        return semester_course


    def format_courses_for_semesters(self, semester_courses, semester_mapping):
        formatted_courses = {}
        for sem_num_str, courses in semester_courses.items():
            sem_num = int(sem_num_str)
            if sem_num in semester_mapping:
                semester_id = semester_mapping[sem_num]
                formatted_courses[semester_id] = [
                    {
                        "course_id": course.get("course_id"),
                        "is_elective": course.get("is_elective", False),
                        "category_id": course.get("category_id") 
                    }
                    for course in courses
                ]
        return formatted_courses

    # add
    def batch_add_all_courses(self, studyplan_id, formatted_courses):
        try:
            for semester_id, courses in formatted_courses.items():
                for course in courses:
                    course_id = course.get('course_id')
                    is_elective = course.get('is_elective', False)
                    category_id = course.get('category_id') if is_elective else None

                    semester_course = SemesterCourses(
                        semester_id=semester_id,
                        course_id=course_id,
                        is_elective=is_elective,
                        category_id=category_id
                    )
                    self.db.add(semester_course)
            self.db.flush()
            self.db.commit()
        except Exception as e:
            raise RuntimeError(f"Failed to add courses to semesters: {str(e)}")
            self.db.rollback()


    # update
    def update_courses(self, formatted_courses):
        try:
            for semester_id, courses in formatted_courses.items():
                self.db.query(SemesterCourses).filter_by(semester_id=semester_id).delete()
                print(f"Updating courses for semester ID: {semester_id}")
            
                for course in courses:
                    semester_course = SemesterCourses(
                        semester_id=semester_id,
                        course_id=course["course_id"],
                        is_elective=course.get("is_elective", False),
                        category_id=course.get("category_id"),
                    )
                    self.db.add(semester_course)


            self.db.commit()
            print(f"Updated11 courses for {len(formatted_courses)} semesters.")
            return {"message": f"Updated courses for {len(formatted_courses)} semesters."}
        except Exception as e:
            self.db.rollback()
            raise RuntimeError(f"Failed to update courses for semester {semester_id}: {str(e)}")
    
    def get_courses_by_semester_id(self, semester_id):
        try:
            return self.db.query(SemesterCourses).filter_by(semester_id=semester_id).options(
                joinedload(SemesterCourses.course),
                joinedload(SemesterCourses.category)
            ).all()
        except Exception as e:
            raise RuntimeError(f"Failed to fetch courses for semester ID {semester_id}: {str(e)}")


    def get_courses_by_semester_ids(self, semester_ids):
        try:
            semester_courses = self.db.query(SemesterCourses).filter(SemesterCourses.semester_id.in_(semester_ids)).all()
            print(f"Fetched {len(semester_courses)} courses for semesters: {semester_ids}")
            return semester_courses
        except Exception as e:
            raise RuntimeError(f"Failed to fetch courses for semester IDs {semester_ids}: {str(e)}")

    def get_all_courses_by_studyplan_id(self, studyplan_id):
        try:
            courses = (
                self.db.query(SemesterCourses)
                .join(Semester, SemesterCourses.semester_id == Semester.id)
                .filter(Semester.studyplan_id == studyplan_id)
                .all()
            )
            print(f"Fetched {len(courses)} courses for studyplan {studyplan_id}.")
            return courses
        except Exception as e:
            raise RuntimeError(f"Failed to fetch courses for studyplan {studyplan_id}: {str(e)}")

    def serialize_courses(self, semester_courses_objs):
        try:
            serialized_courses = []
            for sc in semester_courses_objs:
                course = sc.course
                if not course:
                    continue

                # Serialize course data
                course_data = course.serialize()
                course_data['semester_course_id'] = sc.id
                course_data['is_elective'] = sc.is_elective

                if sc.is_elective and sc.category:
                    course_data['category'] = sc.category.serialize()

                serialized_courses.append(course_data)

            return serialized_courses
        except Exception as e:
            raise RuntimeError(f"Failed to serialize courses: {str(e)}")
    

    # ELECTIVE / VALGEMNER LOGIC

    def create_elective_group(self, new_category):

        if not new_category:
            raise ValueError("Category name cannot be empty.")
        try:
            existing_group = self.db.query(ElectiveGroup).filter_by(name=new_category).first()
            if existing_group:
                raise ValueError(f"Category '{new_category}' already exists.")

            elective_group = ElectiveGroup(category=new_category)
            self.db.add(elective_group)
            self.db.commit()
            return elective_group.serialize()
        except Exception as e:
            self.db.rollback()
            raise RuntimeError(f"Failed to create elective group: {str(e)}")

    
    def get_elective_group(self):
        try:
            elective_groups = self.db.query(ElectiveGroup).all()
            return [group.serialize() for group in elective_groups]
        except Exception as e:
            raise RuntimeError(f"Failed to fetch elective groups: {str(e)}")


    def delete_elective_group(self, group_id):
        try:
            elective_group = self.db.query(ElectiveGroup).get(group_id)
            if not elective_group:
                raise ValueError(f"Elective group with ID {group_id} does not exist.")

            if elective_group.semester_courses:
                raise ValueError(f"Cannot delete elective group '{elective_group.name}' because it has assigned courses.")

            self.db.delete(elective_group)
            self.db.commit()
            return {"message": f"Elective group '{elective_group.name}' deleted successfully."}
        except ValueError as e:
            raise ValueError(str(e))
        except Exception as e:
            self.db.rollback()
            raise RuntimeError(f"Failed to delete elective group: {str(e)}")


    def update_elective_group(self, group_id, new_name):
        if not new_name:
            raise ValueError("New category name cannot be empty.")
        try:
            elective_group = self.db.query(ElectiveGroup).get(group_id)
            if not elective_group:
                raise ValueError(f"Elective group with ID {group_id} does not exist.")

            existing_group = self.db.query(ElectiveGroup).filter_by(name=new_name).first()
            if existing_group:
                raise ValueError(f"Category '{new_name}' already exists.")

            elective_group.name = new_name
            self.db.commit()
            return elective_group.serialize()
        except Exception as e:
            self.db.rollback()
            raise RuntimeError(f"Failed to update elective group: {str(e)}")

    def get_courses_by_category_id(self, category_id):
        try:
            courses = self.db.query(SemesterCourses).filter_by(category_id=category_id).all()
            return courses
        except Exception as e:
            raise RuntimeError(f"Failed to fetch courses for category ID {category_id}: {str(e)}")

    def get_elective_courses_by_semester_id(self, semester_id):
        try:
            elective_courses = (
                self.db.query(SemesterCourses)
                .filter(SemesterCourses.semester_id == semester_id, SemesterCourses.is_elective == True)
                .all()
            )
            return elective_courses
        except Exception as e:
            raise RuntimeError(f"Failed to fetch elective courses for semester ID {semester_id}: {str(e)}")

    def get_elective_courses_by_studyplan_id(self, studyplan_id):
        try:
            elective_courses = (
                self.db.query(SemesterCourses)
                .join(Semester, Semester.id == SemesterCourses.semester_id)
                .filter(Semester.studyplan_id == studyplan_id, SemesterCourses.is_elective == True)
                .all()
            )
            return elective_courses
        except Exception as e:
            raise RuntimeError(f"Failed to fetch elective courses for studyplan ID {studyplan_id}: {str(e)}")

    def get_courses_by_semester_and_category(self, semester_id, category_id):
        try:
            courses = (
                self.db.query(SemesterCourses)
                .filter_by(semester_id=semester_id, category_id=category_id)
                .all()
            )
            print(f"Fetched {len(courses)} courses for semester {semester_id} and category {category_id}.")
            return courses
        except Exception as e:
            raise RuntimeError(f"Failed to fetch courses for semester {semester_id} and category {category_id}: {str(e)}")

    def get_elective_groups_with_courses(self):
        try:
            elective_groups = self.db.query(ElectiveGroup).options(joinedload(ElectiveGroup.semester_courses)).all()
            result = [
                {
                    "id": group.id,
                    "name": group.name,
                    "courses": [course.serialize() for course in group.semester_courses],
                }
                for group in elective_groups
            ]
            return result
        except Exception as e:
            raise RuntimeError(f"Failed to fetch elective groups with courses: {str(e)}")
        