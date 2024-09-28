from flask import jsonify, request, flash, redirect, url_for
from firebase_admin import db
from datetime import datetime
import uuid

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
    
    def get_supplier_stock(self):
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
    
    def get_distributor_price(self):
        data = request.get_json()
        distributor = data['distributor']
        
        # Fetch distributor price data from Firebase
        price_ref = db.reference(f'distributor_prices/{distributor}')
        price_data = price_ref.get()
        
        if price_data:
            return jsonify({"price": price_data})
        else:
            return jsonify({"error": "Distributor price not found"}), 404
    
    def submit_order(self):
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