from threading import Thread, RLock
import socket
import re

hote = "localhost"
port = 12800

connexion_avec_serveur = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
connexion_avec_serveur.connect((hote, port))

"""On indique au serveur la présence d'un nouveau joueur :"""
connexion_avec_serveur.send(b"Nouveau joueur")
msg_recu = connexion_avec_serveur.recv(1024).decode()
if msg_recu == "NA":
    print("Désolé, la partie a dejà commencée ! Fermeture de la connexion.")
    connexion_avec_serveur.close()
else:
    num_joueur = (re.compile(r"[0-9]+").search(msg_recu)).group()
    print(msg_recu)

    class EnvoyerMessages(Thread):
        """Thread pour envoyer un message au serveur"""

        def __init__(self, symbole_robot):
            Thread.__init__(self)
            self.symbole_robot = symbole_robot

        def run(self):
            msg_env = ""
            while msg_env.upper() != "Q":
                msg_env = input("{}>".format(self.symbole_robot))
                connexion_avec_serveur.send((self.symbole_robot + ">" + msg_env).encode())           
            
    class EcouterMessages(Thread):
        """Thread pour ecouter les messages envoyés par le serveur"""

        def run(self):
            msg_recu = ""
            while msg_recu != "Fin de la partie (Q pour quitter).":
                msg_recu = connexion_avec_serveur.recv(1024).decode()
                print(msg_recu)

    thread_1 = EcouterMessages()
    thread_2 = EnvoyerMessages(num_joueur)
    thread_1.start()
    thread_2.start()
    thread_1.join()
    thread_2.join()

    print("Fermeture de la connexion")
    connexion_avec_serveur.close()
