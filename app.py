from flask import Flask, render_template, request
from flask_sqlalchemy import SQLAlchemy
from marshmallow import fields
from marshmallow_sqlalchemy import SQLAlchemyAutoSchema

app = Flask(__name__)
ENV = 'prod'
if ENV == 'dev':
    app.debug = True
    app.config['SQLALCHEMY_DATABASE_URI'] ='postgresql://temi:password@localhost/temidb'
else:
    app.debug = False
    app.config['SQLALCHEMY_DATABASE_URI'] ='postgres://cphmjrvynwjjrr:423e3e2da04142d9be0c841bc15f584f1fb67d620117bc90a144deb78f3d877c@ec2-54-146-84-101.compute-1.amazonaws.com:5432/ddi5051emhns2t'

app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)


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

    def __init__(self, course_code, course_title, level, option,semester, unit):
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
        data=request.form
        GPA=data['gpa']
        part=data['part']
        option = data['options']
        semester = data['semester']
        user_data = Course.query.filter_by(level=part, option=option, semester=semester)
        course_schema = CourseSchema(many=True)
        courses = course_schema.dump(user_data)
        # user_data = Course.query.filter_by(level=part, option=option, semester=semester)
    
        return render_template("next.html", courses = courses) # passes user_data variable into the index.html file.
    return render_template("index.html")
@app.route('/addcourse', methods=['GET', 'POST'])
def course():
    if request.method == "POST":
        course_code = request.form['coursecode']
        course_title = request.form['coursetitle']
        part = request.form['part']
        option = request.form['options']
        unit = request.form['unit']
        semester = request.form['semester'] 
        data = Course(course_code, course_title, part, option, semester,unit)
        db.session.add(data)
        db.session.commit()
        return "done"
    
    return render_template("courseform.html")


if __name__ == '__main__':
    app.run()
