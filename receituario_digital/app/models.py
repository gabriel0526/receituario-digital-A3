from datetime import datetime

from flask_login import UserMixin

from . import db


class User(UserMixin, db.Model):
    __tablename__ = "users"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(150), nullable=False)
    email = db.Column(db.String(180), unique=True, nullable=False, index=True)
    password_hash = db.Column(db.String(255), nullable=False)
    role = db.Column(db.Enum("consultorio", "funcionario", "paciente"), nullable=False)
    is_active_account = db.Column(db.Boolean, default=True, nullable=False)
    doctor_id = db.Column(db.Integer, db.ForeignKey("doctors.id"), nullable=True)
    patient_id = db.Column(db.Integer, db.ForeignKey("patients.id"), nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)

    doctor = db.relationship("Doctor", foreign_keys=[doctor_id], post_update=True)
    patient = db.relationship("Patient", foreign_keys=[patient_id], post_update=True)

    @property
    def is_active(self):
        return self.is_active_account


class Doctor(db.Model):
    __tablename__ = "doctors"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(150), nullable=False)
    crm = db.Column(db.String(30), nullable=False, unique=True)
    specialty = db.Column(db.String(120), nullable=False)
    crm_uf = db.Column(db.String(2), nullable=False)
    digital_certificate = db.Column(db.String(255), nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)

    patients = db.relationship("Patient", back_populates="assigned_doctor", lazy="dynamic")
    appointments = db.relationship("Appointment", back_populates="doctor", lazy="dynamic")
    prescriptions = db.relationship("Prescription", back_populates="doctor", lazy="dynamic")


class Patient(db.Model):
    __tablename__ = "patients"

    id = db.Column(db.Integer, primary_key=True)
    full_name = db.Column(db.String(180), nullable=False)
    cpf = db.Column(db.String(14), nullable=False, unique=True)
    birth_date = db.Column(db.Date, nullable=False)
    sex = db.Column(db.Enum("Feminino", "Masculino", "Outro", "Não informado"), nullable=False)
    address = db.Column(db.String(255), nullable=False)
    medical_history = db.Column(db.Text, nullable=True)
    assigned_doctor_id = db.Column(db.Integer, db.ForeignKey("doctors.id"), nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)

    assigned_doctor = db.relationship("Doctor", back_populates="patients", foreign_keys=[assigned_doctor_id])
    appointments = db.relationship("Appointment", back_populates="patient", cascade="all, delete-orphan")
    prescriptions = db.relationship("Prescription", back_populates="patient", cascade="all, delete-orphan")


class Medication(db.Model):
    __tablename__ = "medications"

    id = db.Column(db.Integer, primary_key=True)
    commercial_name = db.Column(db.String(150), nullable=False)
    active_ingredient = db.Column(db.String(150), nullable=False)
    dosage = db.Column(db.String(80), nullable=False)
    pharmaceutical_form = db.Column(db.String(100), nullable=False)
    control_category = db.Column(db.String(120), nullable=False)
    prescription_issuance = db.Column(db.String(120), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)

    prescriptions = db.relationship("Prescription", back_populates="medication", lazy="dynamic")


class Appointment(db.Model):
    __tablename__ = "appointments"

    id = db.Column(db.Integer, primary_key=True)
    patient_id = db.Column(db.Integer, db.ForeignKey("patients.id"), nullable=False)
    doctor_id = db.Column(db.Integer, db.ForeignKey("doctors.id"), nullable=False)
    appointment_at = db.Column(db.DateTime, nullable=False)
    clinic_name = db.Column(db.String(150), nullable=False)
    notes = db.Column(db.Text, nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)

    patient = db.relationship("Patient", back_populates="appointments")
    doctor = db.relationship("Doctor", back_populates="appointments")
    prescriptions = db.relationship("Prescription", back_populates="appointment")


class Prescription(db.Model):
    __tablename__ = "prescriptions"

    id = db.Column(db.Integer, primary_key=True)
    patient_id = db.Column(db.Integer, db.ForeignKey("patients.id"), nullable=False)
    doctor_id = db.Column(db.Integer, db.ForeignKey("doctors.id"), nullable=False)
    appointment_id = db.Column(db.Integer, db.ForeignKey("appointments.id"), nullable=True)
    clinic_name = db.Column(db.String(150), nullable=False)
    medication_id = db.Column(db.Integer, db.ForeignKey("medications.id"), nullable=False)
    dosage = db.Column(db.String(80), nullable=False)
    frequency = db.Column(db.String(100), nullable=False)
    treatment_duration = db.Column(db.String(100), nullable=False)
    observations = db.Column(db.Text, nullable=True)
    issued_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)

    patient = db.relationship("Patient", back_populates="prescriptions")
    doctor = db.relationship("Doctor", back_populates="prescriptions")
    appointment = db.relationship("Appointment", back_populates="prescriptions")
    medication = db.relationship("Medication", back_populates="prescriptions")
