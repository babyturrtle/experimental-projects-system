CREATE DATABASE IF NOT EXISTS experimental_projects;
USE experimental_projects;

CREATE TABLE schools (
  id int PRIMARY KEY AUTO_INCREMENT,
  school_type varchar(255) NOT NULL,
  name varchar(255) NOT NULL,
  city varchar(255) NOT NULL,
  region varchar(255) NOT NULL
);

CREATE TABLE staff (
  id int PRIMARY KEY AUTO_INCREMENT,
  last_name varchar(255) NOT NULL,
  first_name varchar(255) NOT NULL,
  patronymic varchar(255) NOT NULL,
  description varchar(255)
);

CREATE TABLE projects (
  id int PRIMARY KEY AUTO_INCREMENT,
  name varchar(255) NOT NULL,
  start_year varchar(255) NOT NULL,
  end_year varchar(255) NOT NULL
);

CREATE TABLE project_staff (
  id int PRIMARY KEY AUTO_INCREMENT,
  project_id int NOT NULL,
  head_id int NOT NULL,
  relationship varchar(255) NOT NULL
);

CREATE TABLE project_school (
  id int PRIMARY KEY AUTO_INCREMENT,
  project_id int NOT NULL,
  school_id int NOT NULL
);

CREATE TABLE sci_aid (
  id int PRIMARY KEY AUTO_INCREMENT,
  project_id int NOT NULL,
  lab_id int NOT NULL
);

CREATE TABLE labs (
  id int PRIMARY KEY AUTO_INCREMENT,
  name varchar(255) NOT NULL,
  head_id int NOT NULL
);

ALTER TABLE projects ADD FOREIGN KEY (id) REFERENCES project_staff (project_id);

ALTER TABLE staff ADD FOREIGN KEY (id) REFERENCES project_staff (head_id);

ALTER TABLE projects ADD FOREIGN KEY (id) REFERENCES project_school (project_id);

ALTER TABLE schools ADD FOREIGN KEY (id) REFERENCES project_school (school_id);

ALTER TABLE projects ADD FOREIGN KEY (id) REFERENCES sci_aid (project_id);

ALTER TABLE labs ADD FOREIGN KEY (id) REFERENCES sci_aid (lab_id);

ALTER TABLE labs ADD FOREIGN KEY (head_id) REFERENCES staff (id);
