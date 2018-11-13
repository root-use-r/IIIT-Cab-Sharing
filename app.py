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


# by shubham
@app.route('/signin')
def signin():
    return render_template('Googlesignin.html')



# @app.route('/rides_found/<string:userName>/', methods=['GET', 'POST'])
# def ride(userName):
#     con = sqlite3.connect("CabSharing.db")
#     cur = con.cursor()
#     result = cur.execute("SELECT * FROM rides_offered WHERE userName = ?", [userName])
#     rides = cur.fetchone()
#     # print (rides)
#     result1 = cur.execute("SELECT * FROM USERS WHERE userName = ?", [userName])
#     user = cur.fetchone()
#     return render_template( 'ride.html', rides=rides,user=user )
# by shubham
@app.route('/rides_found/<string:rideId>/<string:userName>', methods=['GET', 'POST'])
def ride(rideId,userName):
    con = sqlite3.connect("CabSharing.db")
    cur = con.cursor()
    result = cur.execute("SELECT * FROM rides_offered WHERE rideId = ?", [rideId])
    rides = cur.fetchone()
    # print (rides)
    result1 = cur.execute("SELECT * FROM USERS WHERE userName = ?", [userName])
    user = cur.fetchone()

    cur.execute("select * from rides_requested where rideId = ? and username = ? " , ( rideId , session['username'] ) )
    taken_result = cur.fetchone()

    print(taken_result)

    if taken_result :
        return render_template( 'ride.html', rides=rides , myUserName=session['username'] , flag=1, user=user  )
    
    return render_template( 'ride.html', rides=rides , myUserName=session['username'] , flag=0, user=user  )


@app.route('/rides_request/<string:rideId>/<string:userName>', methods=['GET', 'POST'])
def rides_request(rideId,userName):
    con = sqlite3.connect("CabSharing.db")
    cur = con.cursor()

    cur.execute("SELECT * FROM rides_offered WHERE rideId = ?", [rideId])
    rides = cur.fetchone()

    print(rides)

    accepted = 0
    print(rideId)
    print(userName)
    print(accepted)

    cur.execute("INSERT INTO rides_requested(rideId , username , accepted ) VALUES( ? , ? , ? ) ", (rideId, userName,accepted) )

    cur.execute("SELECT * FROM USERS WHERE userName = ?", [userName])
    user = cur.fetchone()
    print(user)
    con.commit()

    return render_template( 'ride.html', rides=rides , myUserName = session['username'] , flag =1  , user=user  )



# by shubham

# @app.route('/rides_found')
# def foundrides():
#     # Create cursor
#     name=[]
#     con = sqlite3.connect("CabSharing.db")
#     cur = con.cursor()

#     # Get rides
#     # Show rides only from the user logged in
#     result = cur.execute("SELECT * FROM rides_offered  " )

#     rides = cur.fetchall()
#     total_rides = len(rides)
#     # print
#     # print rides
#     for i in range(total_rides):
#         result1 = cur.execute("SELECT * FROM USERS WHERE userName = ?", [rides[i][1]] )
#         user = cur.fetchone()
#         # print user[0][2]
#         name.append(user[2])
#     # if result > 0:
#     return render_template('dashboard.html', rides=rides, total_rides=total_rides,name=name)
#     # else:
#     #     msg = 'No Articles Found'
#     #     return render_template('dashboard.html', msg=msg)
#     # Close connection
#     cur.close()

# by shubham


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
        date=time.strptime(date,"%Y-%m-%d")
        ride_time = request.form['time']
        
        lt1=request.form['lat1']
        ln1=request.form['long1']
        lt2=request.form['lat2']
        ln2=request.form['long2']
        
        lat1 = radians(float(lt1))
        lon1 = radians(float(ln1))
        lat2 = radians(float(lt2))
        lon2 = radians(float(ln2))

    

        con = sqlite3.connect("CabSharing.db")
        cur = con.cursor()
        result = []
        cur.execute("select * from rides_offered" )
        result = cur.fetchall()
        name=[]
        data_to_display=[]
        for i in range(len(result)):
            tempsourcelat = radians(float(result[i][4]))
            tempsourcelong = radians(float(result[i][5]))
            tempdestinationlat = radians(float(result[i][6]))
            tempdestinationlong = radians(float(result[i][7]))
            
            R = 6373.0
            dlon = tempsourcelong - lon1
            dlat = tempsourcelat - lat1

            a = sin(dlat / 2)**2 + cos(lat1) * cos(lat2) * sin(dlon / 2)**2
            c = 2 * atan2(sqrt(a), sqrt(1 - a))

            distance1 = R * c

            dlon = lon2 - tempdestinationlong
            dlat = lat2 - tempdestinationlat

            a = sin(dlat / 2)**2 + cos(lat1) * cos(lat2) * sin(dlon / 2)**2
            c = 2 * atan2(sqrt(a), sqrt(1 - a))

            distance2 = R * c

            if(distance1<5 and distance2<5):
                data_to_display.append(result[i])
                # user.append(result[i][])
                result1 = cur.execute("SELECT * FROM USERS WHERE userName = ?", [result[i][1]] )
                user = cur.fetchone()
                # print user[0][2]
                name.append(user[2])



        total_rides= len(data_to_display)

        return render_template('rides_found.html',rides=data_to_display,total_rides=total_rides,name=name )
    return render_template('find.html')

@app.route('/rides')
def rides():
    con = sqlite3.connect("CabSharing.db")
    cur = con.cursor()
    result = []
    username = session['username']
    cur.execute("select * from rides_offered where username = ?",[username])
    result = cur.fetchall()
    count = len(result)
    return render_template('rides.html' , result = result , count = count)

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

        with sqlite3.connect("CabSharing.db") as con:
            cur = con.curson()
            cur.execute("select * from rides_offered where username = ?", [session['username']])
            result= cur.fetchall()
            count = len(result)
            return render_template('rides.html' , result = result , count = count)
            con.commit()

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
        return render_template('rides.html' , result)
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
