from flask import Flask, request, render_template, redirect
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

# Home route - Display products and add new products
@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        # Get form data from the request
        product_name = request.form['name']
        product_price = request.form['price']
        quantity = request.form['quantity']
        product_brand = request.form['brand']
        product_supplier = request.form['supplier']
        old_stock = request.form['stock']
        category = request.form['category']

        # Insert the new product into the database
        connection = get_db_connection()
        cursor = connection.cursor()

        query = """
        INSERT INTO products (product_name, product_price, quantity, product_brand, product_supplier, old_stock, category)
        VALUES (%s, %s, %s, %s, %s, %s, %s)
        """
        cursor.execute(query, (product_name, product_price, quantity, product_brand, product_supplier, old_stock, category))
        connection.commit()

        cursor.close()
        connection.close()

    # Fetch all products from the database (for GET request)
    connection = get_db_connection()
    cursor = connection.cursor()
    cursor.execute("SELECT * FROM products")
    products = cursor.fetchall()

    cursor.close()
    connection.close()

    # Render the same page with the list of products
    return render_template('index.html', products=products)

if __name__ == '__main__':
    app.run(debug=True)
