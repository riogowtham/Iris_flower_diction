from flask import Flask, render_template, request, redirect, url_for, session, flash
import json
import os
from sklearn.datasets import load_iris
from sklearn.ensemble import RandomForestClassifier

app = Flask(__name__)
app.secret_key = 'your_secret_key'
USER_FILE = 'users.json'

# Load users from file
def load_users():
    if not os.path.exists(USER_FILE):
        return {}
    with open(USER_FILE, 'r') as f:
        return json.load(f)

# Save users to file
def save_users(users):
    with open(USER_FILE, 'w') as f:
        json.dump(users, f)

# Load the Iris dataset and train model
iris = load_iris()
model = RandomForestClassifier()
model.fit(iris.data, iris.target)
target_names = iris.target_names

@app.route('/', methods=['GET', 'POST'])
def auth():
    users = load_users()

    if request.method == 'POST':
        action = request.form.get('action')
        username = request.form.get('username').strip()
        password = request.form.get('password').strip()

        if action == 'signup':
            if username in users:
                flash('Username already exists.', 'error')
            else:
                users[username] = password
                save_users(users)
                flash('Signup successful. Please log in.', 'success')

        elif action == 'login':
            if users.get(username) == password:
                session['user'] = username
                flash('Login successful.', 'success')
                return redirect(url_for('home'))
            else:
                flash('Invalid login credentials.', 'error')

    return render_template('auth.html')

@app.route('/home')
def home():
    if 'user' not in session:
        return redirect(url_for('auth'))
    return render_template('home.html', username=session['user'])

@app.route('/logout')
def logout():
    session.pop('user', None)
    flash('Logged out.', 'info')
    return redirect(url_for('auth'))

@app.route('/predict', methods=['GET', 'POST'])
def predict():
    if 'user' not in session:
        return redirect(url_for('auth'))

    if request.method == 'POST':
        try:
            sl = float(request.form['sl'])
            sw = float(request.form['sw'])
            pl = float(request.form['pl'])
            pw = float(request.form['pw'])

            input_data = [[sl, sw, pl, pw]]
            prediction = model.predict(input_data)[0]
            result = target_names[prediction].capitalize()

            session['result'] = result
            return redirect(url_for('result'))

        except ValueError:
            flash("Invalid input! Please enter valid numbers.", "error")

    return render_template('prediction.html')

@app.route('/result')
def result():
    if 'user' not in session:
        return redirect(url_for('auth'))

    result = session.get('result')
    return render_template('result.html', result=result)

if __name__ == '__main__':
    app.run(debug=True)
