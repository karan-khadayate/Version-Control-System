from server_init import *


@app.route("/search",methods=["GET"])
def search():
	cur=con=msg=None
	try:
		query = "SELECT branchname from branch"
		a=request.args.get("query",None)
		print(a)
		if(a!=None or len(findall(r"[^a-zA_Z0-9_]",a))!=0):
			query+=f" WHERE branchname like '{a}%';"
		print(query)
		con=pymysql.connect(DBHOST,DBUSER,DBPASS,DBNAME)
		cur=con.cursor()
		cur.execute(query)
		l=cur.fetchall()
		msg=""
		s=[]
		for b in l:
			s.append(b[0].split("/")[0])
		s=list(set(s))
		for repo in s:
			msg+=f"<a href='/dir/{repo}/master'>{repo}</a><br>"
		if(msg==""):
			msg="Not Found"
		msg+="<br><br><br><br><a href='/'>HOME</a>"
	except Exception as e:
		msg=str(e)
	finally:
		if(cur!=None):
			cur.close()
		if(con!=None):
			con.close()
	return render_template("enter.html",form=msg)

@app.route("/deleteFile",methods=["POST"])
def deleteFile():
	try:
		repo,branch,file=request.form.get("reponame"),request.form.get("branchname"),request.form.get("file")
		print(repo,branch,file)
		if(None in (repo,branch,file) or len(findall(r"[^a-zA_Z0-9_]",repo+branch))!=0):
			raise Exception("Invalid Request")
		cmd=f"del {ROOT_PATH}\\files\\{repo}\\{branch}\\{file}"
		system(cmd)
		return "Done"
	except Exception as e:
		return str(e)


@app.route("/dir/<reponame>/<branchname>",methods=["GET"])
def getfilelist(reponame,branchname):
	msg=cur=con=None
	files="Not allowed to view files"
	branchoptions=""
	createBranch=f'''
	<div style="margin-top:20px;border-style:solid;border-width:1px;padding:10px;">
	Create new branch
	<form action="/createBranch" method="POST">
		<input type="text" name="reponame" value="{reponame}" readonly hidden>
		<input type="text" name="src" value="{branchname}" readonly hidden>
		<input type="text" name="branchname" placeholder="Enter branch name">
		<input type="submit" name="sumbit" value="SUBMIT">
	</form>
	</div>
	'''
	uploadform=f'''
		<div style="margin-top:20px;border-style:solid;border-width:1px;padding:10px;">
		Upload New Files
			<form action="/upload/{reponame}/{branchname}" method="POST" enctype="multipart/form-data">
				<input type="file" name="files" style="border-style:none;" multiple>
				<input type="submit" name="SUMBIT" value="UPLOAD">
			</form>
		</div>
	'''
	accessBranch=f'''
	<button onclick="requestAccess('{reponame}','{branchname}');">
	REQUEST ACCESS ON {reponame}/{branchname}
	</button><br>'''
	for b in listdir(f"{ROOT_PATH}\\files\\{reponame}\\"):
		if(b!=branchname):
			branchoptions+=f"<option value='{b}'>{b}</option>"
		else:
			branchoptions+=f"<option value='{b}' selected>{b}</option>"
	try:
		name=session["username"]
	except KeyError:
		return redirect("/login")

	try:
		con=pymysql.connect(DBHOST,DBUSER,DBPASS,DBNAME)
		cur=con.cursor()
		bname=reponame+"/"+branchname
		cur.execute(f'''
			(SELECT username,"1" FROM branch WHERE username="{name}" AND branchname="{bname}")
			UNION
			(SELECT username,"2" FROM branch WHERE username="{name}" AND branchname="{reponame}/master")
			UNION
			(SELECT username,"3" FROM access
			WHERE (username="{name}" OR username="*") AND branchname="{bname}" 
			);''')
		res=cur.fetchall()
		print(res)
		if(len(res)==0):
			#The user not allowed to view branch, so can't create branch, see files and upload files 
			files="Not allowed to view files"
			uploadform=""
			createBranch=""
		else:
			accessBranch=""
			l=listdir(f"{ROOT_PATH}\\files\\{reponame}\\{branchname}")
			files=""
			if(res[0][1]=="1"):
				#The user owns the branch, so he can edit it 
				for x in l:
					files+=f'''
					<tr>
					<td>
					<a href="/{reponame}/{branchname}/{x}">{x}</a>
					</td>
					<td>
					<button onclick="deleteFile('{reponame}','{branchname}','{x}');" style="border-style:none; border-radius:0px;">Delete</button>
					</td>
					</tr>
					'''
			elif(res[0][1]=="2" or res[0][1]=="3"):
				#The user doesn't own the branch (or) has requested access, but he owns the master branch, so he can only view it
				uploadform=""
				for x in l:
					#There is no delete button
					files+=f'''<a href="/{reponame}/{branchname}/{x}">{x}</a><br>'''
			if(len(l)==0):
				files="No files"
	except Exception as e:
		msg=str(e)
	finally:
		if(cur!=None):
			cur.close()
		if(con!=None):
			con.close()
	return render_template("dir.html"\
		,createBranch=createBranch\
		,files=files\
		,accessbranch=accessBranch\
		,reponame=reponame\
		,branchname=branchname\
		,branchoption=branchoptions\
		,msg=msg\
		,uploadform=uploadform)




@app.route("/",methods=["GET"])
def root():
	try:
		session["username"]
		return render_template("index.html",username={"name":session["username"]})
	except KeyError:
		return redirect("/login")

@app.route("/getrepolist",methods=["POST"])
def getrepolist():
	msg=cur=con=None
	try:
		session["username"]
		con=pymysql.connect(DBHOST,DBUSER,DBPASS,DBNAME)
		cur=con.cursor()
		cur.execute(f"SELECT branchname FROM branch WHERE username='{session['username']}';")
		l=cur.fetchall()
		if(len(l)==0):
			msg="No repositories yet"
		else:
			msg=""
			for x in l:
				a=x[0].split("/")
				msg+=f"<a href='/dir/{a[0]}/{a[1]}'><span id='repo'>{a[0]}</span>/<span id='branch'>{a[1]}</span></a><br>"
	except KeyError:
		return redirect("/login")
	except Exception as e:
		msg=str(e)
	finally:
		if(cur!=None):
			cur.close()
		if(con!=None):
			con.close()
	return msg


@app.route("/requestAccess",methods=["POST"])
def requestAccess():
	try:
		name=session["username"]
	except KeyError as e:
		return redirect("/login")
	try:
		reponame=request.form.get("reponame")
		branchname=request.form.get("branchname")
		if(findall(r"[^a-z)-9A-Z_]",branchname+reponame)):
			raise Exception()
	except Exception as e:
		print(e)
		return "Invalid branchname"
	msg=con=cur=None
	try:
		con=pymysql.connect(DBHOST,DBUSER,DBPASS,DBNAME)
		cur=con.cursor()
		cur.execute(f"INSERT INTO access(branchname,username) VALUES('{reponame}/{branchname}','{name}');")
		con.commit()
		msg="Done"
	except Exception as e:
		msg=str(e)
	finally:
		if(cur!=None):
			cur.close()
		if(con!=None):
			con.close()
	return msg	



@app.route("/createBranch",methods=["POST"])
def createBranch():
	try:
		name=session["username"]
	except KeyError as e:
		return redirect("/login")
	try:
		reponame=request.form.get("reponame")
		srcbranch=request.form.get("src")
		branchname=request.form.get("branchname")
		if(findall(r"[^a-z)-9A-Z_]",branchname+reponame)):
			raise Exception()
	except Exception as e:
		print(e)
		return "Invalid branchname"
	msg=con=cur=None
	try:
		con=pymysql.connect(DBHOST,DBUSER,DBPASS,DBNAME)
		cur=con.cursor()
		cur.execute(f"INSERT INTO branch(branchname,reponame,username) VALUES('{reponame}/{branchname}','{reponame}','{name}');")
		try:
			mkdir(f"{ROOT_PATH}\\files\\{reponame}\\{branchname}")
			system(f"copy {ROOT_PATH}\\files\\{reponame}\\{srcbranch}\\* {ROOT_PATH}\\files\\{reponame}\\{branchname}")
			msg=redirect(f"/dir/{reponame}/{branchname}")
		except FileExistsError:
			raise Exception("Can't Create")
		con.commit()
	except Exception as e:
		msg=str(e)
	finally:
		if(cur!=None):
			cur.close()
		if(con!=None):
			con.close()
	return msg	

@app.route("/createRepository",methods=["POST"])
def createRepository():
	try:
		session["username"]
	except:
		return redirect("/login")
	try:
		name=request.form.get("name")
		public=request.form.get("public")
	except Exception as e:
		return "Invalid"
	error=cur=con=None
	if(name=='' or findall("[^0-9a-zA-Z_]",name)!=[]):
		return "Invalid repository name !"
	try:
		con=pymysql.connect(DBHOST,DBUSER,DBPASS,DBNAME)
		cur=con.cursor()
		cur.execute(f"INSERT INTO branch(branchname,reponame,username) VALUES('{name}/master','{name}','{session['username']}');")
		if(public=='true'):
			cur.execute(f"INSERT INTO access VALUES('{name}/master','*');")
		try:
			mkdir(f"{ROOT_PATH}\\files\\{name}")
		except FileExistsError:
			pass
		try:
			mkdir(f"{ROOT_PATH}\\files\\{name}\\master")
		except FileExistsError:
			pass
		con.commit()
	except Exception as e:
		print(e)
		error=str(e)
	finally:
		if con!=None:
			con.close()
		if cur!=None:
			cur.close()
	if(error==None):
		return "Created Repository"
	else:
		return error

@app.route("/upload/<reponame>/<branchname>",methods=["POST"])
def upload(reponame,branchname):
	try:
		username=session["username"]
	except KeyError as e:
		return redirect("/login")
	if(len(findall(r"[^a-zA_Z0-9_]",branchname+reponame))!=0):
		return "Invalid path"
	msg=con=cur=None
	try:
		con=pymysql.connect(DBHOST,DBUSER,DBPASS,DBNAME)
		cur=con.cursor()
		bname=reponame+"/"+branchname
		cur.execute(f"SELECT username FROM branch WHERE branchname='{bname}' AND username='{username}';")
		l=cur.fetchall()
		if(len(l)==0):
			raise Exception("Not allowed")
		for value in request.files.getlist("files"):
			if(value.filename==''):
				raise Exception("No Files Selected")
			value.save(f"{ROOT_PATH}\\files\\{reponame}\\{branchname}\\{value.filename}")
		msg=redirect(f"/dir/{reponame}/{branchname}")
	except Exception as e:
		print(e)
		msg=str(e)
	finally:
		if(cur!=None):
			cur.close()
		if(con!=None):
			con.close()
	return msg









if(__name__=="__main__"):
	app.run("0.0.0.0",debug=True)