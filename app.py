from flask import Flask, render_template, flash, redirect, url_for, session, request, logging


app = Flask(__name__)



# Index
@app.route('/')
def index():
    return render_template('home.html')


@app.route('/findcab')
def findcab():
    return render_template('about.html')

@app.route('/offercab')
def offercab():
    return render_template('about.html')

@app.route('/contactus')
def contactus():
    return render_template('about.html')

@app.route('/login')
def login():
    return render_template('login.html')



if __name__ == '__main__':
    # app.secret_key='secret123'
    app.run(debug=True)
