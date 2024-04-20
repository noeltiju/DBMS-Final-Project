import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt # This is needed to run matplotlib on a server
import datetime

def customer_analytics(cursor, customer_id, start_date, end_date):

    x_axis_months = []
    y_axis_sales = []
    starting_date = datetime.datetime.strptime(start_date, '%Y-%m-%d').date()
    ending_date = datetime.datetime.strptime(end_date, '%Y-%m-%d').date()
    month_count = 0
    current_date = starting_date
    while current_date <= ending_date:
        if current_date.month == 12:
            current_date = current_date.replace(year=current_date.year + 1, month=1)
            
        else:
            current_date = current_date.replace(month=current_date.month + 1)

        current_date_format = current_date.strftime('%Y-%m-%d')
        cursor.execute(f"select SUM(Total_Amount) from Orders where Customer_ID = {customer_id} and Order_Date <= '{current_date_format}'")
        result = cursor.fetchone()
        if result[0] == None:
            result = 0
        else:
            result = int(result[0])

        month_count += 1
        x_axis_months.append(month_count)
        y_axis_sales.append(result)



    plt.plot(x_axis_months, y_axis_sales)
    plt.xlabel('Months')
    plt.ylabel('Sales')
    plt.title('Customer Analytics')
    plt.savefig('static/assets/customer_analytics.png', bbox_inches='tight')


    return x_axis_months, y_axis_sales

def order_analytics(cursor, start_date, end_date):
    x_axis_months = []
    y_axis_sales = []
    starting_date = datetime.datetime.strptime(start_date, '%Y-%m-%d').date()
    ending_date = datetime.datetime.strptime(end_date, '%Y-%m-%d').date()
    month_count = 0
    current_date = starting_date
    while current_date <= ending_date:
        if current_date.month == 12:
            current_date = current_date.replace(year=current_date.year + 1, month=1)
            
        else:
            current_date = current_date.replace(month=current_date.month + 1)

        current_date_format = current_date.strftime('%Y-%m-%d')
        cursor.execute(f"select SUM(Total_Amount) from Orders where Order_Date <= '{current_date_format}'")
        result = cursor.fetchone()
        result = int(result[0])

        month_count += 1
        x_axis_months.append(month_count)
        y_axis_sales.append(result)

    plt.plot(x_axis_months, y_axis_sales)
    plt.xlabel('Months')
    plt.ylabel('Sales')
    plt.title('Customer Analytics')
    plt.savefig('static/assets/customer_analytics.png', bbox_inches='tight')


    return x_axis_months, y_axis_sales

def product_analytics(cursor, product_id, start_date, end_date):
    x_axis_months = []
    y_axis_sales = []
    starting_date = datetime.datetime.strptime(start_date, '%Y-%m-%d').date()
    ending_date = datetime.datetime.strptime(end_date, '%Y-%m-%d').date()
    month_count = 0
    current_date = starting_date
    cursor.execute(f"select Price from Product_Inventory where Product_ID = {product_id}")
    price = cursor.fetchone()[0]
    while current_date <= ending_date:
        if current_date.month == 12:
            current_date = current_date.replace(year=current_date.year + 1, month=1)
            
        else:
            current_date = current_date.replace(month=current_date.month + 1)

        current_date_format = current_date.strftime('%Y-%m-%d')
        cursor.execute(f"select quantity from Orders, Order_Items where Orders.Order_ID = Order_Items.Order_ID and Product_ID = {product_id} and Order_Date <= '{current_date_format}'")
        total_quantity = 0
        for i in cursor:
            total_quantity += i[0]


        result = total_quantity * price
        month_count += 1
        x_axis_months.append(month_count)
        y_axis_sales.append(result)

    plt.plot(x_axis_months, y_axis_sales)
    plt.xlabel('Months')
    plt.ylabel('Sales')
    plt.title('Product Analytics')
    plt.savefig('static/assets/product_analytics.png', bbox_inches='tight')


    return x_axis_months, y_axis_sales