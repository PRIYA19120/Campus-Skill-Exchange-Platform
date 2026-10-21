
from datetime import datetime
from database import db


# ==========================================
# STUDENT MODEL
# ==========================================
class Student(db.Model):
    __tablename__ = "students"

    student_id = db.Column(
        db.Integer,
        primary_key=True
    )

    name = db.Column(
        db.String(100),
        nullable=False
    )

    email = db.Column(
        db.String(120),
        unique=True,
        nullable=False
    )

    password = db.Column(
        db.String(255),
        nullable=False
    )

    department = db.Column(
        db.String(100),
        nullable=True
    )

    semester = db.Column(
        db.String(50),
        nullable=True
    )

    bio = db.Column(
        db.Text,
        nullable=True
    )

    # Student ke teaching aur learning skills
    skills = db.relationship(
        "StudentSkill",
        back_populates="student",
        lazy=True,
        cascade="all, delete-orphan"
    )

    # Student dwara bheji gayi requests
    sent_requests = db.relationship(
        "LearningRequest",
        foreign_keys="LearningRequest.student_id",
        back_populates="sender",
        lazy=True
    )

    # Student ko mili requests
    received_requests = db.relationship(
        "LearningRequest",
        foreign_keys="LearningRequest.partner_id",
        back_populates="receiver",
        lazy=True
    )


# ==========================================
# SKILL MODEL
# ==========================================
class Skill(db.Model):
    __tablename__ = "skills"
    skill_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    

    skill_name = db.Column(
        db.String(100),
        unique=True,
        nullable=False
    )

    category = db.Column(
        db.String(100),
        nullable=True
    )

    student_skills = db.relationship(
        "StudentSkill",
        back_populates="skill",
        lazy=True,
        cascade="all, delete-orphan"
    )

    learning_requests = db.relationship(
        "LearningRequest",
        back_populates="skill",
        lazy=True
    )


# ==========================================
# STUDENT SKILL MODEL
# ==========================================
class StudentSkill(db.Model):
    __tablename__ = "student_skills"
    student_skill_id = db.Column(
    db.Integer,
    primary_key=True,
    autoincrement=True
)


    student_id = db.Column(
        db.Integer,
        db.ForeignKey("students.student_id"),
        nullable=False
    )

    skill_id = db.Column(
        db.Integer,
        db.ForeignKey("skills.skill_id"),
        nullable=False
    )

    # teach = student skill sikha sakta hai
    # learn = student skill seekhna chahta hai
    skill_type = db.Column(
        db.String(20),
        nullable=False
    )


    student = db.relationship(
        "Student",
        back_populates="skills"
    )

    skill = db.relationship(
        "Skill",
        back_populates="student_skills"
    )


# ==========================================
# AVAILABILITY MODEL
# ==========================================

class Availability(db.Model):
    __tablename__ = "availability"

    availability_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    student_id = db.Column(
        db.Integer,
        db.ForeignKey("students.student_id"),
        nullable=False
    )
    day_of_week = db.Column(db.String(15), nullable=False)
    start_time = db.Column(db.Time, nullable=False)
    end_time = db.Column(db.Time, nullable=False)

    student = db.relationship(
        "Student",
        backref=db.backref("availability_slots", lazy=True)
    )
# ==========================================
# LEARNING REQUEST MODEL
# ==========================================
class LearningRequest(db.Model):
    __tablename__ = "learning_requests"

    # Unique request ID
    request_id = db.Column(
        db.Integer,
        primary_key=True
    )

    # Request bhejne wala student
    student_id = db.Column(
        db.Integer,
        db.ForeignKey("students.student_id"),
        nullable=False
    )

    # Request receive karne wala student
    partner_id = db.Column(
        db.Integer,
        db.ForeignKey("students.student_id"),
        nullable=False
    )

    # Seekhi jaane wali skill
    skill_id = db.Column(
        db.Integer,
        db.ForeignKey("skills.skill_id"),
        nullable=False
    )

    # Pending, Accepted ya Rejected
    status = db.Column(
        db.String(20),
        nullable=False,
        default="Pending"
    )

    # Request creation date and time
    created_at = db.Column(
        db.DateTime,
        nullable=False,
        default=datetime.utcnow
    )

    # Request sender
    sender = db.relationship(
        "Student",
        foreign_keys=[student_id],
        back_populates="sent_requests"
    )

    # Request receiver
    receiver = db.relationship(
        "Student",
        foreign_keys=[partner_id],
        back_populates="received_requests"
    )

    # Requested skill
    skill = db.relationship(
        "Skill",
        back_populates="learning_requests"
    )

    def __repr__(self):
        return (
            f"<LearningRequest "
            f"request_id={self.request_id}, "
            f"student_id={self.student_id}, "
            f"partner_id={self.partner_id}, "
            f"skill_id={self.skill_id}, "
            f"status={self.status}>"
        )
