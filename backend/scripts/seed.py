import sqlite3
import pandas as pd
import numpy as np




courselist = []

connection = sqlite3.connect('instance/app.db')
cursor = connection.cursor()


cursor.execute("DELETE FROM course")
cursor.execute("DELETE FROM prerequisites")


# SEED COURSES


xls = pd.ExcelFile('static/Data.xlsx')
courses = pd.read_excel(xls, 'Emner 2018V-2028H')
UHCourses = pd.read_excel('static/DataMedEmnerFraTNSVUH.xlsx', 'Emner ved UH-fak 2018V-2028H')
SVCourses = pd.read_excel('static/DataMedEmnerFraTNSVUH.xlsx', 'Emner ved SV-fak 2018V-2028H')
utvalg = courses[['emnekode','emnenavn_bokmal','vektingstall','terminkode_und_forste','arstall_und_siste','terminkode_und_siste']]
UHutvalg = UHCourses[['emnekode','emnenavn_bokmal','vektingstall','terminkode_und_forste','arstall_und_siste']]
SVutvalg = SVCourses[['emnekode','emnenavn_bokmal','vektingstall','terminkode_und_forste','arstall_und_siste']]



#Endre semester fra Vår/Høst til V/H og fjerne sommmer
utvalg['terminkode_und_forste'] = utvalg['terminkode_und_forste'].str.replace('HØST','H')
utvalg['terminkode_und_forste'] = utvalg['terminkode_und_forste'].str.replace('VÅR','V')
utvalg = utvalg[~utvalg['terminkode_und_forste'].str.contains('SOM', case=True, na=False)]

UHutvalg['terminkode_und_forste'] = UHutvalg['terminkode_und_forste'].str.replace('HØST','H')
UHutvalg['terminkode_und_forste'] = UHutvalg['terminkode_und_forste'].str.replace('VÅR','V')
UHutvalg = UHutvalg[~UHutvalg['terminkode_und_forste'].str.contains('SOM', case=True, na=False)]

SVutvalg['terminkode_und_forste'] = SVutvalg['terminkode_und_forste'].str.replace('HØST','H')
SVutvalg['terminkode_und_forste'] = SVutvalg['terminkode_und_forste'].str.replace('VÅR','V')
SVutvalg = SVutvalg[~SVutvalg['terminkode_und_forste'].str.contains('SOM', case=True, na=False)]

#Legge til emner som e i bruk ette 2023 og sette emner som har siste undervisning i 2024 og 2025 som inavtive
for i in np.asarray(utvalg):
    course = [i[1],i[0],i[3],i[2]]
    if i[4] <= 2024 or i[4] == 2025 and i[5]=="VÅR":
        pass
    elif i[4] == 2025 and i[5]=="HØST":
        cursor.execute("INSERT INTO course (name, courseCode, semester, credits, degree, is_active) VALUES (?, ?, ?, ?, 'Bachelor', False);", course)
        courselist.append(i[0])
    else:
        cursor.execute("INSERT INTO course (name, courseCode, semester, credits, degree, is_active) VALUES (?, ?, ?, ?, 'Bachelor', True);", course)
        courselist.append(i[0])

for i in np.asarray(UHutvalg):
    course = [i[1],i[0],i[3],i[2]]
    if i[4] <= 2023:
        pass
    elif i[4] == 2024 or i[4] == 2025:
        cursor.execute("INSERT INTO course (name, courseCode, semester, credits, degree, is_active) VALUES (?, ?, ?, ?, 'Bachelor', False);", course)
        courselist.append(i[0])
    else:
        cursor.execute("INSERT INTO course (name, courseCode, semester, credits, degree, is_active) VALUES (?, ?, ?, ?, 'Bachelor', True);", course)
        courselist.append(i[0])

for i in np.asarray(SVutvalg):
    course = [i[1],i[0],i[3],i[2]]
    if i[4] <= 2023:
        pass
    elif i[4] == 2024 or i[4] == 2025:
        cursor.execute("INSERT INTO course (name, courseCode, semester, credits, degree, is_active) VALUES (?, ?, ?, ?, 'Bachelor', False);", course)
        courselist.append(i[0])
    else:
        cursor.execute("INSERT INTO course (name, courseCode, semester, credits, degree, is_active) VALUES (?, ?, ?, ?, 'Bachelor', True);", course)
        courselist.append(i[0])
cursor.execute("INSERT INTO course (name, courseCode, semester, credits, degree, is_active) VALUES ('Valgemner 5 Poeng', 'VALGEMNE', 'H', 5, 'Bachelor', True);")
cursor.execute("INSERT INTO course (name, courseCode, semester, credits, degree, is_active) VALUES ('Valgemner 10 Poeng', 'VALGEMNE', 'H', 10, 'Bachelor', True);")
cursor.execute("INSERT INTO course (name, courseCode, semester, credits, degree, is_active) VALUES ('Valgemner 15 Poeng', 'VALGEMNE', 'H', 15, 'Bachelor', True);")
cursor.execute("INSERT INTO course (name, courseCode, semester, credits, degree, is_active) VALUES ('Valgemner 20 Poeng', 'VALGEMNE', 'H', 20, 'Bachelor', True);")
cursor.execute("INSERT INTO course (name, courseCode, semester, credits, degree, is_active) VALUES ('Valgemner 25 Poeng', 'VALGEMNE', 'H', 25, 'Bachelor', True);")
cursor.execute("INSERT INTO course (name, courseCode, semester, credits, degree, is_active) VALUES ('Valgemner 30 Poeng', 'VALGEMNE', 'H', 30, 'Bachelor', True);")

connection.commit()

#Lese data fra excel fil og plukke ut relevant info
preReqs = pd.read_excel('static/cleaned_prerequisites.xlsx')
preReqs = preReqs[['emnekode','kravinnhold','arstall_til']]
activePreReqs = preReqs[preReqs['arstall_til'].isna()]

#Finne id te emnene også legge til i forkunnskap
for i in np.asarray(activePreReqs):
    if i[0] in courselist and isinstance(i[1],str):
        preReqCode = i[1].split()
        course_ID = cursor.execute("SELECT id FROM course WHERE courseCode =?",(i[0],)).fetchone()
        preReq_ID = cursor.execute("SELECT id FROM course WHERE courseCode =?",(preReqCode[0],)).fetchone()
        fetchedCourse = course_ID[0]
        fetchedPreReq = preReq_ID[0]
        cursor.execute("INSERT OR IGNORE INTO prerequisites (course_id, prerequisite_id) VALUES (?,?)",(int(fetchedCourse),int(fetchedPreReq)))

connection.commit()
print("Courses seeded")



cursor.execute("DELETE FROM studyprogram")

# Lese data om studieprogram fra fil og legge til i database
xls = pd.ExcelFile('static/Data.xlsx')
studyprograms = pd.read_excel(xls, 'Studieprogram')
utvalg = studyprograms[['studieprogramkode','studieprognavn','tall_varighet','instituttnr_studieansv','status_utgatt']]

codesToSkip = ["B-BYGG","B-ELE-YVEI","B-ELEKTRO","M-BIOENG","M-DATATEK-5","M-INDØKG","M-INDØKG5","M-LEKTREA","M-RISGOV","M-SAMSIK","M-ROBOT","M-MAFYS5"]

for i in np.asarray(utvalg):
    program = [i[1],i[0],i[3],i[2]]
    if i[0] in codesToSkip:
        continue
    if i[0][0] == "B" and i[4] == "N" and i[1][-6:] != "deltid":
        cursor.execute("INSERT INTO studyprogram (name, program_code, degree_type, institute_id, semester_number) VALUES (?, ?, 'Bachelor', ?, ?);", program)
        pass
    elif i[0][0] == "M" and i[4] == "N" and i[0][-1] != 5 and i[1][-6:] != "deltid":
        cursor.execute("INSERT INTO studyprogram (name, program_code, degree_type, institute_id, semester_number) VALUES (?, ?, 'Master', ?, ?);", program)

print("Studyprograms seeded")






cursor.execute("DELETE FROM studyplan")
cursor.execute("DELETE FROM semester")
cursor.execute("DELETE FROM semester_courses")
cursor.execute("DELETE FROM institute")

institutes = pd.read_excel('static/Data.xlsx','Steder - Fakultet og institutt')
for x in institutes.values:
    if x[2] != 0:
        cursor.execute("INSERT INTO institute VALUES (?,?,?)",(x[2],x[5],None)) 
print("Institutes seeded")



connection.commit()
connection.close()

'''

# Open the CSV file and insert data
studyprogram_years = pd.read_excel('static/StudyprogramCode_Year.xlsx','Sheet1')

courses = pd.read_excel('static/Data.xlsx','Emnekombinasjoner')


#Seed institutes

# Henter emnekombinasjoner med id fra excelfil OBS funker ikke hvis course blir seedet på nytt!!!
studyplan_subjects = pd.read_excel('static/Emnekombinasjoner_med_ID.xlsx')
# Henter id og studieprogram kodene fra database
studyprograms = pd.read_sql("SELECT id,program_code, semester_number FROM studyprogram", connection)


for i in studyprogram_years.values:
    if i[0] in studyprograms.values:
        program = studyprograms[studyprograms["program_code"] == i[0]].head(1)
        cursor.execute("INSERT INTO studyplan (year, studyprogram_id) VALUES (?,?)",(i[1],int(program["id"].values)))
        studyplan_id = cursor.lastrowid
        for j in studyplan_subjects.values:
            if j[0] == program['program_code'].values and j[1] == i[1] and j[2] == 'O' and j[0][-1] != str(5):
                if str(j[5][-3:])=="BAC" or str(j[5][-3:]) == "MAS":
                    j[3] = j[3]+1
                cursor.execute("INSERT OR IGNORE INTO studyplan_courses (studyplan_id,course_id,semester) VALUES (?,?,?)",(studyplan_id,j[7],j[3]))
            if j[0] == program['program_code'].values and j[1] == i[1] and j[2] == 'V' and j[0][-1] != str(5):
                cursor.execute("INSERT OR IGNORE INTO studyplan_courses (studyplan_id,course_id,semester) VALUES (?,?,?)",(studyplan_id,j[7],j[3]))
print("studyplans seeded")

connection.commit()
connection.close()

'''