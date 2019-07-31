import math

"""On définit 2 classes ici :
    - Position : permet de se positionner dans le labyrinthe
    - Deplacement : hérite de Position et s'apparente à un vecteur dans l'espace de coordonnées définit par Position
Il est possible d'utiliser ces classes en 1D, 2D ou 3D, même si le Labyrinthe construit est uniquement en 2D.
"""

class Position:
    """Attributs :
           - x : position en partant de 0 le plus à l'ouest et en allant vers l'est (int),
           - y : position en partant de 0 le plus au nord et en allant vers le sud (int),
           - z : correspond au niveau du labyrinthe de 0 le plus en bas et en allant vers le haut (int).
       Méthodes :
           - Position(x = 0, y = 0, z = 0) : création de la position à partir de ses coordonnées x, y et z, par défaut elles valent 0
           On redéfinit les méthodes spéciales suivantes :
               représentation : (x, y, z)
               = entre 2 positions ;
               representation"""
  
    def __init__(self, x = 0, y = 0, z = 0):
        if not (type(x) == int) and (type(y) == int) and (type(z) == int):
            raise ValueError("Les valeurs x, y, z spécifiées pour la position ne sont pas tous des entiers")
        self.x = x
        self.y = y
        self.z = z

    def __eq__(self, position):
        return (self.x == position.x) and (self.y == position.y) and (self.z == position.z) and (type(position) == type(self))

    def __repr__(self):
        return "({}, {}, {})".format(self.x, self.y, self.z)

    def copy(self):
        return Position(self.x, self.y, self.z)

class Deplacement(Position):
    """Classe définissant un vecteur dans l'espace de coordonnées x, y, z facilitant
    la gestion des déplacements du robot (= modification de sa position).
    Elle hérite de la classe Position.
    On redéfinit les méthodes spéciales suivantes :
        représentation : [x, y, z]
        + addition de deux déplacements ou d'un déplacement et d'une position ;
        multiplication d'un déplacement par un nombre."""

    def __repr__(self):
        return "[{}, {}, {}]".format(self.x, self.y, self.z)

    def __add__(self, deplacement_ou_position):
        """Addition de deux déplacements ou d'un déplacement et d'une position avec l'opérateur +.
        Renvoit une position si on fait déplacement + position ;
        Renvoit un déplacement si on fait déplacement + déplacement."""
        if type(deplacement_ou_position) == Position:
            return Position(self.x + deplacement_ou_position.x, self.y + deplacement_ou_position.y, self.z + deplacement_ou_position.z)
        elif type(deplacement_ou_position) == Deplacement:
            return Deplacement(self.x + deplacement_ou_position.x, self.y + deplacement_ou_position.y, self.z + deplacement_ou_position.z)
        else:
            raise TypeError("{} n'est pas de type Position ou Deplacement, impossible de faire l'addition".format(deplacement_ou_position))

    def __radd__(self, deplacement):
        return self + deplacement

    def __mul__(self, nombre):
        if not type(nombre) == int:
            raise ValueError("Un deplacement ne peut être multiplié que par un entier")
        return Deplacement(nombre * self.x, nombre * self.y, nombre * self.z)

    def __rmul__(self, nombre):
        return self * nombre

    def copy(self):
        return Deplacement(self.x, self.y, self.z)
