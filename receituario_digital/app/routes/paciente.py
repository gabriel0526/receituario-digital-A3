from flask import Blueprint, render_template
from flask_login import current_user, login_required

from ..models import Appointment, Prescription
from .utils import role_required

paciente_bp = Blueprint("paciente", __name__, url_prefix="/paciente")


@paciente_bp.route("/receitas")
@login_required
@role_required("paciente")
def prescriptions():
    records = (
        Prescription.query.filter_by(patient_id=current_user.patient_id)
        .order_by(Prescription.issued_at.desc())
        .all()
    )
    return render_template("paciente/prescriptions.html", prescriptions=records)


@paciente_bp.route("/atendimentos")
@login_required
@role_required("paciente")
def appointments():
    records = (
        Appointment.query.filter_by(patient_id=current_user.patient_id)
        .order_by(Appointment.appointment_at.desc())
        .all()
    )
    return render_template("paciente/appointments.html", appointments=records)
