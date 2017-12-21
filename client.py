"""
** POJEKAT      : predmet Računarske mreže i telekomunikacije
** NAZIV        : Klijent
** OPIS         :      Klijentska strana aplikacije koja je namenjena
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
** DATUM: 21.12.2017.
**
** Copyright (C) Miloš Nikić, 2017.
"""

import socket


"""
Koristimo globalnu varijablu id koja će nam omogućiti 
da lakše vodimo računa o ulgovanim korisnicima
Ona je svaki put kada neko nije ulogovana jednaka praznom
stringu
"""
id = ""

"""
Registracija novih korisnika
"""

def add_new_user(s):
    global id
    print('\n' * 2)
    username = input("Unesite novo korisnicko ime: ")
    s.send(username.encode('ascii'))
    response = s.recv(1024)
    while response.decode('ascii')[0:3] == "ERR":
        print("Vec postoji korisnik sa {} nazivom!".format(username))
        username = input("Unesite neko drugo korisnicko ime: ")
        s.send(username.encode('ascii'))
        response = s.recv(1024)

    password = input("Unesite novu lozinku: ")
    s.send(password.encode('ascii'))
    response = s.recv(1024)
    while response.decode('ascii')[0:3] == "ERR":
        password = input("Unesite neku drugu lozinku: ")
        s.send(password.encode('ascii'))
        response = s.recv(1024)
    print("Uspesno izvrsena registracija!")
    print("-" * 30)
    id = username

"""
Preuzimanje fajlova
"""

def download(s):
    print('\n' * 2)
    code = input("Unesite kod zeljenog fajla za download['q' za prekid]: ")

    while len(code) != 10:
        if code == 'q':
            s.send('q'.encode('ascii'))
            return
        print('Kod za preuzimanje fajla mora imati deset cifara!')
        code = input("Unesite validan kod: ")

    s.send(code.encode())
    response = s.recv(1024)
    if response.decode('ascii') == "ERR":
        print("Dati fajl je nepostojeci.")
    else:
        with open('files/'+ code,'wb') as f:
            f.write(response)
        print("Uspesno preuzet {} fajl!".format(code))
        print("-" * 30)

"""
Funkcija za upload novog fajla
"""

def upload(s):
    global id
    print("\n" * 2)
    text = input("Unesite zeljeni tekst: ")
    while len(text) > 500:
        print("Uneti tekst sadrzi vise od 500 karaktera\n"\
              "Nastavak teksta ce biti odsecen\n"\
              "Ukoliko zelite da potvrdite i izvrsite upload unesite 'p'\n"\
              "Ukoliko ne zelite unesite 'q':")
        opcija = input()
        if opcija[:1] == 'p':
            text = text[0:500]
        elif opcija[:1] == 'q':
            text = input("Unesite zeljeni tekst: ")
    print("Tekst je uspesno unet.")
    s.send(text.encode('ascii'))
    response = s.recv(1024).decode('ascii')
    while response[0:2] != "OK":
        print("Doslo je do greske pri uplodu!")
        s.send(text.encode('ascii'))
        response = s.recv(1024).decode('ascii')
    print("Uspesno uploadovan fajl")
    #Primanje jedinstvenog koda za dati fajl
    code = s.recv(1024).decode('ascii')
    s.send(id.encode('ascii'))
    print("Vas kod potreban za download je: ",code)
    print("---------HINT----------")
    print("(Najbolje bi bilo zapisati ga na papir ;-))")
    print("-" * 30)

"""
Forma za logovanje
"""

def log_in(s):
    global id
    print("-" * 30)
    username = input("Unesite Vase korisnicko ime: ")
    s.send(username.encode('ascii'))
    response = s.recv(1024)
    while response.decode('ascii')[0:3] == "ERR":
        if username == 'q':
            return False
        username = input("Unesite postojece korisnicko ime: ")
        s.send(username.encode('ascii'))
        response = s.recv(1024)

    password = input("Unesite Vasu lozinku: ")
    s.send(password.encode('ascii'))
    response = s.recv(1024)
    while response.decode('ascii')[0:3] == "ERR":
        password = input("Uneli ste pogresnu lozinku\nPokusajte ponovo: ")
        s.send(password.encode('ascii'))
        response = s.recv(1024)
    print("Uspesno izvrseno logovanje!")
    print("-"*30)
    id = username
    return True
"""
Funkcija koja vrši navigaciju kroz aplikaciju
"""

def mainMenu(s):
    global id
    print('\n' * 2)
    while True:
        id = ""
        print("1. Log in")
        print("2. Sign up")
        print("3. Guest..")
        print("UNESITE 'q' ZA IZLAZ")
        option = input("Unesite zeljenu opciju: ")
        print("-" * 30)
        s.send(option.encode('ascii'))
        if option == '1':
            status = log_in(s)
            if status:
                suppMenu(s)
        elif option == '2':
            add_new_user(s)
            suppMenu(s)
        elif option == '3':
            print("Ulogovani ste kao gost\nOmogucen vam je samo download!")
            print("-" * 30)
            download(s)
        elif option == 'q':
            print("Vratite se ponovo.")
            print("-" * 30)
            return
        else:
            print("Unesite validnu komandu: ")
            print("-" * 30)
"""
Meni koji se prikazuje ulogovanim korisnicima
zatim se od njge trazi da unese zeljenu opciju
za nastavak rada
"""

def suppMenu(s):
    global id
    print('\n' * 2)
    while True:
        print('\t\t--Izaberite operaciju--\n\n')
        print("1. Download")
        print("2. Upload")
        print("3. Izlistaj moje fajlove")
        print("UNESITE 'q' ZA LOG OUT")
        userInput = input("Unesite zeljenu opciju: ")
        print("-" * 30)
        s.send(userInput.encode('ascii'))
        if userInput == '1':
            download(s)
        elif userInput == '2':
            upload(s)
        elif userInput == '3':
            s.send(id.encode('ascii'))
            print('Lista Vasih fajlova: ' + s.recv(1024).decode('ascii'))
            print("-" * 30)
        elif userInput == 'q':
            id = ''
            return

"""
Main metoda klijenta
"""

def main():
    host = socket.gethostname()
    port = 10000
    c = '\t'*5
    s = socket.socket()
    try:
        print()
        print('\t\t---Aplikacija za preuzimanje--\n'
              + c + '--i--'
              '\n\t\t--postavljanje fajlova na server--\n')
        s.connect((host,port))
        mainMenu(s)
    except ConnectionRefusedError:
        print("Veza sa serverom nije uspostavljena!")
        s.close()
    except:
        print("Doslo je do prekida konekcije!")
    s.close()

if __name__ == '__main__':
    main()
