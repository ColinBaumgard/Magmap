# Principe du code :
# 1)    Initialiser un polygone modélisant la surface d'étude, et une
#       liste contenant chaque obstacle (à l'intérieur de la surface)
# 2)    Instancier l'objet Boustrophédon(points, espacement tranchée, obstacles) comme sur l'exemple.
# 3)    Effectuer la décomposition trapézoïdale avec la méthode "decomposition"
#       de la classe "Boustrophédon" (toutes les sous parties convexes seront contenues
#       dans la variable de classe "Lcll", sous forme d'une liste d'objets "Poly".
# 4)    Afficher les points du parcours : Pour chaque élément de la variable "Lcll",
#       on peut obtenir des points du boustrophédon associé via la méthode
#       "compute_lines" de la classe "Poly". La méthode retourne une liste de points.
#       Attention, les points ne sont pas (encore) dans l'ordre du boustrophédon :
#       les segments sont tous orientés dans le même sens.

from Boustrophedon import *

if __name__ == '__main__':
    # Definition polygone
    poly_points = ((1, 1), (4, 1), (3, 2), (2, 2))
    obstacle = [((2.5, 1.25), (2.75, 1.5), (2.25, 1.5), (1.2, 1.2))]

    b = Boustrophedon(poly_points, 0.05, obstacles=obstacle)
    # Decomposition en parties convexes
    b.decomposition()
    # example de boustrophédon sur une sous-partie convexe
    ex = b.Lcll[2].compute_lines()

    plt.figure()

    for c in b.Lcll:
        c.draw()
    b.outer.draw('g')
    for o in b.obstacles:
        o.draw('r')

    print(ex)
    for i in range(len(ex)):
        if i==0:
            plt.plot(ex[i].x, ex[i].y, '*y')
        elif i == len(ex) - 1:
            plt.plot(ex[i].x, ex[i].y, '*y')
        else:
            plt.plot(ex[i].x, ex[i].y, '*k')

        if i%2 == 0:
            plt.plot([ex[i].x, ex[i + 1].x], [ex[i].y, ex[i + 1].y], '-b')

    plt.show()
