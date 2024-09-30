from flask import jsonify, request, flash, redirect, url_for
from firebase_admin import db
from datetime import datetime
import uuid
import requests

class api_controller():

    #Transaksi (Internal)
    def get_transactions_data(self):
        transactions_ref = db.reference('transactions')
        transactions = transactions_ref.get()
        return jsonify(transactions)
    
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
    
    
    # Gudang
    def get_stock_data(self):
        stock_ref = db.reference('stock')
        stock = stock_ref.get()
        return jsonify(stock)
    

    # Data Supplier
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
    

    # Data harga ongkir
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
    

    # Submit Order
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
        elif data['id_supplier'] == 'SUP02':
            try:
                response = requests.post('http://167.99.238.114:8000/api/hehe', json=data_post)
                response_data = response.json()
            except Exception as e:
                return jsonify({"error": f"Gagal mengambil data distributor: {str(e)}"}), 500
        elif data['id_supplier'] == 'SUP03':
            try:
                response = requests.post('http://167.99.238.114:8000/api/hehe', json=data_post)
                response_data = response.json()
            except Exception as e:
                return jsonify({"error": f"Gagal mengambil data distributor: {str(e)}"}), 500

        # Save order data
        order_data = {
            'no_resi': response_data['no_resi'],
            'id_distributor': data['distributor'],
            'lama_pengiriman': response_data['lama_pengiriman'], 
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
        
    # Track Order
    def track_order(self):
        data = request.get_json()
        print(data)

        if not data['no_resi'] or not data['id_distributor']:  # Pastikan id_supplier ada
            return jsonify({"error": "No resi, ID distributor, dan ID Supplier diperlukan"}), 400


        if data['id_distributor'] == 'DIS01':
            try:
                response = requests.get('http://167.99.238.114:8000/track_order') # Ganti endpoint
                distributor_data = response.json()
                print(distributor_data)
            except Exception as e:
                return jsonify({"error": f"Gagal menghubungi distributor: {str(e)}"}), 500
        elif data['id_distributor'] == 'DIS02':  
            try:
                response = requests.get('http://167.99.238.114:8000/track_order') # Sesuaikan endpoint jika berbeda
                distributor_data = response.json()
            except Exception as e:
                return jsonify({"error": f"Gagal menghubungi distributor: {str(e)}"}), 500
        elif data['id_distributor'] == 'DIS03':  
            try:
                response = requests.get(f"http://159.223.41.243:8000/api/status/{data['no_resi']}") # Sesuaikan endpoint jika berbeda
                distributor_data = response.json()
                
            except Exception as e:
                return jsonify({"error": f"Gagal menghubungi distributor: {str(e)}"}), 500
        else:
            return jsonify({"error": "Supplier tidak dikenali"}), 400

        distributor_data['no_resi'] = data['no_resi']
        distributor_data['status'] = "Arrived"
        return jsonify(distributor_data), 200

    def get_data_pemesanan(self):
        # Fetch orders from Firebase
        orders_ref = db.reference('orders')
        orders = orders_ref.get()

        return jsonify(orders), 200

    # Konfirmasi Pesanan
    def confirm_order(self):
        data = request.get_json()
        cart_data = data['data_confirm']['cart']
        data_confirm = data['data_confirm']

        for produk in cart_data:
            product_ref = db.reference('inventaris').child(produk['product'])
            existing_data = product_ref.get()
            if existing_data:
                new_quantity = existing_data['quantity'] + produk['quantity']
                product_ref.update({
                    'quantity': new_quantity,
                    'berat': produk['berat'],
                    'product_name': produk['product_name'],
                    'supplier': produk['supplier']
                })
            else:
                product_ref.set({
                    'quantity': produk['quantity'],
                    'berat': produk['berat'],
                    'product_name': produk['product_name'],
                    'supplier': produk['supplier']
                })
        
        data_order = db.reference('orders').get()
        order_id = None
        for order in data_order:
            if data_order[order]['no_resi'] == data_confirm['no_resi']:
                order_id = order
                break
            
        db.reference('orders').child(order_id).delete()

        return jsonify({'message': 'Konfirmasi Berhasil'}), 200
        