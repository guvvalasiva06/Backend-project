import random
import smtplib
from email.mime.text import MIMEText

import flask
from flask import *

import dbclass
from dbclass import executeUpdate, fetchAll

app = flask.Flask(__name__)

app.config['upload_folder'] = "static/images"
app.secret_key = "ISM@12345"


@app.route("/")
def index():
    return render_template("index.html")


@app.route("/register")
def register():
    sql = "select * from register"
    data = dbclass.fetchAll(sql)
    return render_template("register.html", data=data)


@app.route("/registration", methods=["post", "Get"])
def registration():
    name = request.form['name']
    username = request.form['username']
    password = request.form['password']
    email = request.form['email']
    sql = "Insert into register(name,username,password,email) " \
          "values( '%s','%s','%s','%s')" % \
          (name, username, password, email)
    msg = 'Registration Successfully Done'
    dbclass.executeUpdate(sql)
    return redirect(url_for("register", msg=msg))


@app.route("/delete")
def delete():
    sql = "select * from register"
    data = dbclass.fetchAll(sql)
    return render_template("delete.html", data=data)


@app.route("/deletepage")
def deletepage():
    args = request.args
    cid = args['cid']
    print("emid: ", cid)
    sql = "delete from register where cid= '%s'" % (cid)
    dbclass.executeUpdate(sql)
    return redirect(url_for("delete"))


@app.route("/login1")
def login1():
    return render_template("login.html")


@app.route("/login", methods=['POST', 'GET'])
def login():
    try:
        username = request.form['username']
        password = request.form['password']
        sql = "select * from register where username like '%s' and password like '%s'" % (username, password)
        print(sql)
        data = dbclass.fetchAll(sql)

        if (data):
            data = data[0]
            cid = data[0]
            session['cid'] = cid
            print(data)
            return render_template("common.html", data=data)
        else:
            msg = "Invalid UserName/Password"
            return render_template("login.html", msg=msg)
    except Exception as e:
        print(e)
        return render_template("login.html")


@app.route("/forgot")
def forgot():
    return render_template("forgot.html")


def send_mail(subject, body, sender, recepients, password):
    msg = MIMEText(body)
    msg['Subject'] = subject
    msg['From'] = sender
    msg['To'] = ' ,'.join(recepients)
    print(msg)
    with smtplib.SMTP_SSL('smtp.gmail.com', 465) as smtp_server:
        smtp_server.login(sender, password)
        smtp_server.sendmail(sender, recepients, msg.as_string())
    print("Mail Sent Success")


@app.route("/checkemail", methods=["POST", "GET"])
def checkemail():
    try:
        email = request.form['email']
        sql = "Select * from register  where email like '%s'" % (email)
        print("Sql : ", sql)

        conn = dbclass.getConn()
        cursor = conn.cursor()
        cursor.execute(sql)
        row = cursor.fetchone()
        if (row):
            session['email'] = email
            subject = "OTP to reset the password"
            otp = random.randint(1000, 9999)
            session['otp'] = otp
            body = "Thank you for changing the Password, your OTP is : " + str(otp)
            sender = "guvvalasivakumar60@gmail.com"
            recipients = [email]
            password = "kwhasrakvlsxhfqt"
            send_mail(subject, body, sender, recipients, password)
            return render_template("enterotppage.html", email=email)
        else:
            flash("Login Not Success")
            msg = 'Invalid EmailId'
            return render_template("forgot.html", msg=msg)
    except Exception as e:
        return render_template("login.html", msg=e)


@app.route("/checkotp", methods=["POST", "GET"])
def checkotp():
    try:
        sentotp = request.form['otp']
        savedotp = session['otp']
        email = session['email']
        print("Saved Otp : ", savedotp, " Sent Otp : ", sentotp)
        if (int(sentotp) == int(savedotp)):
            return render_template("passwordchangepage.html", email=email)
        else:
            return render_template("enterotppage.html", email=email, msg='Incorrect OTP')
    except Exception as e:
        return render_template("login.html", msg=e)


@app.route("/changepwd", methods=["POST", "GET"])
def changepwd():
    try:
        pwd = request.form['pwd']
        email = session['email']
        sql = "Update register set password = '%s' where email = '%s'" % (pwd, email)
        print("Sql : ", sql)
        conn = dbclass.getConn()
        cursor = conn.cursor()
        cursor.execute(sql)
        conn.commit()
        msg = "Password Changes Success"
        return render_template("login.html", msg=msg)
    except Exception as e:
        return render_template("login.html", msg=e)

@app.route("/booking")
def booking():
    sql = "select * from booking"
    data = dbclass.fetchAll(sql)
    return render_template("bookingtable.html", data=data)

@app.route("/booking1", methods=["POST", "GET"])
def booking1():
        destination = request.form.get('destination')
        members = request.form.get('members')
        bookingdate = request.form.get('bookingdate')
        leavingdate = request.form.get('leavingdate')
        address = request.form.get('address')
        sql = "insert into booking (destination,members,bookingdate,leavingdate,address)" \
              "values('%s','%s','%s','%s','%s')" % \
              (destination, members, bookingdate, leavingdate, address)

        msg = 'Booking Successfully Done'
        dbclass.executeUpdate(sql)
        return render_template("bookingtable.html", msg=msg)
@app.route("/payment")
def payment():
    sql = "select * from payment"
    data = fetchAll(sql)
    return render_template("paymenttable.html", data=data)


@app.route("/payment1", methods=["POST", "GET"])
def payment1():
    cardnumber = request.form['cardnumber']
    cvv = request.form['cvv']
    cardholdername = request.form['cardholdername']
    sql = "insert into payment (cardnumber,cvv,cardholdername)" \
          "values('%s','%s','%s')" % \
          (cardnumber, cvv, cardholdername)
    dbclass.executeUpdate(sql)
    msg = 'payment Successfully Done'
    return render_template("paymenttable.html", msg=msg)


@app.route("/admin")
def admin():
    return render_template("admin.html")


@app.route("/adminmain", methods=["POST", "GET"])
def admin1():
    if request.method == "POST":
        admin = request.form.get('admin')
        password = request.form.get('password')

        if admin == "sivakumar" and password == "kumar@123":
            flash(f"Logged in as {admin}", 'success')
            return render_template("adminheader.html", admin=admin)

    flash("Invalid admin/password", 'error')
    return render_template("admin.html")


if __name__ == "__main__":
    app.run(debug=True)
