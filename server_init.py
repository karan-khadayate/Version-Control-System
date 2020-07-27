from flask import Flask,request,session,redirect,render_template
from os import getcwd,mkdir,listdir,system
import pymysql
from re import findall

DBHOST="localhost"
DBUSER="userk"
DBPASS="tiger"
DBNAME="vcs"

ROOT_PATH=getcwd()
print(f"ROOT_PATH={ROOT_PATH}")

def createDir(dir_name):
	try:
		mkdir(dir_name)
	except FileExistsError:
		pass

#UPLOAD DIR
createDir(ROOT_PATH+"\\files")
app=Flask(__name__,static_url_path="/",static_folder=ROOT_PATH+"\\files",template_folder=ROOT_PATH)
app.secret_key="vcs"


@app.route("/files/<repo>/<branch>",methods=["GET"])
def files(repo,branch):
	res=""
	for x in listdir(ROOT_PATH+"\\files"):
		res+=f"<a href='\\files\\{x}'>{x}</a><br>"
	return res[:-4]


@app.route("/logout",methods=["GET","POST"])
def logout():
	try:
		session.pop("username")
	except Exception as e:
		pass
	return redirect("/login")

@app.route("/login",methods=["POST","GET"])
def login():
	if request.method=="POST":
		if(request.form.get("submit")=='SUBMIT'):
			username=request.form.get("username")
			password=request.form.get("password")
			error=cur=con=None
			if(findall("[\'\"]",username+password)!=[]):
				return "<script>alert('Quotations are not allowed');window.location.assign('/login');</script>;"
			try:
				con=pymysql.connect(DBHOST,DBUSER,DBPASS,DBNAME)
				cur=con.cursor()
				cur.execute(f"SELECT * FROM USER WHERE username='{username}' AND password='{password}'")
				res=cur.fetchall()
				print(res)
				if(len(res)==0):
					error="<script>alert('Does not exist');window.location.assign('/login');</script>;"
			except Exception as e:
				print(e)
				error=str(e)
			finally:
				if con!=None:
					con.close()
				if cur!=None:
					cur.close()
			if(error==None):
				session["username"]=username
				return redirect("/")
			else:
				return error
		else:
			return redirect("/login")
	else:
		try:
			session["username"]
			return redirect("/")
		except Exception:
			a= '''
			<form action="/login" method="POST">
				<input type="text" name="username" placeholder="Enter username" required></input><br>
				<input type="password" name="password" placeholder="Enter password" required></input><br>
				<input type="submit" name="submit" value="SUBMIT"></input>
			</form>
			<br><br>
			<a href="/register">New user?</a>
			'''
			return render_template("enter.html",form=a)

@app.route("/register",methods=["POST","GET"])
def register():
	print(request.form)
	if request.method=="POST":
		if(request.form.get("submit")=='SUBMIT'):
			name=request.form.get("name")
			username=request.form.get("username")
			password=request.form.get("password")
			cpassword=request.form.get("cpassword")
			error=cur=con=None
			if(findall("[\'\"]",username+password+cpassword+name)!=[]):
				return "<script>alert('Quotations are not allowed');window.location.assign('/register');</script>;"
			if(password!=cpassword):
				return "<script>alert('Passwords not matching');window.location.assign('/register');</script>;"
			try:
				con=pymysql.connect(DBHOST,DBUSER,DBPASS,DBNAME)
				cur=con.cursor()
				cur.execute(f"INSERT INTO USER VALUES('{username}','{name}','{password}');")
				con.commit()
			except pymysql.err.IntegrityError as e:
				error="Username already exists"
			except Exception as e:
				print(e)
				error="Unknown Error"
			finally:
				if cur!=None:
					cur.close()
				if con!=None:
					con.close()
			if(error==None):
				session["username"]=username
				return redirect("/")
			else:
				return "Error: "+error
		else:
			return redirect("/register")
	else:
		try:
			session["username"]
			return redirect("/")
		except Exception:
			a= '''
			<form action="/register" method="POST">
				<input type="text" name="name" placeholder="Enter name" required></input><br>
				<input type="text" name="username" placeholder="Enter username" required></input><br>
				<input type="password" name="password" placeholder="Enter password" required></input><br>
				<input type="password" name="cpassword" placeholder="Confirm password" required></input><br>
				<input type="submit" name="submit" value="SUBMIT"></input>
			</form>
			<br><br>
			<a href="/login">Already registered?</a>
			'''
			return render_template("enter.html",form=a)
	