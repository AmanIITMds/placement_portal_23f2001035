from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt, get_jwt_identity
from models.models import db, User, Company, PlacementDrive, Application, Student
from datetime import datetime

company_bp = Blueprint("company", __name__)

def get_company_from_token():
    user_id = get_jwt_identity()
    return Company.query.filter_by(user_id=user_id).first()

def company_required():
    claims = get_jwt()
    return claims.get("role") == "company"


# company profile
@company_bp.route("/profile", methods=["GET"])
@jwt_required()
def get_profile():
    if not company_required():
        return jsonify({"error": "Company access required"}), 403
    company = get_company_from_token()
    if not company:
        return jsonify({"error": "Company profile not found"}), 404
    return jsonify(company.to_dict()), 200


# update company profile
@company_bp.route("/profile", methods=["PUT"])
@jwt_required()
def update_profile():
    if not company_required():
        return jsonify({"error": "Company access required"}), 403
    company = get_company_from_token()
    if not company:
        return jsonify({"error": "Company profile not found"}), 404

    data = request.get_json()
    company.company_name     = data.get("company_name",     company.company_name)
    company.industry         = data.get("industry",         company.industry)
    company.location         = data.get("location",         company.location)
    company.website          = data.get("website",          company.website)
    company.hr_contact_name  = data.get("hr_contact_name",  company.hr_contact_name)
    company.hr_contact_email = data.get("hr_contact_email", company.hr_contact_email)
    company.description      = data.get("description",      company.description)
    db.session.commit()
    return jsonify({"message": "Profile updated successfully"}), 200


# dashboard stats
@company_bp.route("/dashboard", methods=["GET"])
@jwt_required()
def dashboard():
    if not company_required():
        return jsonify({"error": "Company access required"}), 403
    company = get_company_from_token()
    if not company:
        return jsonify({"error": "Company not found"}), 404

    total_drives = PlacementDrive.query.filter_by(company_id=company.id).count()
    total_apps   = Application.query.join(PlacementDrive).filter(
        PlacementDrive.company_id == company.id
    ).count()
    shortlisted  = Application.query.join(PlacementDrive).filter(
        PlacementDrive.company_id == company.id,
        Application.status == "shortlisted"
    ).count()
    selected     = Application.query.join(PlacementDrive).filter(
        PlacementDrive.company_id == company.id,
        Application.status == "selected"
    ).count()

    return jsonify({
        "company":        company.to_dict(),
        "total_drives":   total_drives,
        "total_apps":     total_apps,
        "shortlisted":    shortlisted,
        "selected":       selected
    }), 200


# create a placement drive
@company_bp.route("/drives", methods=["POST"])
@jwt_required()
def create_drive():
    if not company_required():
        return jsonify({"error": "Company access required"}), 403
    company = get_company_from_token()
    if not company:
        return jsonify({"error": "Company not found"}), 404
    if company.approval_status != "approved":
        return jsonify({"error": "Your company must be approved before creating drives"}), 403

    data = request.get_json()
    if not data.get("drive_name") or not data.get("job_title"):
        return jsonify({"error": "Drive name and job title are required"}), 400

    deadline = None
    if data.get("application_deadline"):
        try:
            deadline = datetime.fromisoformat(data["application_deadline"])
        except ValueError:
            return jsonify({"error": "Invalid deadline format"}), 400

    drive = PlacementDrive(
        company_id          = company.id,
        drive_name          = data["drive_name"],
        job_title           = data["job_title"],
        job_description     = data.get("job_description", ""),
        eligibility_branch  = data.get("eligibility_branch", ""),
        eligibility_cgpa    = float(data.get("eligibility_cgpa", 0.0)),
        eligibility_year    = data.get("eligibility_year"),
        salary              = data.get("salary", ""),
        location            = data.get("location", ""),
        application_deadline= deadline,
        interview_type      = data.get("interview_type", "In-person"),
        status              = "pending"
    )
    db.session.add(drive)
    db.session.commit()
    return jsonify({"message": "Drive created and sent for admin approval", "drive": drive.to_dict()}), 201


# get all drives for this company
@company_bp.route("/drives", methods=["GET"])
@jwt_required()
def get_drives():
    if not company_required():
        return jsonify({"error": "Company access required"}), 403
    company = get_company_from_token()
    if not company:
        return jsonify({"error": "Company not found"}), 404

    drives = PlacementDrive.query.filter_by(company_id=company.id).all()
    return jsonify([d.to_dict() for d in drives]), 200


# get applications for a specific drive
@company_bp.route("/drives/<int:drive_id>/applications", methods=["GET"])
@jwt_required()
def get_drive_applications(drive_id):
    if not company_required():
        return jsonify({"error": "Company access required"}), 403
    company = get_company_from_token()
    drive   = PlacementDrive.query.filter_by(id=drive_id, company_id=company.id).first()
    if not drive:
        return jsonify({"error": "Drive not found"}), 404

    applications = Application.query.filter_by(drive_id=drive_id).all()
    result = []
    for app in applications:
        app_dict = app.to_dict()
        if app.student:
            app_dict["student_branch"] = app.student.branch
            app_dict["student_cgpa"]   = app.student.cgpa
            app_dict["student_year"]   = app.student.year
            app_dict["student_phone"]  = app.student.phone
        result.append(app_dict)
    return jsonify(result), 200


# update application status (shortlist, select, reject)
@company_bp.route("/applications/<int:app_id>/status", methods=["PUT"])
@jwt_required()
def update_application_status(app_id):
    if not company_required():
        return jsonify({"error": "Company access required"}), 403

    company = get_company_from_token()
    if not company:
        return jsonify({"error": "Company not found"}), 404

    data = request.get_json()
    status = data.get("status")

    if status not in ["shortlisted", "waiting", "selected", "rejected"]:
        return jsonify({"error": "Invalid status"}), 400

    application = Application.query.get_or_404(app_id)

    # SECURITY CHECK:
    # Verify that the application belongs to a drive owned by this company.
    if (
        not application.drive
        or application.drive.company_id != company.id
    ):
        return jsonify({
            "error": "You are not authorized to update this application."
        }), 403

    application.status = status
    application.remarks = data.get("remarks", application.remarks)

    db.session.commit()

    return jsonify({
        "message": f"Application status updated to {status}"
    }), 200


# schedule interview for a drive
@company_bp.route("/drives/<int:drive_id>/schedule", methods=["PUT"])
@jwt_required()
def schedule_interview(drive_id):
    if not company_required():
        return jsonify({"error": "Company access required"}), 403
    company = get_company_from_token()
    drive   = PlacementDrive.query.filter_by(id=drive_id, company_id=company.id).first()
    if not drive:
        return jsonify({"error": "Drive not found"}), 404

    data = request.get_json()
    if data.get("interview_date"):
        try:
            drive.interview_date = datetime.fromisoformat(data["interview_date"])
        except ValueError:
            return jsonify({"error": "Invalid date format"}), 400
    drive.interview_type = data.get("interview_type", drive.interview_type)
    db.session.commit()
    return jsonify({"message": "Interview scheduled successfully"}), 200