""" Data models. """

from . import db


class Project(db.Model):
    """ Data model for experimental projects. """

    __tablename__ = 'projects'
    id = db.Column(db.Integer(), primary_key=True)
    name = db.Column(db.String(500), unique=True, nullable=False)
    start_year = db.Column(db.String(7), unique=False, nullable=False)
    end_year = db.Column(db.String(7), unique=False, nullable=False)
    schools = db.relationship('School', secondary=schools, lazy='subquery',
                              backref=db.backref('project', lazy=True))
    heads = db.relationship('Staff', secondary=heads, lazy='subquery',
                            backref=db.backref('project', lazy=True))
    org_aid = db.relationship('Staff', secondary=org_aid, lazy='subquery',
                              backref=db.backref('project', lazy=True))
    sci_aid = db.relationship('Lab', secondary=sci_aid, lazy='subquery',
                              backref=db.backref('project', lazy=True))

    def __repr__(self):
        return "<Project {}: {}>".format(self.id, self.name)


class Staff(db.Model):
    """ Data model for staff members. """

    __tablename__ = 'staff'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(200), unique=True, nullable=False)
    phone_num = db.Column(db.String(20), unique=False, nullable=False)
    email = db.Column(db.String(120), unique=False, nullable=False)
    description = db.Column(db.String(1000), unique=False, nullable=True)
    lab = db.relationship('Lab', backref='head', uselist=False)

    def __repr__(self):
        return "<Staff member {}: {}>".format(self.id, self.name)


class School(db.Model):
    """ Data model for schools participating in projects. """

    __tablename__ = 'schools'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(500), unique=True, nullable=False)
    city = db.Column(db.String(100), unique=False, nullable=False)
    district = db.Column(db.String(100), unique=False, nullable=False)
    region = db.Column(db.String(50), unique=False, nullable=False)

    def __repr__(self):
        return "<School {}: {}>".format(self.id, self.name)


class Lab(db.Model):
    """ Data model for scientific laboratories. """

    __tablename__ = 'labs'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(500), unique=True, nullable=False)
    staff_id = db.Column(db.Integer, db.ForeignKey('staff.id'))

    def __repr__(self):
        return "<Lab {}: {}>".format(self.id, self.name)


schools = db.Table(
    db.Column('project_id', db.Integer, db.ForeignKey('projects.id'), primary_key=True),
    db.Column('school_id', db.Integer, db.ForeignKey('schools.id'), primary_key=True)
)


heads = db.Table(
    db.Column('project_id', db.Integer, db.ForeignKey('projects.id'), primary_key=True),
    db.Column('staff_id', db.Integer, db.ForeignKey('staff.id'), primary_key=True)
)


org_aid = db.Table(
    db.Column('project_id', db.Integer, db.ForeignKey('projects.id'), primary_key=True),
    db.Column('staff_id', db.Integer, db.ForeignKey('staff.id'), primary_key=True)
)


sci_aid = db.Table(
    db.Column('project_id', db.Integer, db.ForeignKey('projects.id'), primary_key=True),
    db.Column('lab_id', db.Integer, db.ForeignKey('labs.id'), primary_key=True)
)