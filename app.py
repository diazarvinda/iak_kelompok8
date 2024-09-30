from flask import Flask, redirect, url_for, flash, session
from flask_cors import CORS  # Menambahkan import CORS
from functools import wraps
import firebase_admin
from firebase_admin import credentials, db
from controller.main_controller import main_controller
from controller.api_controller import api_controller

app = Flask(__name__)
app.secret_key = '1234' 
CORS(app, resources={r"/*": {"origins": "*"}})

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

@app.template_filter('to_currency')
def to_currency(value):
    return f"Rp {value:,.0f}".replace(",", ".")

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

@app.route('/pembayaran')  # Mengaktifkan CORS untuk aplikasi
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
# API untuk mengambil data transaksi (Internal)
@app.route('/api/get/transaction_data', methods=['GET'])
def get_transactions_data(): return api_controller().get_transactions_data()

# API untuk simpan transaksi (Internal)
@app.route('/api/save_transaction', methods=['POST'])
@login_required
def save_transaction(): return api_controller().save_transaction()

# API untuk mengambil data stok (supplier)
@app.route('/api/get/stock_data', methods=['GET'])
def get_stock_data(): return api_controller().get_stock_data()

# API untuk konfirmasi barang sudah sampai (distributor)
@app.route('/api/confirm_order', methods=['POST'])
@login_required
def confirm_order(): return api_controller().confirm_order()

@app.route('/api/track/order', methods=['POST'])
@login_required
def track_order(): return api_controller().track_order()

@app.route('/api/get/pemesanan', methods=['GET'])
@login_required
def get_data_pemesanan(): return api_controller().get_data_pemesanan()

# API untuk transaksi dengan role lain
@app.route('/api/get/supplier_stock/<supplier>', methods=['GET'])
@login_required
def get_supplier_stock(supplier): return api_controller().get_supplier_stock(supplier)

@app.route('/api/get/distributor_price', methods=['POST'])
@login_required
def get_distributor_price(): return api_controller().get_distributor_price()

@app.route('/api/submit_order', methods=['POST'])
@login_required
def submit_order(): return api_controller().submit_order()


if __name__ == '__main__':
    app.run(debug=True)  # Run the Flask application
