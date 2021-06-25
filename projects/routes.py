""" Application routes. """

from flask import current_app as app
from flask import redirect, render_template, request, url_for, flash  # , make_response
# from werkzeug.exceptions import abort
# from werkzeug.utils import secure_filename
import json

from .models import Project, Staff, School, Lab, db


@app.route("/projects", methods=["GET"])
def view_projects():
    """ View all the projects in the database in alphabetical order. """

    projects = Project.query.order_by(Project.name).all()
    return render_template('projects.html', projects=projects)


@app.route("/projects/<int:project_id>", methods=["GET"])
def view_project(project_id):
    """ View a specific project and its info based on its id. """

    project = Project.query(Project.id == project_id).first()
    return render_template("project.html", project=project)


""" --------------------------------- """


@app.route("/getallprojects")
def get_all_projects():
    all_projects = Project.query.all()
    return json.dumps(all_projects)


@app.route("/getallschools")
def get_all_schools():
    all_schools = School.query.all()
    return json.dumps(all_schools)


@app.route("/getallstaff")
def get_all_staff():
    all_staff = Staff.query.all()
    return json.dumps(all_staff)


@app.route("/getalllabs")
def get_all_labs():
    all_labs = Lab.query.all()
    return json.dumps(all_labs)


""" --------------------------------- """


@app.route("/projects/<int:project_id>/edit", methods=("GET", "POST"))
def edit_project(project_id):
    """ Edit project information in the database. """

    project = Project.query(Project.id == project_id).first()

    '''
    all_schools = School.query.all()
    all_staff = Staff.query.all()
    all_labs = Lab.query.all()
    '''

    if request.method == "POST":
        name = request.form["name"]
        start_year = request.form["start_year"]
        end_year = request.form["end_year"]
        schools_json = request.form["schools_json"]
        heads_json = request.form["heads_json"]
        sci_aid_json = request.form["sci_aid_json"]
        org_aid_json = request.form["org_aid_json"]

        school_list = json.loads(schools_json)
        head_list = json.loads(heads_json)
        sci_aid_list = json.loads(org_aid_json)
        org_aid_list = json.loads(sci_aid_json)
        error = None
        if not name:
            error = "Введите название проекта."
        if not start_year and not end_year:
            error = "Введите сроки проекта."
        if not head_list:
            error = "Введите руководителя(ей) проекта."
        if not school_list:
            error = "Выберите учреждения образования, участвующие в проекте."
        if not sci_aid_list:
            error = "Выберите научно-методическое сопровождение проекта."
        if not org_aid_list:
            error = "Выберите организационное сопровождение проекта."
        if error is not None:
            flash(error)
        else:
            project.name = name
            project.start_year = start_year
            project.end_year = end_year
            project.schools = school_list
            project.heads = head_list
            project.org_aid = org_aid_list
            project.sci_aid = sci_aid_list
            db.session.add(project)
            db.session.commit()

        return redirect(url_for(view_project(project_id)))

    return render_template("project_edit.html", project=project)


@app.route("/projects/<int:project_id>/delete", methods=("POST",))
def delete_project(project_id):
    """ Delete a project from the database. """

    project = Project.query(Project.id == project_id).first()
    db.session.delete(project)
    project.applications = []
    project.heads = []
    project.org_aid = []
    project.sci_aid = []
    db.session.commit()

    return redirect(url_for(view_projects))


@app.route("/application", methods=["GET", "POST"])
def import_application():
    """ Import application from a word file. """

    if request.method == 'POST':

        region = request.form['region']
        error = None
        if not region:
            error = "Выберите область."
        if error is not None:
            flash(error)

        '''
        if 'file' not in request.files:
            flash('Загрузите файл заявки.')
            return redirect(request.url)
        
        file = request.files['file']

        if file.filename == '':
            flash('Загрузите файл заявки.')
            return redirect(request.url)

        if file:
            filename = secure_filename(file.filename)
            file.save(filename)
            with open(filename) as f:
                file_text = f.read()
        '''

        # projects_json = request.json
        projects_json = request.form["projects_json"]
        projects = json.loads(projects_json)

        for project in projects:

            new_project = Project(name=project['name'], start_year=project['start_year'], end_year=project['end_year'])

            for school in project['schools']:
                new_school = School(name=school['name'], city=school['city'], district=school['district'],
                                    region=region)
                db.session.add(new_school)
                db.session.commit()
                new_project.applications.append(new_school)

            for head in project['heads']:
                new_staff = Staff(name=head['name'], phone_num=head['phone_num'],
                                  email=head['email'], description=head['description'])
                db.session.add(new_staff)
                db.session.commit()
                new_project.heads.append(new_staff)

            for org_aid in project['org_aid']:
                new_staff = Staff(name=org_aid['name'], phone_num=org_aid['phone_num'],
                                  email=org_aid['email'], description=org_aid['description'])
                db.session.add(new_staff)
                db.session.commit()
                new_project.org_aid.append(new_staff)

            for sci_aid in project['sci_aid']:

                new_staff = Staff(name=sci_aid['head_name'], phone_num=sci_aid['head_phone_num'],
                                  email=sci_aid['head_email'], description=sci_aid['head_description'])
                db.session.add(new_staff)
                db.session.commit()

                new_lab = Lab(name=sci_aid['name'])
                new_lab.head = Staff.query.filter(Staff.name == sci_aid['head_name']).first()
                db.session.add(new_lab)
                db.session.commit()

                new_project.sci_aid.append(new_lab)

            db.session.add(new_project)
            db.session.commit()

        return redirect("app.view_projects")

    return render_template("upload.html")


@app.route("/search", methods=["GET"])
def search_projects():
    """ Filter projects based on other parameters. """

    school_list = []
    head_list = []
    sci_aid_list = []
    org_aid_list = []

    query = ''

    if request.method == "POST":
        name = request.form["name"]
        start_year = request.form["start_year"]
        end_year = request.form["end_year"]
        school_name = request.form["school_name"]
        school_region = request.form["school_region"]
        head_name = request.form["head_name"]
        org_aid_name = request.form["org_aid_name"]
        lab_name = request.form["lab_name"]

        if name:
            query += 'Project.name == name'
        if start_year:
            query += 'Project.start_year == start_year'
        if end_year:
            query += 'Project.end_year == end_year'

    result = Project.query(query).all()

    return render_template('search.html', result=result)


@app.route("/search-result")
def view_search_result(search):
    """ View the results of the search. """

    results = []

    return render_template('result.html', results=results)


"""----------------------------"""


@app.route("/schools", methods=["GET"])
def view_schools():
    """ View all the schools in the database in alphabetical order. """

    schools = School.query.order_by(School.name).all()
    return render_template('schools.html', schools=schools)


@app.route("/schools/<int:school_id>", methods=["GET"])
def view_school(school_id):
    """ View a specific school and its info based on its id. """

    school = School.query(School.id == school_id).first()
    return render_template("school.html", school=school)


@app.route("/schools/<int:school_id>/edit", methods=("GET", "POST"))
def edit_school(school_id):
    """ Edit school information in the database. """

    school = School.query(School.id == school_id).first()
    if request.method == "POST":
        name = request.form["name"]
        city = request.form["city"]
        district = request.form["district"]
        region = request.form["region"]
        error = None
        if not name:
            error = "Введите название учреждения образования."
        if not city:
            error = "Введите населенный пункт учреждения образования."
        if not district:
            error = "Введите район учреждения образования."
        if not region:
            error = "Выберите область учреждения образования."
        if error is not None:
            flash(error)
        else:
            school.name = name
            school.city = city
            school.district = district
            school.region = region
            db.session.add(school)
            db.session.commit()
        return redirect(url_for(view_projects))
    return render_template("school_edit.html", school=school)


@app.route("/schools/<int:school_id>/delete", methods=("POST",))
def delete_school(school_id):
    """ Delete a school from the database. """

    school = School.query(School.id == school_id).first()
    db.session.delete(school)
    school.project = ''
    db.session.commit()

    return redirect(url_for(view_projects))


@app.route("/staff", methods=["GET"])
def view_staff():
    """ View all the staff members in the database in alphabetical order. """

    staff = Staff.query.order_by(Staff.name).all()
    return render_template('staff.html', staff=staff)


@app.route("/staff/<int:staff_id>", methods=["GET"])
def view_staff_member(staff_id):
    """ View a specific staff member and their info based on its id. """

    staff_member = Staff.query(Staff.id == staff_id).first()
    return render_template("staff_member.html", staff_member=staff_member)


@app.route("/staff/<int:staff_id>/edit", methods=("GET", "POST"))
def edit_staff(staff_id):
    """ Edit staff member information in the database. """

    staff = Staff.query(Staff.id == staff_id).first()
    if request.method == "POST":
        name = request.form["name"]
        phone_num = request.form["phone_num"]
        email = request.form["email"]
        description = request.form["description"]
        error = None
        if not name:
            error = "Введите ФИО сотрудника."
        if error is not None:
            flash(error)
        else:
            staff.name = name
            staff.phone_num = phone_num
            staff.email = email
            staff.description = description
            db.session.commit()
        return redirect(url_for(view_staff_member(staff_id)))
    return render_template("edit_staff.html", staff=staff)


@app.route("/staff/<int:staff_id>/delete", methods=("POST",))
def delete_staff(staff_id):
    """ Delete a staff member from the database. """

    staff = Staff.query(Staff.id == staff_id).first()
    db.session.delete(staff)
    staff.project = ''
    staff.lab = ''
    db.session.commit()
    return redirect(url_for(view_projects))


@app.route("/labs", methods=["GET"])
def view_labs():
    """ View all the labs in the database in alphabetical order. """

    labs = Lab.query.order_by(Lab.name).all()
    return render_template('labs.html', labs=labs)


@app.route("/labs/<int:lab_id>", methods=["GET"])
def view_lab(lab_id):
    """ View a specific lab and its info based on its id. """

    lab = Lab.query(Lab.id == lab_id).first()
    return render_template("lab.html", lab=lab)


@app.route("/labs/<int:lab_id>/edit", methods=("GET", "POST"))
def edit_lab(lab_id):
    """ Edit lab information in the database. """

    lab = Lab.query(Lab.id == lab_id).first()
    if request.method == "POST":
        name = request.form["name"]
        last_name = request.form["last_name"]
        error = None
        if not name:
            error = "Введите название лаборатории."
        if not last_name:
            error = "Введите сотрудника лаборатории."
        if error is not None:
            flash(error)
        else:
            lab.name = name
            lab.head = Staff.query(Staff.name == last_name).first()
        db.session.commit()
        return redirect(url_for(view_projects))
    return render_template("edit_lab.html", lab=lab)


@app.route("/labs/<int:lab_id>/delete", methods=("POST",))
def delete_lab(lab_id):
    """ Delete a lab from the database. """

    lab = Lab.query(Lab.id == lab_id).first()
    db.session.delete(lab)
    lab.project = ''
    db.session.commit()
    return redirect(url_for(view_projects))
