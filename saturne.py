from Boustrophedon import *

if __name__ == '__main__':
    # Definition polygone
    poly_points = ((1, 1), (4, 1), (3, 2), (2, 2))
    obstacle = [((2.5, 1.25), (2.75, 1.5), (2.25, 1.5), (1.2, 1.2))]

    b = Boustrophedon(poly_points, 0.05, obstacles=obstacle)
    # Decomposition en parties convexes
    b.decomposition()
    # example de boustrophédon sur une sous-partie convexe
    exs = []
    for cv in b.Lcll:
        exs.append(cv.compute_lines())

    plt.figure()

    for c in b.Lcll:
        c.draw()
    b.outer.draw('g')
    for o in b.obstacles:
        o.draw('r')

    #print(ex)
    for ex in exs:
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
