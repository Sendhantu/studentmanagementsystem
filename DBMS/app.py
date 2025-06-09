from flask import Flask, render_template, request, redirect, flash, url_for, session
import mysql.connector

app = Flask(__name__)
app.secret_key = '8f9c35f12e4a45e3b6d83f4291aefb9a'

mydb = mysql.connector.connect(host="localhost", user="root", password="Sendhan@2005", database="student_management_system")
mycursor = mydb.cursor(dictionary=False)

@app.route('/staffloginpage')
def staffloginpage():
    return render_template('staffloginpage.html')

@app.route('/createnewstaffaccount', methods=['POST'])
def createnewstaffaccount():
    staffid = request.form.get('staffid')
    firstname = request.form.get('firstname')
    lastname = request.form.get('lastname')
    department = request.form.get('department')
    email = request.form.get('email')
    address = request.form.get('address')
    username = request.form.get('username')
    password = request.form.get('password')

    print(f"Received values: {staffid=}, {firstname=}, {lastname=}, {department=}, {email=}, {address=}, {username=}, {password=}")

    if not staffid:
        flash("Staff ID is missing. Please fill all the fields.", "danger")
        return redirect(url_for('staffsignup'))

    sqlstaffinfo = 'INSERT INTO STAFF_DETAILS(STAFF_ID,FIRSTNAME,LASTNAME,DEPARTMENT,EMAIL,ADDRESS,USERNAME,PASSWORD) VALUES (%s, %s, %s, %s, %s, %s, %s, %s)'
    mycursor.execute(sqlstaffinfo, (staffid, firstname, lastname, department, email, address, username, password))

    sqlstaffusername = 'INSERT INTO STAFF_LOGIN VALUES (%s, %s, %s)'
    mycursor.execute(sqlstaffusername, (username, password, staffid))

    mydb.commit()

    flash("Signup Successful!", "success")
    return render_template('returnfromsignupadminhome.html')

@app.route('/staffsignup')
def staffsignup():
    return render_template('newstaffaccount.html')

@app.route('/stafflogin', methods=['GET', 'POST'])
def stafflogin():
    if request.method == 'POST':
        username = request.form.get('Username')
        password = request.form.get('Password')

        print(f"Received Username: {username}")
        print(f"Received Password: {password}")

        if not username or not password:
            flash("Username and Password cannot be empty", "danger")
            return render_template('StaffLoginPage.html')

        try:
            sql = "SELECT * FROM STAFF_LOGIN"
            mycursor.execute(sql)  # ✅ No parameters passed here
            users = mycursor.fetchall()

            for row in users:
                print(row)
                if row[0] == username and row[1] == password:
                    print(f"User fetched from DB: {row}")
                    session['staff_username'] = username
                    staffid = row[2] if len(row) > 2 else "UNKNOWN"
                    flash("Login successful!", "success")
                    return redirect(url_for('staff_dashboard', staffid=staffid))

            flash("Invalid Username or Password", "danger")

        except Exception as e:
            print("Error during login:", e)
            flash("Something went wrong. Please try again.", "danger")

    return render_template('StaffLoginPage.html')


@app.route('/markpage',methods = ['GET'])
def markpage():
    stuid = request.args.get('stuid')
    print(stuid)
    sql = 'SELECT * FROM MARKS WHERE STUID = %s'
    mycursor.execute(sql,(stuid,))
    data = mycursor.fetchall()
    print(data)
    return render_template('marks.html', marks=data)



@app.route('/staff_dashboard/<staffid>')
def staff_dashboard(staffid):
    sql = "SELECT * FROM STAFF_DETAILS WHERE STAFF_ID = %s"
    mycursor.execute(sql, (staffid,))
    user = mycursor.fetchone()

    if user:
        userlist = list(user)
        print(f"User fetched from DB: {userlist}")
        return render_template('Staff Home Page.html', values=userlist)
    else:
        flash("Invalid Username or Password", "danger")
        return render_template('StaffLoginPage.html')

@app.route('/staffstudentmark', methods=['GET', 'POST'])
def staffstudentmark():
    print('Hello')
    return "Attendance function executed successfully!", 200

@app.route('/staffstudentatten', methods=['POST'])
def staffstudentatten():
    print('staffstudentatten')
    return "Attendance function executed successfully!", 200

@app.route('/update_marks', methods=['POST'])
def update_marks():
    student_id = request.form.get('student_id')
    subject = request.form.get('subject')
    marks = request.form.get('marks')

    sql = "INSERT INTO STUDENT_MARKS (STUDENT_ID, SUBJECT, MARKS) VALUES (%s, %s, %s) ON DUPLICATE KEY UPDATE MARKS=%s"
    mycursor.execute(sql, (student_id, subject, marks, marks))
    mydb.commit()

    flash("Marks updated successfully!", "success")
    return redirect(url_for('staff_dashboard'))

@app.route('/mark_attendance', methods=['POST'])
def mark_attendance():
    student_id = request.form.get('student_id')
    status = request.form.get('status')

    sql = "INSERT INTO STUDENT_ATTENDANCE (STUDENT_ID, STATUS) VALUES (%s, %s) ON DUPLICATE KEY UPDATE STATUS=%s"
    mycursor.execute(sql, (student_id, status, status))
    mydb.commit()

    flash("Attendance marked successfully!", "success")
    return redirect(url_for('staff_dashboard'))

@app.route('/studentmainpage', methods=['POST'])
def student_main():
    username = request.form.get('Username')
    password = request.form.get('Password')

    print(f"Received Username: {username}, Password: {password}")

    mycursor.execute("SELECT * FROM student_login_details WHERE Username=%s AND Password=%s", (username, password))
    user = mycursor.fetchone()

    print("Query Result:", user)

    if user:
        session['username'] = username
        return redirect(url_for('gotostudentmainpage'))
    else:
        flash("Invalid Username or Password", "danger")
        return redirect(url_for('studentlogin')), 401

@app.route('/gotostudentmainpage', methods=['GET'])
def gotostudentmainpage():
    username = session.get('username')

    if not username:
        flash("Session expired. Please log in again.", "danger")
        return redirect(url_for('studentlogin'))

    mycursor.execute("SELECT * FROM STUDENT_DETAILS WHERE Username=%s", (username,))
    user = mycursor.fetchone()

    if user:
        id, fname, lname, dob, email = user[:5]  # Unpack tuple
        valuesdata = [id, fname, lname, dob, email]
        return render_template('Student Main Page.html', values=valuesdata)
    else:
        flash("User not found!", "danger")
        return redirect(url_for('studentlogin'))

@app.route('/')
def index():
    return render_template('HomePage.html')

@app.route('/studentlogin')
def studentlogin():
    return render_template('LoginPage.html')

@app.route('/student_portal', methods=['POST'])
def student_portal():
    username = request.form.get('username')
    password = request.form.get('password')

    sql = "SELECT * FROM STUDENT_LOGIN_DETAILS WHERE USERNAME = %s AND PASSWORD = %s"
    mycursor.execute(sql, (username, password))
    myresult = mycursor.fetchone()

    if myresult:
        return render_template('Student Main Page.html')
    else:
        return "Invalid Student Credentials!"

@app.route('/admin')
def admin():
    return render_template('AdminLogin.html')

@app.route('/Stusignup')
def Stusignup():
    return render_template('SignUpPage.html')

@app.route('/StudentSignUp', methods=['POST'])
def StudentSignUp():
    regno = request.form.get('registration_number')
    fname = request.form.get('firstname')
    lastname = request.form.get('lastname')
    dob = request.form.get('dob')
    email = request.form.get('email')
    username = request.form.get('username')
    password = request.form.get('password')

    sqlstudentinfo = "INSERT INTO STUDENT_DETAILS (REGNO, FNAME, LNAME, DOB, EMAIL, USERNAME, PASSWORD) VALUES (%s, %s, %s, %s, %s, %s, %s)"
    mycursor.execute(sqlstudentinfo, (regno, fname, lastname, dob, email, username, password))
    mydb.commit()

    sqlstudentlogininfo = "INSERT INTO STUDENT_LOGIN_DETAILS (USERNAME, PASSWORD) VALUES (%s, %s)"
    mycursor.execute(sqlstudentlogininfo, (username, password))
    mydb.commit()

    flash("Signup Successful!", "success")
    return render_template('returnfromsignupadminhome.html')

@app.route('/returnfromadminstudentdata')
def returnfromadminstudentdata():
    return render_template('Admin Page.html')

@app.route('/viewdata')
def viewdata():
    sql = "SELECT * FROM STUDENT_DETAILS"
    mycursor.execute(sql)
    students = mycursor.fetchall()
    return render_template('dataofmultiplestudenttoadmin.html', students=students)

@app.route('/adminlogin', methods=['POST'])
def adminlogin():
    username = request.form.get('Username')
    password = request.form.get('Password')

    sql = "SELECT * FROM ADMIN_LOGIN_DETAILS WHERE username=%s AND password=%s"
    mycursor.execute(sql, (username, password))
    result = mycursor.fetchone()

    if result:
        return render_template('Admin Page.html')
    else:
        return "Invalid Admin Credentials!"

if __name__ == '__main__':
    app.run(debug=True)
