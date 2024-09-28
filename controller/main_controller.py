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

