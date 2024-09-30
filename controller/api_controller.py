from flask import jsonify, request, flash, redirect, url_for
from firebase_admin import db
from datetime import datetime
import uuid
import requests

class api_controller():
    def get_transactions_data(self):
        transactions_ref = db.reference('transactions')
        transactions = transactions_ref.get()
        return jsonify(transactions)
    
    def get_stock_data(self):
        stock_ref = db.reference('stock')
        stock = stock_ref.get()
        return jsonify(stock)
    
    def save_transaction(self):
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
    

    # Simulasi
    def get_supplier_stock(self, supplier):

        if supplier == 'SUP01':
            try:
                response = requests.get('http://167.99.238.114:8000/products')
                stock_data = response.json()
            except Exception as e:
                return jsonify({"error": f"Failed to fetch supplier stock: {str(e)}"}), 500
        elif supplier == 'SUP02':
            try:
                response = requests.get('http://167.99.238.114:8000/products')
                stock_data = response.json()
            except Exception as e:
                return jsonify({"error": f"Failed to fetch supplier stock: {str(e)}"}), 500
        elif supplier == 'SUP03':
            try:
                response = requests.get('http://167.99.238.114:8000/products')
                stock_data = response.json()
            except Exception as e:
                return jsonify({"error": f"Failed to fetch supplier stock: {str(e)}"}), 500
        else:
            return jsonify({"error": "Supplier not recognized"}), 400

        
        if stock_data:
            return jsonify(stock_data)
        else:
            return jsonify({"error": "Stock data not found"}), 404
    
    def get_distributor_price(self):
        data = request.get_json()
        data_post = data.copy()
        del data_post['id_supplier']


        if data['id_supplier'] == 'SUP01':
            try:
                response = requests.post('http://167.99.238.114:8000/check_price', json=data_post)
                distributor_data = response.json()
                print(distributor_data)
            except Exception as e:
                return jsonify({"error": f"Gagal mengambil data distributor: {str(e)}"}), 500
        elif data['id_supplier'] == 'SUP02':
            try:
                response = requests.post('http://167.99.238.114:8000/api/hehe', json=data_post)
                distributor_data = response.json()
            except Exception as e:
                return jsonify({"error": f"Gagal mengambil data distributor: {str(e)}"}), 500
        elif data['id_supplier'] == 'SUP03':
            try:
                response = requests.post('http://167.99.238.114:8000/api/hehe', json=data_post)
                distributor_data = response.json()
            except Exception as e:
                return jsonify({"error": f"Gagal mengambil data distributor: {str(e)}"}), 500
        else:
            return jsonify({"error": "Supplier tidak dikenali"}), 400

        return jsonify(distributor_data), 200
    
    def submit_order(self):
        data = request.get_json()
        data_post = {'id_log': data['id_log']}
        
        if data['id_supplier'] == 'SUP01':
            try:
                response = requests.post('http://167.99.238.114:8000/place_order', json=data_post)
                response_data = response.json()
                print(response_data)
            except Exception as e:
                return jsonify({"error": f"Gagal mengambil data distributor: {str(e)}"}), 500    

        # Save order data
        order_data = {
            'no_resi': response_data['no_resi'],
            'id_distributor': data['distributor'],
            'lama pengiriman': response_data['lama_pengiriman'], 
            'harga_pengiriman': response_data['harga_pengiriman'],
            'cart': data['cart'],
            'total_price': data['total_price'],
            'date': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        }
        
        # Update database
        try:
            db.reference('orders').push(order_data)
            return jsonify({"message": "Order submitted successfully"}), 200
        except Exception as e:
            return jsonify({"error": f"Failed to submit order: {str(e)}"}), 500
        
    def confirm_order(self, app):
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