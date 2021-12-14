from flask import Flask, render_template, request
from flask_sqlalchemy import SQLAlchemy
from marshmallow import fields
from marshmallow_sqlalchemy import SQLAlchemyAutoSchema
import os
import pickle
from joblib import load
import numpy as np
import pandas as pd

app = Flask(__name__)
ENV = 'prod'
if ENV == 'env':
    app.debug = True
    app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://temi:password@localhost/temidb'
else:
    app.debug = True
    app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://mzxkrgcsaxjpmb:789a71c49a2876f8a8b01528a8d67dcb094b2d12a6009da7891b49732af1d7d9@ec2-54-146-84-101.compute-1.amazonaws.com:5432/devhf16j3594ku'


app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)



courses_dict = {
    "P2_1_ENGR": ["CPE 203", "CHE 201", "MSE 201", "MEE 205", "EEE 201", "EEE 291"],
    "P2_1_ECN": ["CPE 203", "ECN 203", "ECN 201", "MTH 201", "MEE 203", "CSC 201"],
    "P2_1_MTH": ["CPE 203", "MTH 205", "STT 201", "MTH 201", "MEE 203", "CSC 201"],
    "P2_2_ENGR": ["CPE 204", "CSC 202", "AGE 202", "CVE 202", "MEE 206", "MEE 204", "EEE 202", "EEE 292", "MTH 202"],
    "P2_2_ECN": ["CPE 204", "CPE 206", "ECN 204", "ECN 202", "MTH 202", "MEE 204", "CSC 202"],
    "P2_2_MTH": ["CPE 204", "CPE 206", "MTH 306", "STT 202", "MTH 202", "MEE 204", "CSC 202"],
    "P3_1_ENGR": ["CPE 301", "CPE 303", "CPE 307", "CPE 309", "EEE 301", "EEE 309", "MEE 303", "MSE 201", "CHE 305"],
    "P3_1_ECN": ["CPE 301", "CSC 307", "CSC 305", "CSC 311", "CSC 315", "CSC 317", "ECN 301", "ECN 313"],
    "P3_1_MTH": ["CPE 301", "CSC 307", "CSC 305", "CSC 311", "CSC 315", "CSC 317", "MTH 301"],
    "P3_2_ENGR": ["CSC 302", "CSC 306", "CSC 308", "CPE 310", "CPE 316", "CPE 314", "EEE 302", "CHE 306", "AGE 302"],
    "P3_2_ECN": ["CSC 302", "CSC 306", "CSC 308", "CPE 310", "CPE 316", "CSC 304", "CSC 312", "ECN 302", "ECN 314"],
    "P3_2_MTH": ["CSC 302", "CSC 306", "CSC 308", "CPE 310", "CPE 316", "CSC 304", "CSC 312", "MTH 302"],
    "P4_1_ENGR": ["CPE 401", "CPE 405", "CSC 403", "CSC 415", "CPE 409", "CVE 401"],
    "P4_1_ECN": ["CPE 401", "CPE 405", "CSC 403", "CSC 415", "CSC 407", "ECN 401", "ECN 421", "CVE 401"], 
    "P4_1_MTH": ["CPE 401", "CPE 405", "CSC 403", "CSC 415", "MTH207", "CVE 401"]
}

course_unit = pd.read_csv("CSC courses & units - courses_table.csv")


###Models####
class Course(db.Model):
    __tablename__ = "courses"
    id = db.Column(db.Integer, primary_key=True)
    course_code = db.Column(db.String(10))
    course_title = db.Column(db.String(100))
    level = db.Column(db.String(100))
    option = db.Column(db.String(100))
    semester = db.Column(db.String(100))
    unit = db.Column(db.Integer)

    # def create(self):
    #     db.session.add(self)
    #     db.session.commit()
    #     return self

    def __init__(self, course_code, course_title, level, option, semester, unit):
        self.course_code = course_code
        self.course_title = course_title
        self.level = level
        self.option = option
        self.semester = semester
        self.unit = unit

    # def __repr__(self):
    #     return '' % self.id


# db.create_all()


class CourseSchema(SQLAlchemyAutoSchema):
    class Meta:
        model = Course
        sqla_session = db.session

    id = fields.Number(dump_only=True)
    course_code = fields.String(required=True)
    course_title = fields.String(required=True)
    level = fields.String(required=True)
    option = fields.String(required=True)
    semester = fields.String(required=True)
    unit = fields.Number(required=True)
@app.route('/')
def hello_world():  # put application's code here
    return render_template('index.html')

@app.route('/next', methods=["GET", "POST"])
def home():
    if request.form:
        data = request.form
        part = data['part']
        option = data['options']
        semester = data['semester']
        Last_CGPA = data['cpga']
        user_data = Course.query.filter_by(
            level=part, option=option, semester=semester)
        if semester == "Harmattan":
            sem = 1
            unit = int(1 + ((int(part)-1)*2))
        elif semester == "Rain":
            sem = 2
            unit = int((1 + ((int(part)-1)*2)) + 1)
        course_schema = CourseSchema(many=True)
        courses = course_schema.dump(user_data)
        
        if (part == 2) and (sem == 1) and (option == "Engineering"):
            print("got here")
            course_by_student = courses_dict.get('P2_1_ENGR')
        elif part == 2 and sem == 2 and option == "Engineering":
            course_by_student = courses_dict.get('P2_2_ENGR')

        elif part == 2 and sem == 1 and option == "Economics":
            course_by_student = courses_dict.get('P2_1_ECN')
        elif part == 2 and sem == 2 and option == "Economics":
            course_by_student = courses_dict.get('P2_2_ECN')
        elif part == 2 and sem == 1 and option == "Maths":
            course_by_student = courses_dict.get('P2_1_MTH')
        elif part == 2 and sem == 2 and option == "Maths":
            course_by_student = courses_dict.get('P2_2_MTH')

# for part 3    
        elif part == 3 and sem == 1 and option == "Engineering":
            course_by_student = courses_dict.get('P3_1_ENGR')
        elif part == 3 and sem == 2 and option == "Engineering":
            course_by_student = courses_dict.get('P3_2_ENGR')

        elif part == 3 and sem == 1 and option == "Economics":
            course_by_student = courses_dict.get('P3_1_ECN')
        elif part == 3 and sem == 2 and option == "Economics":
            course_by_student = courses_dict.get('P3_2_ECN')

        elif part == 3 and sem == 1 and option == "Maths":
            course_by_student = courses_dict.get('P3_1_MTH')
        elif part == 3 and sem == 2 and option == "Maths":
            course_by_student = courses_dict.get('P3_2_MTH')
        
        elif part == 4 and sem == 1 and option == "Engineering":
            course_by_student = courses_dict.get('P4_1_ENGR')

        elif part == 4 and sem == 1 and option == "Economics":
            course_by_student = courses_dict.get('P4_1_ECN')
        elif part == 4 and sem == 1 and option == "Maths":
            course_by_student = courses_dict.get('P4_1_MTH')
        

        
    u = [course_unit[course_unit["Course"]== i]["Unit"].tolist() for i in course_by_student]
    flat_list_u = [item for sublist in u for item in sublist]
    df = pd.DataFrame({"courses": course_by_student, "Units": flat_list_u}).sort_values(by = "Units")

    if Last_CGPA < 3.5:
        valid = []
        others = []
        for i in df["courses"]:
            if i[:3] == "CSC" or i[:3] == "CPE":
                others.append(i)
            else:
                valid.append(i)
        units = []
        flat_list = []
        rem_course = []  

        for i in valid:
            units.append(course_unit[course_unit["Course"]== i]["Unit"].tolist())
            
        flat_list = [item for sublist in units for item in sublist]
        units_sum = sum(flat_list)
            
        if units_sum < 20:
            for i in others:
                unit = course_unit[course_unit["Course"]== i]["Unit"].tolist()
                units_sum = np.add(units_sum, unit)
                rem_course.append(i)
                if units_sum + unit > 20:
                    break
                elif units_sum < 20:
                    continue
                
                
            required_courses = valid + rem_course
            response = "The required course you should register for this semester are:",required_courses,"With total units of:",units_sum
        else:
            response=valid, "With total units of:",units_sum
    else:
        response = "You can go ahead to register for all your courses" 
 
    return render_template("next.html", unit=unit,courses=courses, response=response)

def ValuePredictor(to_predict_list, n):
    to_predict = np.array(to_predict_list).reshape(1, n)
    if n == 2:  
        loaded_model = pickle.load(open('CGPA2.sav', 'rb'))
        print("got here")
        
    elif n == 3:
        loaded_model = pickle.load(open("CGPA3.sav", "rb"))
    elif n == 4:
        loaded_model = pickle.load(open("CGPA4.sav", "rb"))
    elif n == 5:
        loaded_model = pickle.load(open("CGPA5.sav", "rb"))
    elif n == 6:
        loaded_model = pickle.load(open("CGPA6.sav", "rb"))
    result = loaded_model.predict(to_predict)
    return result

@app.route('/result', methods=['POST'])
def result():
    if request.method == 'POST':
        to_predict_list = request.form.to_dict()
        to_predict_list = list(to_predict_list.values())
        n= len(to_predict_list)
        result = ValuePredictor(to_predict_list, n)
        test_list = [float(i) for i in to_predict_list]
        former_cpg=test_list[n-1]
        #the grade point of this current semseter.
        cga=(result[0])- (former_cpg)+result[0]
        return render_template("result.html", prediction=to_predict_list, n=n, result=round(result[0],2),  cga=round(cga,2))

@app.route('/addcourse', methods=['GET', 'POST'])
def course():
    if request.method == "POST":
        course_code = request.form['coursecode']
        course_title = request.form['coursetitle']
        part = request.form['part']
        option = request.form['options']
        unit = request.form['unit']
        semester = request.form['semester']
        data = Course(course_code, course_title, part, option, semester, unit)
        db.session.add(data)
        db.session.commit()
        return "done"

    return render_template("courseform.html")


if __name__ == '__main__':
    app.run()
