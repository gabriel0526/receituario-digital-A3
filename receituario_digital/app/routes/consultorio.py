from flask import Blueprint, flash, redirect, render_template, request, url_for
from flask_login import login_required
from sqlalchemy.exc import IntegrityError
from werkzeug.security import generate_password_hash

from .. import db
from ..models import Doctor, Patient, User
from .utils import flash_form_error, parse_date, role_required

consultorio_bp = Blueprint("consultorio", __name__, url_prefix="/consultorio")


@consultorio_bp.route("/medicos")
@login_required
@role_required("consultorio")
def doctors():
    records = Doctor.query.order_by(Doctor.name).all()
    return render_template("consultorio/doctors.html", doctors=records)


@consultorio_bp.route("/medicos/novo", methods=["GET", "POST"])
@login_required
@role_required("consultorio")
def doctor_create():
    if request.method == "POST":
        doctor = Doctor(
            name=request.form["name"].strip(),
            crm=request.form["crm"].strip(),
            specialty=request.form["specialty"].strip(),
            crm_uf=request.form["crm_uf"].strip().upper(),
            digital_certificate=request.form.get("digital_certificate", "").strip() or None,
        )
        user_email = request.form.get("email", "").strip().lower()
        user_password = request.form.get("password", "")
        try:
            db.session.add(doctor)
            db.session.flush()
            if user_email and user_password:
                db.session.add(
                    User(
                        name=doctor.name,
                        email=user_email,
                        password_hash=generate_password_hash(user_password),
                        role="funcionario",
                        doctor_id=doctor.id,
                    )
                )
            db.session.commit()
            flash("Médico cadastrado.", "success")
            return redirect(url_for("consultorio.doctors"))
        except IntegrityError as error:
            db.session.rollback()
            flash_form_error("CRM ou e-mail já cadastrado.")
        except Exception as error:
            db.session.rollback()
            flash_form_error(error)

    return render_template("consultorio/doctor_form.html", doctor=None)


@consultorio_bp.route("/medicos/<int:doctor_id>/editar", methods=["GET", "POST"])
@login_required
@role_required("consultorio")
def doctor_edit(doctor_id):
    doctor = db.get_or_404(Doctor, doctor_id)
    if request.method == "POST":
        doctor.name = request.form["name"].strip()
        doctor.crm = request.form["crm"].strip()
        doctor.specialty = request.form["specialty"].strip()
        doctor.crm_uf = request.form["crm_uf"].strip().upper()
        doctor.digital_certificate = request.form.get("digital_certificate", "").strip() or None
        try:
            db.session.commit()
            flash("Médico atualizado.", "success")
            return redirect(url_for("consultorio.doctors"))
        except IntegrityError:
            db.session.rollback()
            flash_form_error("CRM já cadastrado.")
    return render_template("consultorio/doctor_form.html", doctor=doctor)


@consultorio_bp.route("/medicos/<int:doctor_id>/excluir", methods=["POST"])
@login_required
@role_required("consultorio")
def doctor_delete(doctor_id):
    doctor = db.get_or_404(Doctor, doctor_id)
    if doctor.appointments.count() or doctor.prescriptions.count():
        flash("Não é possível excluir médico com atendimentos ou receitas.", "warning")
        return redirect(url_for("consultorio.doctors"))
    User.query.filter_by(doctor_id=doctor.id).delete()
    db.session.delete(doctor)
    db.session.commit()
    flash("Médico excluído.", "success")
    return redirect(url_for("consultorio.doctors"))


@consultorio_bp.route("/pacientes")
@login_required
@role_required("consultorio")
def patients():
    records = Patient.query.order_by(Patient.full_name).all()
    return render_template("consultorio/patients.html", patients=records)


@consultorio_bp.route("/pacientes/novo", methods=["GET", "POST"])
@login_required
@role_required("consultorio")
def patient_create():
    doctors = Doctor.query.order_by(Doctor.name).all()
    if request.method == "POST":
        patient = Patient(
            full_name=request.form["full_name"].strip(),
            cpf=request.form["cpf"].strip(),
            birth_date=parse_date(request.form["birth_date"]),
            sex=request.form["sex"],
            address=request.form["address"].strip(),
            medical_history=request.form.get("medical_history", "").strip() or None,
            assigned_doctor_id=request.form.get("assigned_doctor_id") or None,
        )
        user_email = request.form.get("email", "").strip().lower()
        user_password = request.form.get("password", "")
        try:
            db.session.add(patient)
            db.session.flush()
            if user_email and user_password:
                db.session.add(
                    User(
                        name=patient.full_name,
                        email=user_email,
                        password_hash=generate_password_hash(user_password),
                        role="paciente",
                        patient_id=patient.id,
                    )
                )
            db.session.commit()
            flash("Paciente cadastrado.", "success")
            return redirect(url_for("consultorio.patients"))
        except IntegrityError:
            db.session.rollback()
            flash_form_error("CPF ou e-mail já cadastrado.")
        except Exception as error:
            db.session.rollback()
            flash_form_error(error)

    return render_template("consultorio/patient_form.html", patient=None, doctors=doctors)


@consultorio_bp.route("/pacientes/<int:patient_id>/editar", methods=["GET", "POST"])
@login_required
@role_required("consultorio")
def patient_edit(patient_id):
    patient = db.get_or_404(Patient, patient_id)
    doctors = Doctor.query.order_by(Doctor.name).all()
    if request.method == "POST":
        patient.full_name = request.form["full_name"].strip()
        patient.cpf = request.form["cpf"].strip()
        patient.birth_date = parse_date(request.form["birth_date"])
        patient.sex = request.form["sex"]
        patient.address = request.form["address"].strip()
        patient.medical_history = request.form.get("medical_history", "").strip() or None
        patient.assigned_doctor_id = request.form.get("assigned_doctor_id") or None
        try:
            db.session.commit()
            flash("Paciente atualizado.", "success")
            return redirect(url_for("consultorio.patients"))
        except IntegrityError:
            db.session.rollback()
            flash_form_error("CPF já cadastrado.")
    return render_template("consultorio/patient_form.html", patient=patient, doctors=doctors)


@consultorio_bp.route("/pacientes/<int:patient_id>/excluir", methods=["POST"])
@login_required
@role_required("consultorio")
def patient_delete(patient_id):
    patient = db.get_or_404(Patient, patient_id)
    User.query.filter_by(patient_id=patient.id).delete()
    db.session.delete(patient)
    db.session.commit()
    flash("Paciente excluído.", "success")
    return redirect(url_for("consultorio.patients"))
