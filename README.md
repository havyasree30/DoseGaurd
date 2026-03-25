
# DoseGuard – Smart Medicine Reminder & Stock Tracker

## Overview
DoseGuard is a web-based application designed to help patients (especially elderly individuals and those with chronic illnesses) manage their medication schedules effectively.
The system allows users to:
- Track medicines
- Receive reminders for doses
- Log medication intake
- Monitor medicine stock
- Enable caregivers to track adherence

## Problem Statement
Medication non-adherence is a serious issue due to:
- Forgetting doses
- Complex schedules
- Lack of monitoring
- Running out of medicines

DoseGuard solves this by introducing:
- Reminder-based tracking
- Caregiver monitoring
- Stock management

## Target Users
### Primary Users
- Elderly individuals
- Chronic illness patients
### Secondary Users
- Caregivers
- Family members

## Features
### 🔐 User Management
- User Registration
- Login / Logout
- Role-based access (Patient / Caregiver)
### Medicine Management
- Add medicines
- Edit medicines
- Delete medicines
- View medicine list
### Dose Scheduling
- Set reminder times
- View daily schedule
- Mark doses as taken
### Tracking & Monitoring
- Dose history
- Missed dose alerts
- Low stock alerts

## Tech Stack
### Frontend
- HTML5
- CSS3
- Bootstrap
- JavaScript
- jQuery
### Backend
- Python
- Flask
### Database
- SQLite / MySQL

## Project Structure
doseguard/
│
├── app.py
├── config.py
├── database.sql
├── requirements.txt
│
├── templates/
│ ├── base.html
│ ├── index.html
│ ├── login.html
│ ├── register.html
│ └── dashboard.html
│ └── add_medicine.html
│ └── edit_medicine.html
│ └── history.html
│ └── medicines.html
│ └── profile.html
│ └── schedule.html
│ └── stock.html
│
├── static/
│ ├── css/
│ ├── js/
│ └── images/


To make further changes or develeop further, one can close this repository. Create a virtual environment in python.
Then install all the requirements using pip install -r requirements.txt
Make changes
Then run the app. Open it in any browser.
