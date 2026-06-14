from datetime import datetime

from flask import Blueprint, flash, redirect, render_template, request, url_for
from flask_login import current_user, login_required
from sqlalchemy.exc import IntegrityError

from .. import db
from ..models import Appointment, Doctor, Medication, Patient, Prescription
from .utils import flash_form_error, parse_datetime_local, role_required

funcionario_bp = Blueprint("funcionario", __name__, url_prefix="/funcionario")


def current_doctor():
    return db.session.get(Doctor, current_user.doctor_id)


def doctor_patients_query():
    return Patient.query.filter_by(assigned_doctor_id=current_user.doctor_id).order_by(Patient.full_name)


@funcionario_bp.route("/medicamentos")
@login_required
@role_required("consultorio", "funcionario")
def medications():
    records = Medication.query.order_by(Medication.commercial_name).all()
    return render_template("shared/medications.html", medications=records)


@funcionario_bp.route("/medicamentos/novo", methods=["GET", "POST"])
@login_required
@role_required("consultorio", "funcionario")
def medication_create():
    if request.method == "POST":
        medication = Medication(
            commercial_name=request.form["commercial_name"].strip(),
            active_ingredient=request.form["active_ingredient"].strip(),
            dosage=request.form["dosage"].strip(),
            pharmaceutical_form=request.form["pharmaceutical_form"].strip(),
            control_category=request.form["control_category"].strip(),
            prescription_issuance=request.form["prescription_issuance"].strip(),
        )
        db.session.add(medication)
        db.session.commit()
        flash("Medicamento cadastrado.", "success")
        return redirect(url_for("funcionario.medications"))
    return render_template("shared/medication_form.html", medication=None)


@funcionario_bp.route("/medicamentos/<int:medication_id>/editar", methods=["GET", "POST"])
@login_required
@role_required("consultorio", "funcionario")
def medication_edit(medication_id):
    medication = db.get_or_404(Medication, medication_id)
    if request.method == "POST":
        medication.commercial_name = request.form["commercial_name"].strip()
        medication.active_ingredient = request.form["active_ingredient"].strip()
        medication.dosage = request.form["dosage"].strip()
        medication.pharmaceutical_form = request.form["pharmaceutical_form"].strip()
        medication.control_category = request.form["control_category"].strip()
        medication.prescription_issuance = request.form["prescription_issuance"].strip()
        db.session.commit()
        flash("Medicamento atualizado.", "success")
        return redirect(url_for("funcionario.medications"))
    return render_template("shared/medication_form.html", medication=medication)


@funcionario_bp.route("/medicamentos/<int:medication_id>/excluir", methods=["POST"])
@login_required
@role_required("consultorio", "funcionario")
def medication_delete(medication_id):
    medication = db.get_or_404(Medication, medication_id)
    if medication.prescriptions.count():
        flash("Não é possível excluir medicamento usado em receitas.", "warning")
        return redirect(url_for("funcionario.medications"))
    db.session.delete(medication)
    db.session.commit()
    flash("Medicamento excluído.", "success")
    return redirect(url_for("funcionario.medications"))


@funcionario_bp.route("/atendimentos")
@login_required
@role_required("funcionario")
def appointments():
    records = (
        Appointment.query.filter_by(doctor_id=current_user.doctor_id)
        .order_by(Appointment.appointment_at.desc())
        .all()
    )
    return render_template("funcionario/appointments.html", appointments=records)


@funcionario_bp.route("/atendimentos/novo", methods=["GET", "POST"])
@login_required
@role_required("funcionario")
def appointment_create():
    patients = doctor_patients_query().all()
    if request.method == "POST":
        appointment = Appointment(
            patient_id=request.form["patient_id"],
            doctor_id=current_user.doctor_id,
            appointment_at=parse_datetime_local(request.form["appointment_at"]),
            clinic_name=request.form["clinic_name"].strip(),
            notes=request.form.get("notes", "").strip() or None,
        )
        db.session.add(appointment)
        db.session.commit()
        flash("Atendimento registrado.", "success")
        return redirect(url_for("funcionario.appointments"))
    return render_template("funcionario/appointment_form.html", appointment=None, patients=patients)


@funcionario_bp.route("/atendimentos/<int:appointment_id>/editar", methods=["GET", "POST"])
@login_required
@role_required("funcionario")
def appointment_edit(appointment_id):
    appointment = Appointment.query.filter_by(id=appointment_id, doctor_id=current_user.doctor_id).first_or_404()
    patients = doctor_patients_query().all()
    if request.method == "POST":
        appointment.patient_id = request.form["patient_id"]
        appointment.appointment_at = parse_datetime_local(request.form["appointment_at"])
        appointment.clinic_name = request.form["clinic_name"].strip()
        appointment.notes = request.form.get("notes", "").strip() or None
        db.session.commit()
        flash("Atendimento atualizado.", "success")
        return redirect(url_for("funcionario.appointments"))
    return render_template("funcionario/appointment_form.html", appointment=appointment, patients=patients)


@funcionario_bp.route("/atendimentos/<int:appointment_id>/excluir", methods=["POST"])
@login_required
@role_required("funcionario")
def appointment_delete(appointment_id):
    appointment = Appointment.query.filter_by(id=appointment_id, doctor_id=current_user.doctor_id).first_or_404()
    if appointment.prescriptions:
        flash("Não é possível excluir atendimento com receita vinculada.", "warning")
        return redirect(url_for("funcionario.appointments"))
    db.session.delete(appointment)
    db.session.commit()
    flash("Atendimento excluído.", "success")
    return redirect(url_for("funcionario.appointments"))


@funcionario_bp.route("/receitas")
@login_required
@role_required("funcionario")
def prescriptions():
    records = (
        Prescription.query.filter_by(doctor_id=current_user.doctor_id)
        .order_by(Prescription.issued_at.desc())
        .all()
    )
    return render_template("funcionario/prescriptions.html", prescriptions=records)


@funcionario_bp.route("/receitas/nova", methods=["GET", "POST"])
@login_required
@role_required("funcionario")
def prescription_create():
    doctor = current_doctor()
    patients = doctor_patients_query().all()
    medications = Medication.query.order_by(Medication.commercial_name).all()
    appointments = (
        Appointment.query.filter_by(doctor_id=current_user.doctor_id)
        .order_by(Appointment.appointment_at.desc())
        .all()
    )

    if request.method == "POST":
        try:
            appointment_id = request.form.get("appointment_id") or None
            appointment = None
            if appointment_id:
                appointment = Appointment.query.filter_by(
                    id=appointment_id,
                    doctor_id=current_user.doctor_id,
                ).first_or_404()
            else:
                appointment = Appointment(
                    patient_id=request.form["patient_id"],
                    doctor_id=current_user.doctor_id,
                    appointment_at=parse_datetime_local(request.form["appointment_at"]),
                    clinic_name=request.form["clinic_name"].strip(),
                    notes=request.form.get("appointment_notes", "").strip() or None,
                )
                db.session.add(appointment)
                db.session.flush()

            prescription = Prescription(
                patient_id=appointment.patient_id,
                doctor_id=current_user.doctor_id,
                appointment_id=appointment.id,
                clinic_name=appointment.clinic_name,
                medication_id=request.form["medication_id"],
                dosage=request.form["dosage"].strip(),
                frequency=request.form["frequency"].strip(),
                treatment_duration=request.form["treatment_duration"].strip(),
                observations=request.form.get("observations", "").strip() or None,
                issued_at=datetime.utcnow(),
            )
            db.session.add(prescription)
            db.session.commit()
            flash("Receita emitida.", "success")
            return redirect(url_for("funcionario.prescriptions"))
        except (IntegrityError, ValueError) as error:
            db.session.rollback()
            flash_form_error(error)

    return render_template(
        "funcionario/prescription_form.html",
        doctor=doctor,
        patients=patients,
        medications=medications,
        appointments=appointments,
    )


@funcionario_bp.route("/relatorios")
@login_required
@role_required("funcionario")
def reports():
    start = request.args.get("start")
    end = request.args.get("end")

    appointments_query = Appointment.query.filter_by(doctor_id=current_user.doctor_id)
    prescriptions_query = Prescription.query.filter_by(doctor_id=current_user.doctor_id)

    if start:
        start_dt = datetime.strptime(start, "%Y-%m-%d")
        appointments_query = appointments_query.filter(Appointment.appointment_at >= start_dt)
        prescriptions_query = prescriptions_query.filter(Prescription.issued_at >= start_dt)
    if end:
        end_dt = datetime.strptime(end, "%Y-%m-%d").replace(hour=23, minute=59, second=59)
        appointments_query = appointments_query.filter(Appointment.appointment_at <= end_dt)
        prescriptions_query = prescriptions_query.filter(Prescription.issued_at <= end_dt)

    appointments = appointments_query.order_by(Appointment.appointment_at.desc()).all()
    prescriptions = prescriptions_query.order_by(Prescription.issued_at.desc()).all()
    return render_template(
        "funcionario/reports.html",
        appointments=appointments,
        prescriptions=prescriptions,
        start=start,
        end=end,
    )
