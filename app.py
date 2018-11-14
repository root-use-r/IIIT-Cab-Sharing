import requests
from flask import Flask, render_template, flash, redirect, url_for, session, request, logging
from wtforms import Form, StringField, TextAreaField, PasswordField, validators
from functools import wraps
from math import sin, cos, sqrt, atan2, radians
import time
from datetime import date
from passlib.hash import sha256_crypt
import sqlite3
from flask_mail import Mail
from flask_mail import Message
import random

app = Flask(__name__)
mail = Mail(app)

app.config['MAIL_SERVER']='smtp.gmail.com'
app.config['MAIL_PORT'] = 465
app.config['MAIL_USERNAME'] = 'sankettheflash@gmail.com'
app.config['MAIL_PASSWORD'] = 'Sanky@711'
app.config['MAIL_USE_TLS'] = False
app.config['MAIL_USE_SSL'] = True
mail = Mail(app)





@app.route('/')
def index():
    return render_template('home.html')


@app.route('/signin')
def signin():
    return render_template('Googlesignin.html')


@app.route('/booking_history')
def booking_history():
    con = sqlite3.connect("CabSharing.db")
    cur = con.cursor()
    user_bookings=[]

    username = session['username']
    
    print(username)
    cur.execute("select * from rides_requested where username = ? and accepted = 1",[username])

    result = cur.fetchall()
    print()
    print(result)

    today = date.today()
    today = time.strptime( str(today) , "%Y-%m-%d")

    for i in range(len(result)):
        cur.execute("select * from rides_offered where rideId = ? ", [result[i][0]]  )
        final_result = cur.fetchone()
        user_date=time.strptime(final_result[8],"%Y-%m-%d")
        if user_date <= today:
            user_bookings.append(final_result)
    print(user_bookings)
    cur.close()

    return render_template('booking_history.html',result = user_bookings , count=len(user_bookings))



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

@app.route('/rides_accept/<string:rideId>/<string:userName>', methods=['GET', 'POST'])
@is_logged_in
def ride_accept(rideId,userName):
    
    con = sqlite3.connect("CabSharing.db")
    cur = con.cursor()
    cur.execute("select * from rides_offered where rideid = ?", [rideId])
    temp_result= cur.fetchall()
    con.commit()


    reason='Your ride from '+ str(temp_result[0][2]) + ' to ' + str(temp_result[0][3]) +' at ' + str(temp_result[0][8])+ ' is confirmed.'
    con = sqlite3.connect("CabSharing.db")
    cur = con.cursor()
    cur.execute("update rides_requested set accepted=1 where rideId = ? and username = ?" , ( rideId , userName )) 

    cur.execute("select * from users where username = ? " , [userName] )
    contact = cur.fetchone()

    cur.execute("INSERT INTO notification(rideId , username , detail ) VALUES( ? , ? , ? ) ", (rideId, userName , reason) )
    con.commit()
    cur.execute("select * from rides_offered where rideId = ?", [rideId])
    ride_data=cur.fetchone()
    # print ride_data
    # print ride_data[14]
    seats_left=ride_data[14] - 1
    cur.execute("update rides_offered set seatsleft=? where rideId = ? " , (seats_left , rideId )) 
    if seats_left==0:
        reason='Your ride from '+ str(temp_result[0][2]) + ' to ' + str(temp_result[0][3]) +' at ' + str(temp_result[0][8])+ ' is cancelled because car is full.'
        cur.execute("update rides_requested set accepted=3 where rideId = ? and accepted=0" , [rideId]) 
        cur.execute("select * from rides_requested where accepted=3 and rideId= ?", [rideId])
        ridecancelled=cur.fetchall()
        for i in range(len(ridecancelled)):
            cur.execute("INSERT INTO notification(rideIride.htmld , username , detail ) VALUES( ? , ? , ? ) ", (rideId, ridecancelled[i][1] , reason) )
   
    con.commit()
    cur.close()


    con = sqlite3.connect("CabSharing.db")
    cur = con.cursor()
    result = cur.execute("SELECT * FROM rides_offered WHERE rideId = ?", [rideId])
    rides = cur.fetchone()
    result1 = cur.execute("SELECT * FROM USERS WHERE userName = ?", [session['username']])
    user = cur.fetchone()

    cur.execute("select * from rides_requested where rideId = ? and username = ? " , ( rideId , session['username'] ) )
    taken_result = cur.fetchone()

    cur.execute("select * from rides_requested where rideId = ? and accepted = 0" , [rideId] )
    ride_request=cur.fetchall()

    user_who_requested=[]
    for i in range(len(ride_request)):
        cur.execute("SELECT * FROM USERS WHERE userName = ?", [ride_request[i][1]])
        temp_user=cur.fetchone()
        user_who_requested.append(temp_user)


    cur.execute(" select * from rides_requested where rideId = ? and accepted = 1 " , [rideId] )
    temp_users_whose_ride_accepted = cur.fetchall()
    
    # print(temp_users_whose_ride_accepted)
    # print("mother")

    users_whose_ride_accepted = []
    j=0
    for i in range(len(temp_users_whose_ride_accepted) ):
        users_whose_ride_accepted.append( temp_users_whose_ride_accepted[i][1] )
        j=j+1
 
    # print()
    # print(j)
    # print()
    # cur.execute("select * from rides_requested where rideId = ? and accepted = 1" , [rideId] )
    # ride_accepted=cur.fetchall()
    if taken_result :
        return render_template( 'ride.html', contact=contact , rides=rides ,  myUserName=session['username'] , flag=1, user=user ,user_who_requested=user_who_requested , users_whose_ride_accepted=users_whose_ride_accepted , len_users_whose_ride_accepted = j )
    
    return render_template( 'ride.html',contact=contact, rides=rides,  myUserName=session['username'] , flag=0, user=user ,user_who_requested=user_who_requested, users_length=len(user_who_requested) , users_whose_ride_accepted=users_whose_ride_accepted , len_users_whose_ride_accepted = j )



@app.route('/rides_reject/<string:rideId>/<string:userName>', methods=['GET', 'POST'])
@is_logged_in
def ride_reject(rideId,userName):

    con = sqlite3.connect("CabSharing.db")
    cur = con.cursor()
    cur.execute("select * from rides_offered where rideid = ?", [rideId])
    temp_result= cur.fetchall()
    con.commit()


    reason='Your ride from '+ str(temp_result[0][2]) + ' to ' + str(temp_result[0][3]) +' at ' + str(temp_result[0][8])+ ' is rejected by owner.'

    con = sqlite3.connect("CabSharing.db")
    cur = con.cursor()
    cur.execute("update rides_requested set accepted=2 where rideId = ? and username = ?" , ( rideId , userName )) 
    cur.execute("INSERT INTO notification(rideId , username , detail ) VALUES( ? , ? , ? ) ", (rideId, userName , reason) )
    con.commit()
    cur.close()


    con = sqlite3.connect("CabSharing.db")
    cur = con.cursor()
    result = cur.execute("SELECT * FROM rides_offered WHERE rideId = ?", [rideId])
    rides = cur.fetchone()
    result1 = cur.execute("SELECT * FROM USERS WHERE userName = ?", [session['username']])
    user = cur.fetchone()

    cur.execute("select * from users where username = ? " , [userName])
    contact = cur.fetchone()


    cur.execute("select * from rides_requested where rideId = ? and username = ? " , ( rideId , session['username'] ) )
    taken_result = cur.fetchone()

    cur.execute("select * from rides_requested where rideId = ? and accepted = 0" , [rideId] )
    ride_request=cur.fetchall()

    user_who_requested=[]
    for i in range(len(ride_request)):
        cur.execute("SELECT * FROM USERS WHERE userName = ?", [ride_request[i][1]])
        temp_user=cur.fetchone()
        user_who_requested.append(temp_user)

    
    print(user_who_requested)



    cur.execute(" select * from rides_requested where rideId = ? and accepted = 1 " , [rideId] )
    temp_users_whose_ride_accepted = cur.fetchall()
    
    # print(temp_users_whose_ride_accepted)
    # print("mother")

    users_whose_ride_accepted = []
    j=0
    for i in range(len(temp_users_whose_ride_accepted)):
        users_whose_ride_accepted.append( temp_users_whose_ride_accepted[i][1] )
        j=j+1




    if taken_result :
        return render_template( 'ride.html',contact=contact, rides=rides , myUserName=session['username'] , flag=1, user=user ,user_who_requested=user_who_requested , users_whose_ride_accepted=users_whose_ride_accepted , len_users_whose_ride_accepted = j)
    
    return render_template( 'ride.html', contact = contact ,  rides=rides , myUserName=session['username'] , flag=0, user=user ,user_who_requested=user_who_requested, users_length=len(user_who_requested) , users_whose_ride_accepted=users_whose_ride_accepted , len_users_whose_ride_accepted = j)




@app.route('/rides_found/<string:rideId>/<string:userName>', methods=['GET', 'POST'])
@is_logged_in
def ride(rideId,userName):
    con = sqlite3.connect("CabSharing.db")
    cur = con.cursor()
    result = cur.execute("SELECT * FROM rides_offered WHERE rideId = ?", [rideId])
    rides = cur.fetchone()
    result1 = cur.execute("SELECT * FROM USERS WHERE userName = ?", [userName])
    user = cur.fetchone()

    cur.execute("select * from users where username = ? " , [userName])
    contact = cur.fetchone()

    cur.execute("select * from rides_requested where rideId = ? and username = ? " , ( rideId , session['username'] ) )
    taken_result = cur.fetchone()

    cur.execute("select * from rides_requested where rideId = ? and accepted = 0" , [rideId] )
    ride_request=cur.fetchall()

    user_who_requested=[]
    for i in range(len(ride_request)):
        cur.execute("SELECT * FROM USERS WHERE userName = ?", [ride_request[i][1]])
        temp_user=cur.fetchone()
        user_who_requested.append(temp_user)

    
    # print(user_who_requested)
    cur.execute(" select * from rides_requested where rideId = ? and accepted = 1 " , [rideId] )
    temp_users_whose_ride_accepted = cur.fetchall()
    
    # print(temp_users_whose_ride_accepted)
    # print("mother")

    users_whose_ride_accepted = []
    j=0
    for i in range(len(temp_users_whose_ride_accepted)):
        users_whose_ride_accepted.append( temp_users_whose_ride_accepted[i][1] )
        j=j+1



    if taken_result :
        return render_template( 'ride.html', contact = contact, rides=rides , myUserName=session['username'] , flag=1, user=user ,user_who_requested=user_who_requested ,  users_whose_ride_accepted=users_whose_ride_accepted , len_users_whose_ride_accepted = j)
    
    return render_template( 'ride.html', contact=contact ,  rides=rides , myUserName=session['username'] , flag=0, user=user ,user_who_requested=user_who_requested, users_length=len(user_who_requested) ,  users_whose_ride_accepted=users_whose_ride_accepted , len_users_whose_ride_accepted = j)


@app.route('/rides_request/<string:rideId>/<string:userName>', methods=['GET', 'POST'])
@is_logged_in
def rides_request(rideId,userName):
    con = sqlite3.connect("CabSharing.db")
    cur = con.cursor()
    cur.execute("SELECT * FROM rides_offered WHERE rideId = ?", [rideId])
    rides = cur.fetchone()
    accepted = 0

    cur.execute("select * from users where username = ? " , [userName] )
    contact = cur.fetchone()


    cur.execute("INSERT INTO rides_requested(rideId , username , accepted ) VALUES( ? , ? , ? ) ", (rideId, userName,accepted) )

    cur.execute("SELECT * FROM USERS WHERE userName = ?", [userName])
    user = cur.fetchone()
    con.commit()


    cur.execute(" select * from rides_requested where rideId = ? and accepted = 1 " , [rideId] )
    temp_users_whose_ride_accepted = cur.fetchall()
    
    # print(temp_users_whose_ride_accepted)
    # print("mother")

    users_whose_ride_accepted = []
    j=0
    for i in range(len(temp_users_whose_ride_accepted)):
        users_whose_ride_accepted.append( temp_users_whose_ride_accepted[2] )
        j=j+1

    

    return render_template( 'ride.html', contact=contact, rides=rides , myUserName = session['username'] , flag =1  , user=user  ,  users_whose_ride_accepted=users_whose_ride_accepted , len_users_whose_ride_accepted = j)






@app.route('/dashboard')
@is_logged_in
def tdashboard():
    username=session['username']
    with sqlite3.connect("CabSharing.db") as con:
        cur = con.cursor()
        cur.execute("select * from users where userName = ? ", [username])
        name = cur.fetchone()

        result = []
        cur.execute("select * from notification where username = ? ", [username])
        result = cur.fetchall()

    return render_template('tdashboard.html' , username = name[2] , result= result , count = len(result))

@app.route('/findcab' , methods=['GET', 'POST'])
def findcab():
    if request.method == 'POST':
        print("here")
        source = request.form['source']
        destination = request.form['destination']
        date = request.form['date']
        date = date[:10]
        print date
        date=time.strptime(date,"%m/%d/%Y")
        # ride_time = request.form['time']
        
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
            temp_date=time.strptime(result[i][8],"%Y-%m-%d")

            if(distance1<5 and distance2<5 and temp_date>=date and result[i][13]==1 and result[i][14]>0):
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
@is_logged_in
def rides():
    con = sqlite3.connect("CabSharing.db")
    cur = con.cursor()
    result = []
    username = session['username']
    cur.execute("select * from rides_offered where username = ? and valid = 1",[username])
    result = cur.fetchall()
    count = len(result)
    con.commit()
    return render_template('rides.html' , result = result , count = count , flag = 0)

@app.route('/rides_delete/<string:rideId>', methods=['GET', 'POST'])
@is_logged_in
def rides_delete(rideId):
    con = sqlite3.connect("CabSharing.db")
    cur = con.cursor()
    cur.execute(" update rides_offered set valid=0 where rideId = ? and username = ? " , (rideId,session['username']) )
    con.commit()
    cur.close()
    return redirect(url_for('rides'))



@app.route('/see_cotravellers/<string:rideId>/<string:userName>', methods=['GET', 'POST'])
@is_logged_in
def see_cotravellers(rideId,userName):
    con = sqlite3.connect("CabSharing.db")
    cur = con.cursor()
    cotravellers = []
    result=[]
    temp_users_whose_ride_accepted=[]
    
    cur.execute(" select * from rides_requested where rideId = ? and accepted = 1 " , [rideId] )
    temp_users_whose_ride_accepted = cur.fetchall()

    cur.execute("SELECT * FROM rides_offered WHERE  username = ? and rideid = ?",  (userName, rideId ) )
    result = cur.fetchall()

    cur.execute("SELECT * FROM users WHERE  username = ? ", [userName] )
    cotravellers.append(cur.fetchone())

    cur.execute(" select * from rides_requested where rideId = ? and accepted = 1 " , [rideId] )
    temp_users_whose_ride_accepted = cur.fetchall()

    # print(temp_users_whose_ride_accepted)


    for i in range(len(temp_users_whose_ride_accepted)):
        cur.execute("SELECT * FROM users WHERE  username = ? ", [temp_users_whose_ride_accepted[i][1]] )
        temp =  cur.fetchone()
        cotravellers.append( temp)  

    for i in range(len(cotravellers)):
        print(cotravellers[i])
    # print(len(cotravellers))
    # print(result)

    return render_template('see_cotravellers.html' , result = result ,cotravellers = cotravellers , len_cotravellers = len(cotravellers) , admin = cotravellers[0][2])



@app.route('/past_rides')
@is_logged_in
def past_rides():
    con = sqlite3.connect("CabSharing.db")
    cur = con.cursor()
    result = []
    username = session['username']
    cur.execute("select * from rides_offered where username = ? and valid = ?",(username , 0) )
    result = cur.fetchall()
    count = len(result)
    print()
    print(result)
    print(count)
    con.commit()
    return render_template('past_rides.html' , result = result , count = count)

@app.route('/bookings')
@is_logged_in
def bookings():
    con = sqlite3.connect("CabSharing.db")
    cur = con.cursor()
    user_bookings=[]
    username = session['username']
    cur.execute("select * from rides_requested where username = ? and accepted = 1",[username])
    result = cur.fetchall()
    for i in range(len(result)):
        cur.execute("select * from rides_offered where rideId = ? and valid = 1",[result[i][0]] )
        temp=cur.fetchone()
        if temp:
            user_bookings.append(temp)
    cur.close()

    return render_template('bookings.html',result = user_bookings,count=len(user_bookings))

@app.route('/messages')
@is_logged_in
def messages():
    return render_template('messages.html')


@app.route('/contactus')
def contactus():
    return render_template('about.html')




@app.route('/offercab', methods=['GET', 'POST'])
@is_logged_in
def offer():
    if request.method == 'POST':
        form = {}
        form['details']= ""
        form['source'] = request.form['source']
        form['destination'] = request.form['destination']
        form['date'] = request.form['date']
        form['time'] = request.form['time']
        form['price'] = request.form['price']
        form['numberOfSeats'] = request.form['seats']
        form['lat1'] = request.form['lat1']
        form['long1'] = request.form['long1']
        form['lat2'] = request.form['lat2']
        form['long2'] = request.form['long2']
        form['valid'] = 1
        username=session['username']

        if int(form['numberOfSeats']) > 3:
            flash('You can not share more than 3 seats ', 'danger')
            return render_template('offer_map.html')

        with sqlite3.connect("CabSharing.db") as con:
            cur = con.cursor()
            cur.execute("INSERT INTO rides_offered(userName, source, destination, lat1, long1, lat2, long2, offeredDate, offeredTime, offeredPrice, offeredSeats, details, valid,seatsleft) VALUES(? , ? , ? , ? , ? , ? , ? , ? , ? , ? ,? , ? , ? ,?)" , (username , form['source'], form['destination'], form['lat1'], form['long1'], form['lat2'], form['long2'], form['date'], form['time'], form['price'], form['numberOfSeats'], form['details'], form['valid'], form['numberOfSeats'] , ))
            con.commit()

        flash('Your Post has been put live ', 'success')

        with sqlite3.connect("CabSharing.db") as con:
            cur = con.cursor()
            cur.execute("select * from rides_offered where username = ? and valid=1", [session['username']])
            result= cur.fetchall()
            count = len(result)
            return render_template('rides.html' , result = result , count = count)
            con.commit()


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

emailotp=0000
email_toverify=""
@app.route('/verify', methods=['GET', 'POST'])
def verify():
    global emailotp
    global email_toverify
    if 'logged_in' in session:
        uname = session['username']
        with sqlite3.connect("CabSharing.db") as con:
                result = []
                cur = con.cursor()
                cur.execute("select * from users where username = ?",[uname])
                result = cur.fetchall()
                email_toverify=result[0][4]
                cur.close()
    if request.method == 'POST':
        eotp = request.form['eotp']
        print eotp
        if int(eotp)==emailotp:
            with sqlite3.connect("CabSharing.db") as con:
                cur = con.cursor()
                cur.execute("update users set email_verified=1 where email=?", [email_toverify])
                con.commit()
            flash('Your email is verified', 'success')
            if 'logged_in' in session:
                 return redirect(url_for('tdashboard'))
            return redirect(url_for('login'))
        else:
            flash('Invalid OTP', 'danger')

    emailotp=random.randrange(1000, 9999, 1)
    subject='Your sharcab OTP is'+ str(emailotp)
    msg = Message(subject, sender = 'sankettheflash@gmail.com', recipients = [email_toverify])
    msg.body = subject
    mail.send(msg)
    print emailotp

    return render_template('verify.html')



phoneotp=0000
@app.route('/verifyphone', methods=['GET', 'POST'])
def verifyphone():
    global phoneotp
    if 'logged_in' in session:
        uname = session['username']
        with sqlite3.connect("CabSharing.db") as con:
                result = []
                cur = con.cursor()
                cur.execute("select * from users where username = ?",[uname])
                result = cur.fetchall()
                phone_toverify=result[0][3]
                cur.close()
    if request.method == 'POST':
        eotp = request.form['eotp']
        print eotp
        if eotp==phoneotp:
            with sqlite3.connect("CabSharing.db") as con:
                cur = con.cursor()
                cur.execute("update users set mobile_verified=1 where phone=?", [phone_toverify])
                con.commit()
            flash('Your number is verified', 'success')
            if 'logged_in' in session:
                 return redirect(url_for('tdashboard'))
            return redirect(url_for('login'))
        else:
            flash('Invalid OTP', 'danger')

    url = "https://www.fast2sms.com/dev/bulk"
    a= random.choice('ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789@#$%&')
    b= random.choice('ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789@#$%&')
    c= random.choice('ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789@#$%&')
    d= random.choice('ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789@#$%&')
    e= random.choice('ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789@#$%&')
    phoneotp=a+b+c+d+e
    querystring = {"authorization":"8nH2jShLcMyCNUZwQIYmO5gvbzs0uxDV3Xq1eaEJG7PlRprFAovt8Fye6uTGw1QEakM5HIXYBhmLUxKR","sender_id":"FSTSMS","language":"english","route":"qt","numbers":""+phone_toverify+"","message":"3193","variables":"{AA}","variables_values":""+phoneotp+""}

    headers = {
    'cache-control': "no-cache"
    }

    response = requests.request("GET", url, headers=headers, params=querystring)

    print(response.text)
    print phoneotp


    return render_template('verifyphone.html')


@app.route('/profile', methods=['GET', 'POST'])
@is_logged_in
def profile():

    con = sqlite3.connect("CabSharing.db")
    cur = con.cursor()
    cur.execute("select * from users where username = ?",[session['username']])
    result = cur.fetchone()
    if request.method == 'POST':
        name = request.form['name']
        email = request.form['email']
        phone = request.form['phone']
        birth_year = request.form['birthyear']
        bio = request.form['bio']
        print bio
        cur.execute("update users set name=?,email=?,phone=?, birth_year=?,bio=? where username=?", (name, email,phone,birth_year,bio,session['username']))
        con.commit()
        flash("Saved successfully.")
        cur.close()
    return render_template('profile.html',result=result)


# User Register
@app.route('/register', methods=['GET', 'POST'])
def registr():
    global email_toverify
    form = RegisterForm(request.form)
    if request.method == 'POST' and form.validate():
        name = form.name.data
        email = form.email.data
        username = form.username.data
        password = sha256_crypt.encrypt(str(form.password.data))
        # password = form.password.data
        contact = form.contact.data
        address = form.address.data


        with sqlite3.connect("CabSharing.db") as con:
            cur = con.cursor()
            cur.execute("select * from users where username=? or email=? or phone=?", (username, email,contact))
            result=cur.fetchall()
            if result:
                flash('Username or email or phone already taken', 'danger')
                return render_template('register.html', form=form)
            con.commit()

        with sqlite3.connect("CabSharing.db") as con:
            cur = con.cursor()
            cur.execute("INSERT INTO users(name, email, username, password,phone,address) VALUES(?,?,?,?,?,?)", (name, email, username, password,contact,address))

            con.commit()
        flash('You are now registered. Please verify your email address', 'success')
        email_toverify=email
        return redirect(url_for('verify'))
        

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
                if sha256_crypt.verify(password_candidate, password):
                # if (password_candidate == password):
                    # Passed
                    session['logged_in'] = True
                    session['username'] = username

                    # flash('You are now logged in', 'success')
                    # return redirect(url_for('dashboard'))
                    cur.execute("select * from users where username = ?" , [username])
                    name = cur.fetchone()

                    result = []
                    cur.execute("select * from notification where username = ? ", [username])
                    result = cur.fetchall()

                    return render_template('tdashboard.html' , username = name[2] , result= result , count = len(result) )
                else:
                    error = 'Invalid login'
                    return render_template('login.html', error=error)
                # Close connection
                cur.close()
        else:
            error = 'Username not found'
            return render_template('login.html', error=error)

    return render_template('Googlesignin.html')


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
