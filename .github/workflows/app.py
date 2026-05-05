from flask import Flask, render_template, request, redirect, session, url_for

app = Flask(__name__)
app.secret_key = 'simple_secret_key'  # Change this in production

assets = [
    {'id': 1, 'name': 'Laptop', 'category': 'Computer', 'location': 'Room 101', 'status': 'available'},
    {'id': 2, 'name': 'Projector', 'category': 'Equipment', 'location': 'Room 102', 'status': 'available'},
    {'id': 3, 'name': 'Chair', 'category': 'Furniture', 'location': 'Room 103', 'status': 'available'}
]

requests = []  # List of requests: {'user': username, 'asset_id': id, 'purpose': str, 'duration': str, 'status': 'approved'/'returned'}

users = {
    'admin': {
        'password': 'password',
        'full_name': 'System Administrator',
        'email': 'admin@example.com',
        'role': 'admin'
    },
    'user1': {
        'password': 'pass1',
        'full_name': 'Student One',
        'email': 'user1@example.com',
        'role': 'user'
    }
}

@app.route('/')
def home():
    if 'username' in session:
        return render_template('index.html', username=session['username'], role=session['role'])
    return render_template('login.html')

@app.route('/login')
def login_choice():
    if 'username' in session:
        return redirect(url_for('home'))
    return render_template('login.html')

@app.route('/user_login', methods=['GET', 'POST'])
def user_login():
    if 'username' in session:
        return redirect(url_for('home'))
    error = None
    if request.method == 'POST':
        username = request.form['username'].strip()
        password = request.form['password']
        user = users.get(username)
        if user and user['role'] == 'user' and user['password'] == password:
            session['username'] = username
            session['role'] = user['role']
            return redirect(url_for('home'))
        error = 'Invalid user credentials.'
    return render_template('user_login.html', error=error)

@app.route('/admin_login', methods=['GET', 'POST'])
def admin_login():
    if 'username' in session:
        return redirect(url_for('home'))
    error = None
    if request.method == 'POST':
        username = request.form['username'].strip()
        password = request.form['password']
        user = users.get(username)
        if user and user['role'] == 'admin' and user['password'] == password:
            session['username'] = username
            session['role'] = user['role']
            return redirect(url_for('home'))
        error = 'Invalid admin credentials.'
    return render_template('admin_login.html', error=error)

@app.route('/register', methods=['GET', 'POST'])
def register():
    if 'username' in session:
        return redirect(url_for('home'))
    error = None
    if request.method == 'POST':
        username = request.form['username'].strip()
        full_name = request.form['full_name'].strip()
        email = request.form['email'].strip()
        password = request.form['password']
        confirm_password = request.form['confirm_password']

        if not username or not full_name or not email or not password:
            error = 'All fields are required.'
        elif username in users:
            error = 'Username is already taken.'
        elif password != confirm_password:
            error = 'Passwords do not match.'
        else:
            users[username] = {
                'password': password,
                'full_name': full_name,
                'email': email,
                'role': 'user'
            }
            session['username'] = username
            session['role'] = 'user'
            return redirect(url_for('home'))
    return render_template('registration.html', error=error)

@app.route('/logout')
def logout():
    session.pop('username', None)
    session.pop('role', None)
    return redirect(url_for('login_choice'))

@app.route('/profile')
def profile():
    if 'username' not in session:
        return redirect(url_for('login_choice'))
    user = users.get(session['username'], {})
    assigned_requests = [r for r in requests if r['user'] == session['username'] and r['status'] == 'approved']
    assigned_assets = [next((a for a in assets if a['id'] == req['asset_id']), None) for req in assigned_requests]
    assigned_assets = [asset for asset in assigned_assets if asset]
    return render_template('profile.html', user=user, assigned_assets=assigned_assets)

@app.route('/request_asset', methods=['GET', 'POST'])
def request_asset():
    if 'username' not in session or session.get('role') != 'user':
        return redirect(url_for('user_login'))
    error = None
    if request.method == 'POST':
        asset_id = int(request.form['asset_id'])
        purpose = request.form['purpose'].strip()
        duration = request.form['duration'].strip()
        if not purpose or not duration:
            error = 'Please provide purpose and duration.'
        else:
            requests.append({
                'user': session['username'],
                'asset_id': asset_id,
                'purpose': purpose,
                'duration': duration,
                'status': 'approved'
            })
            for asset in assets:
                if asset['id'] == asset_id:
                    asset['status'] = 'assigned'
                    break
            return redirect(url_for('view_assets'))
    available_assets = [a for a in assets if a['status'] == 'available']
    return render_template('request_asset.html', assets=available_assets, error=error)

@app.route('/return_asset', methods=['GET', 'POST'])
def return_asset():
    if 'username' not in session or session.get('role') != 'user':
        return redirect(url_for('user_login'))
    user_requests = [r for r in requests if r['user'] == session['username'] and r['status'] == 'approved']
    assigned_assets = [next((a for a in assets if a['id'] == req['asset_id']), None) for req in user_requests]
    assigned_assets = [asset for asset in assigned_assets if asset]
    if request.method == 'POST':
        asset_id = int(request.form['asset_id'])
        for req in requests:
            if req['user'] == session['username'] and req['asset_id'] == asset_id and req['status'] == 'approved':
                req['status'] = 'returned'
                break
        for asset in assets:
            if asset['id'] == asset_id:
                asset['status'] = 'available'
                break
        return redirect(url_for('view_assets'))
    return render_template('return_asset.html', assets=assigned_assets)

@app.route('/view_assets')
def view_assets():
    if 'username' not in session:
        return redirect(url_for('login_choice'))
    return render_template('view_assets.html', assets=assets, requests=requests, username=session['username'], role=session['role'])

@app.route('/admin')
def admin():
    if session.get('role') != 'admin':
        return 'Access denied'
    return render_template('admin.html', assets=assets, requests=requests)

@app.route('/add_asset', methods=['GET', 'POST'])
def add_asset():
    if session.get('role') != 'admin':
        return 'Access denied'
    if request.method == 'POST':
        name = request.form['name'].strip()
        category = request.form['category'].strip()
        location = request.form['location'].strip()
        if name and category and location:
            asset_id = max([a['id'] for a in assets], default=0) + 1
            assets.append({
                'id': asset_id,
                'name': name,
                'category': category,
                'location': location,
                'status': 'available'
            })
            return redirect(url_for('admin'))
    return render_template('add_asset.html')

if __name__ == '__main__':
    app.run(debug=True)
