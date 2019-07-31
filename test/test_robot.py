import sys
import unittest
sys.path[:0] = ['../']
from robot import *
from labyrinthe import *

class RobotTest(unittest.TestCase):
    """Test case utilisé pour tester les fonctons de la classe Robot."""

    def setUp(self):
        """Initialisation des tests. Création d'un labyrinthe et d'un robot."""
        Labyrinthe.DOSSIER_LABYRINTHES = os.path.join(os.path.dirname( __file__ ),"labyrinthes")
        self.labyrinthe = Labyrinthe.load_labyrinthes()['facile']
        self.robot = Robot(self.labyrinthe, "X")
        self.murer = Obstacle.MODIFICATIONS_POSSIBLES["M"]
        self.percer = Obstacle.MODIFICATIONS_POSSIBLES["P"]
        
    def tearDown(self):
        """Méthode appelée après chaque test."""
        pass

    def test_se_deplacer(self):
        """Test de la méthode robot._se_deplacer(deplacement)."""

        for deplacement in Robot.DEPLACEMENTS_UNITAIRES_POSSIBLES.values():
            position_init = self.robot.position
            position_finale = position_init + deplacement
            self.robot._se_deplacer(deplacement)
            self.assertEqual(self.robot.position, position_finale)

    def test_modifier(self):
        """Test de la méthode robot._modifier(modification_obstacle)."""
        self.robot.position = Position(3,5)

        for direction in Robot.DEPLACEMENTS_UNITAIRES_POSSIBLES.values():
            modification_obstacle = ModificationObstacle(self.percer, direction)
            self.robot._modifier(modification_obstacle)
            self.assertEqual(Labyrinthe.find_case_from(self.labyrinthe.cases, self.robot.position + direction).obstacle, Obstacle("."))

        for direction in Robot.DEPLACEMENTS_UNITAIRES_POSSIBLES.values():
            modification_obstacle = ModificationObstacle(self.murer, direction)
            self.robot._modifier(modification_obstacle)
            self.assertEqual(Labyrinthe.find_case_from(self.labyrinthe.cases, self.robot.position + direction).obstacle, Obstacle("O"))        

    def test_convertir(self):
        """Test de la méthode Robot.convertir(instruction)."""
        tests = [(1, 4, TypeError),
                (2, "Z", ValueError),
                (3, "ne", ValueError),
                (4, "n1.5", ValueError),
                (5, "", [Deplacement(0,0)]),
                (6, "n", [Deplacement(0,-1)]),
                (7, "s", [Deplacement(0,1)]),
                (8, "e", [Deplacement(1,0)]),
                (9, "o", [Deplacement(-1,0)]),
                (10, "s3", [Deplacement(0,1), Deplacement(0,1), Deplacement(0,1)]),
                (11, 0, [Deplacement(0,0)]),
                (12, "m", ValueError),
                (13, "mz", ValueError),
                (14, "pnn", ValueError),
                (15, "pn", [ModificationObstacle(self.percer, Deplacement(0,-1))]),
                (16, "ms", [ModificationObstacle(self.murer, Deplacement(0,1))])]
                            
        for (num_test, instruction, resultat_attendu) in tests:
            if type(resultat_attendu) == type:
                with self.assertRaises(resultat_attendu):
                    Robot.convertir(instruction)
            elif type(resultat_attendu) == list:
                self.assertEqual((num_test, resultat_attendu), (num_test, Robot.convertir(instruction)))

    def test_peut_executer(self):
        """Test de la méthode robot.peut_executer(deplacements)."""
        self.robot.position = Position(5,5)
        self.autre_robot = Robot(self.labyrinthe, "x")
        self.autre_robot.position = Position(8,5)

        tests = [(1, [], True),
                (2, [Deplacement()], True),
                (3, [Deplacement(0,1)], False),
                (4, [Deplacement(0,-1)], False),
                (5, [Deplacement(1,0)], True),
                (6, [Deplacement(-1,0)], False),
                (7, [Deplacement(-1,0), Deplacement(-1,0)], False),
                (8, [Deplacement(1,0), Deplacement(1,0)], True),
                (9, [Deplacement(-1,0), Deplacement(-1,0), Deplacement(-1,0), Deplacement(-1,0), Deplacement(-1,0), Deplacement(-1,0)], False),
                (10, [Deplacement(1,0), Deplacement(1,0), Deplacement(1,0), Deplacement(1,0)], False),
                (11, [ModificationObstacle(self.murer, Deplacement(-1,0))], False),
                (12, [ModificationObstacle(self.percer, Deplacement(-1,0))], True),
                (13, [ModificationObstacle(self.percer, Deplacement(-1,0)), Deplacement(-1,0), Deplacement(-1,0), ModificationObstacle(self.murer, Deplacement(1,0))], True)]
        
        for num_test, instructions, resultat_attendu in tests:
            self.assertEqual((num_test, resultat_attendu), (num_test, self.robot.peut_executer(instructions)))

    def test_enregistrer(self):
        """Test de la méthode robot.enregistrer(instruction)."""
        self.robot.position = Position(5,7)

        tests = [(1, None, (True, 1), [Deplacement(0,0)]),
                (2, "", (True, 1), [Deplacement(0,0)]),
                (3, "z", (True, 0), []),
                (4, "o2", (True, 2), [Deplacement(-1,0), Deplacement(-1,0)]),
                (5, "o3", (False, 0), []),
                (6, "n", (False, 0), []),
                (7, Deplacement(1,0), (True, 1), [Deplacement(1,0)]),
                (8, Deplacement(0,-1), (False, 0), []),
                (9, "pn", (True, 1), [ModificationObstacle(self.percer, Deplacement(0,-1))]),
                (10, ModificationObstacle(self.percer, Deplacement(1,0)), (False, 0), []), 
                (11, ["o","o","z","o","e"], [(True, 1), (True, 1), (True, 0), (False, 0), (True, 1)], [[Deplacement(-1,0)], [Deplacement(-1,0), Deplacement(-1,0)], [Deplacement(-1,0), Deplacement(-1,0)], [], [Deplacement(1,0)]])]

        for num_test, instruction, resultat_attendu, a_executer_attendu in tests:
            self.robot.instructions = []
            if not type(instruction) == list:
                self.assertEqual((num_test, resultat_attendu, a_executer_attendu), (num_test, self.robot.enregistrer(instruction), self.robot.instructions))
            else:
                for i in range(0, len(instruction)):
                    self.assertEqual((num_test, resultat_attendu[i], a_executer_attendu[i]), (num_test, self.robot.enregistrer(instruction[i]), self.robot.instructions))

    def test_prochaine_instruction(self):
        """Test de la méthode robot.prochaine_instruction."""
        self.robot.position = Position(5,3)
        self.autre_robot = Robot(self.labyrinthe, "x")
        self.autre_robot.position = Position(8,3)

        tests_robot = [(1, [], (False, 0), []),
                      (2, [Deplacement()], (True, 0), []),
                      (3, [Deplacement(1,0)], (True, 0), []),
                      (4, [Deplacement(0,-1)], (False, 0), []),
                      (5, [Deplacement(1,0), Deplacement(1,0)], (True, 1), [Deplacement(1,0)]),
                      (6, [Deplacement(1,0), Deplacement(1,0), Deplacement(1,0)], (False, 0), []),
                      (7, [Deplacement(1,0), Deplacement(1,0)], (True, 1), [Deplacement(1,0)]),
                      (8, [Deplacement(1,0), Deplacement(1,0)], (True, 1), [Deplacement(1,0)]),
                      (9, [ModificationObstacle(self.percer, Deplacement(0,1))], (True, 0), [])]

        tests_autre_robot = [(1, [Deplacement()], (True, 0), []),
                             (2, [Deplacement()], (True, 0), []),
                             (3, [Deplacement()], (True, 0), []),
                             (4, [Deplacement()], (True, 0), []),
                             (5, [Deplacement()], (True, 0), []),
                             (6, [Deplacement()], (True, 0), []),
                             (7, [Deplacement(-1,0)], (True, 0), []),
                             (8, [Deplacement(-1,0), Deplacement(-1,0)], (False, 0), []),
                             (9, [Deplacement(0,1), ModificationObstacle(self.percer, Deplacement(-1,0)), Deplacement(-1,0), Deplacement(-1,0),
                                  ModificationObstacle(self.murer, Deplacement(-1,0))], (True, 4), [ModificationObstacle(self.percer, Deplacement(-1,0)),
                                  Deplacement(-1,0), Deplacement(-1,0), ModificationObstacle(self.murer, Deplacement(-1,0))])]

        for i in range(0, len(tests_robot)):
            self.robot.position = Position(5,3)
            self.autre_robot.position = Position(8,3)
            
            num_test_robot, a_executer_robot, resultat_attendu_robot, a_executer_attendu_robot = tests_robot[i]
            num_test_autre_robot, a_executer_autre_robot, resultat_attendu_autre_robot, a_executer_attendu_autre_robot = tests_autre_robot[i]
            
            self.robot.instructions = a_executer_robot
            self.autre_robot.instructions = a_executer_autre_robot

            resultat_robot = self.robot.prochaine_instruction()
            resultat_autre_robot = self.autre_robot.prochaine_instruction()

            self.assertEqual((num_test_robot, resultat_attendu_robot, a_executer_attendu_robot), (num_test_robot, resultat_robot, self.robot.instructions))
            self.assertEqual((num_test_autre_robot, resultat_attendu_autre_robot, a_executer_attendu_autre_robot), (num_test_autre_robot, resultat_autre_robot, self.autre_robot.instructions))                   
        


