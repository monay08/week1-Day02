import pymysql

# MySQL Configuration
DB_HOST = 'localhost'
DB_USER = 'root'
DB_PASSWORD = ''
DB_NAME = 'weekone_db'

def create_db():
    try:
        # Connect without specifying a database
        conn = pymysql.connect(
            host=DB_HOST,
            user=DB_USER,
            password=DB_PASSWORD
        )
        cursor = conn.cursor()

        # Create database if it doesn't exist
        cursor.execute(f"CREATE DATABASE IF NOT EXISTS {DB_NAME}")
        conn.commit()

        # Now connect to the newly created database
        conn.select_db(DB_NAME)

        # Create users table if it doesn't exist
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS users (
                id INT AUTO_INCREMENT PRIMARY KEY,
                name VARCHAR(100) NOT NULL,
                bday VARCHAR(100) NOT NULL,
                address VARCHAR(255) NOT NULL,
                username VARCHAR(100) UNIQUE NOT NULL,
                password VARCHAR(100) NOT NULL
            )
        """)

        conn.commit()
        print("Database and tables created successfully.")

    except pymysql.Error as e:
        print(f"Error creating database or tables: {e}")
    finally:
        cursor.close()
        conn.close()

# Run the function to create the database and tables
create_db()