CREATE DATABASE IF NOT EXISTS clinic_booking CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
USE clinic_booking;

CREATE TABLE IF NOT EXISTS doctors (
  id INT AUTO_INCREMENT PRIMARY KEY,
  full_name VARCHAR(150) NOT NULL,
  specialty VARCHAR(120) NOT NULL,
  is_active TINYINT(1) NOT NULL DEFAULT 1
);

CREATE TABLE IF NOT EXISTS services (
  id INT AUTO_INCREMENT PRIMARY KEY,
  service_name VARCHAR(150) NOT NULL,
  duration_minutes INT NOT NULL,
  is_active TINYINT(1) NOT NULL DEFAULT 1
);

CREATE TABLE IF NOT EXISTS appointments (
  id INT AUTO_INCREMENT PRIMARY KEY,
  patient_name VARCHAR(150) NOT NULL,
  phone VARCHAR(30) NOT NULL,
  doctor_id INT NOT NULL,
  service_id INT NOT NULL,
  appointment_at DATETIME NOT NULL,
  notes TEXT NULL,
  status ENUM('pending', 'confirmed', 'completed', 'cancelled') NOT NULL DEFAULT 'pending',
  created_at DATETIME NOT NULL,
  CONSTRAINT fk_appointments_doctor FOREIGN KEY (doctor_id) REFERENCES doctors(id),
  CONSTRAINT fk_appointments_service FOREIGN KEY (service_id) REFERENCES services(id)
);

INSERT INTO doctors (full_name, specialty) VALUES
('د. أحمد سالم', 'باطنة'),
('د. سارة علي', 'جلدية');

INSERT INTO services (service_name, duration_minutes) VALUES
('كشف عادي', 30),
('متابعة', 20),
('استشارة سريعة', 15);
