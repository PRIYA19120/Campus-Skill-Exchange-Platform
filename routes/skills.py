from flask import Blueprint, request
from database import db
from models import Skill

skills_bp = Blueprint("skills", __name__, url_prefix="/api/skills")


@skills_bp.route("/", methods=["GET"])
def get_skills():
    skills = Skill.query.all()

    return {
        "skills": [
            {
                "skill_id": skill.skill_id,
                "skill_name": skill.skill_name
            }
            for skill in skills
        ]
    }, 200