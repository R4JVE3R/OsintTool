import requests
import json
import os
from dotenv import load_dotenv
load_dotenv()

#########
#For Phone
#########
def phone_data(number,mode='x'):
    headers= {"Authorization": os.getenv('TRUECALLER_AUTH'), "User-Agent":"Truecaller/11.74.6 (Android;6.0.1)"}
    res = requests.get(f"https://search5-noneu.truecaller.com/v2/search?q={number}&countryCode=IN&type=4",headers=headers)

    data = json.loads(res.text)

    name = data['data'][0]['name']
    carrier = data['data'][0]['phones'][0]['carrier']
    address = data['data'][0]['addresses'][0]['city']
    email = ''
    if(data['data'][0]['internetAddresses']):
        email = data['data'][0]['internetAddresses'][0]['id']

    try:
        image = data['data'][0]['image']
        if(mode == 'w'):
            if(email):
                exportdata = [name,carrier,address,email,image]
                exportname = ['Name:','Carrier:','Address:','Email:','Image:']
                return exportdata, exportname
            else:
                exportdata = [name,carrier,address,image]
                exportname = ['Name:','Carrier:','Address:','Image:']
                return exportdata, exportname
        if(email):
            print(f"\nNumber: {number}\nName: {name}\nEmail: {email}\nCarrier: {carrier}\nAddress: {address}\nImage: {image}")
        else:
            print(f"\nNumber: {number}\nName: {name}\nCarrier: {carrier}\nAddress: {address}\nImage: {image}")
        print(f'\nMight be available on Facebook\n------------------------------\nhttps://www.facebook.com/search/top?q={number}')
    except:
        if(mode == 'w'):
            if(email):
                exportdata = [name,carrier,address,email]
                exportname = ['Name:','Carrier:','Address:','Email:']
                return exportdata, exportname
            else:
                exportdata = [name,carrier,address]
                exportname = ['Name:','Carrier:','Address:']
                return exportdata, exportname
        if(email):
            print(f"\nNumber: {number}\nName: {name}\nEmail: {email}\nCarrier: {carrier}\nAddress: {address}")
        else:
            print(f"\nNumber: {number}\nName: {name}\nCarrier: {carrier}\nAddress: {address}")
        print(f'\nMight be available on Facebook\n------------------------------\nhttps://www.facebook.com/search/top?q={number}')
#########
#For Web
#########
whois_key = os.getenv('WHOIS_KEY')
def basic_info(ip,mode='c'):
    res = requests.get(f"https://ipinfo.io/{ip}/json")
    data = json.loads(res.text)
    address = data['city']+', '+data['region']+', '+data['country']+'.'
    loc = data['loc']
    org = data['org']
    if(mode == 'w'):
        return address,loc,org
    print(f"Server Location: {address}\nLatitude & Longitude: {loc}\nISP: {org}\n")

def get_whois(domain,mode='c'):
    res = requests.get(f"https://api.ip2whois.com/v2?key={whois_key}&domain={domain}")
    whois = json.loads(res.text)

    create_date = whois['create_date'].split('T')[0]
    update_date = whois['update_date'].split('T')[0]
    expire_date = whois['expire_date'].split('T')[0]
    registrar = whois['registrar']['name']
    nameservers = whois['nameservers'][0]
    owner_name = whois['registrant']['name']
    owner_organization = whois['registrant']['organization']
    owner_email = whois['registrant']['email']
    owner_phone = whois['registrant']['phone']
    owner_street_address = whois['registrant']['street_address']
    owner_city = whois['registrant']['city'] 
    owner_region = whois['registrant']['region']
    owner_country = whois['registrant']['country']
    owner_zip = whois['registrant']['zip_code']

    if(mode == 'w'):
        whoisdata = []
        whoisdata.extend((create_date,update_date,expire_date,registrar,nameservers,owner_name,owner_organization,owner_email,owner_phone,owner_street_address,owner_city,owner_region,owner_zip,owner_country))
        whoisname = []
        whoisname.extend(('Register Date','Update Date','Expiration Date','Registrar','Name Server'))
        whoisname.extend(('Owner Name','Owner Organization','Owner Email','Owner Phone','Owner Address','Owner City','Owner Region','Owner Zip','Owner Country'))
        return whoisname, whoisdata

    print(f"Register Date: {create_date}\nUpdate Date: {update_date}\nExpiration Date: {expire_date}\nRegistrar: {registrar}\nName Server: {nameservers}")
    print("\nOwner Name: "+owner_name)
    print("Owner Organization: "+owner_organization)
    print("Owner Email: "+owner_email)
    print("Owner Phone: "+owner_phone)
    print("Owner Address: "+owner_street_address)
    print("Owner City: "+owner_city)
    print("Owner Region: "+owner_region)
    print("Owner Zip: "+owner_zip)
    print("Owner Country: "+owner_country)

def get_subdomains(domain,mode='c'):
    url = "https://api.securitytrails.com/v1/domain/"+domain+"/subdomains"
    parameter = {
        "apikey": os.getenv('SECURITYTRAILS_KEY')
    }
    respo = requests.get(url,params=parameter)

    Ans = respo.text
    x = json.loads(Ans)
    if(mode == 'w'):
        return x
    
    for i,onesub in enumerate(x["subdomains"]):
        subdo = onesub+"."+domain
        print(f"{i+1}. {subdo}")

def get_reverseip(ip):
    res = requests.get(f"https://api.hackertarget.com/reverseiplookup/?q={ip}")
    print(res.text)

#########
#For Email
#########

def get_breaches(email,mode='c'):
    headers = {
        'hibp-api-key': os.getenv('HIBP_KEY'),
        'user-agent': 'whatever (Android client)'
    }
    try:
        res =  requests.get(f'https://haveibeenpwned.com/api/v3/breachedaccount/{email}?includeUnverified=false&truncateResponse=false',headers=headers)
        data = json.loads(res.text)
        if(mode == 'w'):
            return data
        for i,one in enumerate(data):
            domain = one['Domain']
            breach_date = one['BreachDate']
            breach_contains = ", ".join(one['DataClasses'])
            print(f'\n{i+1}. {domain}\nBreach Date: {breach_date}\nBreach Contains: {breach_contains}')
    except:
        print("")

cookie = os.getenv('G_COOKIE')
def get_gid(email,mode='c'):
    data = {
        'id':email,
        'type':'EMAIL',
        'matchType':'EXACT'
    }
    headers = {
        'X-HTTP-Method-Override': 'GET',
        'Authorization': os.getenv('HANGOUTS_Authorization'),
        'Origin': 'https://hangouts.google.com',
        'Cookie': cookie
    }
    url = 'https://people-pa.clients6.google.com/v2/people/lookup?key=' + os.getenv('HANGOUTS_KEY')
    try:
        res = requests.post(url,data=data,headers=headers)
        jsondata = json.loads(res.text)
        gid = jsondata['matches'][0]['personId'][0]
        if(mode == 'w'):
            return gid
        get_name(gid)
    except:
        if(mode == 'w'):
            return 'null','null'
   

def get_name(gid,mode='c'):
    headers = {
        'Authorization': os.getenv('GDRIVE_Authorization'),
        'Origin': 'https://drive.google.com',
        'Cookie': cookie
    }
    url= f'https://people-pa.clients6.google.com/v2/people?person_id={gid}&request_mask.include_container=PROFILE&request_mask.include_container=DOMAIN_PROFILE&request_mask.include_field.paths=person.metadata.best_display_name&request_mask.include_field.paths=person.photo&request_mask.include_field.paths=person.email&core_id_params.enable_private_names=true&key='+os.getenv('GDRIVE_KEY')
    res = requests.get(url,headers=headers)
    data = json.loads(res.text)
    name = data['personResponse'][0]['person']['metadata']['bestDisplayName']['displayName']
    photo = data['personResponse'][0]['person']['photo'][0]['url']
    reviews = 'https://www.google.com/maps/contrib/'+gid
    if(mode == 'w'):
        return name, photo, reviews
    print(f'Name: {name}\nPhoto: {photo}\nMap Reviews: {reviews}')