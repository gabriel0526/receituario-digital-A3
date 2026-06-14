from flask import Blueprint, render_template
from flask_login import login_required, current_user

from ..models import Appointment, Doctor, Medication, Patient, Prescription

shared_bp = Blueprint("shared", __name__)


@shared_bp.route("/dashboard")
@login_required
def dashboard():
    if current_user.role == "consultorio":
        stats = {
            "doctors": Doctor.query.count(),
            "patients": Patient.query.count(),
            "medications": Medication.query.count(),
            "appointments": Appointment.query.count(),
            "prescriptions": Prescription.query.count(),
        }
        return render_template("consultorio/dashboard.html", stats=stats)

    if current_user.role == "funcionario":
        doctor_id = current_user.doctor_id
        stats = {
            "patients": Patient.query.filter_by(assigned_doctor_id=doctor_id).count(),
            "appointments": Appointment.query.filter_by(doctor_id=doctor_id).count(),
            "prescriptions": Prescription.query.filter_by(doctor_id=doctor_id).count(),
        }
        return render_template("funcionario/dashboard.html", stats=stats)

    stats = {
        "appointments": Appointment.query.filter_by(patient_id=current_user.patient_id).count(),
        "prescriptions": Prescription.query.filter_by(patient_id=current_user.patient_id).count(),
    }
    return render_template("paciente/dashboard.html", stats=stats)
