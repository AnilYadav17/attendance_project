-- Attendance Management System Schema
CREATE DATABASE IF NOT EXISTS attendance_db;
USE attendance_db;
-- Users Table (Extending Django Auth)
CREATE TABLE IF NOT EXISTS attendance_project_user (
    id BIGINT AUTO_INCREMENT PRIMARY KEY,
    password VARCHAR(128) NOT NULL,
    last_login DATETIME(6),
    is_superuser TINYINT(1) NOT NULL,
    username VARCHAR(150) NOT NULL UNIQUE,
    first_name VARCHAR(150) NOT NULL,
    last_name VARCHAR(150) NOT NULL,
    email VARCHAR(254) NOT NULL,
    is_staff TINYINT(1) NOT NULL,
    is_active TINYINT(1) NOT NULL,
    date_joined DATETIME(6) NOT NULL,
    is_student TINYINT(1) NOT NULL DEFAULT 0,
    is_teacher TINYINT(1) NOT NULL DEFAULT 0
);
-- Batch Table
CREATE TABLE IF NOT EXISTS attendance_project_batch (
    id BIGINT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(50) NOT NULL UNIQUE,
    year INT NOT NULL
);
-- Subject Table
CREATE TABLE IF NOT EXISTS attendance_project_subject (
    id BIGINT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    code VARCHAR(20) NOT NULL UNIQUE,
    batch_id BIGINT NOT NULL,
    FOREIGN KEY (batch_id) REFERENCES attendance_project_batch(id)
);
-- Student Table
CREATE TABLE IF NOT EXISTS attendance_project_student (
    id BIGINT AUTO_INCREMENT PRIMARY KEY,
    roll_number VARCHAR(20) NOT NULL UNIQUE,
    user_id BIGINT NOT NULL UNIQUE,
    batch_id BIGINT,
    FOREIGN KEY (user_id) REFERENCES attendance_project_user(id),
    FOREIGN KEY (batch_id) REFERENCES attendance_project_batch(id)
);
-- Teacher Table
CREATE TABLE IF NOT EXISTS attendance_project_teacher (
    id BIGINT AUTO_INCREMENT PRIMARY KEY,
    user_id BIGINT NOT NULL UNIQUE,
    FOREIGN KEY (user_id) REFERENCES attendance_project_user(id)
);
-- Teacher-Subject Many-to-Many
CREATE TABLE IF NOT EXISTS attendance_project_teacher_subjects (
    id BIGINT AUTO_INCREMENT PRIMARY KEY,
    teacher_id BIGINT NOT NULL,
    subject_id BIGINT NOT NULL,
    FOREIGN KEY (teacher_id) REFERENCES attendance_project_teacher(id),
    FOREIGN KEY (subject_id) REFERENCES attendance_project_subject(id)
);
-- Attendance Session Table
CREATE TABLE IF NOT EXISTS attendance_project_attendancesession (
    id BIGINT AUTO_INCREMENT PRIMARY KEY,
    session_id CHAR(32) NOT NULL UNIQUE,
    -- UUID
    start_time DATETIME(6) NOT NULL,
    end_time DATETIME(6),
    is_active TINYINT(1) NOT NULL DEFAULT 1,
    teacher_id BIGINT NOT NULL,
    subject_id BIGINT NOT NULL,
    batch_id BIGINT NOT NULL,
    FOREIGN KEY (teacher_id) REFERENCES attendance_project_teacher(id),
    FOREIGN KEY (subject_id) REFERENCES attendance_project_subject(id),
    FOREIGN KEY (batch_id) REFERENCES attendance_project_batch(id)
);
-- Attendance Record Table
CREATE TABLE IF NOT EXISTS attendance_project_attendancerecord (
    id BIGINT AUTO_INCREMENT PRIMARY KEY,
    timestamp DATETIME(6) NOT NULL,
    status VARCHAR(10) NOT NULL DEFAULT 'Present',
    session_id BIGINT NOT NULL,
    student_id BIGINT NOT NULL,
    FOREIGN KEY (session_id) REFERENCES attendance_project_attendancesession(id),
    FOREIGN KEY (student_id) REFERENCES attendance_project_student(id),
    UNIQUE KEY unique_attendance (session_id, student_id)
);
-- Audit Log Table
CREATE TABLE IF NOT EXISTS attendance_project_auditlog (
    id BIGINT AUTO_INCREMENT PRIMARY KEY,
    action VARCHAR(255) NOT NULL,
    timestamp DATETIME(6) NOT NULL,
    details LONGTEXT,
    user_id BIGINT,
    FOREIGN KEY (user_id) REFERENCES attendance_project_user(id)
);