from flask import Flask,render_template,request,flash,redirect,url_for,session,logging
from data import Articles
from flask_mysqldb  import MySQL
from wtforms import Form,StringField,TextAreaField,PasswordField,validators
from passlib.hash import sha256_crypt
from functools import wraps

app=Flask(__name__)


# Config MySQL

app.config['MYSQL_HOST']='localhost'
app.config['MYSQL_USER']='root'
app.config['MYSQL_PASSWORD']='Amit1508!'
app.config['MYSQL_DB']='myapp'
app.config['MYSQL_CURSORCLASS']='DictCursor'

#Initialise MYSQL
mysql=MySQL(app)

Articles=Articles()


#index
@app.route("/")
def index():
	return render_template("home.html")

#layout
def layout():
	return render_template("layout.html")# dont need to repeat the head tag body tag again and again	we use templates folder
	# and we use the nav bar on every single page thats why use includes folder


#about
@app.route("/about")
def about():
	return render_template("about.html")


#Articles
@app.route("/articles")
def articles():
	return render_template("articles.html",articles=Articles)


#Single article
@app.route("/article/<string:id>/")
def article(id):
	return render_template("article.html",id=id)


#Register Form class
class RegisterForm(Form):  #WT-forms website
	name=StringField('Name',[validators.Length(min=1,max=50)])
	username=StringField('Username',[validators.Length(min=4,max=25)])
	email=StringField('Email',[validators.Length(min=6,max=50)])
	password=PasswordField('password',[
		validators.DataRequired(),
		validators.EqualTo('confirm',message="Password do not match")
		])
	confirm=PasswordField("Confirm Password")


#Register
@app.route('/register',methods=['GET','POST'])# post because we submit the form otherwise the default is GET no need to write it
def register():
	form = RegisterForm(request.form)
	if request.method=='POST' and form.validate():
		name=form.name.data
		email=form.email.data
		username=form.username.data
		password=sha256_crypt.encrypt(form.password.data)
		
		#Create cursor
		cur=mysql.connection.cursor()

		#Execute query
		cur.execute("INSERT INTO users(name,email,username,password) VALUES(%s,%s,%s,%s)",(name,email,username,password))

		#Commit to DB
		mysql.connection.commit()

		#Close connection
		cur.close()

		flash("You are now registered and can login",'success')
		
		return redirect(url_for('login'))
		

	return render_template('register.html',form=form)	



#login
@app.route("/login",methods=["GET","POST"])
def login():
	if request.method=="POST":
			#FORM FIELDS
		username=request.form['username']
		password_candidate=request.form['password']
			#CREATE CURSOR
		cur=mysql.connection.cursor()

			#get user by username
		result=cur.execute("SELECT * FROM users WHERE username = %s",[username])

		if(result>0):
				#get stored hash
			data=cur.fetchone()
			password=data['password']

				#COmpare the password

			if(sha256_crypt.verify(password_candidate,password)):
				#PASSED
				session['logged_in']=True
				session['username']=username
				flash('You are now logged in','success')
				return redirect(url_for('dashboard'))
			else:
				error= 'Invalid login'
				return render_template('login.html',error=error)
			# Close connection
			cur.close()	
		else:
			error = "Usename Not Found"
			return render_template('login.html',error=error)		

	return render_template("login.html")


#check if user logged in
def is_logged_in(f):
	@wraps(f)
	def wrap(*args,**kwargs):
		if 'logged_in' in session:
			return f(*args,**kwargs)
		else:
			flash("Unauthorised, Please login",'danger')
			return redirect(url_for('login'))
	return wrap		
			


# Logout
@app.route('/logout')
def logout():
	session.clear()
	flash('You are now logged out','success')
	return redirect(url_for('login'))



# Dashboard
@app.route('/dashboard')
@is_logged_in
def dashboard():
	return render_template('dashboard.html')


if __name__ == '__main__':
	app.secret_key='secret123'
	app.run(debug=True)
	
