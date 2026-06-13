from flask import Blueprint, request, jsonify, send_from_directory
from flask_jwt_extended import jwt_required, get_jwt, get_jwt_identity
from models.models import db, User, Student, PlacementDrive, Application, Company
from werkzeug.security import generate_password_hash
import os

student_bp = Blueprint("student", __name__)

def get_student_from_token():
    user_id = get_jwt_identity()
    return Student.query.filter_by(user_id=user_id).first()

def student_required():
    claims = get_jwt()
    return claims.get("role") == "student"


# student profile
@student_bp.route("/profile", methods=["GET"])
@jwt_required()
def get_profile():
    if not student_required():
        return jsonify({"error": "Student access required"}), 403
    student = get_student_from_token()
    if not student:
        return jsonify({"error": "Student profile not found"}), 404
    return jsonify(student.to_dict()), 200


# update student profile
@student_bp.route("/profile", methods=["PUT"])
@jwt_required()
def update_profile():
    if not student_required():
        return jsonify({"error": "Student access required"}), 403
    student = get_student_from_token()
    if not student:
        return jsonify({"error": "Student profile not found"}), 404

    data = request.get_json()
    student.full_name   = data.get("full_name",   student.full_name)
    student.branch      = data.get("branch",      student.branch)
    student.department  = data.get("department",  student.department)
    student.cgpa        = float(data.get("cgpa",  student.cgpa))
    student.year        = int(data.get("year",    student.year or 1))
    student.skills      = data.get("skills",      student.skills)
    student.phone       = data.get("phone",       student.phone)
    student.roll_number = data.get("roll_number", student.roll_number)
    db.session.commit()
    return jsonify({"message": "Profile updated successfully"}), 200


# get all approved drives (with optional search)
@student_bp.route("/drives", methods=["GET"])
@jwt_required()
def get_drives():
    if not student_required():
        return jsonify({"error": "Student access required"}), 403

    search = request.args.get("search", "")
    query  = PlacementDrive.query.filter_by(status="approved")

    if search:
        query = query.join(Company).filter(
            (PlacementDrive.job_title.ilike(f"%{search}%")) |
            (PlacementDrive.drive_name.ilike(f"%{search}%")) |
            (Company.company_name.ilike(f"%{search}%"))
        )

    drives = query.all()
    student = get_student_from_token()

    result = []
    for drive in drives:
        d = drive.to_dict()
        # check if student already applied
        existing = Application.query.filter_by(
            student_id=student.id,
            drive_id=drive.id
        ).first()
        d["already_applied"] = existing is not None
        d["application_status"] = existing.status if existing else None
        result.append(d)

    return jsonify(result), 200


# apply to a drive
@student_bp.route("/drives/<int:drive_id>/apply", methods=["POST"])
@jwt_required()
def apply_to_drive(drive_id):
    if not student_required():
        return jsonify({"error": "Student access required"}), 403

    student = get_student_from_token()
    if not student:
        return jsonify({"error": "Student profile not found"}), 404

    if student.is_blacklisted:
        return jsonify({"error": "Your account is blacklisted"}), 403

    drive = PlacementDrive.query.get_or_404(drive_id)

    if drive.status != "approved":
        return jsonify({"error": "This drive is not open for applications"}), 400

    # check duplicate application
    existing = Application.query.filter_by(
        student_id=student.id,
        drive_id=drive_id
    ).first()
    if existing:
        return jsonify({"error": "You have already applied to this drive"}), 409

    # eligibility check
    if drive.eligibility_cgpa and student.cgpa < drive.eligibility_cgpa:
        return jsonify({
            "error": f"You do not meet the minimum CGPA requirement of {drive.eligibility_cgpa}"
        }), 400

    if drive.eligibility_branch and drive.eligibility_branch.strip().lower() not in ["all", "any", ""]:
        allowed_branches = [b.strip().lower() for b in drive.eligibility_branch.split(",")]
        if student.branch and student.branch.lower() not in allowed_branches:
            return jsonify({
                "error": f"Your branch is not eligible. Allowed: {drive.eligibility_branch}"
            }), 400

    application = Application(
        student_id=student.id,
        drive_id=drive_id,
        status="applied"
    )
    db.session.add(application)
    db.session.commit()
    return jsonify({"message": "Application submitted successfully"}), 201


# get student's own applications
@student_bp.route("/applications", methods=["GET"])
@jwt_required()
def get_applications():
    if not student_required():
        return jsonify({"error": "Student access required"}), 403

    student      = get_student_from_token()
    applications = Application.query.filter_by(student_id=student.id).all()
    return jsonify([a.to_dict() for a in applications]), 200


# dashboard stats
@student_bp.route("/dashboard", methods=["GET"])
@jwt_required()
def dashboard():
    if not student_required():
        return jsonify({"error": "Student access required"}), 403

    student      = get_student_from_token()
    total_apps   = Application.query.filter_by(student_id=student.id).count()
    shortlisted  = Application.query.filter_by(student_id=student.id, status="shortlisted").count()
    selected     = Application.query.filter_by(student_id=student.id, status="selected").count()
    rejected     = Application.query.filter_by(student_id=student.id, status="rejected").count()
    total_drives = PlacementDrive.query.filter_by(status="approved").count()

    return jsonify({
        "student":       student.to_dict(),
        "total_apps":    total_apps,
        "shortlisted":   shortlisted,
        "selected":      selected,
        "rejected":      rejected,
        "total_drives":  total_drives
    }), 200
