from flask import Flask, request, render_template, redirect, url_for, jsonify
import mysql.connector

app = Flask(__name__)


# Database connection
def get_db_connection():
    connection = mysql.connector.connect(
        host="localhost",
        user="root",
        password="Manish@123",
        database="billing-software",
    )
    return connection


@app.route("/")
def index():
    # Fetch all products from the database
    connection = get_db_connection()
    cursor = connection.cursor()
    cursor.execute("SELECT * FROM products")
    products = cursor.fetchall()

    # Fetch all customers from the database
    cursor.execute("SELECT * FROM customers")  # Assuming you have a 'customers' table
    customers = cursor.fetchall()

    cursor.close()
    connection.close()

    return render_template("index.html", products=products, customers=customers)


@app.route("/add-product", methods=["POST"])
def add_product():
    if request.method == "POST":
        # Get form data
        product_name = request.form["name"]
        product_price = request.form["price"]
        quantity = request.form["quantity"]
        product_brand = request.form["brand"]
        product_supplier = request.form["supplier"]
        old_stock = request.form["stock"]
        category = request.form["category"]

        # Insert data into the database
        connection = get_db_connection()
        cursor = connection.cursor()

        try:
            query = """
            INSERT INTO products (product_name, product_price, quantity, product_brand, product_supplier, old_stock, category)
            VALUES (%s, %s, %s, %s, %s, %s, %s)
            """
            cursor.execute(
                query,
                (
                    product_name,
                    product_price,
                    quantity,
                    product_brand,
                    product_supplier,
                    old_stock,
                    category,
                ),
            )
            connection.commit()

            # Check if the insertion was successful
            if cursor.rowcount > 0:
                print("Product added to the database.")

        except mysql.connector.Error as err:
            print(f"Error: {err}")

        finally:
            cursor.close()
            connection.close()

        # Redirect to the home page
        return redirect(url_for("index"))


@app.route("/add-customer", methods=["POST"])
def add_customer():
    if request.method == "POST":
        # Get form data
        name = request.form["name"]
        gender = request.form["gender"]
        contact = request.form["contact"]
        email = request.form["email"]

        # Insert data into the database
        connection = get_db_connection()
        cursor = connection.cursor()

        try:
            query = """
            INSERT INTO customers (name, gender, contact, email)
            VALUES (%s, %s, %s, %s)
            """
            cursor.execute(query, (name, gender, contact, email))
            connection.commit()

            # Check if the insertion was successful
            if cursor.rowcount > 0:
                print("Customer added to the database.")

        except mysql.connector.Error as err:
            print(f"Error: {err}")

        finally:
            cursor.close()
            connection.close()

        # Redirect to the home page
        return redirect(url_for("index"))


@app.route("/submit-bill", methods=["POST"])
def submit_bill():
    data = request.get_json()
    customer_name = data["customerName"]
    products = data["products"]

    connection = get_db_connection()
    cursor = connection.cursor()

    try:
        for product in products:
            product_id = product["productId"]
            quantity = product["quantity"]

            # Update the stock in the products table
            cursor.execute(
                """
            UPDATE products 
            SET quantity = quantity - %s 
            WHERE id = %s
            """,
                (quantity, product_id),
            )

            # Insert into the sales table
            cursor.execute(
                """
            INSERT INTO sales (product_id, quantity)
            VALUES (%s, %s)
            """,
                (product_id, quantity),
            )

        connection.commit()
        return jsonify({"status": "success", "message": "Bill submitted successfully"})

    except mysql.connector.Error as err:
        connection.rollback()
        return jsonify({"status": "error", "message": str(err)})

    finally:
        cursor.close()
        connection.close()


@app.route("/get-sales-data")
def get_sales_data():
    connection = get_db_connection()
    cursor = connection.cursor()

    try:
        # Query to get total units sold
        cursor.execute("SELECT SUM(quantity) as total_units_sold FROM sales")
        total_units_sold_result = cursor.fetchone()
        total_units_sold = total_units_sold_result[0] if total_units_sold_result[0] is not None else 0

        # Query to get total revenue
        cursor.execute("""
            SELECT SUM(products.product_price * sales.quantity) AS total_revenue 
            FROM sales 
            JOIN products ON sales.product_id = products.id
        """)
        total_revenue_result = cursor.fetchone()
        total_revenue = total_revenue_result[0] if total_revenue_result[0] is not None else 0

    finally:
        cursor.close()
        connection.close()

    # Return the results as JSON
    return jsonify({
        "total_units_sold": total_units_sold,
        "total_revenue": total_revenue
    })


if __name__ == "__main__":
    app.run(port=5001, debug=True)
