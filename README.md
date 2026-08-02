# Placement Portal Application V2 (MAD 2 Project)

## Overview

Placement Portal Application V2 is a multi-user web application designed to streamline campus recruitment activities. It provides a centralized platform where institutes, companies, and students can efficiently manage the complete placement process.

The application is built using **Flask**, **Vue.js**, **SQLite**, **Redis**, and **Celery**, following a role-based architecture with secure authentication and asynchronous task processing.

---

## Features

### User Roles

The application consists of three different user roles:

- Admin (Institute Placement Cell)
- Company
- Student

---

## Admin Module

### Authentication

- Pre-configured admin account
- No registration allowed
- Secure login authentication

### Dashboard

- View total students
- View total companies
- View total placement drives
- View pending approvals

### Company Management

- Approve company registrations
- Reject company registrations
- Blacklist companies
- Blacklisting automatically closes all active placement drives

### Drive Management

- Approve placement drives
- Reject placement drives
- Close active drives manually

### Student Management

- View all registered students
- Blacklist student accounts
- Reactivate student accounts

### Search

- Search companies by company name
- Search students by name
- Search students by roll number

### Application Tracking

- View all student applications across every company and placement drive

---

## Company Module

### Authentication

Registration fields:

- Username
- Email
- Password
- Company Name
- Industry
- Location

Companies can log in only after admin approval.

### Dashboard

- Total placement drives
- Total applications
- Shortlisted candidates
- Selected candidates

### Profile Management

- Company website
- HR contact details
- Company description
- Edit profile

### Placement Drive Management

Create placement drives with:

- Job title
- Job description
- Eligibility branch
- Minimum CGPA
- Eligible year
- Salary package
- Job location
- Application deadline
- Interview type

All drives require admin approval before becoming visible to students.

### Application Management

- View applications received for each drive
- Update application status

Available statuses:

- Shortlisted
- Waiting
- Selected
- Rejected

---

## Student Module

### Authentication

Registration fields:

- Username
- Email
- Password
- Full Name
- Branch
- CGPA
- Year

### Dashboard

- View profile
- Edit profile

Profile fields include:

- Branch
- CGPA
- Skills
- Phone Number
- Roll Number

### Placement Drives

- Browse all approved placement drives
- Search drives by company name
- Search drives by job title

### Applications

- Apply to placement drives
- Automatic eligibility validation
- Branch eligibility validation
- CGPA eligibility validation
- Duplicate applications prevented at database level

### Application Tracking

- View application status
- View placement history
- View selected applications

### CSV Export

- Export complete application history
- Runs asynchronously using Celery
- Completion notification after export

---



Functionality:

- Sends reminders to students about upcoming application deadlines.

### Monthly Placement Report

Schedule:

- First day of every month at **8:00 AM IST**

Functionality:

Generates an HTML report containing:

- Total placement drives
- Total students
- Total applications
- Total selections

Reports are automatically saved inside the `reports/` directory.

### Asynchronous CSV Export

Triggered by:

- Student dashboard

Exports:

- Company name
- Drive title
- Application status
- Application dates

---


## Technology Stack

### Backend

- Flask
- Flask-SQLAlchemy
- Flask-JWT-Extended
- Flask-CORS
- Celery
- Flask-Caching

### Frontend

- Vue.js (CDN)
- Bootstrap 5

### Database

- SQLite

### Caching & Message Broker

- Redis (Memurai)

### Security

- Werkzeug Password Hashing

---

## Authentication & Authorization

The application uses **JWT-based authentication** with **role-based access control (RBAC)**.

Supported roles:

- Admin
- Company
- Student

Each role has access only to its authorized resources and operations.

---

## Project Highlights

- Multi-role authentication system
- Role-based access control using JWT
- Admin approval workflow
- Placement drive management
- Student application tracking
- Automatic eligibility validation
- Duplicate application prevention
- Background task processing using Celery
- Scheduled reminder and reporting jobs
- Redis-based caching
- CSV export through asynchronous processing
- Responsive interface built with Bootstrap and Vue.js

---

## Technologies Used

| Technology | Purpose |
|------------|---------|
| Flask | Backend API development |
| Vue.js (CDN) | Reactive frontend |
| Bootstrap 5 | UI and responsive design |
| Flask-SQLAlchemy | ORM |
| SQLite | Database |
| Flask-JWT-Extended | Authentication and authorization |
| Flask-CORS | Cross-origin resource sharing |
| Redis (Memurai) | Message broker and caching |
| Celery | Background task processing |
| Flask-Caching | API response caching |
| Werkzeug | Password hashing and security |
