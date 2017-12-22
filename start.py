import os

"""
Skripta koja ce izvrsiti inicijalizaciju hijerarhije fajlova

"""


"""
Dobijanje potrebnih putanja
"""
path = os.getcwd()
serverPath = path + '\\server'
clientPath = path + '\\client'


"""
Kreiranje server i klijent direktorijuma
"""
if not os.path.isdir(serverPath):
    os.mkdir(serverPath)
if not os.path.isdir(serverPath + '\\db'):
    os.mkdir(serverPath + '\\db')
if not os.path.isdir(clientPath):
    os.mkdir(clientPath)


"""
Kreiranje direktorijuma za skladistenje kako preuzetih tako i uploadovanih fajlova
"""
if not os.path.isdir(serverPath + '\\db\\files'):
    os.mkdir(serverPath + '\\db\\files')
if not os.path.isdir(clientPath + '\\files'):
    os.mkdir(clientPath + '\\files')


"""
Premestanje skripti u odgovarajuce direktorijume
"""
if not os.path.isfile(serverPath + '\\server.py'):
    os.rename(path + '\\server.py', serverPath + '\\server.py')
if not os.path.isfile(clientPath + '\\client.py'):
    os.rename(path + '\\client.py', clientPath + '\\client.py')
print('Inicijalizacija projekta uspesno izvrsena!')