from flask_sqlalchemy import SQLAlchemy
from datetime import datetime, timezone

db = SQLAlchemy()

# USER  (unified model for all 3 roles)

class User(db.Model):
    __tablename__ = "users"

    id            = db.Column(db.Integer, primary_key=True)
    username      = db.Column(db.String(80),  unique=True, nullable=False)
    email         = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(256), nullable=False)
    role          = db.Column(db.String(20),  nullable=False)  # 'admin' | 'company' | 'student'
    is_active     = db.Column(db.Boolean, default=True)
    created_at    = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))

    # Relationships
    company_profile = db.relationship("Company", back_populates="user", uselist=False)
    student_profile = db.relationship("Student", back_populates="user", uselist=False)

    def to_dict(self):
        return {
            "id":         self.id,
            "username":   self.username,
            "email":      self.email,
            "role":       self.role,
            "is_active":  self.is_active,
            "created_at": self.created_at.isoformat()
        }


# COMPANY PROFILE

class Company(db.Model):
    __tablename__ = "companies"

    id              = db.Column(db.Integer, primary_key=True)
    user_id         = db.Column(db.Integer, db.ForeignKey("users.id"), unique=True, nullable=False)
    company_name    = db.Column(db.String(150), nullable=False)
    industry        = db.Column(db.String(100))
    location        = db.Column(db.String(100))
    website         = db.Column(db.String(200))
    hr_contact_name = db.Column(db.String(100))
    hr_contact_email= db.Column(db.String(120))
    description     = db.Column(db.Text)
    approval_status = db.Column(db.String(20), default="pending")  # pending | approved | rejected | blacklisted
    created_at      = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))

    # Relationships
    user   = db.relationship("User", back_populates="company_profile")
    drives = db.relationship("PlacementDrive", back_populates="company", cascade="all, delete-orphan")

    def to_dict(self):
        return {
            "id":               self.id,
            "user_id":          self.user_id,
            "company_name":     self.company_name,
            "industry":         self.industry,
            "location":         self.location,
            "website":          self.website,
            "hr_contact_name":  self.hr_contact_name,
            "hr_contact_email": self.hr_contact_email,
            "description":      self.description,
            "approval_status":  self.approval_status,
            "created_at":       self.created_at.isoformat()
        }



# STUDENT PROFILE

class Student(db.Model):
    __tablename__ = "students"

    id          = db.Column(db.Integer, primary_key=True)
    user_id     = db.Column(db.Integer, db.ForeignKey("users.id"), unique=True, nullable=False)
    full_name   = db.Column(db.String(150), nullable=False)
    roll_number = db.Column(db.String(50),  unique=True)
    branch      = db.Column(db.String(100))
    department  = db.Column(db.String(100))
    cgpa        = db.Column(db.Float, default=0.0)
    year        = db.Column(db.Integer)           # current year of study
    skills      = db.Column(db.Text)              # comma-separated
    resume_path = db.Column(db.String(300))       # file path for uploaded resume
    phone       = db.Column(db.String(20))
    is_blacklisted = db.Column(db.Boolean, default=False)
    created_at  = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))

    # Relationships
    user         = db.relationship("User", back_populates="student_profile")
    applications = db.relationship("Application", back_populates="student", cascade="all, delete-orphan")

    def to_dict(self):
        return {
            "id":             self.id,
            "user_id":        self.user_id,
            "full_name":      self.full_name,
            "roll_number":    self.roll_number,
            "branch":         self.branch,
            "department":     self.department,
            "cgpa":           self.cgpa,
            "year":           self.year,
            "skills":         self.skills,
            "resume_path":    self.resume_path,
            "phone":          self.phone,
            "is_blacklisted": self.is_blacklisted,
            "created_at":     self.created_at.isoformat()
        }


# PLACEMENT DRIVE

class PlacementDrive(db.Model):
    __tablename__ = "placement_drives"

    id                  = db.Column(db.Integer, primary_key=True)
    company_id          = db.Column(db.Integer, db.ForeignKey("companies.id"), nullable=False)
    drive_name          = db.Column(db.String(150), nullable=False)
    job_title           = db.Column(db.String(150), nullable=False)
    job_description     = db.Column(db.Text)
    eligibility_branch  = db.Column(db.String(200))  # e.g. "CSE,ECE,IT"
    eligibility_cgpa    = db.Column(db.Float, default=0.0)
    eligibility_year    = db.Column(db.Integer)
    salary              = db.Column(db.String(100))   # e.g. "6 LPA"
    location            = db.Column(db.String(100))
    application_deadline= db.Column(db.DateTime)
    interview_date      = db.Column(db.DateTime, nullable=True)
    interview_type      = db.Column(db.String(50))    # In-person | Online
    status              = db.Column(db.String(20), default="pending")  # pending | approved | closed | rejected
    created_at          = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))

    # Relationships
    company      = db.relationship("Company", back_populates="drives")
    applications = db.relationship("Application", back_populates="drive", cascade="all, delete-orphan")

    def to_dict(self):
        return {
            "id":                   self.id,
            "company_id":           self.company_id,
            "drive_name":           self.drive_name,
            "job_title":            self.job_title,
            "job_description":      self.job_description,
            "eligibility_branch":   self.eligibility_branch,
            "eligibility_cgpa":     self.eligibility_cgpa,
            "eligibility_year":     self.eligibility_year,
            "salary":               self.salary,
            "location":             self.location,
            "application_deadline": self.application_deadline.isoformat() if self.application_deadline else None,
            "interview_date":       self.interview_date.isoformat() if self.interview_date else None,
            "interview_type":       self.interview_type,
            "status":               self.status,
            "created_at":           self.created_at.isoformat(),
            "company_name":         self.company.company_name if self.company else None
        }


# APPLICATION

class Application(db.Model):
    __tablename__ = "applications"

    id           = db.Column(db.Integer, primary_key=True)
    student_id   = db.Column(db.Integer, db.ForeignKey("students.id"), nullable=False)
    drive_id     = db.Column(db.Integer, db.ForeignKey("placement_drives.id"), nullable=False)
    status       = db.Column(db.String(20), default="applied")  # applied | shortlisted | waiting | selected | rejected
    applied_date = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))
    remarks      = db.Column(db.Text)

    # Prevent duplicate applications, one student can apply to a drive only once
    __table_args__ = (
        db.UniqueConstraint("student_id", "drive_id", name="unique_student_drive"),
    )

    # Relationships
    student = db.relationship("Student", back_populates="applications")
    drive   = db.relationship("PlacementDrive", back_populates="applications")

    def to_dict(self):
        return {
            "id":           self.id,
            "student_id":   self.student_id,
            "drive_id":     self.drive_id,
            "status":       self.status,
            "applied_date": self.applied_date.isoformat(),
            "remarks":      self.remarks,
            "drive_name":   self.drive.drive_name if self.drive else None,
            "job_title":    self.drive.job_title if self.drive else None,
            "company_name": self.drive.company.company_name if self.drive and self.drive.company else None,
            "student_name": self.student.full_name if self.student else None
        }
    