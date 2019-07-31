# coding=utf-8
from position import * # importe les classes Position et Deplacement
from labyrinthe import * # importe les classes Labyrinthe, Case et Obstacle

"""On définit la classe Robot, permettant la création et gestion du robot dans le labyrinthe"""

class Robot:
    """
    Attributs :
        - labyrinthe : le labyrinthe où est crée le robot (de la classe Labyrinthe)
        - position : sa position dans le labyrinthe (de la classe Position)
        - symbole : son symbole pour le représenter (str)
        - instructions : liste des instructions à executer dans l'ordre
    Attributs de classe :
        - DEPLACEMENTS_UNITAIRES_POSSIBLES : un dictionnaire des deplacements unitaires possibles pour l'ensemble des robots
        - AIDE_UTILISATEUR : l'aide utilisateur pour que l'utilisateur puisse connaitre les déplacement autorisés et instructions textes associées (str)
        - MODIFICATIONS_POSSIBLES : un dictionnaire des modifications des obstacles du labyrinthe possibles pour l'ensemble des robots
    Méthodes :
        - Robot(labyrinthe, symbole) : création du robot avec son symbole et positionnement de celui-ci dans le labyrinthe
        - robot._se_deplacer(deplacement) : le robot se déplace selon le déplacement donné.
        - robot._modifier(modification_obstacle) : le robot modifie l'obstacle sur la case adjacente dans la direction donnée
        - Robot.convertir(instruction_txt) : permet de convertir une instruction texte en une liste de déplacements/modifications d'obstacles
        - robot.peut_executer(instructions) : verifie que le robot peut exectuer les instructions (boolean)
        - robot.enregistrer(instruction) : enregistre l'instruction à la fin des instructions
        - robot.prochaine_instruction() : execute la prochaine instruction pour que le robot se déplace
        - self.__repr__() : on représente le robot par son symbole
    """

    """On définit les déplacement unitaires possibles pour le robot.
    4 directions possibles : Nord (N), Est (E), Sud (S) et Ouest (O)."""
    DEPLACEMENTS_UNITAIRES_POSSIBLES = {"N" : Deplacement(0,-1),
                                        "E" : Deplacement(1,0),
                                        "S" : Deplacement(0,1),
                                        "O" : Deplacement(-1,0)}

    """On récupère les modifications des obstacles possibles :"""
    MODIFICATIONS_POSSIBLES = Obstacle.MODIFICATIONS_POSSIBLES
    
    AIDE_UTILISATEUR = """Commandes pour déplacer le robot :
- N pour déplacer le robot d'une case vers le nord (c'est-à-dire le haut de votre écran)
- E pour déplacer le robot d'une case vers l'est (c'est-à-dire la droite de votre écran)
- S pour déplacer le robot d'une case vers le sud (c'est-à-dire le bas de votre écran)
- O pour déplacer le robot d'une case vers l'ouest (c'est-à-dire la gauche de votre écran)
Chacune des directions ci-dessus suivies d'un nombre permet d'avancer de plusieurs cases (par exemple E3 pour avancer de trois cases vers l'est)
- M + une direction (N/E/S/O) pour murer une porte
- P + une direction (N/E/S/O) pour percer un mur et mettre une porte"""

    def __init__(self, labyrinthe, symbole = "X", position = None):
        """Creation du robot"""
        self.position = labyrinthe.positionner(self, position)
        self.labyrinthe = labyrinthe
        self.symbole = str(symbole)
        self.instructions = []
        
    def _se_deplacer(self, deplacement):
        """Le robot se déplace selon le déplacement donné."""
        self.position += deplacement

    def _modifier(self, modification_obstacle):
        """le robot modifie l'obstacle sur la case adjacente dans la direction donnée."""
        symbole_avant, symbole_apres = modification_obstacle.modification
        direction = modification_obstacle.direction
        case_a_modifier = Labyrinthe.find_case_from(self.labyrinthe.cases, self.position + direction)
        assert case_a_modifier.obstacle.symbole == symbole_avant
        case_a_modifier.obstacle.symbole = symbole_apres
    
    def enregistrer(self, instruction):
        """Enregistre l'instruction à la fin des instructions. La convertie si elle est au format txt.
            Supprime l'ensemble des instructions à exécuter si celles_ci font faire au robot une instruction non autorisée.
            Retourne un tuple :
            (instructions accessibles (boolean), le nb d'instructions enregistrées)."""
        instructions_valides = True
        
        if (type(instruction) == str) or (not instruction):
            try:
                instruction = self.convertir(instruction)
            except ValueError:
                nb_instructions_enr = 0
            else:
                self.instructions.extend(instruction)
                nb_instructions_enr = len(instruction)
        elif type(instruction) in [Deplacement, ModificationObstacle]:
            self.instructions.append(instruction)
            nb_instructions_enr = 1
        else:
            print("L'instruction '{}' n'est pas au format Str ou Deplacement ou ModificationObstacle".format(instruction))
            nb_instructions_enr = 0

        if not self.peut_executer(self.instructions):        
            self.instructions = []
            nb_instructions_enr = 0
            instructions_valides = False

        return (instructions_valides, nb_instructions_enr)

    def prochaine_instruction(self):
        """Execute la prochaine instruction.
            Supprime l'ensemble des instructions à exécuter si celle ci fait
            faire au robot une instruction non autorisée.
            Renvoi un tuple :
            (instruction exécutée (boolean), le nb d'instructions restantes)"""
        instruction_executee = False
        if self.instructions:
            if not self.peut_executer(self.instructions):
                self.instructions = []
            else:
                instruction = self.instructions.pop(0)
                if type(instruction) == Deplacement:
                    self._se_deplacer(instruction)
                elif type(instruction) == ModificationObstacle:
                    self._modifier(instruction)
                instruction_executee = True
        else:
            print("Pas d'instruction à executer dans {}".format(self.instructions))

        return (instruction_executee, len(self.instructions))

    def peut_executer(self, instructions):
        """Verifie que le robot peut acceder à une position cible en suivant la liste d'instructions :
            => pas d'obstacle non accéssible (sauf si modifié à temps), de case en dehors du labyrinthe ou un autre robot. """
        position_test = self.position
        estAccessible = True
        i = 0
        nbInstructions = len(instructions)
        cases_copiees = self.labyrinthe.copy_cases()
        
        while estAccessible and (i < nbInstructions):
            instruction = instructions[i]
            positions_occupees = self.labyrinthe.positions_robots.copy()
            positions_occupees.remove(self.position)
            if type(instruction) == Deplacement:
                position_test += instruction
                case = Labyrinthe.find_case_from(cases_copiees, position_test)
                if not case:
                    estAccessible = False
                else:
                    estAccessible = (case.obstacle.isAccessible) and (case.position not in positions_occupees)
                    i += 1
            elif type(instruction) == ModificationObstacle:
                modification = instruction.modification
                direction = instruction.direction
                position_case_modifiee = position_test + direction
                case = self.labyrinthe.find_case_from(cases_copiees, position_case_modifiee)
                if not case:
                    estAccessible = False
                else:
                    symbole_avant, symbole_apres = modification
                    estAccessible = (case.obstacle.symbole == symbole_avant) and (case.position not in positions_occupees)
                    case.obstacle.symbole = symbole_apres
                    i += 1

        if not estAccessible:
            print("""La liste des instructions enregistrées font arriver le robot en dehors du labyrinthe
                    ou traverser une case avec un obstacle infranchissable/autre robot
                    ou faire un modification d'obstacle impossible.
                    Ensemble des instructions effacées.""")

        return estAccessible
            
    @classmethod                             
    def convertir(cls, instruction_txt):
        """Transforme une instruction texte en une liste de Deplacements/Modifications d'obstacles.Format de l'instruction texte :
                => (clé d'un des DEPLACEMENTS_UNITAIRES_POSSIBLES) + (nombre de fois qu'on souhaite répéter le déplacement choisit)
                Exemples : "N" pour se déplacer d'une case vers le nord, "E3" pour se déplacer de 3 cases vers l'est.
                => (clé d'une des MODIFICATIONS_POSSIBLES) + (clé d'un des DEPLACEMENTS_UNITAIRES_POSSIBLES pour indiquer la direction où trouver la case à modifier)
                Exemples : "ME" pour murer la porte juste à l'est, "PN" pour percer le mure juste au nord"""

        if not instruction_txt:
            return [Deplacement(0,0)]
        elif not type(instruction_txt) == str:
            raise TypeError("Instruction '{}' n'est pas au format texte.".format(instruction_txt))
        else:
            premiere_lettre = instruction_txt[0].upper()
            premiere_lettre_est_deplacement = premiere_lettre in cls.DEPLACEMENTS_UNITAIRES_POSSIBLES.keys()
            premiere_lettre_est_modification = premiere_lettre in cls.MODIFICATIONS_POSSIBLES.keys()
            if not (premiere_lettre_est_deplacement or premiere_lettre_est_modification):
                print("Première lettre '{}' de l'instruction texte non valide. Doit être égale à une de ces listes : {},{}"
                                 .format(instruction_txt[0], cls.DEPLACEMENTS_UNITAIRES_POSSIBLES.keys(), cls.MODIFICATIONS_POSSIBLES.keys()))
                raise ValueError
            elif premiere_lettre_est_deplacement:
                if not instruction_txt[1:]:
                    return [cls.DEPLACEMENTS_UNITAIRES_POSSIBLES[premiere_lettre]]
                else:
                    try:
                        nombre = int(instruction_txt[1:])
                    except ValueError:
                        print("Vous devez indiquez un entier ou rien après la première lettre de l'instruction : '{}'".format(instruction_txt))
                        raise ValueError
                    return [cls.DEPLACEMENTS_UNITAIRES_POSSIBLES[premiere_lettre] for i in range(nombre)]
            elif premiere_lettre_est_modification:
                if not instruction_txt[1:]:
                    print("Il manque la deuxieme lettre de l'instruction après '{}'. Doit être égale à une de cette liste : {}"
                                 .format(instruction_txt[0], cls.DEPLACEMENTS_UNITAIRES_POSSIBLES.keys()))
                    raise ValueError
                elif not len(instruction_txt[1:]) == 1:
                    print("Seulement une lettre après la première indiquée : '{}'. Doit être égale à une de cette liste : {}"
                                 .format(instruction_txt[0], cls.DEPLACEMENTS_UNITAIRES_POSSIBLES.keys()))
                    raise ValueError
                else:
                    deuxieme_lettre = instruction_txt[1].upper()
                    if not (deuxieme_lettre in cls.DEPLACEMENTS_UNITAIRES_POSSIBLES.keys()):
                        print("Deuxième lettre '{}' de l'instruction texte non valide. Doit être égale à une de ces listes : {}"
                                         .format(instruction_txt[1], cls.DEPLACEMENTS_UNITAIRES_POSSIBLES.keys()))
                        raise ValueError
                    else:
                        return [ModificationObstacle(cls.MODIFICATIONS_POSSIBLES[premiere_lettre], cls.DEPLACEMENTS_UNITAIRES_POSSIBLES[deuxieme_lettre])]

    def __repr__(self):
        return str(self.symbole)

class ModificationObstacle:
    """Associe une modification (un tuple symbole_avant, symbole_apres) et une direction (un déplacement qui donne la direction pour savoir quel obstacle adjacent modifier)."""

    def __init__(self, modification, direction):
        self.modification = modification
        self.direction = direction

        assert modification in Obstacle.MODIFICATIONS_POSSIBLES.values()
        assert direction in Robot.DEPLACEMENTS_UNITAIRES_POSSIBLES.values()

    def __eq__(self, autre):
        return (self.modification == autre.modification) and (self.direction == autre.direction)
