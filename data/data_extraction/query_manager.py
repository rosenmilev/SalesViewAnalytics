from data.database.database_utils import create_connection


class Connector:

    DATABASE_LOCATION = '../database/db.sqlite3'

    def __init__(self):
        self.connection = create_connection(Connector.DATABASE_LOCATION)
        self.cursor = self.connection.cursor()

    def close_connection(self):
        self.cursor.close()
        self.connection.close()

    def fetch_result(self, sql, params=None):
        self.cursor.execute(sql, params or ())
        return self.cursor.fetchall()


class DataExtractor:
    def __init__(self):
        self.connector = Connector()
        self.connection = self.connector.connection
        self.cursor = self.connection.cursor()

    #
    # def close_connection(self):
    #     self.cursor.close()
    #     self.connection.close()
    #
    # def fetch_result(self, sql, params=None):
    #     self.cursor.execute(sql, params or ())
    #     return self.cursor.fetchall()

    def top_ten_customers(self, year):
        query = '''
            SELECT c.customer_name, SUM(od.sales) AS customer_purchases
            FROM customers c
            JOIN sales_transactions st ON c.customer_id = st.customer_id
            JOIN order_details od ON st.order_id = od.order_id
            WHERE strftime('%Y', st.order_date) = ?
            GROUP BY c.customer_name
            ORDER BY customer_purchases DESC 
            LIMIT 10;
        '''
        result = self.connector.fetch_result(query, (year,))
        return result

    def top_ten_sub_categories(self, year):
        query = '''
        SELECT p.sub_category, SUM(od.sales) AS sub_category_sales
        FROM products p
        JOIN order_details od ON p.product_id = od.product_id
        JOIN sales_transactions st ON od.order_id = st.order_id
        WHERE strftime('%Y', st.order_date) = ?
        GROUP BY p.sub_category
        ORDER BY sub_category_sales DESC
        LIMIT 10'''

        result = self.connector.fetch_result(query, (year,))
        return result

    def monthly_sales(self, year):
        query = '''
        SELECT 
            strftime('%m', st.order_date) AS Month, 
            SUM(od.sales) AS TotalSales
        FROM 
            sales_transactions st
        INNER JOIN 
            order_details od ON st.order_id = od.order_id
        WHERE 
            strftime('%Y', st.order_date) = ?
        GROUP BY 
            Month
        ORDER BY 
            Month;'''

        result = self.connector.fetch_result(query, (year,))
        return result

    def segment_sales(self, year):
        query = '''
        SELECT 
            c.segment, 
            SUM(od.sales) AS SegmentSales
        FROM 
            sales_transactions st
        INNER JOIN 
            order_details od ON st.order_id = od.order_id
        INNER JOIN
            customers c ON st.customer_id = c.customer_id
        WHERE 
            strftime('%Y', st.order_date) = ?
        GROUP BY 
            c.segment
        ORDER BY 
            SegmentSales DESC;'''

        result = self.connector.fetch_result(query, (year,))
        return result


    def determine_current_date(self):
        query = '''
            SELECT order_date 
            FROM sales_transactions
            ORDER BY order_date DESC
            '''

        result = self.connector.fetch_result(query)
        return result

    def daily_sales(self, start_date, end_date, filter_type=None, filter_value=None):
        # Base query
        query = '''
                SELECT 
                    strftime('%Y-%m-%d', st.order_date) AS order_date, 
                    ROUND(SUM(od.sales), 2) AS total_sales
                FROM sales_transactions st
                JOIN order_details od ON st.order_id = od.order_id
                JOIN customers c ON st.customer_id = c.customer_id
                '''

        # Initialize parameters list with start and end dates
        params = [start_date, end_date]

        # Conditional WHERE clauses based on filter_type and filter_value
        where_clauses = " WHERE st.order_date BETWEEN ? AND ?"
        if filter_type and filter_value:
            where_clauses += f" AND {filter_type} = ?"
            params.append(filter_value)

        # Finalize query with GROUP BY and ORDER BY clauses
        query += where_clauses + " GROUP BY order_date ORDER BY order_date"

        # Fetch and return the result
        result = self.connector.fetch_result(query, params)
        return result


    def customer_count_for_period(self, start_date, end_date):
        query = '''
            SELECT COUNT(DISTINCT customer_id) AS unique_customers_count
            FROM sales_transactions
            WHERE order_date BETWEEN ? AND ?;
            '''

        result = self.connector.fetch_result(query, (start_date, end_date))
        return result

    def sales_for_period(self, start_date, end_date):
        query = '''
            SELECT ROUND(SUM(sales), 2) AS total_sales
            FROM sales_transactions 
            JOIN order_details ON sales_transactions.order_id = order_details.order_id
            WHERE order_date BETWEEN ? AND ?;
            '''

        result = self.connector.fetch_result(query, (start_date, end_date))
        return result

    def order_count_for_period(self, start_date, end_date):
        query = '''
            SELECT COUNT(DISTINCT order_id) AS order_count
            FROM sales_transactions
            WHERE order_date BETWEEN ? AND ?;
            '''

        result = self.connector.fetch_result(query, (start_date, end_date))
        return result


class QueryGenerator:
    def __init__(self):
        self.connector = Connector()
        self.connection = self.connector.connection
        self.cursor = self.connection.cursor()
        self.base_query = ''
        self.select_clause = ''
        self.where_clause = ''
        self.group_by_clause = ''
        self.order_by_clause = ''
        self.include_product = ''
        self.initiate_query()

    def initiate_query(self):
        self.base_query = '''SELECT {} FROM sales_transactions 
                           JOIN customers ON sales_transactions.customer_id = customers.customer_id 
                           JOIN order_details ON sales_transactions.order_id = order_details.order_id'''
        self.select_clause = ''  # Start with an empty select clause
        self.where_clause = ''
        self.group_by_clause = ''
        self.order_by_clause = 'ORDER BY order_date'
        self.include_product = False


    def set_date_range(self, start_date, end_date):
        # Set the date range for the WHERE clause, but don't include the dates in the SELECT clause
        self.where_clause = f"WHERE order_date BETWEEN '{start_date}' AND '{end_date}'"

    def add_segment(self):
        self.select_clause += ', segment'
        if 'segment' not in self.group_by_clause:
            if self.group_by_clause:
                self.group_by_clause += ', segment'
            else:
                self.group_by_clause = 'GROUP BY segment'

    def remove_segment(self):
        self.select_clause = self.select_clause.replace(', segment', '')
        self.group_by_clause = self.group_by_clause.replace(', segment', '').replace('segment, ', '').replace(
            'GROUP BY segment', '')

    def add_customer(self):
        self.select_clause += ', customer_name, customers.customer_id'
        if 'customer_name' not in self.group_by_clause and 'customers.customer_id' not in self.group_by_clause:
            if self.group_by_clause:
                self.group_by_clause += ', customer_name, customers.customer_id'
            else:
                self.group_by_clause = 'GROUP BY customer_name, customers.customer_id'

    def remove_customer(self):
        self.select_clause = self.select_clause.replace(', customer_name, customers.customer_id', '')
        self.group_by_clause = self.group_by_clause.replace(', customer_name, customers.customer_id', '').replace(
            'customer_name, ', '').replace('customers.customer_id, ', '').replace(
            'GROUP BY customer_name, customers.customer_id', '')

    def add_region(self):
        self.select_clause += ', region'
        if 'region' not in self.group_by_clause:
            if self.group_by_clause:
                self.group_by_clause += ', region'
            else:
                self.group_by_clause = 'GROUP BY region'

    def remove_region(self):
        self.select_clause = self.select_clause.replace(', region', '')
        self.group_by_clause = self.group_by_clause.replace(', region', '').replace('region, ', '').replace(
            'GROUP BY region', '')

    def add_product(self):
        self.include_product = True
        # Join with the products table
        self.base_query += ' JOIN products ON order_details.product_id = products.product_id'
        # Include product details in the SELECT clause
        self.select_clause += ', products.product_name, products.product_id'
        # Adjust the GROUP BY clause
        if 'products.product_id' not in self.group_by_clause:
            if self.group_by_clause:
                self.group_by_clause += ', products.product_name, products.product_id'
            else:
                self.group_by_clause = 'GROUP BY products.product_name, products.product_id'

    def remove_product(self):
        self.include_product = False
        self.select_clause = self.select_clause.replace(
            ', products.product_name, products.product_id', '')
        self.group_by_clause = self.group_by_clause.replace(', products.product_name, products.product_id', '').replace(
            'products.product_name, ', '').replace('products.product_id, ', '').replace(
            'GROUP BY products.product_name, products.product_id', '')

    def generate_query(self, include_segment=False, include_customer=False, include_region=False, include_product=False):
        # Build the dynamic select clause and column names based on conditions
        dynamic_parts = []
        column_names = ['Total Sales']  # Start with the column always present

        if include_product:
            # Add product-specific selections
            dynamic_parts.append('products.product_name, products.product_id')
            column_names.extend(['Product Name', 'Product ID'])

        if include_segment:
            dynamic_parts.append('segment')
            column_names.append('Segment')

        if include_customer:
            dynamic_parts.append('customer_name, customers.customer_id')
            column_names.extend(['Customer Name', 'Customer ID'])

        if include_region:
            dynamic_parts.append('region')
            column_names.append('Region')

        # Combine the dynamic parts with the initial selection
        final_select_clause = 'ROUND(SUM(sales), 2) as TotalSales' + (', ' + ', '.join(dynamic_parts) if dynamic_parts else '')

        query = self.base_query.format(final_select_clause) + ' ' + self.where_clause
        if self.group_by_clause:
            query += ' ' + self.group_by_clause
        query += ' ' + self.order_by_clause
        print(query)
        # Execute the query and fetch results
        rows = self.connector.fetch_result(query)

        # Prepend the manually constructed column names
        result = [column_names] + rows
        self.initiate_query()

        return result





