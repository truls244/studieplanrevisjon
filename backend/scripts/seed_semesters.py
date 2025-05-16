import pandas as pd
import os
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.exc import IntegrityError
from app.models import Studyplan, Semester, SemesterCourses, Studyprogram, Course, ElectiveGroup

from app import db, create_app
app = create_app()

def seed_studyplans(file_path):
    """
    Seed studyplans from Excel file with columns:
    - studyprogram_code
    - year
    """
    print("Seeding studyplans...")
    
    # Read Excel file
    df = pd.read_excel(file_path)
    
    studyplans_created = 0
    studyplans_skipped = 0
    
    with app.app_context():
        for _, row in df.iterrows():
            studyprogram_code = row['Studieprogramkode']
            year = int(row['Arstall fra - emnekomb'])
            
            # Find the studyprogram by code
            studyprogram = Studyprogram.query.filter_by(program_code=studyprogram_code).first()
            
            if not studyprogram:
                print(f"Warning: Studyprogram with code {studyprogram_code} not found. Skipping.")
                continue
            
            # Check if studyplan already exists
            existing_studyplan = Studyplan.query.filter_by(
                year=year, 
                studyprogram_id=studyprogram.id
            ).first()
            
            if existing_studyplan:
                print(f"Studyplan for {studyprogram_code} year {year} already exists. Skipping.")
                studyplans_skipped += 1
                continue
            
            # Create new studyplan
            studyplan = Studyplan(
                year=year,
                studyprogram_id=studyprogram.id
            )
            
            try:
                db.session.add(studyplan)
                db.session.flush()  # Flush to get the ID but don't commit yet
                
                # Create 10 semesters for this studyplan (5 years × 2 semesters)
                for i in range(1,studyprogram.semester_number+1):
                    term = 'H' if i % 2 == 1 else 'V'
                    semester = Semester(
                        semester_number=i,
                        studyplan_id=studyplan.id,
                        term=term
                    )
                    db.session.add(semester)
                
                db.session.commit()
                studyplans_created += 1
                print(f"Created studyplan for {studyprogram_code} year {year} with 10 semesters.")
                
            except IntegrityError as e:
                db.session.rollback()
                print(f"Error creating studyplan for {studyprogram_code} year {year}: {e}")
                studyplans_skipped += 1
    




def seed_semester_courses(file_path):
    """
    Seed semester_courses from Excel file with columns:
    - studyprogram_code
    - year
    - semester_number
    - course_code
    """
    print("Seeding semester courses...")
    
    # Read Excel file
    df = pd.read_excel(file_path)
    
    courses_linked = 0
    courses_skipped = 0
    
    with app.app_context():
        for _, row in df.iterrows():
            studyprogram_code = row['Studieprogramkode']
            if pd.isna(row['Arstall fra - emnekomb']):
                continue
            year = int(row['Arstall fra - emnekomb'])
            course_code = row['courseCode']
            elective_status = row['Emnevalgstatuskode']


            if pd.isna(row['Terminnr default']):
                course_test = db.session.query(Course).get(course_code)
                if not course_test:
                    continue
                if course_test.semester == "V":
                    semester_number = 2  # Default value
                else:
                    semester_number = 3
            else:
                semester_number = int(row['Terminnr default'])
            course_code = row['courseCode']
            elective_status = row['Emnevalgstatuskode']
            
            # Find the studyprogram by code
            studyprogram = Studyprogram.query.filter_by(program_code=studyprogram_code).first()
            
            if not studyprogram:
                print(f"Warning: Studyprogram with code {studyprogram_code} not found. Skipping.")
                courses_skipped += 1
                continue
            
            # Find the studyplan
            studyplan = Studyplan.query.filter_by(
                year=year, 
                studyprogram_id=studyprogram.id
            ).first()
            
            if not studyplan:
                print(f"Warning: Studyplan for {studyprogram_code} year {year} not found. Skipping.")
                courses_skipped += 1
                continue
            
            try: 
                if str(course_code[-3:])=="BAC" or str(course_code[-3:]) == "MAS":
                    semester_number += 1
            except:
                print(course_code)
            # Find the semester
            semester = Semester.query.filter_by(
                semester_number=semester_number,
                studyplan_id=studyplan.id
            ).first()
            
            if not semester:
                print(f"Warning: Semester {semester_number} for {studyprogram_code} year {year} not found. Skipping.")
                courses_skipped += 1
                continue
            
            # Find the course by code
            course = Course.query.filter_by(courseCode=course_code).first()
            
            if not course:
                print(f"Warning: Course with code {course_code} not found. Skipping.")
                courses_skipped += 1
                continue
            
            # Check if the course is already linked to this semester
            existing_link = SemesterCourses.query.filter_by(
                semester_id=semester.id,
                course_id=course.id
            ).first()
            
            if existing_link:
                print(f"Course {course_code} already linked to semester {semester_number} for {studyprogram_code} year {year}. Skipping.")
                courses_skipped += 1
                continue
            if pd.isna(row['Emnevalgstatuskode']):
                elective_status = "O"
            # Create new semester_course link (assuming most courses are mandatory, not elective)
            # You may need to adjust this logic if your Excel has data about elective courses
            if elective_status == "O":
                semester_course = SemesterCourses(
                    semester_id=semester.id,
                    course_id=course.id,
                    is_elective=False  # Assuming most courses are mandatory
                )
            else:
                continue
            
            try:
                db.session.add(semester_course)
                db.session.commit()
                courses_linked += 1
                print(f"Linked course {course_code} to semester {semester_number} for {studyprogram_code} year {year}.")
            except IntegrityError as e:
                db.session.rollback()
                print(f"Error linking course {course_code} to semester {semester_number}: {e}")
                courses_skipped += 1


def seed_elective_courses(file_path):
    
    print("Seeding elective courses...")
    
    # Read Excel file
    df = pd.read_excel(file_path)
    
    # Add a default category column if it doesn't exist
    if 'Emnevalgstatuskode' not in df.columns:
        df['category'] = 'Anbefalte valgemner'
    
    electives_linked = 0
    electives_skipped = 0
    
    with app.app_context():
        for _, row in df.iterrows():
            studyprogram_code = row['Studieprogramkode']
            if pd.isna(row['Arstall fra - emnekomb']):
                continue
            year = int(row['Arstall fra - emnekomb'])
            elect = row['Emnevalgstatuskode']
            if elect == "O":
                continue
            if pd.isna(row['Emnevalgstatuskode']):
                continue
            # 'Velg ett emne', 'Anbefalte valgemner', 'Andre valgemner'

            cat1 = db.session.query(ElectiveGroup).get(1)
            cat2 = db.session.query(ElectiveGroup).get(2)
            cat3 = db.session.query(ElectiveGroup).get(3)

            # Handle missing semester_number

            course_code = row['courseCode']
            if pd.isna(row['Terminnr default']):
                course_test = db.session.query(Course).get(course_code)
                if not course_test:
                    continue
                if course_test.semester == "V":
                    semester_number = 2  # Default value
                else:
                    semester_number = 3
            else:
                semester_number = int(row['Terminnr default'])
                
            
            
            '''
            # Validate category
            if category not in SemesterCourses.elective_categories:
                print(f"Warning: Invalid category '{category}' for course {course_code}. Using 'Anbefalte valgemner'.")
                category = 'Anbefalte valgemner'
            '''
            # Find the studyprogram by code
            studyprogram = Studyprogram.query.filter_by(program_code=studyprogram_code).first()
            
            if not studyprogram:
                print(f"Warning: Studyprogram with code {studyprogram_code} not found. Skipping.")
                electives_skipped += 1
                continue
            
            # Find the studyplan
            studyplan = Studyplan.query.filter_by(
                year=year, 
                studyprogram_id=studyprogram.id
            ).first()
            
            if not studyplan:
                print(f"Warning: Studyplan for {studyprogram_code} year {year} not found. Skipping.")
                electives_skipped += 1
                continue
            
            # Find the semester
            semester = Semester.query.filter_by(
                semester_number=semester_number,
                studyplan_id=studyplan.id
            ).first()
            
            if not semester:
                print(f"Warning: Semester {semester_number} for {studyprogram_code} year {year} not found. Skipping.")
                electives_skipped += 1
                continue
            
            # Find the course by code
            course = Course.query.filter_by(courseCode=course_code).first()
            
            if not course:
                print(f"Warning: Course with code {course_code} not found. Skipping.")
                electives_skipped += 1
                continue
            
            # Check if the course is already linked to this semester
            existing_link = SemesterCourses.query.filter_by(
                semester_id=semester.id,
                course_id=course.id
            ).first()
            category = ElectiveGroup
            if existing_link:
                print(f"Course {course_code} already linked to semester {semester_number} for {studyprogram_code} year {year}. Skipping.")
                electives_skipped += 1
                continue
            if elect == "V":
                category = cat2
            elif elect[0] == "M":
                category = cat1
            # Create new semester_course link for elective course
            try:
                semester_course = SemesterCourses(
                    semester_id=semester.id,
                    course_id=course.id,
                    is_elective=True,
                    category_id=category.id
                )
                
                db.session.add(semester_course)
                db.session.commit()
                electives_linked += 1
                print(f"Linked elective course {course_code} in category '{category}' to semester {semester_number} for {studyprogram_code} year {year}.")
            except IntegrityError as e:
                db.session.rollback()
                print(f"Error linking elective course {course_code} to semester {semester_number}: {e}")
                electives_skipped += 1
            except ValueError as e:
                print(f"Error with elective course {course_code}: {e}")
                electives_skipped += 1
    
    print(f"Finished seeding elective courses. Linked: {electives_linked}, Skipped: {electives_skipped}")

def seed_elective_groups():

    with app.app_context():
        cat1 = ElectiveGroup(category="Velg ett emne")
        cat2 = ElectiveGroup(category="Anbefalt valgemner")
        cat3 = ElectiveGroup(category="Andre valgemner")
        db.session.add(cat1)
        db.session.add(cat2)
        db.session.add(cat3)
        db.session.commit()
        print("Seeda Elective Groups")


if __name__ == "__main__":
    # Update these paths with your actual Excel file paths
    studyplans_file = "static/test.xlsx"
    semester_courses_file = "static/StudyprogramCode_Year.xlsx"
    electives_file = "static/test.xlsx"
    # Uncomment the lines below to run the seeding
    seed_studyplans(semester_courses_file)
    seed_semester_courses(studyplans_file)
    seed_elective_groups()
    seed_elective_courses(electives_file)
    
    print("Seeding completed!")
