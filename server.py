import subprocess
import re
from flask import Flask, render_template
import corefunctions as cf
import socket
import requests

app = Flask(__name__)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/username')
def username():
    return render_template('username.html')

@app.route('/username/<usrname>')
def usernameGo(usrname):
    usrname = usrname.replace("&","").replace("|","").replace(";","").replace("`","").replace("$","")
    # If you have multiple python versions installed on your system, replace below 'python' with 'python3'. 
    full = subprocess.check_output('python UsernameLookup.py '+usrname+' --timeout 5',shell=True)
    full = full.decode("utf-8")
    full = full.replace('\n','<br>')
    names =  re.findall(r'[A-Z][A-Za-z0-9.!_-]{2,20}:',full)
    links = re.findall(r'[h][t][A-Za-z://.0-9@]{2,90}',full)
    return render_template('username.html',username=usrname,full=full,names=names,links=links)

@app.route('/email')
def email():
    return render_template('email.html')
@app.route('/email/<email>')
def emailGo(email):
    email = email.replace("&","").replace("|","").replace(";","").replace("`","").replace("$","")
    emailusedin = []
    # If you have multiple python versions installed on your system, replace below 'python' with 'python3'.
    full = subprocess.check_output('cd holehe & python core.py '+email,shell=True)
    full = full.decode("utf-8")
    full = re.findall(r'\[\+\] [a-z0-9]+\.[a-z]+',full)
    for x in full:
        emailusedin.append(x.split('[+] ')[1])
    try:
        breaches = cf.get_breaches(email,'w')
        blen = len(breaches)
    except:
        blen = 0
    if(email.endswith('@gmail.com')):
        glen = 1
        gid = cf.get_gid(email,'w')
        if (gid == 'null'):
            name,photo,review = 'null','https://google.com','null'
        else:
            name,photo,review = cf.get_name(gid,'w')
    else:
        name=1
        photo=1
        review=1
        glen = 0
    return render_template('email.html',email=email,emailusedin=emailusedin,breaches=breaches,name=name,photo=photo,review=review,blen=blen,glen=glen)

@app.route('/phone')
def phone():
    return render_template('phone.html')
@app.route('/phone/<phone>')
def phoneGo(phone):
    if(len(phone) == 10 and isinstance(int(phone),int)):
        data,dname = cf.phone_data(int(phone),'w')
        return render_template('phone.html',data=data,dname=dname,phone=phone)
    else:
        return "Incorrect Phone Number"

@app.route('/website')
def website():
    return render_template('website.html')
@app.route('/website/<website>')
def websiteGo(website):
    ip = socket.gethostbyname(website)
    address,loc,org = cf.basic_info(ip,'w')
    whoisname, whoisdata = cf.get_whois(website,'w')
    subdomains = cf.get_subdomains(website,'w')
    res = requests.get(f"https://api.hackertarget.com/reverseiplookup/?q={ip}")
    res = res.text.split('\n')
    return render_template('website.html',ip=ip,domain=website,address=address,loc=loc,org=org,whoisname=whoisname,whoisdata=whoisdata,subdomains=subdomains,reverseip=res)

if __name__ == '__main__':
    app.run(debug=True)