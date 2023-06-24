from flask import Flask, render_template, request, redirect, url_for, session
import pickle
import sqlite3
import warnings

warnings.filterwarnings('ignore')


complaints_model = pickle.load(open("complaint_classification_model_dtc.pkl",'rb'))

app = Flask(__name__)
#secret keys are important for sessions


app.secret_key = 'iowngolcondafort'



@app.route('/',methods=['POST', 'GET'])
def home():
    home_page = '<html><h1>welcome ...!!</h1><body style="text-decoration: none;"><a href="/pro1.html">Click here </a>to direct you to complaint page</html>'
    return home_page


@app.route('/pro1.html',methods=['POST', 'GET'])
def complaint_submission():
    
    if request.method == 'POST':
        #fetch form data
        complaints = request.form
        date = complaints['dmy']
        name = complaints['customer_name']
        submitting_medium = complaints['complaint_submitting_via']
        complaint = complaints['customer_complaint']
        
        print(complaint)
        department_name = complaints_model.predict([complaint])
        print(department_name)
        
        
        conn = sqlite3.connect('complaint_db.db')
        cur = conn.cursor()
        cur.execute("INSERT INTO complaints(dmy, customer_name, complaint_submitting_via, customer_complaint, department_name) VALUES(?,?,?,?,?)",(date, name, submitting_medium, complaint, str(department_name)[2:-2]))
        
        refno = cur.lastrowid
        cur.execute("commit")
        cur.close()
        return 'successfully registered the complaint,your complaint is redirected to DEPARTMENT : '+str(department_name)[1:-1]+'. please save the refno for checking status of your complaint.your REFERENCE NUMBER is : '+str(refno)+'. Thank you for using this portal.'
    return render_template('pro1.html')
@app.route('/check_complaints_status.html', methods =['GET','POST'])
def status():
    sta =""
    if request.method =='POST' and 'refno' in request.form:
        refno = request.form['refno']
        conn = sqlite3.connect('complaint_db.db')
        cur = conn.cursor()
        cur.execute('SELECT status,refno FROM complaints WHERE refno = ?', (refno,))
        one = cur.fetchone()
        if one:
            session['refno'] = one[0]
            session['status'] = one[1]
            sta = 'complaint exist in database'
            return render_template('status_disp.html',sta = sta)
        else:
            sta = 'complaint doesnot exist in the database.please check reference number and try again'
       
    return render_template('check_complaints_status.html',sta = sta)
        
 
    
@app.route('/login_id.html', methods =['GET', 'POST'])
def login():
    msg =''
    if request.method =='POST' and 'employee_id' in request.form and 'password' in request.form:
        employee_id = request.form['employee_id']
        password = request.form['password']
        conn = sqlite3.connect('complaint_db.db')
        cur = conn.cursor()
        cur.execute('SELECT * FROM employee WHERE employee_id = ? AND password = ?', (employee_id, password,))
        emp = cur.fetchone()
        if emp:
            session['loggedin'] = True
            session['id'] = emp[0]
            session['employee_id'] = emp[1]
            session['department_name'] = emp[3]
            msg = 'logged in sucessfully !'
            return render_template('profile.html', msg = msg)
        else:
            msg = 'Incorrect employee_id / password.please check and try again '
        
    return render_template('login_id.html',msg = msg)
@app.route('/logout.html')
def logout():
    session.pop('loggedin', None)
    session.pop('id', None)
    session.pop('employee_id', None)
    return redirect(url_for('login'))
@app.route('/profile.html',methods=['POST', 'GET'])
def com_data():
    if request.method =='POST':
        refno = request.form['refno']
        status = request.form['status']
        conn = sqlite3.connect('complaint_db.db')
        cur = conn.cursor()
        cur.execute('UPDATE complaints set status = ? WHERE refno = ?',(status, refno))
        cur.execute("commit")
        cur.close()
    
    return 'status is updated sucessfully'

if __name__ == '__main__':
    app.run(debug=False)

