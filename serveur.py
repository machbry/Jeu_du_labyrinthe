from partie import * # importe la classe Partie
import socket
import select
import re

hote = ''
port = 12800

connexion_principale = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
connexion_principale.bind((hote, port))
connexion_principale.listen(5)

partie = Partie()

print("On attend les joueurs.")

accepte_nouveaux_joueurs = True
partie_finie = False
clients_connectes = []
nb_joueurs = 0
robots = {}
debut_msg_joueur = re.compile(r"^[0-9]{1}>") # pour identifier facilement le client (joueur)
symbole_prochain_robot = ""

while not partie_finie:

    msg_recu = b""

    """ On va vérifier que de nouveaux clients ne demandent pas à se connecter"""
    connexions_demandees, wlist, xlist = select.select([connexion_principale],
        [], [], 0.05)
        
    for connexion in connexions_demandees:
        connexion_avec_client, infos_connexion = connexion.accept()
        if accepte_nouveaux_joueurs:
            clients_connectes.append(connexion_avec_client)
        else:
            connexion_avec_client.send(b"NA")
    
    """ Maintenant, on écoute la liste des clients connectés
        Les clients renvoyés par select sont ceux devant être lus (recv)
        Si la liste de clients connectés est vide, une exception peut être levée """
    clients_a_lire = []
    try:
        clients_a_lire, wlist, xlist = select.select(clients_connectes,
                [], [], 0.05)
    except select.error:
        pass
    else:
        for client in clients_a_lire:

            msg_recu = client.recv(1024)
            """ Peut planter si le message contient des caractères spéciaux"""
            msg_recu = msg_recu.decode()
            
            if msg_recu != "Nouveau joueur":
                symbole_robot = ((debut_msg_joueur.match(msg_recu)).group())[0]
                msg_recu = msg_recu[2:]
              
            # ARRIVEE DUN NOUVEAU JOUEUR
            if msg_recu == "Nouveau joueur" and accepte_nouveaux_joueurs:
                nb_joueurs += 1
                symbole_robot = str(nb_joueurs)
                robots[symbole_robot] = client
                partie.nouveau_joueur(symbole_robot)
                client.send(("Bienvenue joueur {} ! Entrez C pour commencer a jouer ou Q pour quitter.".format(nb_joueurs)).encode())

            # LANCEMENT DUNE PARTIE
            elif msg_recu.upper() == "C" and accepte_nouveaux_joueurs:
                accepte_nouveaux_joueurs = False
                for client_connecte in clients_connectes:
                    client_connecte.send(b"Debut de la partie ! (Q pour quitter)")
                    client_connecte.send(str(partie).encode())

                partie.debut()
                symbole_prochain_robot = partie.prochain_robot_a_jouer.symbole
                robots[symbole_prochain_robot].send(("A toi - joueur {} - d'entrer une commande.".format(symbole_prochain_robot)).encode())

            # JOUER LA PARTIE
            elif symbole_robot == symbole_prochain_robot:
                partie.prise_en_compte(msg_recu, symbole_robot) 
                partie_finie, symbole_prochain_robot = partie.jouer()
                
                for client_connecte in clients_connectes:
                    client_connecte.send(("Joueur {} a joué.".format(symbole_robot)).encode())
                    client_connecte.send(str(partie).encode())                

                if not partie_finie:
                    robots[symbole_prochain_robot].send(("A toi - joueur {} - d'entrer une commande.".format(symbole_prochain_robot)).encode())
                    
            # QUITTER LA PARTIE
            elif msg_recu.upper() == "Q":
                accepte_nouveaux_joueurs = False
                partie_finie = True

print("Fermeture des connexions")
for client in clients_connectes:
    client.send(b"Fin de la partie (Q pour quitter).")
    client.close()

connexion_principale.close()
