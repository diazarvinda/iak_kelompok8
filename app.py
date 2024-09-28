from flask import Flask, redirect, url_for, flash, session
from functools import wraps
import firebase_admin
from firebase_admin import credentials, db
from controller.main_controller import main_controller
from controller.api_controller import api_controller


app = Flask(__name__)
app.secret_key = '1234' 

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

@app.route('/', methods=['GET', 'POST'])
def login(): return main_controller().login()

@app.route('/set_session', methods=['POST'])
def set_session(): return main_controller().set_session()

@app.route('/register', methods=['GET', 'POST'])
def register(): return main_controller().register()



# Semua View Route
@app.route('/about')
@login_required
def about():return main_controller().about()

@app.route('/pembayaran')
@login_required
def pembayaran():return main_controller().pembayaran()

@app.route('/histori')
@login_required
def histori():return main_controller().histori()

@app.route('/gudang')
@login_required
def gudang(): return main_controller().gudang()

@app.route('/pemasok')
@login_required
def pemasok(): return main_controller().pemasok()

@app.route('/pemesanan')
@login_required
def pemesanan(): return main_controller().pemesanan()

@app.route('/logout', methods=['GET'])
def logout():return main_controller().logout()



# Semua API

# API untuk mengambil data transaksi
@app.route('/api/get/transaction_data', methods=['GET'])
def get_transactions_data(): return api_controller().get_transactions_data()

# API untuk mengambil data stok
@app.route('/api/get/stock_data', methods=['GET'])
def get_stock_data(): return api_controller().get_stock_data()

@app.route('/api/confirm_order', methods=['POST'])
@login_required
def confirm_order(): return api_controller().confirm_order(app)

@app.route('/api/submit_order', methods=['POST'])
@login_required
def submit_order(): return api_controller().submit_order()

@app.route('/api/save_transaction', methods=['POST'])
@login_required
def save_transaction(): return api_controller().save_transaction()

@app.route('/api/get/distributor_price', methods=['POST'])
@login_required
def get_distributor_price(): return api_controller().get_distributor_price()

@app.route('/api/get/supplier_stock', methods=['POST'])
@login_required
def get_supplier_stock(): return api_controller().get_supplier_stock()


# Database init
def initialize_database():
    # Initialize supplier stock
    supplier_stock = {
        "Toko Roda": {
            "Roda A": {"price": 100000, "stock": 50},
            "Roda B": {"price": 150000, "stock": 40},
            "Roda C": {"price": 200000, "stock": 30}
        },
        "Toko Frame": {
            "Frame A": {"price": 500000, "stock": 25},
            "Frame B": {"price": 750000, "stock": 20},
            "Frame C": {"price": 1000000, "stock": 15}
        },
        "Toko Stang": {
            "Stang A": {"price": 200000, "stock": 35},
            "Stang B": {"price": 300000, "stock": 30},
            "Stang C": {"price": 400000, "stock": 25}
        }
    }
    db.reference('supplier_stock').set(supplier_stock)

    # Initialize distributor prices
    distributor_prices = {
        "Distributor A": 50000,
        "Distributor B": 75000,
        "Distributor C": 100000
    }
    db.reference('distributor_prices').set(distributor_prices)

# Call this function once to initialize the database
initialize_database()

if __name__ == '__main__':
    app.run(debug=True)  # Run the Flask application
