from celery import Celery
from celery.schedules import crontab
from datetime import datetime, timedelta
import csv
import io
import os

celery = Celery("placement_portal")
celery.conf.broker_url = "redis://localhost:6379/0"
celery.conf.result_backend = "redis://localhost:6379/0"

celery.conf.beat_schedule = {
    "daily-deadline-reminder": {
        "task": "tasks.jobs.send_deadline_reminders",
        "schedule": crontab(hour=9, minute=0),
    },
    "monthly-placement-report": {
        "task": "tasks.jobs.generate_monthly_report",
        "schedule": crontab(day_of_month=1, hour=8, minute=0),
    },
}
celery.conf.timezone = "Asia/Kolkata"


@celery.task(name="tasks.jobs.send_deadline_reminders")
def send_deadline_reminders():
    from app import create_app
    from models.models import db, Student, PlacementDrive, Application

    app = create_app()
    with app.app_context():
        tomorrow = datetime.now() + timedelta(days=1)
        upcoming_drives = PlacementDrive.query.filter(
            PlacementDrive.status == "approved",
            PlacementDrive.application_deadline <= tomorrow,
            PlacementDrive.application_deadline >= datetime.now()
        ).all()

        reminder_log = []
        for drive in upcoming_drives:
            students = Student.query.filter_by(is_blacklisted=False).all()
            for student in students:
                already_applied = Application.query.filter_by(
                    student_id=student.id, drive_id=drive.id
                ).first()
                if not already_applied:
                    message = (
                        f"Reminder: Deadline for {drive.job_title} at "
                        f"{drive.company.company_name} is tomorrow."
                    )
                    reminder_log.append({
                        "student": student.full_name,
                        "drive": drive.drive_name,
                        "message": message
                    })

        print(f"Sent {len(reminder_log)} reminders")
        return {"reminders_sent": len(reminder_log)}


@celery.task(name="tasks.jobs.generate_monthly_report")
def generate_monthly_report():
    from app import create_app
    from models.models import db, Student, Company, PlacementDrive, Application

    app = create_app()
    with app.app_context():
        total_drives   = PlacementDrive.query.count()
        total_students = Student.query.filter_by(is_blacklisted=False).count()
        total_applied  = Application.query.count()
        total_selected = Application.query.filter_by(status="selected").count()

        html_report = f"""
        <html>
        <body>
        <h2>Monthly Placement Activity Report</h2>
        <p>Report generated on: {datetime.now().strftime('%Y-%m-%d')}</p>
        <table border="1" cellpadding="8">
            <tr><th>Metric</th><th>Count</th></tr>
            <tr><td>Total Drives Conducted</td><td>{total_drives}</td></tr>
            <tr><td>Total Active Students</td><td>{total_students}</td></tr>
            <tr><td>Total Applications</td><td>{total_applied}</td></tr>
            <tr><td>Total Students Selected</td><td>{total_selected}</td></tr>
        </table>
        </body>
        </html>
        """

        reports_dir = os.path.join(os.path.dirname(__file__), "..", "reports")
        os.makedirs(reports_dir, exist_ok=True)
        report_path = os.path.join(reports_dir, f"report_{datetime.now().strftime('%Y_%m')}.html")
        with open(report_path, "w") as f:
            f.write(html_report)

        print(f"Monthly report generated at {report_path}")
        return {"report_path": report_path}


@celery.task(name="tasks.jobs.export_applications_csv")
def export_applications_csv(student_id):
    from app import create_app
    from models.models import db, Student, Application

    app = create_app()
    with app.app_context():
        student      = Student.query.get(student_id)
        applications = Application.query.filter_by(student_id=student_id).all()

        exports_dir = os.path.join(os.path.dirname(__file__), "..", "uploads", "exports")
        os.makedirs(exports_dir, exist_ok=True)

        filename  = f"applications_{student_id}_{datetime.now().strftime('%Y%m%d%H%M%S')}.csv"
        file_path = os.path.join(exports_dir, filename)

        with open(file_path, "w", newline="") as csvfile:
            writer = csv.writer(csvfile)
            writer.writerow(["Student ID", "Company Name", "Drive Title", "Application Status", "Applied Date"])
            for app_record in applications:
                writer.writerow([
                    student_id,
                    app_record.drive.company.company_name if app_record.drive else "",
                    app_record.drive.job_title if app_record.drive else "",
                    app_record.status,
                    app_record.applied_date.strftime("%Y-%m-%d")
                ])

        print(f"CSV export completed: {filename}")
        return {"filename": filename, "path": file_path}