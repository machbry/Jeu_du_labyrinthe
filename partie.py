from position import * # importe les classes Position et Deplacement
from labyrinthe import * # importe les classes Labyrinthe, Case et Obstacle
from robot import * # importe la classe Robot

"""On définit ici la classe Partie permettant la gestion d'une partie."""

class Partie:
    """
    Attributs :
        - labyrinthes : dictionnaire des labyrinthes auxquels on peut jouer (de la classe Labyrinthe)
        - choix_labyrinthes : dictionnaire avec un numéro pour que l'utilisateur puisse faire son choix en clé
                            et en valeur le nom du labyrinthe
        - labyrinthe : le labyrinthe dans lequel la partie va se joueur (de la classe Labyrinthe)
        - nb_joueurs_max : nb max de joueurs (= nb total de positions de départ possibles pour un robot)
        - joueurs : dictionnaire permettant de retrouver rapidement un robot à partir de son symbole
        - partie_finie : boolean indiquant si la partie est finie ou pas
    Propriétés :
        - robots : liste des robots présents dans le labyrinthe
    Méthodes :
        - Partie() : crée une Partie     
        - partie.choisir_labyrinthe() : choix du labyrinthe par l'utilisateur
        - partie.jouer() : permet de jouer à la partie
        """

    def __init__(self):
        """Création d'une partie"""

        """Chargement des labyrinthes :"""
        self.labyrinthes = Labyrinthe.load_labyrinthes()

        self.choix_labyrinthe = {}
        i = 1
        for name in self.labyrinthes:
            self.choix_labyrinthe[i] = name
            i += 1        

        """On demande à l'utilisateur de choisir un labyrinthe :"""
        self.labyrinthe = self.choisir_labyrinthe()

        self.nb_joueurs_max = len(self.labyrinthe.positions_possibles())
        self.joueurs = {}
        self.partie_finie = False

    @property
    def robots(self):
        return self.labyrinthe.robots

    @property
    def case_sortie(self):
        return self.labyrinthe.case_sortie

    def choisir_labyrinthe(self):
        """Choix du labyrinthe par l'utilisateur : (renvoit le labyrinthe choisi)"""
        print("Labyrinthes existants :")
        for numero, name in self.choix_labyrinthe.items():
            print("    {} - {}".format(numero,name))

        labyrinthe_est_choisi = False
        while not labyrinthe_est_choisi:
            choix_saisi = input("Entrez le numéro de labyrinthe dans lequel va se jouer la partie :")
            try:
                num_labyrinthe_choisi = int(choix_saisi)
            except ValueError:
                print("Choix '{}' saisi non valide : ce n'est pas un numéro.".format(choix_saisi))
            else:
                if num_labyrinthe_choisi in self.choix_labyrinthe:
                    labyrinthe_est_choisi = True
                    name_labyrinthe_choisi = self.choix_labyrinthe[num_labyrinthe_choisi]
                    return self.labyrinthes[name_labyrinthe_choisi]
                else:
                    print("Le numéro '{}' saisi n'est pas dans la liste.".format(num_labyrinthe_choisi))

    def nouveau_joueur(self, symbole_robot):
        if len(self.robots) < min(self.nb_joueurs_max, 9):
            robot = Robot(self.labyrinthe, symbole_robot)
            self.joueurs[symbole_robot] = robot
        else:
            print("Plus de place dans le labyrinthe pour un nouveau joueur")

    def debut(self):
        """Méthode lancée en début de partie."""
        if self.robots:
            self.num_joueur = 0
            self.prochain_robot_a_jouer = self.robots[self.num_joueur]
            self.partie_lancee = True
            self.nb_joueurs = len(self.robots)
        else:
            raise ValueError("Aucun robot pour lancer la partie")

    def prise_en_compte(self, instruction_txt, symbole_robot):
        """Méthode pour prendre en compte l'instruction entrée par un joueur."""
        robot = self.joueurs[symbole_robot]
        robot.enregistrer(instruction_txt)

    def jouer(self):
        """Méthode pour réaliser le prochain tour de la partie (un robot fait une action)
            Retourne (la partie est finie (boolean), le symbole du robot du joueur à qui il faut demander de rentrer une commande)"""
        if not self.partie_lancee:
            self.debut()

        partie_finie = False

        while (self.prochain_robot_a_jouer.instructions) and not (partie_finie):
        
            executee, nb_restantes = self.prochain_robot_a_jouer.prochaine_instruction()
            
            if executee:
                if self.prochain_robot_a_jouer.position == self.case_sortie.position:
                    partie_finie = True
                else:
                    self.num_joueur = (self.num_joueur + 1) % self.nb_joueurs
                    self.prochain_robot_a_jouer = self.robots[self.num_joueur]

        return (partie_finie, self.prochain_robot_a_jouer.symbole)
     
    def __repr__(self):
        return str(self.labyrinthe)
    

    
