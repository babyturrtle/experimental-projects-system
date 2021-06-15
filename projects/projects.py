import pymysql
from app import app
from app import db
from flask import flash
from flask import render_template
from flask import request
from flask import redirect
from flask import url_for
from werkzeug.exceptions import abort

connection = db.connect()
cursor = connection.cursor(pymysql.cursors.DictCursor)


""" 
Fragment functions 
"""


def get_project(project_id):
    """ Get a project from the database. """

    cursor.execute(
        "SELECT projects.id, projects.name, projects.start_year, projects.end_year"
        " FROM projects"
        " WHERE projects.id = ?",
        (project_id,),
    )
    project = cursor.fetchone()

    if project is None:
        abort(404, "Проект №{0} не находится в базе данных.".format(project_id))

    return project


def get_project_schools(project_id):
    """ Get a list of schools relating to a specific project in the database. """

    cursor.execute(
        "SELECT schools.id, schools.name"
        " FROM project_school"
        " INNER JOIN projects on projects.id = project_school.project_id"
        " INNER JOIN schools on schools.id = project_school.school_id"
        " WHERE projects.id = ?",
        (project_id,),
    )
    schools = cursor.fetchall()

    if schools is None:
        abort(404, "Учреждения образования не связаны с проектом №{0} в базе данных.".format(project_id))

    return schools


def get_project_heads(project_id):
    """ Get a list of heads of a specific project in the database. """

    cursor.execute(
        "SELECT staff.id, staff.last_name, staff.first_name, staff.patronymic, staff.description"
        " FROM project_staff"
        " INNER JOIN projects on projects.id = project_staff.project_id"
        " INNER JOIN staff on staff.id = project_staff.head_id"
        " WHERE project_staff.relationship = 'руководитель'"
        " AND projects.id = ?",
        (project_id,),
    )
    heads = cursor.fetchall()

    if heads is None:
        abort(404, "Руководители не связаны с проектом №{0} в базе данных.".format(project_id))

    return heads


def get_project_sci_aid(project_id):
    """ Get a list of labs relating to a specific project in the database. """

    cursor.execute(
        "SELECT labs.id, labs.name"
        " FROM sci_aid"
        " INNER JOIN projects on projects.id = sci_aid.project_id"
        " INNER JOIN labs on labs.id = sci_aid.lab_id"
        " WHERE projects.id = ?",
        (project_id,),
    )
    sci_aid = cursor.fetchall()

    if sci_aid is None:
        abort(404, "Лаборатории не связаны с проектом №{0} в базе данных.".format(project_id))

    return sci_aid


def get_project_org_aid(project_id):
    """ Get a list of organizational aid staff members relating to a specific project in the database. """

    cursor.execute(
        "SELECT staff.id, staff.last_name, staff.first_name, staff.patronymic"
        " FROM project_staff"
        " INNER JOIN projects on projects.id = project_staff.project_id"
        " INNER JOIN staff on staff.id = project_staff.head_id"
        " WHERE project_staff.relationship = 'сопровождение'"
        " AND projects.id = ?",
        (project_id,),
    )
    org_aid = cursor.fetchall()

    if org_aid is None:
        abort(404, "Организационное сопровождение не связано с проектом №{0} в базе данных.".format(project_id))

    return org_aid


def get_staff_member(staff_id):
    """ Get a staff member from the database. """

    cursor.execute(
        "SELECT id, last_name, first_name, patronymic, description"
        " FROM staff"
        " WHERE staff.id = ?",
        (staff_id,),
    )
    staff_member = cursor.fetchone()

    if staff_member is None:
        abort(404, "Сотрудник №{0} не находится в базе данных.".format(staff_id))

    return staff_member


def get_lab(lab_id):
    """ Get a lab from the database. """

    cursor. execute(
        "SELECT labs.id, labs.name, labs.head_id, staff.last_name, staff.first_name, staff.patronimic"
        " FROM labs"
        " INNER JOIN staff ON labs.head_id = staff.id"
        " WHERE labs.id = ?",
        (lab_id,),
    )
    lab = cursor.fetchone()

    if lab is None:
        abort(404, "Лаборатория №{0} не находится в базе данных.".format(lab_id))

    return lab


def get_school(school_id):
    """ Get a school from the database. """

    cursor.execute(
        "SELECT id, type, name, city, region"
        " FROM schools"
        " WHERE schools.id = ?",
        (school_id,),
    )
    school = cursor.fetchone()

    if school is None:
        abort(404, "Учреждение образования №{0} не находится в базе данных.".format(school_id))

    return school


""" 
View functions 
"""


@app.route("/")
def index():
    """ View the main page. """

    return render_template("index.html")


# 1. PROJECTS

@app.route("/projects")
def view_projects():
    """ View all the projects in the database in alphabetical order. """

    cursor.execute(
        "SELECT id, name, start_year, end_year FROM projects"
    )
    projects = cursor.fetchall()

    return render_template("projects.html", projects=projects)


@app.route("/projects/<int:project_id>")
def view_project(project_id):
    """ View a specific project and its info based on its id. """

    project = get_project(project_id)
    schools = get_project_schools(project_id)
    heads = get_project_heads(project_id)
    sci_aid = get_project_sci_aid(project_id)
    org_aid = get_project_org_aid(project_id)

    return render_template("project.html", project=project, schools=schools, heads=heads, sci_aid=sci_aid, org_aid=org_aid)


@app.route("/projects/<int:project_id>/edit", methods=("GET", "POST"))
def edit_project(project_id):
    """ Edit project information in the database. """

    project = get_project(project_id)
    if request.method == "POST":
        name = request.form["name"]
        start_year = request.form["start_year"]
        end_year = request.form["end_year"]

        error = None
        if not name:
            error = "Введите название проекта."
        if not start_year and not end_year:
            error = "Введите сроки проекта."
        if error is not None:
            flash(error)
        else:
            cursor.execute(
                "UPDATE projects SET name = ?, start_year = ?, end_year = ?"
                " WHERE projects.id = ?",
                (name, start_year, end_year, project_id)
            )
        db.connection.commit()
        return redirect(url_for(view_project(project_id)))
    return render_template("edit_project.html", project=project)


@app.route("/add_project", methods=("GET", "POST"))
def add_project():
    """ Add a new project to the database. """

    if request.method == "POST":
        name = request.form["name"]
        start_year = request.form["start_year"]
        end_year = request.form["end_year"]
        schools = request.form["schools"]
        sci_aid = request.form["sci_aid"]
        org_aid = request.form["org_aid"]
        heads = request.form["org_aid"]
        error = None
        if not name:
            error = "Введите название проекта."
        if not start_year and not end_year:
            error = "Введите сроки проекта."
        if not heads:
            error = "Введите руководителя(ей) проекта."
        if not schools:
            error = "Выберите учреждения образования, участвующие в проекте."
        if not sci_aid:
            error = "Выберите научно-методическое сопровождение проекта."
        if not org_aid:
            error = "Выберите организационное сопровождение проекта."
        if error is not None:
            flash(error)
        else:
            cursor.execute(
                "INSERT OR IGNORE INTO projects (name, start_year, end_year)"
                " VALUES (?, ?, ?)",
                (name, start_year, end_year),
            )
            db.connection.commit()

            project_id = cursor.lastrowid

            # Руководители
            head_id_list = []
            for head in heads:
                head_id_tuple = cursor.execute(
                    "SELECT id FROM staff"
                    " WHERE last_name = ?",
                    (head,),
                ).fetchone()
                head_id = head_id_tuple[0]
                head_id_list.append(head_id)

            for head_id in head_id_list:
                cursor.execute(
                    "INSERT OR IGNORE INTO project_staff (project_id, head_id, relationship)"
                    " VALUES (?, ?, ?)",
                    (project_id, head_id, "Руководитель")
                )
                db.connection.commit()

            # Организационное сопровождение
            cursor.execute(
                "INSERT OR IGNORE INTO project_staff (project_id, head_id, relationship)"
                " VALUES (?, ?, ?)",
                (project_id, org_id, "Сопровождение")
            )
            db.connection.commit()

            # Учреждения образования
            cursor.execute(
                "INSERT OR IGNORE INTO project_school (project_id, school_id)"
                " VALUES (?, ?)",
                (project_id, school_id)
            )
            db.connection.commit()

            # Научно-методическое сопровождение
            cursor.execute(
                "INSERT OR IGNORE INTO sci_aid (project_id, lab_id)"
                " VALUES (?, ?)",
                (project_id, lab_id)
            )
            db.connection.commit()

        return redirect(url_for(index()))
    return render_template("add_project.html")


@app.route("/projects/<int:project_id>/delete", methods=("POST",))
def delete_project(project_id):
    """ Delete a project from the database. """

    get_project(project_id)

    cursor.execute(
        "DELETE FROM projects WHERE id = ?",
        (project_id,)
    )
    cursor.execute(
        "DELETE FROM project_staff WHERE project_id = ?",
        (project_id,)
    )
    cursor.execute(
        "DELETE FROM project_school WHERE project_id = ?",
        (project_id,)
    )
    cursor.execute(
        "DELETE FROM sci_aid WHERE project_id = ?",
        (project_id,)
    )

    db.connection.commit()
    return redirect(url_for(index()))


# 2. STAFF

@app.route("/staff")
def view_staff():
    """ View all the staff members in the database in alphabetical order. """

    cursor.execute(
        "SELECT id, last_name, first_name, patronymic, description"
        " FROM staff"
        " ORDER BY last_name;"
    )
    staff = cursor.fetchall()

    return render_template("staff.html", staff=staff)


@app.route("/staff/<int:staff_id>/")
def view_staff_member(staff_id):
    """ View a specific staff member and their info in the database. """

    staff_member = get_staff_member(staff_id)
    return render_template("staff_member.html", staff_member=staff_member)


@app.route("/staff/<int:staff_id>/edit", methods=("GET", "POST"))
def edit_staff(staff_id):
    """ Edit staff member information in the database. """

    staff_member = get_staff_member(staff_id)
    if request.method == "POST":
        last_name = request.form["last_name"]
        first_name = request.form["first_name"]
        patronymic = request.form["patronymic"]
        description = request.form["description"]
        error = None
        if not last_name:
            error = "Введите фамилию сотрудника."
        if not first_name:
            error = "Введите имя сотрудника."
        if not patronymic:
            error = "Введите отчество сотрудника."
        if error is not None:
            flash(error)
        else:
            cursor.execute(
                " UPDATE staff SET last_name = ?, first_name = ?, patronymic = ?, description = ?"
                " WHERE staff.id = ?",
                (last_name, first_name, patronymic, description, staff_id)
            )
        db.connection.commit()
        return redirect(url_for(view_staff_member(staff_id)))
    return render_template("edit_staff.html", staff_member=staff_member)


@app.route("/add_staff", methods=("GET", "POST"))
def add_staff():
    """ Add a new staff member to the database. """

    if request.method == "POST":
        last_name = request.form["last_name"]
        first_name = request.form["first_name"]
        patronymic = request.form["patronymic"]
        description = request.form["description"]
        error = None
        if not last_name:
            error = "Введите фамилию сотрудника."
        if not first_name:
            error = "Введите имя сотрудника."
        if not patronymic:
            error = "Введите отчество сотрудника."
        if error is not None:
            flash(error)
        else:
            cursor.execute(
                "INSERT OR IGNORE INTO staff (last_name, first_name, patronymic, description)"
                " VALUES (?, ?, ?, ?)",
                (last_name, first_name, patronymic, description),
            )
        db.connection.commit()
        return redirect(url_for(index()))
    return render_template("add_staff.html")


@app.route("/staff/<int:staff_id>/delete", methods=("POST",))
def delete_staff(staff_id):
    """ Delete a staff member from the database. """

    get_staff_member(staff_id)

    cursor.execute(
        "DELETE FROM staff WHERE id = ?",
        (staff_id,)
    )
    cursor.execute(
        "DELETE FROM labs WHERE head_id = ?",
        (staff_id,)
    )
    cursor.execute(
        "DELETE FROM project_staff WHERE head_id = ?",
        (staff_id,)
    )

    db.connection.commit()
    return redirect(url_for(index()))


# 3. LABS

@app.route("/labs")
def view_labs():
    """ View all the labs in the database in alphabetical order. """

    cursor.execute(
        "SELECT labs.id, labs.name, labs.head_id, staff.last_name, staff.first_name, staff.patronymic"
        " FROM labs"
        " INNER JOIN staff ON labs.head_id = staff.id"
        " ORDER BY labs.name;"
    )
    labs = cursor.fetchall()

    return render_template("labs.html", labs=labs)


@app.route("/labs/<int:lab_id>/")
def view_lab(lab_id):
    """ View a specific lab and its info in the database. """

    lab = get_lab(lab_id)
    return render_template("lab.html", lab=lab)


@app.route("/labs/<int:lab_id>/edit", methods=("GET", "POST"))
def edit_lab(lab_id):
    """ Edit lab information in the database. """

    lab = get_lab(lab_id)
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
            cursor.execute(
                "SELECT staff.id"
                " FROM staff"
                " WHERE staff.last_name = ?",
                (last_name,),
            )
            staff_id = cursor.fetchone()
            for i in staff_id:
                cursor.execute(
                    "UPDATE labs SET name = ?, head_id = ?"
                    " WHERE labs.id = ?",
                    (name, i, lab_id),
                )
        db.connection.commit()
        return redirect(url_for(index()))
    return render_template("edit_lab.html", lab=lab)


@app.route("/add_lab", methods=("GET", "POST"))
def add_lab():
    """ Add a new lab to the database. """

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
            cursor.execute(
                "SELECT staff.id"
                " FROM staff"
                " WHERE staff.last_name = ?",
                (last_name,),
            )
            staff_id = cursor.fetchone()
            for i in staff_id:
                cursor.execute(
                    "INSERT OR IGNORE INTO labs (name, head_id)"
                    " VALUES (?, ?)",
                    (name, i),
                )
        db.connection.commit()
        return redirect(url_for(index()))
    return render_template("add_lab.html")


@app.route("/labs/<int:lab_id>/delete", methods=("POST",))
def delete_lab(lab_id):
    """ Delete a lab from the database. """

    get_lab(lab_id)

    cursor.execute(
        "DELETE FROM labs WHERE id = ?",
        (lab_id,)
    )
    cursor.execute(
        "DELETE FROM sci_aid WHERE lab_id = ?",
        (lab_id,)
    )

    db.connection.commit()
    return redirect(url_for(index()))


# 4. SCHOOLS

@app.route("/schools")
def view_schools():
    """ View all the schools in the database in alphabetical order. """

    cursor.execute(
        "SELECT id, name"
        " FROM schools"
        " ORDER BY name;"
    )
    schools = cursor.fetchall()

    return render_template("schools.html", schools=schools)


@app.route("/schools/<int:school_id>/")
def view_school(school_id):
    """ View a specific school and its info in the database. """

    school = get_school(school_id)
    return render_template("school.html", school=school)


@app.route("/schools/<int:school_id>/edit", methods=("GET", "POST"))
def edit_school(school_id):
    """ Edit school information in the database. """

    school = get_school(school_id)
    if request.method == "POST":
        school_type = request.form["school_type"]
        name = request.form["name"]
        city = request.form["city"]
        region = request.form["region"]
        error = None
        if not school_type:
            error = "Выберите тип учреждения образования."
        if not name:
            error = "Введите название учреждения образования."
        if not city:
            error = "Введите населенный пункт учреждения образования."
        if not region:
            error = "Выберите область учреждения образования."
        if error is not None:
            flash(error)
        else:
            cursor.execute(
                "UPDATE schools SET school_type = ?, name = ?, city = ?, region = ?"
                " WHERE id = ?",
                (school_type, name, city, region, school_id),
            )
        db.connection.commit()
        return redirect(url_for(index()))
    return render_template("edit_school.html", school=school)


@app.route("/add_school", methods=("GET", "POST"))
def add_school():
    """ Add a new school to the database. """

    if request.method == "POST":
        school_type = request.form["school_type"]
        name = request.form["name"]
        city = request.form["city"]
        region = request.form["region"]
        error = None
        if not school_type:
            error = "Выберите тип учреждения образования."
        if not name:
            error = "Введите название учреждения образования."
        if not city:
            error = "Введите населенный пункт учреждения образования."
        if not region:
            error = "Выберите область учреждения образования."
        if error is not None:
            flash(error)
        else:
            cursor.execute(
                "INSERT OR IGNORE INTO schools (school_type, name, city, region)"
                " VALUES (?, ?, ?, ?)",
                (school_type, name, city, region),
            )
        db.connection.commit()
        return redirect(url_for(index()))
    return render_template("add_school.html")


@app.route("/schools/<int:school_id>/delete", methods=("POST",))
def delete_school(school_id):
    """ Delete a school from the database. """

    get_school(school_id)

    cursor.execute(
        "DELETE FROM schools WHERE id = ?",
        (school_id,)
    )
    cursor.execute(
        "DELETE FROM project_school WHERE school_id = ?",
        (school_id,)
    )

    db.connection.commit()
    return redirect(url_for(index()))


""" 
Search functions 
"""


""" 
File+Folder functions 
"""
