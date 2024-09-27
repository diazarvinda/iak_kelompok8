from flask import Flask, render_template, redirect, url_for, flash, request, session, jsonify
from functools import wraps
import firebase_admin
from firebase_admin import credentials, auth, db  # Make sure to import db
from datetime import datetime


app = Flask(__name__)
app.secret_key = '1234'  # Necessary for session management and flashing messages

# Initialize Firebase Admin SDK
cred = credentials.Certificate('config/iak-retail-kelompok-8-firebase-adminsdk-3jgwz-e3f029a870.json')  # Path to your service account key

# Initialize the Firebase Admin app with the database URL
firebase_admin.initialize_app(cred, {
    'databaseURL': 'https://iak-retail-kelompok-8-default-rtdb.firebaseio.com/'  # Your Realtime Database URL
})

# Function to check if user is logged in
def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user' not in session:
            flash("You need to login first!", "danger")
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated_function

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    # If it's a GET request, just render the login page
    return render_template('login.html')

@app.route('/set_session', methods=['POST'])
def set_session():
    data = request.get_json()
    session['user'] = data['email']  # Set the session variable to user email
    return '', 204  # No content

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        try:
            user = auth.create_user(email=email, password=password)
            flash("Account successfully created!", "success")
            return redirect(url_for('login'))  # Redirect to login page after successful registration
        except Exception as e:
            flash(str(e), "danger")
    return render_template('register.html')

# Semua View Route

@app.route('/about')
@login_required
def about():
    return render_template('about.html')

@app.route('/pembayaran')
@login_required
def pembayaran():
    return render_template('pembayaran.html')


@app.route('/histori')
@login_required
def histori():
    # Retrieve payment data from Firebase Realtime Database
    transactions_ref = db.reference('transactions')
    transactions = transactions_ref.get()  # Fetch all transaction data

    return render_template('histori.html', transactions=transactions)

@app.route('/gudang')
@login_required
def gudang():
    return render_template('gudang.html')

@app.route('/pemesanan')
@login_required
def pemesanan():
    return render_template('pemesanan.html')

@app.route('/logout', methods=['GET'])
def logout():
    session.pop('user', None)  # Clear the session
    flash("You have been logged out.", "info")
    return redirect(url_for('login'))


# Semua API

# API untuk mengambil data transaksi
@app.route('/api/get/transaction_data', methods=['GET'])
def get_transactions_data():
    transactions_ref = db.reference('transactions')
    transactions = transactions_ref.get()
    return jsonify(transactions)

# API untuk mengambil data stok
@app.route('/api/get/stock_data', methods=['GET'])
def get_stock_data():
    stock_ref = db.reference('stock')
    stock = stock_ref.get()
    return jsonify(stock)

# API untuk mengambil data pemesanan
@app.route('/save_transaction', methods=['POST'])
@login_required
def save_transaction():
    item = request.form['item']
    quantity = request.form['quantity']  # Change to match your input name
    price = request.form['price']        # Change to match your input name
    
    # Save the transaction data to Firebase Realtime Database
    try:
        db.reference('transactions').push({
            'item': item,
            'quantity': quantity,
            'price': price,
            'date': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        })
        flash("Transaction saved successfully!", "success")
    except Exception as e:
        flash(f"Failed to save transaction: {str(e)}", "danger")

    return redirect(url_for('pembayaran'))  # Redirect back to pembayaran page or another page as needed



if __name__ == '__main__':
    app.run(debug=True)  # Run the Flask application
