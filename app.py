from flask import Flask, request, render_template, session, redirect, url_for
import sqlite3
app = Flask(__name__, static_url_path='/static')
app.secret_key ='24'  # Change this to a random secret key
DATABASE = 'detail.db'
# You can insert data using excel file

# def insert_data_from_excel(excel_file):
#     df = pd.read_excel(excel_file)
#     data_to_insert = df.to_dict(orient='records')

#     conn = sqlite3.connect(DATABASE)
#     cursor = conn.cursor()
#     for record in data_to_insert:
#         cursor.execute('INSERT INTO user(username,email,password,usertype) VALUES (?, ?, ?,?)',
#                        (record['username'], record['email'], record['password'],'user'))
#     conn.commit()
#     conn.close()
#     print("data inserted successFully")
def create_database():
    conn = sqlite3.connect(DATABASE)
    cursor = conn.cursor()
    # Create a table
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS user(
        username TEXT PRIMARY KEY,
        email TEXT NOT NULL,
        password TEXT NOT NULL,
        usertype TEXT NOT NULL
    )
''')
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS flights(
        flight_number TEXT PRIMARY KEY,
        flight_name TEXT NOT NULL,
        source TEXT NOT NULL,
        destination TEXT NOT NULL,
        fare REAL NOT NULL,
        flight_atime TEXT NOT NULL,
        flight_dtime TEXT NOT NULL,
        flight_date TEXT NOT NULL,
        available_seats INTEGER NOT NULL DEFAULT 60
    )
''')
    conn.execute('''
    CREATE TABLE IF NOT EXISTS bookings (
        name TEXT NOT NULL,
        flight_number TEXT NOT NULL,
        flight_atime TEXT NOT NULL,
        available_seats INTEGER NOT NULL,
        PRIMARY KEY (name,flight_number)
    )
''')
    
    conn.commit()
    conn.close()

create_database()

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        usertype = request.form['usertype']

        # Connect to the database
        conn = sqlite3.connect('detail.db')
        cursor = conn.cursor()

        cursor.execute("SELECT username, password, usertype FROM user WHERE username = ?", (username,))
        user = cursor.fetchone()
        conn.close()

        if user and user[1] == password:
            session['username'] = user[0]
            session['usertype'] = user[2]  # Store usertype in the session
            if user[2]=='admin':
                return redirect(url_for('admin_details'))
            else:
                return redirect(url_for('user_details'))
        else:
            return render_template('Fail.html')

    return render_template('login.html')


@app.route('/user_details')
def user_details():
    if 'username' in session:
        conn = sqlite3.connect(DATABASE)
        cursor = conn.cursor()

        cursor.execute("SELECT username, email FROM user WHERE username = ?", (session['username'],))
        data = cursor.fetchone()
        conn.close()

        return render_template('user_details.html', data=data)
    else:
        return redirect(url_for('login'))
@app.route('/admin_details')
def admin_details():
    if 'username' in session:
        conn = sqlite3.connect(DATABASE)
        cursor = conn.cursor()

        cursor.execute("SELECT username, email FROM user WHERE username = ?", (session['username'],))
        data = cursor.fetchone()
        conn.close()

        return render_template('admin_details.html', data=data)
    else:
        return redirect(url_for('login'))

@app.route('/logout')
def logout():
    session.pop('username', None)
    return redirect(url_for('index'))

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        email = request.form['email']
        password = request.form['password']

        # Connect to the database
        conn = sqlite3.connect(DATABASE)
        cursor = conn.cursor()

        # Insert user registration data into the database
        cursor.execute('INSERT INTO user (username, email, password, usertype) VALUES (?, ?, ?, ?)',(username, email, password, 'user'))

        # Commit changes and close the connection
        conn.commit()
        conn.close()

        return render_template('Success.html')

    return render_template('register.html')
@app.route('/adminreg', methods=['GET', 'POST'])
def adminreg():
    if request.method == 'POST':
        secret_key = request.form['secret_key']
        
        # Check if the secret key matches the expected value
        if secret_key == 'hello':  # Replace with the actual secret key
            return render_template('adminreg.html')
        else:
            return "Invalid secret key. Access denied."

    return render_template('admin_key.html')
@app.route('/register_admin',methods=['GET','POST'])
def register_admin():
    username = request.form['username']
    email = request.form['email']
    password = request.form['password']
    usertype = request.form['usertype']
    # Connect to the admin database
    conn = sqlite3.connect('detail.db')
    cursor = conn.cursor()

    # Insert admin registration data into the admin database
    cursor.execute('INSERT INTO user(username, email, password,usertype) VALUES (?,?,?,?)',
                   (username, email, password,usertype))

    # Commit changes and close the connection
    conn.commit()
    conn.close()

    return render_template('Success.html')
# Admin adding flights

@app.route('/add_flight', methods=['GET', 'POST'])
def add_flight():
    if request.method == 'POST':
        flight_number = request.form['flight_number']
        flight_name = request.form['flight_name']
        source = request.form['source']
        destination = request.form['destination']
        fare = request.form['fare']
        flight_atime = request.form['flight_atime']
        flight_dtime = request.form['flight_dtime']
        flight_date = request.form['flight_date']

        # Connect to the database
        conn = sqlite3.connect(DATABASE)
        cursor = conn.cursor()

        # Insert flight data into the flights table
        cursor.execute('''
            INSERT INTO flights (flight_number, flight_name, source, destination,fare,flight_atime,flight_dtime,flight_date)
            VALUES (?, ?, ?, ?, ?, ?, ?,?)
        ''', (flight_number, flight_name, source, destination, fare, flight_atime, flight_dtime,flight_date))

        # Commit changes and close the connection
        conn.commit()
        conn.close()

        return render_template('Flight_s.html')

    return render_template('add_flight.html')


# Admin removes the flight

@app.route('/remove_flights', methods=['GET', 'POST'])
def remove_flights():
    if request.method == 'POST':
        flight_number = request.form['flight_number']
        # Connect to the database
        conn = sqlite3.connect(DATABASE)
        cursor = conn.cursor()

        # Delete the flight based on flight_number
        cursor.execute('DELETE FROM flights WHERE flight_number = ?', (flight_number,))

        # Commit changes and close the connection
        conn.commit()
        conn.close()
        return render_template('Flight_r.html')
    # Fetch and display the list of flights
    conn = sqlite3.connect(DATABASE)
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM flights')
    flights = cursor.fetchall()
    conn.close()
    return render_template('remove_flights.html', flights=flights)
# For searching of flights for user
@app.route('/search_flight', methods=['GET','POST'])
def search_flight():
    if request.method == 'POST':
        search_date = request.form['search_date']
        search_time = request.form['search_time']
        # Connect to the database
        conn = sqlite3.connect(DATABASE)
        cursor = conn.cursor()
        # Query flights based on search date and time
        cursor.execute('SELECT * FROM flights WHERE flight_date = ? AND flight_atime = ?', (search_date, search_time))
        matching_flights = cursor.fetchall()
        conn.close()
        return render_template('search_flight.html', flights=matching_flights)
    return render_template('search_flight.html', flights=None)
# For Booking the tickets
@app.route('/book_ticket')
def book_ticket():
    flight_number = request.args.get('flight_number')
    flight_name = request.args.get('flight_name')
    flight_date = request.args.get('flight_date')
    source = request.args.get('source')
    destination = request.args.get('destination')
    arrival_time = request.args.get('arrival_time')
    departure_time = request.args.get('departure_time')
    fare = request.args.get('fare')

    return render_template('book_ticket.html', flight_number=flight_number, flight_name=flight_name, flight_date=flight_date, source=source, destination=destination, arrival_time=arrival_time, departure_time=departure_time, fare=fare)
# For confirming Ticket

@app.route('/confirm_ticket', methods=['POST'])
def confirm_ticket():
    # Retrieve flight details from form
    if request.method == 'POST':
        username=request.form.get('username')
        flight_number = request.form.get('flight_number')
        arrival_time = request.form.get('arrival_time')
        conn = sqlite3.connect(DATABASE)
        c = conn.cursor()
        # Check available seats and book the seat
        c.execute('SELECT available_seats FROM flights WHERE flight_number = ?', (flight_number,))
        available_seats = c.fetchone()[0]
        if available_seats <= 0:
            conn.close()
            return render_template('fully_booked.html')
        try:
            available_seats1=available_seats-1
            c.execute('INSERT INTO bookings (name, flight_number, flight_atime, available_seats) VALUES (?, ?, ?, ?)',(username, flight_number,arrival_time,available_seats1))
            c.execute('UPDATE flights SET available_seats = available_seats - 1 WHERE flight_number = ?', (flight_number,))
            conn.commit()
            conn.close()
            return render_template('success_booked.html')
        except sqlite3.IntegrityError as e:
            if "UNIQUE constraint failed" in str(e):
                return render_template('already_exists.html')
    return render_template('book_ticket.html', flight_number=flight_number, flight_atime=arrival_time)
@app.route('/view_bookings', methods=['GET', 'POST'])
def view_bookings():
    if request.method == 'POST':
        flight_number = request.form['flight_number']
        flight_atime = request.form['flight_atime']
        # Connect to the database
        conn = sqlite3.connect(DATABASE)
        cursor = conn.cursor()
        # Delete the flight based on flight_number
        cursor.execute('select * FROM bookings WHERE flight_number = ? AND flight_atime=?', (flight_number,flight_atime))
        flights = cursor.fetchall()

        # Commit changes and close the connection
        conn.commit()
        conn.close()
        return render_template('view_bookings.html', flights=flights)
    return render_template('view_bookings.html')

@app.route('/view_mybokings', methods=['GET', 'POST'])
def view_mybokings():
    username = request.args.get('username')
    # Connect to the database
    conn = sqlite3.connect(DATABASE)
    cursor = conn.cursor()
    # Delete the flight based on flight_number
    print(username)
    cursor.execute('SELECT * FROM bookings WHERE name = ?', (username,))
    flights = cursor.fetchall()
    # Commit changes and close the connection
    conn.commit()
    conn.close()
    return render_template('view_mybokings.html', flights=flights)



if __name__ == '__main__':
    app.run(debug=True)