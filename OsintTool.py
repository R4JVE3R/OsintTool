from argparse import ArgumentParser
import os
import corefunctions as cf
import socket

parser = ArgumentParser()

parser.add_argument('-u','--username',help = 'Use this option for Username Lookup')
parser.add_argument("-e",'--email', help = "Use this option for Email Lookup")
parser.add_argument("-p",'--phone', help = "Use this option for Phone Lookup")
parser.add_argument("-w",'--website', help = "Use this option for Website Lookup, just enter domain name")

args = parser.parse_args()

if args.username:
    os.system(f'python UsernameLookup.py {args.username} --timeout 10')
    exit()
if args.email:
    email = args.email
    print(f"Checking for {email}")
    os.system(f'cd holehe && python core.py {email}')

    print('\n----------------------------------------\nEmail compromised in following breaches\n----------------------------------------')
    cf.get_breaches(email)

    if(email.endswith('@gmail.com')):
        print('\n------------\nGoogle Info\n------------\n')
        cf.get_gid(email)

    print(f'\nMight be available on Facebook\n------------------------------\nhttps://www.facebook.com/search/top?q={email}') 
    exit()
if args.phone:
    cf.phone_data(args.phone)
    exit()
if args.website:
    domain = args.website
    ip = socket.gethostbyname(domain)
    print(f"\nDomain: {domain}\nIP: {ip}")
    cf.basic_info(ip)
    print(f"{'-'*len('Whois Information')}\nWhois Information\n{'-'*len('Whois Information')}")
    cf.get_whois(domain)
    print(f"\n{'-'*len('Subdomains')}\nSubdomains\n{'-'*len('Subdomains')}")
    cf.get_subdomains(domain)
    print(f"\n{'-'*len('Reverse IP')}\nReverse IP\n{'-'*len('Reverse IP')}")
    cf.get_reverseip(ip)
    exit()

print("Use -h argument for help or guide.")