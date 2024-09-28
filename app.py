from flask import Flask, render_template, redirect, url_for, flash, request, session, jsonify
from functools import wraps
import firebase_admin
from firebase_admin import credentials, auth, db  
from datetime import datetime
import uuid

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
def login():
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

@app.route('/save_transaction', methods=['POST'])
@login_required
def save_transaction():
    cart_items = request.get_json()
    transaction_id = str(uuid.uuid4())
    transactions = []
    stock_ref = db.reference('stock')
    stock_data = stock_ref.get()

    # Convert stock_data to a dictionary for easier lookup
    stock_dict = {item['nama_produk']: item for item in stock_data}

    for item in cart_items:
        model = item['item'].split()[-1]  # Get the model (A, B, or C)
        parts = [f"Roda {model}", f"Frame {model}", f"Stang {model}"]
        
        # Check if all required parts are in stock
        for part in parts:
            if stock_dict[part]['stock'] < item['quantity']:
                return jsonify({"error": f"Stok tidak cukup untuk {part}"}), 400

        # If we have enough stock, update the stock and save the transaction
        try:
            # Update stock
            for part in parts:
                stock_dict[part]['stock'] -= item['quantity']
            
            # Save the transaction
            transaction = {
                'transaction_id': transaction_id,
                'item': item['item'],
                'quantity': item['quantity'],
                'price': item['price'] * item['quantity'],
                'date': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            }
            transactions.append(transaction)
            db.reference('transactions').push(transaction)
        except Exception as e:
            return jsonify({"error": f"Failed to save transaction for {item['item']}: {str(e)}"}), 500

    # Update the stock in Firebase
    stock_ref.set([stock_dict[key] for key in stock_dict])

    return jsonify({"message": "Semua transaksi berhasil disimpan!"})

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
    # Fetch stock data from Firebase
    stock_ref = db.reference('stock')
    stock_data = stock_ref.get()

    # If stock_data is None or empty, initialize it with default values
    if not stock_data:
        default_stock = [
            {"id_produk": "RA", "nama_produk": "Roda A", "stock": 0},
            {"id_produk": "RB", "nama_produk": "Roda B", "stock": 0},
            {"id_produk": "RC", "nama_produk": "Roda C", "stock": 0},
            {"id_produk": "FA", "nama_produk": "Frame A", "stock": 0},
            {"id_produk": "FB", "nama_produk": "Frame B", "stock": 0},
            {"id_produk": "FC", "nama_produk": "Frame C", "stock": 0},
            {"id_produk": "SA", "nama_produk": "Stang A", "stock": 0},
            {"id_produk": "SB", "nama_produk": "Stang B", "stock": 0},
            {"id_produk": "SC", "nama_produk": "Stang C", "stock": 0},
        ]
        stock_ref.set(default_stock)
        stock_data = default_stock

    return render_template('gudang.html', stock_data=stock_data)

@app.route('/pemasok')
@login_required
def pemasok():
    return render_template('pemasok.html')

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

@app.route('/api/get/supplier_stock', methods=['POST'])
@login_required
def get_supplier_stock():
    data = request.get_json()
    supplier = data['supplier']
    product = data['product']
    
    # Fetch stock data from Firebase
    stock_ref = db.reference(f'supplier_stock/{supplier}/{product}')
    stock_data = stock_ref.get()
    
    if stock_data:
        return jsonify({"stock": stock_data['stock'], "price": stock_data['price']})
    else:
        return jsonify({"error": "Stock data not found"}), 404

@app.route('/api/get/distributor_price', methods=['POST'])
@login_required
def get_distributor_price():
    data = request.get_json()
    distributor = data['distributor']
    
    # Fetch distributor price data from Firebase
    price_ref = db.reference(f'distributor_prices/{distributor}')
    price_data = price_ref.get()
    
    if price_data:
        return jsonify({"price": price_data})
    else:
        return jsonify({"error": "Distributor price not found"}), 404

@app.route('/api/submit_order', methods=['POST'])
@login_required
def submit_order():
    data = request.get_json()
    cart = data['cart']
    distributor = data['distributor']
    
    # Generate a unique order ID
    order_id = str(uuid.uuid4())
    
    # Calculate total price and update stock
    total_price = 0
    stock_updates = {}
    
    for item in cart:
        supplier = item['supplier']
        product = item['product']
        quantity = item['quantity']
        
        # Fetch current stock and price
        stock_ref = db.reference(f'supplier_stock/{supplier}/{product}')
        stock_data = stock_ref.get()
        
        if stock_data is None or stock_data['stock'] < quantity:
            return jsonify({"error": f"Insufficient stock for {product}"}), 400
        
        price = stock_data['price']
        total_price += price * quantity
        
        new_stock = stock_data['stock'] - quantity
        stock_updates[f'supplier_stock/{supplier}/{product}/stock'] = new_stock
    
    # Fetch distributor price
    distributor_price_ref = db.reference(f'distributor_prices/{distributor}')
    distributor_price = distributor_price_ref.get()
    
    if distributor_price is None:
        return jsonify({"error": "Distributor price not found"}), 404
    
    total_price += distributor_price
    
    # Save order data
    order_data = {
        'order_id': order_id,
        'cart': cart,
        'distributor': distributor,
        'total_price': total_price,
        'date': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    }
    
    # Update database
    try:
        db.reference('orders').push(order_data)
        db.reference().update(stock_updates)
        return jsonify({"message": "Order submitted successfully"}), 200
    except Exception as e:
        return jsonify({"error": f"Failed to submit order: {str(e)}"}), 500

@app.route('/pemesanan')
@login_required
def pemesanan():
    # Fetch orders from Firebase
    orders_ref = db.reference('orders')
    orders = orders_ref.get()
    
    # If no orders are found, set orders to an empty dict
    if orders is None:
        orders = {}
    
    return render_template('pemesanan.html', orders=orders)

@app.route('/api/confirm_order', methods=['POST'])
@login_required
def confirm_order():
    try:
        data = request.get_json()
        order_id = data['order_id']
        
        # Fetch the order from Firebase
        orders_ref = db.reference('orders')
        order = orders_ref.child(order_id).get()
        
        if not order:
            return jsonify({"error": "Order not found"}), 404
        
        # Update stock for each item in the order
        stock_ref = db.reference('stock')
        stock_data = stock_ref.get()
        
        if stock_data is None:
            stock_data = []
        
        stock_dict = {item['nama_produk']: item for item in stock_data}
        
        for item in order['cart']:
            product = item['product']
            quantity = item['quantity']
            
            # Update stock
            if product in stock_dict:
                stock_dict[product]['stock'] += quantity
            else:
                # If the product doesn't exist in stock, create a new entry
                stock_dict[product] = {
                    'id_produk': product[:2].upper(),
                    'nama_produk': product,
                    'stock': quantity
                }
        
        # Update the stock in Firebase
        stock_ref.set([stock_dict[key] for key in stock_dict])
        
        # Remove the order from the 'orders' node
        orders_ref.child(order_id).delete()
        
        return jsonify({"message": "Order confirmed and stock updated successfully"}), 200
    except Exception as e:
        app.logger.error(f"Error in confirm_order: {str(e)}")
        return jsonify({"error": f"An error occurred: {str(e)}"}), 500

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


if __name__ == '__main__':
    app.run(debug=True)  # Run the Flask application
