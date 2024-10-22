from flask import Flask, request, render_template, redirect, url_for
import mysql.connector

app = Flask(__name__)

# Database connection
def get_db_connection():
    connection = mysql.connector.connect(
        host="localhost",
        user="root",
        password="Manish@123",
        database="billing-software"
    )
    return connection

@app.route('/')
def index():
    # Fetch all products from the database
    connection = get_db_connection()
    cursor = connection.cursor()
    cursor.execute("SELECT * FROM products")
    products = cursor.fetchall()
    cursor.close()
    connection.close()
    
    return render_template('index.html', products=products)


@app.route('/add-product', methods=['POST'])
def add_product():
    if request.method == 'POST':
        # Get form data
        product_name = request.form['name']
        product_price = request.form['price']
        quantity = request.form['quantity']
        product_brand = request.form['brand']
        product_supplier = request.form['supplier']
        old_stock = request.form['stock']
        category = request.form['category']

        # Insert data into the database
        connection = get_db_connection()
        cursor = connection.cursor()

        try:
            query = """
            INSERT INTO products (product_name, product_price, quantity, product_brand, product_supplier, old_stock, category)
            VALUES (%s, %s, %s, %s, %s, %s, %s)
            """
            cursor.execute(query, (product_name, product_price, quantity, product_brand, product_supplier, old_stock, category))
            connection.commit()

            # Check if the insertion was successful
            if cursor.rowcount > 0:
                print("Product added to the database.")

        except mysql.connector.Error as err:
            print(f"Error: {err}")

        finally:
            cursor.close()
            connection.close()

        # Redirect to the home page, passing the new product to be displayed
        return redirect(url_for('index'))
    
if __name__ == '__main__':
    app.run( port=5001,debug=True)
