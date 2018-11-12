from flask import Flask, render_template, flash, redirect, url_for, session, request, logging
from wtforms import Form, StringField, TextAreaField, PasswordField, validators
from functools import wraps
from math import sin, cos, sqrt, atan2, radians
import time
import sqlite3

app = Flask(__name__)



# Index
@app.route('/')
def index():
    return render_template('home.html')



@app.route('/signin')
def signin():
    return render_template('Googlesignin.html')


# @app.route('/offercab')
# def offercab():
#     return render_template('offer_map.html')

@app.route('/dashboard')
def tdashboard():
    return render_template('tdashboard.html')

@app.route('/findcab' , methods=['GET', 'POST'])
def findcab():
    if request.method == 'POST':
        print("here")
        source = request.form['source']
        destination = request.form['destination']
        date = request.form['date']
        ride_time = request.form['time']
        print source
        print destination
        print date
        print ride_time
        R = 6373.0
        lt1=request.form['lat1']
        ln1=request.form['long1']
        lt2=request.form['lat2']
        ln2=request.form['long2']
        print lt1
        print ln1
        print lt2
        print ln2
        lat1 = radians(float(lt1))
        lon1 = radians(float(ln1))
        lat2 = radians(float(lt2))
        lon2 = radians(float(ln2))

        dlon = lon2 - lon1
        dlat = lat2 - lat1

        a = sin(dlat / 2)**2 + cos(lat1) * cos(lat2) * sin(dlon / 2)**2
        c = 2 * atan2(sqrt(a), sqrt(1 - a))

        distance = R * c

        print("Result:", distance)
        con = sqlite3.connect("CabSharing.db")
        cur = con.cursor()
        result = []
        cur.execute("select * from rides_offered" )
        result = cur.fetchall()

        print result[0][8]
        date=time.strptime(result[0][8],"%Y-%m-%d")
        print date

        for i in range(len(result)):
            print result[i][0]

        # print("Here")
        # for data in result:
        #     print(data)
        # return render_template('findresults.html' , result = result)
        return render_template('about.html')
    return render_template('find.html')

@app.route('/rides')
def rides():
    con = sqlite3.connect("CabSharing.db")
    cur = con.cursor()
    result = []
    username = session['username']
    cur.execute("select * from rides_offered where username = ?",[username])
    result = cur.fetchall()
    return render_template('rides.html' , result = result)

@app.route('/bookings')
def bookings():
    return render_template('bookings.html')

@app.route('/messages')
def messages():
    return render_template('messages.html')


@app.route('/contactus')
def contactus():
    return render_template('about.html')


# class OfferedSeat(Form):
#     source = StringField('Source')
#     destination = StringField('Destination')
#     date = StringField('Date')
#     time = StringField('Time ')
#     offeredSeats = StringField('Offered Seats')
#     offeredPrice = StringField('Offered Price')

@app.route('/offercab', methods=['GET', 'POST'])
def offer():
    if request.method == 'POST':
        # Get Form Fields
        form = {}
        form['details']= ""
        form['source'] = request.form['source']
        form['destination'] = request.form['destination']
        form['date'] = request.form['date']
        form['time'] = request.form['time']
        form['price'] = request.form['price']
        form['numberOfSeats'] = request.form['seats']
        # details = request.form['details']
        form['lat1'] = request.form['lat1']
        form['long1'] = request.form['long1']
        form['lat2'] = request.form['lat2']
        form['long2'] = request.form['long2']
        form['valid'] = 0
        username=session['username']
        with sqlite3.connect("CabSharing.db") as con:
            cur = con.cursor()
            cur.execute("INSERT INTO rides_offered(userName, source, destination, lat1, long1, lat2, long2, offeredDate, offeredTime, offeredPrice, offeredSeats, details, valid) VALUES(? , ? , ? , ? , ? , ? , ? , ? , ? , ? ,? , ? , ? )" , (username , form['source'], form['destination'], form['lat1'], form['long1'], form['lat2'], form['long2'], form['date'], form['time'], form['price'], form['numberOfSeats'], form['details'], form['valid'], ))
            con.commit()

        flash('Your Post has been put live ', 'success')


    # form = OfferedSeat(request.form)
    # if request.method == 'POST' and form.validate():
    #     source = form.source.data
    #     destination = form.destination.data
    #     date = form.date.data
    #     time = form.time.data
    #     offeredPrice = form.offeredPrice.data
    #     offeredPrice = int(offeredPrice)
    #     offeredSeats = form.offeredSeats.data
    #     offeredSeats = int(offeredSeats)
    #
    #     with sqlite3.connect("CabSharing.db") as con:
    #         cur = con.cursor()
    #         cur.execute("INSERT INTO rides_offered(userName , source, destination, offeredDate, offeredTime , offeredPrice , offeredSeats , valid) VALUES(? , ? , ? , ? , ? , ? , ? , ? )" , ("tarun" , source, destination, date, time, offeredPrice, offeredSeats , 0))
    #
    #         con.commit()
    #
    #     flash('Your Post has been put live ', 'success')
    #
        return render_template('rides.html' )
    return render_template('offer_map.html')


class RegisterForm(Form):
    name = StringField('Name', [validators.Length(min=1, max=50)])
    username = StringField('Username', [validators.Length(min=4, max=25)])
    email = StringField('Email', [validators.Length(min=6, max=50)])
    contact = StringField('Contact', [validators.Length(min=6, max=15)])
    address = StringField('Address', [validators.Length(min=6, max=100)])
    password = PasswordField('Password', [
        validators.DataRequired(),
        validators.EqualTo('confirm', message='Passwords do not match')
    ])
    confirm = PasswordField('Confirm Password')



# User Register
@app.route('/register', methods=['GET', 'POST'])
def register():
    form = RegisterForm(request.form)
    if request.method == 'POST' and form.validate():
        name = form.name.data
        email = form.email.data
        username = form.username.data
        # password = sha256_crypt.encrypt(str(form.password.data))
        password = form.password.data
        contact = form.contact.data
        address = form.address.data


        with sqlite3.connect("CabSharing.db") as con:
            cur = con.cursor()
            cur.execute("INSERT INTO users(name, email, username, password,phone,address) VALUES(?,?,?,?,?,?)", (name, email, username, password,contact,address))

            con.commit()

        flash('You are now registered and can log in', 'success')

        return redirect(url_for('login'))
    return render_template('register.html', form=form)


# User login 
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        # Get Form Fields
        username = request.form['username']
        password_candidate = request.form['password']

        # # Create cursor
        # cur = mysql.connection.cursor()

        # # Get user by username
        # result = cur.execute("SELECT * FROM users WHERE username = %s", [username])

        con = sqlite3.connect("CabSharing.db")
        # con.row_factory = sqlite3.Row
        cur = con.cursor()
        result = []
        cur.execute("select * from users where username = ?",[username])
        result = cur.fetchall()
        count = len(result)

        # print(count)
        # for data in result:
        #     print ("---------------------sanket-------------")
        #     print (data)
        #     print ("--------------------------------------")
        #     password = data[1]
        #     print(password)

        # print(result.rowcount)
        if (count) > 0:
            # Get stored hash
            # data = result.fetchone()
            password =""
            for data in result:
                print ("---------------------sanket-------------")
                print (data)
                print ("--------------------------------------")
                password = data[1]
                print(password)

                print("here")
                print(password)
                # Compare Passwords
                # if sha256_crypt.verify(password_candidate, password):
                if (password_candidate == password):
                    # Passed
                    session['logged_in'] = True
                    session['username'] = username

                    # flash('You are now logged in', 'success')
                    # return redirect(url_for('dashboard'))
                    return render_template('tdashboard.html' , name = username )
                else:
                    error = 'Invalid login'
                    return render_template('login.html', error=error)
                # Close connection
                cur.close()
        else:
            error = 'Username not found'
            return render_template('login.html', error=error)

    return render_template('login.html')


# Check if user logged in
def is_logged_in(f):
    @wraps(f)
    def wrap(*args, **kwargs):
        if 'logged_in' in session:
            return f(*args, **kwargs)
        else:
            flash('Unauthorized, Please login', 'danger')
            return redirect(url_for('login'))
    return wrap

# Logout
@app.route('/logout')
@is_logged_in
def logout():
    session.clear()
    flash('You are now logged out', 'success')
    return redirect(url_for('login'))


if __name__ == '__main__':
    app.secret_key='secret123'
    app.run(debug=True)
