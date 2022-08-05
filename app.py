from flask import Flask, render_template, request, redirect, url_for, session,flash
from flask_mysqldb import MySQL
import MySQLdb.cursors
import re
import os
from os.path import join, dirname, realpath
import pandas as pd

app = Flask(__name__)
app.secret_key = '1a2b3c4d5e'

app.config['MYSQL_HOST'] = 'localhost'
app.config['MYSQL_USER'] = 'root'
app.config['MYSQL_PASSWORD'] = 'root'
app.config['MYSQL_DB'] = 'school_db'

mysql = MySQL(app)

UPLOAD_FOLDER = 'static\\files'
app.config['UPLOAD_FOLDER'] =  UPLOAD_FOLDER

@app.route('/login/', methods=['GET', 'POST'])
def login():
    if request.method == 'POST' and 'username' in request.form and 'password' in request.form:
        username = request.form['username']
        password = request.form['password']
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute('SELECT * FROM accounts WHERE username = %s AND password = %s', (username, password))
        account = cursor.fetchone()
        if account:
            session['loggedin'] = True
            session['id'] = account['id']
            session['username'] = account['username']
            return redirect(url_for('home'))
        else:
            flash("Incorrect username/password!", "danger")
    return render_template('login.html',title="Login")

@app.route('/logout')
def logout():
    if session.get('loggedin'):
        del session['loggedin']
        flash('You have successfully logged yourself out.')
    return redirect('/login')

@app.route('/')
def root():
    return redirect('/home')

@app.route('/home')
def home():
    return render_template('index.html', title="Home")
      
@app.route('/result')
def result():
    if 'loggedin' in session:
        return render_template('result.html',title="Result")
    return redirect(url_for('login')) 

@app.route('/result', methods=['POST'])
def uploadFiles():
      uploaded_file = request.files['formFile']
      if uploaded_file.filename != '':
           filename_parts = uploaded_file.filename.split('.')
           file_extension = filename_parts[len(filename_parts) - 1]
           file_path = os.path.join(app.root_path, app.config['UPLOAD_FOLDER'], uploaded_file.filename)
           uploaded_file.save(file_path)
           class_id = request.form['class']
           
           if file_extension == 'csv':
               parseCSV(file_path, class_id)
           elif file_extension == 'xlsx':
               parseXlsx(file_path, class_id)
           else:
               flash('File format not supported.')
           
      return redirect(url_for('result'))

def parseCSV(filePath, class_id):
      col_names = ['Roll_No','S01','S02', 'S03', 'S04' , 'S05','S06','S07', 'S08', 'S09' , 'S10']
      csvData = pd.read_csv(filePath,names=col_names,header=0,na_filter= False)
      csvData.fillna('')
      cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
      
      try:
        for index,row in csvData.iterrows():
            sql = "INSERT INTO result_data (roll_no, s01, s02, s03, s04, s05, s06, s07, s08, s09, s10) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)"
            values = (class_id,row['Roll_No'],row['S01'],row['S02'],row['S03'],row['S04'],row['S05'],row['S06'],row['S07'],row['S08'],row['S09'],row['S10'])
            #cursor.execute(sql, values)
            cursor.callproc('p_results_ins', values)
            mysql.connection.commit()
        cursor.close()
        mysql.connection.close()
        flash('File have successfully uploaded.')  
      except Exception as e:
        cursor.close()
        mysql.connection.close()
        flash('Error occured: ' + str(e))

def parseXlsx(filePath, class_id):
    df = pd.read_excel(filePath, sheet_name=0,na_filter= False)
    cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)

    try:
        for index, row in df.iterrows():
            sql = "INSERT INTO result_data (roll_no, s01, s02, s03, s04, s05, s06, s07, s08, s09, s10) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)"
            values = (class_id,row['Roll_No'],row['S01'],row['S02'],row['S03'],row['S04'],row['S05'],row['S06'],row['S07'],row['S08'],row['S09'],row['S10'])
            #cursor.execute(sql, values)
            cursor.callproc('p_results_ins', values)
            mysql.connection.commit() 
        cursor.close()
        mysql.connection.close()
        flash('File have successfully uploaded.')  
    except Exception as e:
        cursor.close()
        mysql.connection.close()
        flash('Error occured: ' + str(e))

@app.route('/showresult')
def showresult():
    if 'loggedin' in session:
        return render_template('show-result.html',title="Show Result")
    return redirect(url_for('login')) 

@app.route('/showresult', methods=['POST'])
def displayresult():
        number = request.form['number']
        class_id = request.form['class']
        option = request.form['optradio']
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)

        if (option == "1"):
            cursor.execute("""select (select count(*) from results r,registrations reg where reg.registration_id=r.registration_id  and division<>"F" and reg.class_id=%s) passed, 
(select count(*) from results r,registrations reg where reg.registration_id=r.registration_id and division="F" and reg.class_id=%s) failed""" % (class_id, class_id))
            summary = cursor.fetchall()
            data = None
        elif (option == "2"):
            cursor.execute("""select s.name,r.total_marks,r.mark_obtained,r.percentage,r.division  from results r,registrations reg,students s 
                    where reg.registration_id = r.registration_id and s.student_id = reg.student_id and reg.class_id = %s 
                    and division<>'F' order by mark_obtained desc limit %s""" % (class_id, number))
            data = cursor.fetchall()
            summary = None
        elif (option == "3"):
            cursor.execute("""select s.name,r.total_marks,r.mark_obtained,r.percentage,r.division  from results r,registrations reg,students s
                    where reg.registration_id = r.registration_id and s.student_id = reg.student_id and reg.class_id = %s
                    order by mark_obtained LIMIT %s""" % (class_id, number))
            data = cursor.fetchall()
            summary = None
        elif (option == "4"):
            cursor.execute("""select s.name,r.total_marks,r.mark_obtained,r.percentage,r.division  from results r,registrations reg,students s
                    where reg.registration_id = r.registration_id and s.student_id = reg.student_id and reg.class_id = %s
                    order by mark_obtained desc""" % (class_id))
            data = cursor.fetchall()
            summary = None
        else:
               flash('Select an option.')
               data = None
               summary = None

        if((data is not None) and (len(data) == 0)):
            flash("No record found")

        return render_template('show-result.html', value=data, status=summary)

    
if __name__ =='__main__':
	app.run(debug=True)
