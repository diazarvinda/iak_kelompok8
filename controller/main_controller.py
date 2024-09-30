from flask import render_template, request, session, flash, redirect, url_for
from firebase_admin import db, auth

class main_controller():
    def index(self):
        return render_template('../index.html')
    
    def login(self):
        return render_template('login.html')
    
    def set_session(self):
        data = request.get_json()
        session['user'] = data['email']  # Set the session variable to user email
        return '', 204  # No content
    
    def register(self):
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
    
    def about(self):
        return render_template('about.html')
    
    def pembayaran(self):
        return render_template('pembayaran.html')

    def histori(self):
        transactions_ref = db.reference('transactions')
        transactions = transactions_ref.get()  # Fetch all transaction data

        # If no transactions are found, set transactions to an empty list
        if transactions is None:
            transactions = []

        return render_template('histori.html', transactions=transactions)
    
    def gudang(self):
        # Fetch stock data from Firebase
        stock_ref = db.reference('inventaris')
        stock_data = stock_ref.get()

        # Extract product_id, product_name, and quantity
        stock_items = [{'product_id': key, 'product_name': value['product_name'], 'quantity': value['quantity']} for key, value in stock_data.items()]

        # Calculate bikes
        bike_items = self.calculate_bikes(stock_items)

        return render_template('gudang.html', stock_items=stock_items, bike_items=bike_items)
    
    def calculate_bikes(self, stock_items):
        bike_formulas = {
            'Sepeda Ontel - ALPHA': {'PROD001': 2, '3-PRO': 1, 'P03-16': 1},
            'Sepeda Ontel - SIGMA': {'PROD002': 2, '4-PRO': 1, 'P03-17': 1},
            'Sepeda Ontel - BETA': {'PROD003': 2, '5-PRO': 1, 'P03-18': 1},
        }

        bikes = {name: float('inf') for name in bike_formulas}

        for bike, parts in bike_formulas.items():
            for part, required_qty in parts.items():
                available_qty = next((item['quantity'] for item in stock_items if item['product_id'] == part), 0)
                bikes[bike] = min(bikes[bike], available_qty // required_qty)

        return [{'bike_name': bike, 'quantity': int(qty)} for bike, qty in bikes.items()]

    def pemasok(self):
        return render_template('pemasok.html')
    
    def pemesanan(self):
        # Fetch orders from Firebase
        orders_ref = db.reference('orders')
        orders = orders_ref.get()
        
        # If no orders are found, set orders to an empty dict
        if orders is None:
            orders = {}
        
        return render_template('pemesanan.html', orders=orders)

    
    def logout(self):
        session.pop('user', None)  # Clear the session
        flash("You have been logged out.", "info")
        return redirect(url_for('login'))

