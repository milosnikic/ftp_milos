"""
** POJEKAT      : predmet Računarske mreže i telekomunikacije
** NAZIV        : Server
** OPIS         :      Serverska strana aplikacije koja je namenjena
**                     za jednostavnu razmenu fajlova između servera
**                     i klijenta. Vrši se prikaz glavnog menija. Omogućeno
**                     je klijentu da vrši registraciju, log in.
**                     Klijentu je takođe omogućeno da izadje u bilo kom trenutku.
**                     Klijenti koji su ulogovani mogu dobiti spisak do tada uploadovanih
**                     fajlova.
**
**
**
**
**                      Ovde je dat prikaz stukture podataka u kojoj se čuvaju korisnici
**
**                                Primer izgleda koriscenog recnika
**
**                                korisnici = {
**                                    "korisnik1":{
**                                        "password":"fon123",
**                                        "files":[
**                                        "Gq37zTq432",
**                                        "mX6A1njGxZ",
**                                        ]
**                                    },
**                                    "korisnik2":{
**                                        "password":"fon321",
**                                        "files":[
**                                        "Gq37zTq432",
**                                       "mX6A1njGxZ",
**                                        ]
**                                    },
**                                }
**
** DATUM: 21.12.2017.
**
** Copyright (C) Miloš Nikić, 2017.
"""
import socket
import random
import threading
import json
import os

"""
Obavezno učitavanje json datoteke radi korišcenja 
rečnika korisnici
"""

def json_in(path):
    if os.path.isfile(path):
        with open(path, 'r') as q:
            data = q.read()
        return json.loads(data)
    else:
        return dict()


korisnici = json_in('db/korisnici.json')
ulogovani_korisnici = []

"""
Registracija novih korisnika
"""

def add_new_user(sock):
    username = sock.recv(1024)

    while username.decode('ascii') in korisnici.keys():
        sock.send("ERR".encode('ascii'))
        username = sock.recv(1024)
    sock.send("OK".encode('ascii'))

    p = sock.recv(1024)

    username = username.decode('ascii')
    password = p.decode('ascii')
    new_dic = {'password': password, 'files': []}
    korisnici[username] = new_dic
    ulogovani_korisnici.append(username)
    extract(korisnici)

"""
Preuzimanje fajlova
"""

def download(sock):
    code = sock.recv(1024).decode('ascii')
    if code == 'q':
        print('Zatvorio download')
        return
    status = False
    for file in os.listdir('db/files'):
        if os.path.basename(file) == code:
            with open('db/files/' + code,'rb') as f:
                text = f.read()
            sock.send(text)
            status = True
            break
    if not status:
        sock.send("ERR".encode('ascii'))
"""
Proveravanje da li kod vec postoji u bazi
"""

def check(code):
    for item in korisnici:
        if code in korisnici[item]['files']:
            return True
    return False

"""
Funkcija za upload novog fajla
"""

def upload(sock):
    text = sock.recv(1024).decode('ascii')
    while not text:
        sock.send("ERR".encode('ascii'))
        text = sock.recv(1024).decode('ascii')
    sock.send("OK".encode('ascii'))
    code = code_generator()
    #Provera da generisani kod ne postoji vec u bazi
    while check(code):
        code = code_generator()

    sock.send(code.encode('ascii'))
    with open('db/files/' + code,'wb') as f:
        f.write(text.encode('ascii'))
    username = sock.recv(1024).decode('ascii')
    korisnici[username]['files'].append(code)
    extract(korisnici)

"""
Forma za logovanje
"""

def log_in(sock):
    username = sock.recv(1024).decode('ascii')

    while username not in korisnici.keys():
        if username == 'q':
            sock.send('ERR'.encode('ascii'))
            print('Napustio log in.')
            return False
        sock.send("ERR".encode('ascii'))
        username = sock.recv(1024).decode('ascii')
    sock.send("OK".encode('ascii'))

    password = sock.recv(1024).decode('ascii')
    while password != korisnici[username]['password']:
        sock.send("ERR".encode('ascii'))
        password = sock.recv(1024).decode('ascii')
    sock.send("OK".encode('ascii'))
    ulogovani_korisnici.append(username)
    return True
"""
Funkcija koja vrši navigaciju kroz aplikaciju
"""

def mainMenu(sock):
    try:
        while True:
            userInput = sock.recv(1024)
            if userInput.decode('ascii') == '1':
                status = log_in(sock)
                if status:
                    suppMenu(sock)
            elif userInput.decode('ascii') == '2':
                add_new_user(sock)
                suppMenu(sock)
            elif userInput.decode('ascii') == '3':
                download(sock)
            elif userInput.decode('ascii') == 'q':
                print("Zatvorio konekciju za soket >>>")
                sock.close()
                return
    except:
        print("Doslo je do nasilnog prekida konekcije od strane klijenta!")

"""
Meni koji se prikazuje ulogovanim korisnicima
zatim se od njge trazi da unese zeljenu opciju
za nastavak rada
"""

def suppMenu(sock):
    while True:
        userInput = sock.recv(1024)
        if userInput.decode('ascii') == '1':
            download(sock)
        elif userInput.decode('ascii') == '2':
            upload(sock)
        elif userInput.decode('ascii') == '3':
            username = sock.recv(1024).decode('ascii')
            if not korisnici[username]['files']:
                sock.send('Nemate uploadovanih fajlova'.encode('ascii'))
            else:
                sock.send(", ".join(korisnici[username]['files']).encode('ascii'))
        elif userInput.decode('ascii') == 'q':
            return


"""
## UTILS
"""
"""
Generator jedinstvenog koda od deset karaktera(A-Z,a-z,0-9)
"""

def code_generator():
    letters = "abcdefghijklmnopqrstuvwxyz"
    upper_letters = letters.upper()
    numbers = "0123456789"
    sequence = letters + upper_letters + numbers
    code = ''
    for i in range(10):
        code += random.choice(sequence)
    return code

"""
Ekstrakcija recnika u JSON file.
"""

def extract(recnik):
    with open("db/korisnici.json",'w') as f:
        f.write(json.dumps(recnik,indent=2))

"""
Main metoda servera
"""

def main():
    host = socket.gethostname()
    port = 10000

    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    try:
        s.bind((host, port))
    except:
        print("Trazeni port je zauzet!")
        s.close()
        main()


    s.listen(5)

    print("Server je pokrenut...")
    while True:
        c, addr = s.accept()
        print("Konektovao se korisnik sa adresom: >>> {}:{}".format(addr[0],addr[1]))
        t = threading.Thread(target=mainMenu, args=(c,))
        t.start()

    s.close()

if __name__ == '__main__':
    main()