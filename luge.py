from roblib import *  # available at https://www.ensta-bretagne.fr/jaulin/roblib.py
from scipy import optimize


ax=init_figure(-10, 100, -30, 70)



dt = 0.1
d = 200
l = 10


X = array([[0], [0], [0], [0], [2]])
Z = array([[-l], [0], [0], [4], [0], [0]])

x = []
y = []

x_l = []
y_l = []
x_l_voulu = []
y_l_voulu = []

x_courbe = linspace(0, 100, 300)
y_coubre = 20*sin(x_courbe/5) + 7*cos(x_courbe/20)*sin(x_courbe/3)
Wp_l = vstack((x_courbe.T, y_coubre.T)).T


Wp = array([Wp_l[0, :]])
for i in range(Wp_l.shape[0]-1):
    #Wp_r = vstack((Wp_r, Wp[i, :]))
    phi1 = arctan2(Wp_l[i+1, 1] - Wp_l[i, 1], Wp_l[i+1, 0] - Wp_l[i, 0])
    #phi2 = arctan2(Wp_l[i+2, 1] - Wp_l[i+1, 1], Wp_l[i+2, 0] - Wp_l[i+1, 0])
    Wp = vstack((Wp, Wp_l[i+1, :] + array([l*cos(phi1), l*sin(phi1)])))
    #Wp = vstack((Wp, Wp_l[i+1, :] + array([l*cos(phi2), l*sin(phi2)])))

def f1(x, X, dy):
    X = X.flatten()
    return X[4]*cos(x) + X[4]*sin(x - X[3])*sin(X[3]) - dy

def f2(x, X, dy):
    X = X.flatten()
    return X[4]*sin(x) - X[4]*sin(x - X[3])*sin(X[3]) - dy

def X_dot(X, u):
    X = X.flatten()
    u = u.flatten()
    return array([[X[4]*cos(X[2])], [X[4]*sin(X[2])], [u[0]], [X[4]/l*sin(X[2]-X[3])], [u[1]]])

def Z_dot(Z, a):
    Z = Z.flatten()
    a = a.flatten()
    return array([[Z[2]*cos(Z[4])], [Z[2]*sin(Z[4])], [Z[3]], [a[0]], [Z[5]], [a[1]]])



def h(X):
    X = X.flatten()
    return array([[X[0] - l*cos(X[3])], [X[1] - l*sin(X[3])]])


def correcteur(X, luge, Wp):
    X = X.flatten()
    a = Wp[0, :].flatten()
    b = Wp[1, :].flatten()
    #m = array(luge).flatten()
    m = X[:2]
    if (sqrt((b[0] - m[0])**2 + (b[1] - m[1])**2)) < 1.5:
        Wp = Wp[1:, :]
        theta, Wp = correcteur(X, luge, Wp)
    else:
        phi = arctan2(b[1] - a[1], b[0] - a[0])
        e = det(array([ [b[0] - a[0], m[0] - a[0]], [b[1] - a[1], m[1] - a[1]] ]))/norm(b-a)
        print(e)
        theta_ = phi-arctan(e)
        theta = arctan(tan((theta_- X[2])/2))
    return theta, Wp

for t in arange(0, d, dt):
    clear(ax)
    luge = h(X)
    theta, Wp = correcteur(X, luge, Wp)
    u = array([[theta], [0]])
    
    X = X + dt*X_dot(X, u)
    x.append(X[0])
    y.append(X[1])
    x_l.append(luge[0, 0])
    y_l.append(luge[1, 0])

    draw_tank(X[[0, 1, 2], :])
    draw_tank(array([[luge[0]], [luge[1]], [X[3, 0]]]), 'red')
    draw_segment((x[-1], y[-1]), luge)
    plot(x, y)
    plot(x_l, y_l)
    plot(Wp_l[:, 0], Wp_l[:, 1])
    plot(Wp[:, 0], Wp[:, 1])
    #plot(x_courbe, y_coubre, 'green')
pause(5)

'''
for t in arange(0, d, dt):
    clear(ax)

    u = array([[0], [0]])
   
    
    Z = Z + dt*Z_dot(Z, u)
    x.append(Z[0] + cos(Z[4]))
    y.append(Z[1] + sin(Z[4]))
    
    x_l.append(Z[0, 0])
    y_l.append(Z[1, 0])

    draw_tank(array([[x[-1]], [y[-1]],  [0]]), 'blue')
    draw_tank(Z[:3, :], 'red')
    draw_segment((x[-1], y[-1]), Z[:2, :])
    plot(x, y, 'b')
    plot(x_l, y_l, 'r')
pause(5)'''