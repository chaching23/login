from flask import Flask, render_template, request, redirect, flash, session
from mysqlconn import connectToMySQL
import re
from flask_bcrypt import Bcrypt

app = Flask(__name__)
app.secret_key = "keep it secret"
EMAIL_REGEX = re.compile(r'^[a-zA-Z0-9.+_-]+@[a-zA-Z0-9._-]+\.[a-zA-Z]+$')
bcrypt = Bcrypt(app) 

USER_KEY ="user_id"

@app.route("/")
def index():
    mysql = connectToMySQL('mydb')
    user = mysql.query_db('SELECT * FROM login;')  
    return render_template("index.html", all_users = user)


@app.route('/register', methods=['POST'])
def create_user():
    is_valid = True		
    if len(request.form['fname']) < 2:
        is_valid = False
        flash("need first name")
    if len(request.form['lname']) < 2:
        is_valid = False
        flash("need last name")
    if not EMAIL_REGEX.match(request.form['email']):   
        flash("Invalid email address!")
        return redirect('/')
    if len(request.form['password']) < 8:
        is_valid = False
        flash("invalid password")
    if (request.form['cpassword']) != (request.form['password']):
        is_valid = False
        flash("passwords don't match")
    if "_flashes" in session:
        return redirect("/")
    if not is_valid:
        return redirect("/")
    else:
        mysql = connectToMySQL('mydb')
        pw_hash = bcrypt.generate_password_hash(request.form['password'])
        print(pw_hash)
        query = "INSERT INTO login (first_name, last_name, email, password) VALUES (%(fn)s, %(ln)s, %(em)s,%(p)s);"
        data = {
            "fn": request.form["fname"],
            "ln": request.form["lname"],
            "em": request.form["email"],
            "p": pw_hash,



        }
        user_id= mysql.query_db(query,data)
        session[USER_KEY] = user_id 
        flash("Successfully Added!")
   
    return redirect("/main")


@app.route("/main")
def index3():
    mysql = connectToMySQL('mydb')
    query = 'SELECT * FROM login WHERE id =%(id)s;'
    data = {
		'id' : session[USER_KEY]
	}
    user = mysql.query_db(query, data)
    print(user)
    return render_template("main.html", all_users = user)


@app.route('/login', methods=['POST'])
def login():
    the_email=request.form['email2']
    pasword=request.form['password2']

    mysql = connectToMySQL("mydb")
    query = "SELECT id, password FROM login WHERE email = %(em)s;"
    data = { 
        "em" : request.form["email2"] 
        }
    result = mysql.query_db(query, data)

    if result:
        x = bcrypt.check_password_hash(result[0]['password'], request.form['password2'])
        if x == False:
            flash("You could not be logged in")
            return redirect("/")
        else:
            session[USER_KEY] = result[0]['id']
            return redirect('/main')
    return redirect("/")





    
            
if __name__ == "__main__":
    app.run(debug=True)
    