import os
import random
from position import * # importe les classes Position et Deplacement

"""On définit 3 classes ici :
    - Labyrinthe : classe permettant la création et gestion d'un labyrinthe 2D.
    - Case : une case du labyrinthe, définit par sa Position et contenant un Obstacle
    - Obstacle : définit par un symbole et si celui est accessible ou non
"""

class Labyrinthe:
    """Attributs :
            - cases : les cases du labyrinthe (de la classe Case)
            - case_sortie : la case à atteindre pour sortir du labyrinthe
            - name : le nom du labyrinthe
            - robots : liste des robots présents dans le labyrinthe {de la classe Robot}
       Attributs de classe :
            - DOSSIER_LABYRINTHES : le dossier où sont stockés les labyrinthes au format texte 
            - LABYRINTHES : un dictionnaire permettant de stocker les labyrinthes {nom : Labyrinthe} une fois qu'ils sont chargés et crées depuis les fichiers textes
        Propriétés :
            - positions_robots : liste des positions des robots présents dans le labyrinthe
    => Méthodes :
            - Labyrinthe(name, cases, case_sortie) : création du labyrinthe
            - Labyrinthe.convert_from(fichier_txt) : création attributs du labyrinthe à partir d'un fichier texte
            - Labyrinthe.load_labyrinthes() : chargement des labyrinthes stockés au format texte
            - labyrinthe.positions_possibles() : renvoie la liste des positions possibles pour placer un nouveau robot
            - labyrinthe.positionner(robot) : positionnement aléatoire d'un robot dans le labyrinthe (si c'est possible)
            - labyrinthe.find_case_from(position) : permet de trouver la case correspondant à la position.
            - labyrinthe.get_robot_from(position) : méthode pour trouver un robot à une position donnée
            - .__repr__() : représentation du labyrinthe à partir de la représentation de l'ensemble des obstacles contenus par les cases du labyrinthe."""

    DOSSIER_LABYRINTHES = os.path.join(os.path.dirname( __file__ ),"labyrinthes")
    """Les labyrinthes déjà crées sont stockés dans un dictionnaire avec leur nom
    en clé. Il sont enregistrés dans des fichiers externes .txt qu'on chargera
    à chaque lancement du jeu (dans le dossier DOSSIER_LABYRINTHES)."""
    LABYRINTHES = {}

    def __init__(self, name, cases, case_sortie):
        """Création du labyrinthe"""
        self.name = name
        self.cases = cases
        self.case_sortie = case_sortie
        self.robots = []

    @classmethod
    def convert_from(cls, fichier_txt):
        """Création des attributs du labyrinthe à partir du fichier texte fichier_txt"""
        try:
            name,ext = os.path.splitext(os.path.basename(fichier_txt))
            assert fichier_txt.is_file() and ext == ".txt"
        except AssertionError:
            raise AssertionError("Fichier {} descriptif du labyrinthe au mauvais format".format(os.path.basename(fichier_txt)))

        """On créait l'ensemble des cases avec leurs obstacles, en faisant
        une liste de chaque ligne étant elle-même une liste de cases.
        self.cases[y][x] renverra donc la case à la x-ème colonne et y-ème ligne."""
        cases = []
        nb_case_sortie = 0
        with open(fichier_txt) as f:
            y = 0
            for line in f.readlines():
                line_cases = []
                x = 0
                for symbole in line:
                    if symbole != "\n":
                        case = Case(Position(x,y),Obstacle(symbole))
                        #on définit la case de sortie du labirynthe    
                        if symbole == Obstacle.SYMBOLE_SORTIE:
                            case_sortie = case
                            nb_case_sortie += 1
                        line_cases.append(case)    
                        x += 1
                cases.append(line_cases)
                y += 1
        #on vérifie qu'il y a bien une unique case sortie
        if not (nb_case_sortie == 1):
            raise AssertionError("Trop ou aucune case sortie {} definie(s) dans le fichier {}".format(os.path.basename(Obstacle.SYMBOLE_SORTIE, fichier_txt)))        
        
        return [name, cases, case_sortie]

    @classmethod
    def load_labyrinthes(cls):
        """Recupère, crée et renvoie la liste des labyrinthes disponibles et les met dans cls.LABYRINTHES"""

        cls.LABYRINTHES = {}
        """On regarde la liste des fichiers .txt enregistrés dans le dossier DOSSIER_LABYRINTHES."""
        for file in os.scandir(cls.DOSSIER_LABYRINTHES):
            name,ext = os.path.splitext(os.path.basename(file))
            if ext == ".txt":
                labyrinthe = Labyrinthe(*cls.convert_from(file))
                cls.LABYRINTHES[labyrinthe.name] = labyrinthe

        if not cls.LABYRINTHES:
            raise FileNotFoundError("Aucun labyrinthe enregistré !")

        return cls.LABYRINTHES

    def positions_possibles(self):
        """Renvoie la liste des positions possibles pour placer un nouveau robot."""
        positions = []

        for line in self.cases:
            for case in line:
                if (not case.position in self.positions_robots) and (case.obstacle == Obstacle()):
                    positions.append(case.position)
        
        return positions

    # à tester ?
    def positionner(self, robot, position = None):
        """Positionne aléatoirement un robot sur une case vide, sauf si une position est spécifiée."""

        if not position:
            positions = self.positions_possibles()
            if positions:
                position = random.choice(positions)
                robot.position = position
                self.robots.append(robot)
                return position
        else:
            robot.position = position
            self.robots.append(robot)
            return position

    @property
    def positions_robots(self):
        """Retourne une liste des positions des robots présents dans le labyrinthe"""
        return [robot.position for robot in self.robots]

    @classmethod
    def find_case_from(cls, cases, position):
        """Renvoi la case correspondant à la position dans la liste de cases. Renvoi None s'il y en a pas à cette position."""
        try:
            return cases[position.y][position.x]
        except IndexError:
            pass

    def get_robot_from(self, position):
        """Fonction pour trouver un robot à une position donnée."""
        pos_robots = self.positions_robots
        if position in pos_robots:
            i = 0
            while pos_robots[i] != position:
                i += 1
            return self.robots[i]
                
    def __repr__(self):
        """On représente les cases du labyrinthe avec le symbole des obstacles de
        chaque case, sauf pour celles où sont positionnés les robots, où on
        affichera leur symbole"""
        representation = ""
        pos_robots = self.positions_robots
        
        for line in self.cases:
            for case in line:
                if case.position in pos_robots:
                    representation += self.get_robot_from(case.position).symbole
                else:
                    representation += str(case)
            representation += "\n"
        return representation

    def copy_cases(self):
        """Renvoi une copie de self.cases contenant des copies de chaque case"""
        cases_copiees = []
        
        for line in self.cases:
            line_cases = []
            for case in line:
                line_cases.append(case.copy())
            cases_copiees.append(line_cases)

        return cases_copiees

class Obstacle:
    """
        Attributs :
            - symbole : symbole utilisé pour le représenter au format str
            - isAccessible : True si le robot peut s'y déplacer, False sinon (Boolean)
        Attribut de classe :
            - SYMBOLE_SORTIE : le symbole associé à la sortie du labyrinthe
            - LISTE_OBSTACLES : dictionnaire permettant de définir les obstacles qu'on peut avoir dans une case : {symbole : [nom, est accessible pour le robot]}
            - MODIFICATIONS_POSSIBLES : dictionnaire donnant les modifications possibles d'un obstacle par un robot
        Méthodes :
            - Obstacle(symbole = " ") : création d'un obstacle à partir de son symbole, par défaut il est vide
            - == de deux obstacles s'ils ont le même symbole
            - .__repr__() : représentation de l'Obstacle à partir de son symbole
            """

    SYMBOLE_SORTIE = "U"
    LISTE_OBSTACLES = {
                       SYMBOLE_SORTIE : ["Sortie", True],
                       " " : ["Vide", True],
                       "O" : ["Mur", False],
                       "." : ["Porte", True], 
                       }

    """On définit les modifications des obstacles possibles :
        - 'M' : murer une porte => obstacle passe de "." à "O"
        - 'P' : percer un mur en une porte => obstacle passe de "O" à "." """
    MODIFICATIONS_POSSIBLES = {"M" : (".","O"),
                               "P" : ("O",".")}

    def __init__(self, symbole = " "):
        """
          si pas d'obstacle
        O pour un mur
        . pour une porte
        U pour la sortie
        """
        self.symbole = str(symbole).upper()
        if self.symbole not in self.LISTE_OBSTACLES:
            raise ValueError("{} : symbole d'obstacle inexistant".format(symbole))

    @property
    def isAccessible(self):
        return self.LISTE_OBSTACLES[self.symbole][1]

    @property
    def nom(self):
        return self.LISTE_OBSTACLES[self.symbole][0] 

    def __eq__(self, obstacle):
        return self.symbole == obstacle.symbole

    def __repr__(self):
        return self.symbole

    def copy(self):
        return Obstacle(self.symbole)

class Case:
    """
    Attributs :
        - position: sa position (de la classe Position)
        - obstacle : l'obstacle qu'elle contient (de la classe Obstacle)
    Méthodes :
        - Case(position, obstacle = Obstacle()) : crée une case à la position donnée avec l'obstacle spécifié (celui-ci est par défaut vide)
        - == entre deux cases
        - .__repr__() : la représentation de la case renvoit la représentation de son obstacle"""

    def __init__(self, position, obstacle = Obstacle()):
        self.position = position
        self.obstacle = obstacle

    def __eq__(self, case):
        return (self.position == case.position) and (self.obstacle == case.obstacle)

    def __repr__(self):
        return str(self.obstacle)

    def copy(self):
        return Case(self.position.copy(), self.obstacle.copy())
        
    
