from flask import Blueprint, request, jsonify
from werkzeug.security import generate_password_hash, check_password_hash
from flask_jwt_extended import create_access_token, jwt_required, get_jwt_identity
from models.models import db, User, Student, Company

auth_bp = Blueprint("auth", __name__)


# ─────────────────────────────────────────
# REGISTER
# ─────────────────────────────────────────
@auth_bp.route("/register", methods=["POST"])
def register():
    data = request.get_json()

    # Validate required fields
    required = ["username", "email", "password", "role"]
    for field in required:
        if not data.get(field):
            return jsonify({"error": f"{field} is required"}), 400

    role = data["role"]
    if role not in ["student", "company"]:
        return jsonify({"error": "Role must be student or company"}), 400

    # Check duplicates
    if User.query.filter_by(username=data["username"]).first():
        return jsonify({"error": "Username already taken"}), 409
    if User.query.filter_by(email=data["email"]).first():
        return jsonify({"error": "Email already registered"}), 409

    # Create user
    user = User(
        username      = data["username"],
        email         = data["email"],
        password_hash = generate_password_hash(data["password"]),
        role          = role
    )
    db.session.add(user)
    db.session.flush()  # get user.id before commit

    # Create role-specific profile
    if role == "student":
        student = Student(
            user_id   = user.id,
            full_name = data.get("full_name", data["username"]),
            branch    = data.get("branch", ""),
            cgpa      = float(data.get("cgpa", 0.0)),
            year      = int(data.get("year", 1)),
            phone     = data.get("phone", "")
        )
        db.session.add(student)

    elif role == "company":
        company = Company(
            user_id         = user.id,
            company_name    = data.get("company_name", data["username"]),
            industry        = data.get("industry", ""),
            location        = data.get("location", ""),
            website         = data.get("website", ""),
            hr_contact_name = data.get("hr_contact_name", ""),
            hr_contact_email= data.get("hr_contact_email", data["email"]),
            approval_status = "pending"
        )
        db.session.add(company)

    db.session.commit()
    return jsonify({"message": f"{role.capitalize()} registered successfully!"}), 201


# ─────────────────────────────────────────
# LOGIN
# ─────────────────────────────────────────
@auth_bp.route("/login", methods=["POST"])
def login():
    data = request.get_json()

    if not data.get("username") or not data.get("password"):
        return jsonify({"error": "Username and password required"}), 400

    user = User.query.filter_by(username=data["username"]).first()

    if not user or not check_password_hash(user.password_hash, data["password"]):
        return jsonify({"error": "Invalid username or password"}), 401

    if not user.is_active:
        return jsonify({"error": "Your account has been deactivated"}), 403

    # Build extra info to send back
    extra = {}
    if user.role == "company":
        company = Company.query.filter_by(user_id=user.id).first()
        if company:
            extra["approval_status"] = company.approval_status
            extra["company_id"]      = company.id
            if company.approval_status != "approved":
                messages = {
                 "pending": "Your company registration is pending admin approval.",
                 "rejected": "Your company registration has been rejected.",
                 "blacklisted": "Your company has been blacklisted."
                }

                return jsonify({
                    "error": messages.get(
                        company.approval_status,
                        "Company account is not approved."
                    )
                }), 403

    if user.role == "student":
        student = Student.query.filter_by(user_id=user.id).first()
        if student:
            extra["student_id"]     = student.id
            extra["is_blacklisted"] = student.is_blacklisted
            if student.is_blacklisted:
                return jsonify({"error": "Your account has been blacklisted"}), 403

    # Create JWT token
    access_token = create_access_token(
        identity=str(user.id),
        additional_claims={"role": user.role, "username": user.username}
    )

    return jsonify({
        "access_token": access_token,
        "role":         user.role,
        "username":     user.username,
        "user_id":      user.id,
        **extra
    }), 200


# ─────────────────────────────────────────
# GET CURRENT USER (protected route test)
# ─────────────────────────────────────────
@auth_bp.route("/me", methods=["GET"])
@jwt_required()
def me():
    user_id = get_jwt_identity()
    user    = User.query.get(user_id)
    if not user:
        return jsonify({"error": "User not found"}), 404
    return jsonify(user.to_dict()), 200
