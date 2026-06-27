from flask import Blueprint, request, jsonify, current_app
from flask_jwt_extended import jwt_required, get_jwt
from models.models import db, User, Student, Company, PlacementDrive, Application

admin_bp = Blueprint("admin", __name__)

def admin_required():
    claims = get_jwt()
    return claims.get("role") == "admin"


# dashboard stats
@admin_bp.route("/dashboard", methods=["GET"])
@jwt_required()
def dashboard():
    if not admin_required():
        return jsonify({"error": "Admin access required"}), 403

    total_students  = Student.query.count()
    total_companies = Company.query.count()
    total_drives    = PlacementDrive.query.count()
    total_apps      = Application.query.count()
    pending_companies = Company.query.filter_by(approval_status="pending").count()

    return jsonify({
        "total_students":      total_students,
        "total_companies":     total_companies,
        "total_drives":        total_drives,
        "total_applications":  total_apps,
        "pending_companies":   pending_companies
    }), 200


# get all companies
@admin_bp.route("/companies", methods=["GET"])
@jwt_required()
def get_companies():
    if not admin_required():
        return jsonify({"error": "Admin access required"}), 403

    search    = request.args.get("search", "")
    cache_key = f"companies_search_{search}"
    cache     = current_app.extensions["ppa_cache"]

    cached = cache.get(cache_key)
    if cached is not None:
        return jsonify(cached), 200

    query = Company.query
    if search:
        query = query.filter(Company.company_name.ilike(f"%{search}%"))

    companies = query.all()
    result    = [c.to_dict() for c in companies]
    cache.set(cache_key, result, timeout=60)
    return jsonify(result), 200


# approve or reject company
@admin_bp.route("/companies/<int:company_id>/status", methods=["PUT"])
@jwt_required()
def update_company_status(company_id):
    if not admin_required():
        return jsonify({"error": "Admin access required"}), 403

    data    = request.get_json()
    status  = data.get("status")
    if status not in ["approved", "rejected", "blacklisted", "pending"]:
        return jsonify({"error": "Invalid status"}), 400

    company = Company.query.get_or_404(company_id)
    company.approval_status = status

    # if blacklisted cancel all drives
    if status == "blacklisted":
        for drive in company.drives:
            drive.status = "closed"

    db.session.commit()

    cache = current_app.extensions["ppa_cache"]
    cache.clear()

    return jsonify({"message": f"Company status updated to {status}"}), 200


# get all students
@admin_bp.route("/students", methods=["GET"])
@jwt_required()
def get_students():
    if not admin_required():
        return jsonify({"error": "Admin access required"}), 403

    search    = request.args.get("search", "")
    cache_key = f"students_search_{search}"
    cache     = current_app.extensions["ppa_cache"]

    cached = cache.get(cache_key)
    if cached is not None:
        return jsonify(cached), 200

    query = Student.query
    if search:
        query = query.filter(
            (Student.full_name.ilike(f"%{search}%")) |
            (Student.roll_number.ilike(f"%{search}%"))
        )

    students = query.all()
    result   = [s.to_dict() for s in students]
    cache.set(cache_key, result, timeout=60)
    return jsonify(result), 200

# blacklist or activate student
@admin_bp.route("/students/<int:student_id>/status", methods=["PUT"])
@jwt_required()
def update_student_status(student_id):
    if not admin_required():
        return jsonify({"error": "Admin access required"}), 403

    data    = request.get_json()
    action  = data.get("action")
    student = Student.query.get_or_404(student_id)
    user    = User.query.get(student.user_id)

    if action == "blacklist":
        student.is_blacklisted = True
        user.is_active         = False
    elif action == "activate":
        student.is_blacklisted = False
        user.is_active         = True
    else:
        return jsonify({"error": "Invalid action"}), 400

    db.session.commit()

    cache = current_app.extensions["ppa_cache"]
    cache.clear()

    return jsonify({"message": f"Student {action}d successfully"}), 200


# get all drives
@admin_bp.route("/drives", methods=["GET"])
@jwt_required()
def get_drives():
    if not admin_required():
        return jsonify({"error": "Admin access required"}), 403

    drives = PlacementDrive.query.all()
    return jsonify([d.to_dict() for d in drives]), 200


# approve or reject drive
@admin_bp.route("/drives/<int:drive_id>/status", methods=["PUT"])
@jwt_required()
def update_drive_status(drive_id):
    if not admin_required():
        return jsonify({"error": "Admin access required"}), 403

    data   = request.get_json()
    status = data.get("status")
    if status not in ["approved", "rejected", "closed", "pending"]:
        return jsonify({"error": "Invalid status"}), 400

    drive        = PlacementDrive.query.get_or_404(drive_id)
    drive.status = status
    db.session.commit()

    cache = current_app.extensions["ppa_cache"]
    cache.clear()

    return jsonify({"message": f"Drive status updated to {status}"}), 200


# get all applications
@admin_bp.route("/applications", methods=["GET"])
@jwt_required()
def get_applications():
    if not admin_required():
        return jsonify({"error": "Admin access required"}), 403

    applications = Application.query.all()
    return jsonify([a.to_dict() for a in applications]), 200