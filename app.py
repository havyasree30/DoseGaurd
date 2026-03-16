from flask import Flask, render_template, request, redirect, url_for, session, flash
from config import Config
from database import db, User, Medicine, Schedule, Dose, Stock
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime, date

app = Flask(__name__)
app.config.from_object(Config)

db.init_app(app)

with app.app_context():
    db.create_all()

# Helper function
def is_logged_in():
    return 'user_id' in session

@app.route('/')
def index():
    if is_logged_in():
        return redirect(url_for('dashboard'))
    return render_template('index.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    if is_logged_in():
        return redirect(url_for('dashboard'))

    if request.method == 'POST':
        full_name = request.form.get('full_name')
        email = request.form.get('email')
        password = request.form.get('password')
        role = request.form.get('role')
        
        # New optional personal details
        age = request.form.get('age', type=int)
        weight = request.form.get('weight', type=float)

        existing_user = User.query.filter_by(email=email).first()
        if existing_user:
            flash('Email already registered. Please login.', 'danger')
            return redirect(url_for('register'))

        hashed_password = generate_password_hash(password)
        new_user = User(
            full_name=full_name,
            email=email,
            password=hashed_password,
            role=role,
            age=age,
            weight=weight
        )
        db.session.add(new_user)
        db.session.commit()

        flash('Registration successful! Please login.', 'success')
        return redirect(url_for('login'))

    return render_template('register.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if is_logged_in():
        return redirect(url_for('dashboard'))

    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')

        user = User.query.filter_by(email=email).first()

        if not user or not check_password_hash(user.password, password):
            flash('Invalid email or password.', 'danger')
            return redirect(url_for('login'))

        session['user_id'] = user.id
        session['user_name'] = user.full_name
        session['user_role'] = user.role
        session['email'] = getattr(user, 'email', '')
        
        # Save account creation year roughly for profile page
        if hasattr(user, 'created_at') and user.created_at:
            session['created_at'] = getattr(user.created_at, 'strftime', lambda x: str(user.created_at))('%Y')

        flash(f'Welcome back, {user.full_name}!', 'success')
        return redirect(url_for('dashboard'))

    return render_template('login.html')

@app.route('/dashboard')
def dashboard():
    if not is_logged_in():
        flash('Please login first.', 'warning')
        return redirect(url_for('login'))

    user = User.query.get(session['user_id'])
    medicines = Medicine.query.filter_by(user_id=session['user_id']).all()
    
    todays_doses = 0
    low_stock_alerts = 0
    
    # Simple logic for dashboard metrics based on db schemas
    for med in medicines:
        stock = Stock.query.filter_by(medicine_id=med.id).first()
        if stock and stock.quantity <= stock.low_stock_threshold:
            low_stock_alerts += 1
            
        scheds = Schedule.query.filter_by(medicine_id=med.id).all()
        todays_doses += len(scheds)

    # Simplified adherence %
    adherence_percentage = 100

    return render_template('dashboard.html', 
                           user_details=user, 
                           medicines=medicines,
                           todays_doses=todays_doses,
                           low_stock_alerts=low_stock_alerts,
                           adherence_percentage=adherence_percentage)

@app.route('/logout')
def logout():
    session.clear()
    flash('You have been logged out.', 'info')
    return redirect(url_for('login'))

@app.route('/medicines')
def medicines():
    if not is_logged_in():
        return redirect(url_for('login'))
        
    user_meds = Medicine.query.filter_by(user_id=session['user_id']).all()
    return render_template('medicines.html', medicines=user_meds)

@app.route('/add_medicine', methods=['GET', 'POST'])
def add_medicine():
    if not is_logged_in():
        return redirect(url_for('login'))
        
    if request.method == 'POST':
        name = request.form.get('name')
        dosage = request.form.get('dosage')
        frequency = request.form.get('frequency')
        scheduled_time = request.form.get('scheduled_time')
        days = request.form.get('days')
        quantity = request.form.get('quantity', type=int)
        low_stock_threshold = request.form.get('low_stock_threshold', type=int)
        
        new_med = Medicine(
            user_id=session['user_id'],
            name=name,
            dosage=dosage,
            frequency=frequency
        )
        db.session.add(new_med)
        db.session.flush() # Flush to assign new_med.id before committing next inserts
        
        new_sched = Schedule(
            medicine_id=new_med.id,
            scheduled_time=scheduled_time,
            days=days
        )
        db.session.add(new_sched)
        
        new_stock = Stock(
            medicine_id=new_med.id,
            quantity=quantity,
            low_stock_threshold=low_stock_threshold
        )
        db.session.add(new_stock)
        
        db.session.commit()
        flash('Medicine added successfully.', 'success')
        return redirect(url_for('medicines'))
        
    return render_template('add_medicine.html')

@app.route('/edit_medicine/<int:id>', methods=['GET', 'POST'])
def edit_medicine(id):
    if not is_logged_in():
        return redirect(url_for('login'))
        
    medicine_obj = Medicine.query.get_or_404(id)
    if medicine_obj.user_id != session['user_id']:
        flash('Unauthorized access.', 'danger')
        return redirect(url_for('medicines'))
        
    schedule = Schedule.query.filter_by(medicine_id=medicine_obj.id).first()
    stock = Stock.query.filter_by(medicine_id=medicine_obj.id).first()
    
    if request.method == 'POST':
        medicine_obj.name = request.form.get('name')
        medicine_obj.dosage = request.form.get('dosage')
        medicine_obj.frequency = request.form.get('frequency')
        
        if schedule:
            schedule.scheduled_time = request.form.get('scheduled_time')
            schedule.days = request.form.get('days')
            
        if stock:
            stock.quantity = request.form.get('quantity', type=int)
            stock.low_stock_threshold = request.form.get('low_stock_threshold', type=int)
            
        db.session.commit()
        flash('Medicine updated successfully.', 'success')
        return redirect(url_for('medicines'))
    
    # Bundle data cleanly for template processing
    med_data = {
        'id': medicine_obj.id,
        'name': medicine_obj.name,
        'dosage': medicine_obj.dosage,
        'frequency': medicine_obj.frequency,
        'scheduled_time': schedule.scheduled_time if schedule else '',
        'days': schedule.days if schedule else 'Everyday',
        'quantity': stock.quantity if stock else 0,
        'low_stock_threshold': stock.low_stock_threshold if stock else 5
    }
    return render_template('edit_medicine.html', medicine=med_data)

@app.route('/delete_medicine/<int:id>', methods=['POST'])
def delete_medicine(id):
    if not is_logged_in():
        return redirect(url_for('login'))
        
    medicine = Medicine.query.get_or_404(id)
    if medicine.user_id != session['user_id']:
        flash('Unauthorized access.', 'danger')
        return redirect(url_for('medicines'))
        
    # Delete related dependencies first (adjust logic if cascade is enabled in SQLAlchemy models)
    Schedule.query.filter_by(medicine_id=medicine.id).delete()
    Dose.query.filter_by(medicine_id=medicine.id).delete()
    Stock.query.filter_by(medicine_id=medicine.id).delete()
    
    db.session.delete(medicine)
    db.session.commit()
    
    flash('Medicine deleted.', 'success')
    return redirect(url_for('medicines'))

@app.route('/schedule', methods=['GET', 'POST'])
def schedule():
    if not is_logged_in():
        return redirect(url_for('login'))
        
    if request.method == 'POST':
        action = request.form.get('action')
        schedule_id = request.form.get('schedule_id')
        if action == 'mark_taken' and schedule_id:
            sched = Schedule.query.get(schedule_id)
            if sched:
                dose = Dose(
                    medicine_id=sched.medicine_id,
                    schedule_id=sched.id,
                    status='taken'
                )
                db.session.add(dose)
                
                stock = Stock.query.filter_by(medicine_id=sched.medicine_id).first()
                if stock and stock.quantity > 0:
                    stock.quantity -= 1
                    
                db.session.commit()
                flash('Dose marked as taken!', 'success')
        return redirect(url_for('schedule'))
        
    user_meds = Medicine.query.filter_by(user_id=session['user_id']).all()
    med_ids = [m.id for m in user_meds]
    
    schedules = []
    if med_ids:
        schedules = Schedule.query.filter(Schedule.medicine_id.in_(med_ids)).all()
        
    schedule_data = []
    today = date.today()
    for s in schedules:
        med = Medicine.query.get(s.medicine_id)
        # Check if logged today by getting latest dose
        dose = Dose.query.filter_by(schedule_id=s.id).order_by(Dose.logged_at.desc()).first()
        status = 'pending'
        
        if dose and hasattr(dose, 'logged_at') and dose.logged_at:
            dose_date = getattr(dose.logged_at, 'date', lambda: None)()
            if dose_date == today:
                status = dose.status
        
        schedule_data.append({
            'id': s.id,
            'medicine_name': med.name,
            'dosage': med.dosage,
            'scheduled_time': s.scheduled_time,
            'status': status
        })
        
    return render_template('schedule.html', schedule=schedule_data, current_date=today.strftime('%B %d, %Y'))

@app.route('/history')
def history():
    if not is_logged_in():
        return redirect(url_for('login'))
        
    filter_name = request.args.get('medicine_name', '').lower()
    filter_date = request.args.get('date', '')
    
    user_meds = Medicine.query.filter_by(user_id=session['user_id']).all()
    med_dict = {m.id: m for m in user_meds}
    
    history_records = []
    if med_dict:
        doses = Dose.query.filter(Dose.medicine_id.in_(med_dict.keys())).order_by(Dose.logged_at.desc()).all()
        
        for d in doses:
            med = med_dict.get(d.medicine_id)
            sched = Schedule.query.get(d.schedule_id)
            
            if filter_name and filter_name not in med.name.lower():
                continue
                
            dt_str = ''
            if d.logged_at:
                if hasattr(d.logged_at, 'strftime'):
                    dt_str = d.logged_at.strftime('%Y-%m-%d %H:%M')
                    if filter_date and d.logged_at.strftime('%Y-%m-%d') != filter_date:
                        continue
                else:
                    dt_str = str(d.logged_at)
                    if filter_date and not dt_str.startswith(filter_date):
                        continue
                        
            history_records.append({
                'medicine_name': med.name,
                'scheduled_time': sched.scheduled_time if sched else 'N/A',
                'status': d.status,
                'logged_at': dt_str
            })
            
    return render_template('history.html', history_records=history_records)

@app.route('/stock')
def stock():
    if not is_logged_in():
        return redirect(url_for('login'))
        
    user_meds = Medicine.query.filter_by(user_id=session['user_id']).all()
    stock_data = []
    
    for m in user_meds:
        st = Stock.query.filter_by(medicine_id=m.id).first()
        if st:
            stock_data.append({
                'id': m.id,
                'name': m.name,
                'dosage': m.dosage,
                'quantity': st.quantity,
                'low_stock_threshold': st.low_stock_threshold
            })
            
    return render_template('stock.html', medicines=stock_data)

@app.route('/profile', methods=['GET', 'POST'])
def profile():
    if not is_logged_in():
        return redirect(url_for('login'))
        
    user = User.query.get(session['user_id'])
    
    if request.method == 'POST':
        action = request.form.get('action')
        
        if action == 'update_profile':
            full_name = request.form.get('full_name')
            if full_name:
                user.full_name = full_name
                db.session.commit()
                session['user_name'] = user.full_name
                flash('Profile updated successfully.', 'success')
                
        elif action == 'change_password':
            current_password = request.form.get('current_password')
            new_password = request.form.get('new_password')
            confirm_new_password = request.form.get('confirm_new_password')
            
            if not check_password_hash(user.password, current_password):
                flash('Incorrect current password.', 'danger')
            elif new_password != confirm_new_password:
                flash('New passwords do not match.', 'danger')
            elif len(new_password) < 6:
                flash('New password must be at least 6 characters.', 'danger')
            else:
                user.password = generate_password_hash(new_password)
                db.session.commit()
                flash('Password changed successfully.', 'success')
                
        return redirect(url_for('profile'))
        
    return render_template('profile.html')

if __name__ == '__main__':
    app.run(debug=True)