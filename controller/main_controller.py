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

        return render_template('histori.html', transactions=transactions)
    
    def gudang(self):
        # Fetch stock data from Firebase
        stock_ref = db.reference('inventaris')
        stock_data = stock_ref.get()

        # Extract product_name and quantity
        stock_items = [{'product_name': item['product_name'], 'quantity': item['quantity']} for item in stock_data.values()]

        return render_template('gudang.html', stock_items=stock_items)
    
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

