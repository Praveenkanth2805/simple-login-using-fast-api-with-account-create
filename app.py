from fastapi import FastAPI, Request, Form
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse, RedirectResponse as rr
import sqlite3

app=FastAPI()

con=sqlite3.connect("userdb",check_same_thread=False)
cur=con.cursor()

cur.execute("""
            create table if not exists users(
                id integer primary key autoincrement,
                username text unique not null,
                password text
            );
            """)
#first time run without cmd line next two line
#cur.execute("insert into users (username,password) values('praveen','2005');")
#con.commit()

cur.execute("select username, password from users")
row=cur.fetchall()
user={uname:pw for uname,pw in row}
print(user)

t=Jinja2Templates(directory="templates")

# user={
        # "praveen":"2005"
    # }


@app.get("/", response_class=HTMLResponse)
def home(request:Request):
    return t.TemplateResponse('login.html',{"request":request,"message":""})

@app.post("/login", response_class=HTMLResponse)
def login(request:Request,uname:str=Form(..., alias="username"),
          pw:str=Form(...,alias="password")):
    
    if uname in user and pw==user[uname]:
        return t.TemplateResponse("after_login.html",{"request":request,"message":f""})
    msg="username or password is not match"
    return t.TemplateResponse("login.html",{"request":request,"error":msg})

@app.get("/logout" ,response_class=HTMLResponse)
def logout(request:Request):
    return rr(url="/",status_code=302)

@app.get("/signup", response_class=HTMLResponse)
def goSignPage(request:Request):
    return t.TemplateResponse("signup.html",{"request":request,"msg":""})

@app.post("/addAccount", response_class=HTMLResponse)
def account(request:Request, un:str=Form(..., alias="username"),
            pw:str=Form(..., alias="password"), 
            cpw:str=Form(..., alias="confirmPassword")):
    if pw==cpw:
        if un in user:
            return t.TemplateResponse("signup.html",{"request":request,"msg":"user name is already exist"})
        cur.execute("insert into users (username,password) values(?,?)",(un,pw))
        con.commit()
        con.close()
        #user[un]=pw
        msg=f"registered sucessfully"
        return t.TemplateResponse("signup.html",{"request":request,"msg":msg})
    return t.TemplateResponse("signup.html", {"request":request,"msg":"password and confirm password is must same!"})
