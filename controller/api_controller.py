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
        try:
            cart_items = request.get_json()
            transaction_id = str(uuid.uuid4())
            total_price = sum(item['price'] * item['quantity'] for item in cart_items)
            transaction_data = {
                'transaction_id': transaction_id,
                'items': cart_items,
                'date': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                'total_price': total_price
            }

            # Update stock and save transaction
            stock_ref = db.reference('inventaris')
            stock_data = stock_ref.get()
            stock_dict = {key: value for key, value in stock_data.items()}

            bike_parts = {
                'ALPHA': {'PROD001': 2, '3-PRO': 1, 'P03-16': 1},
                'SIGMA': {'PROD002': 2, '4-PRO': 1, 'P03-17': 1},
                'BETA': {'PROD003': 2, '5-PRO': 1, 'P03-18': 1}
            }

            for item in cart_items:
                model = item['item'].split()[-1]
                parts = bike_parts[model]

                for part, qty in parts.items():
                    if stock_dict[part]['quantity'] < item['quantity'] * qty:
                        return jsonify({"error": f"Stok tidak cukup untuk {part}"}), 400

                for part, qty in parts.items():
                    stock_dict[part]['quantity'] -= item['quantity'] * qty

            db.reference('transactions').push(transaction_data)
            stock_ref.set(stock_dict)

            return jsonify({"message": "Semua transaksi berhasil disimpan!"}), 200
        except Exception as e:
            return jsonify({"error": f"Terjadi kesalahan: {str(e)}"}), 500
    
    # Gudang
    def get_stock_data(self):
        stock_ref = db.reference('inventaris')
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
                response = requests.get('https://suplierman.pythonanywhere.com/products/api/products')
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
                response = requests.post('http://165.22.187.192:8000/api/supplier/cek_harga', json=data_post)
                distributor_data = response.json()
                print(distributor_data)
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
