#from Vertex import *
#from Polygon import *
import matplotlib.pyplot as plt
from sympy import Polygon, Line, Point2D, Segment2D
import numpy as np
import sys


def convex_width(p):
    # function found at https://github.com/dbworth/minimum-area-bounding-rectangle/
    hull_points_2d = np.zeros((len(p.vertices) - 1, 2))
    # transfor into array fitting the function
    for i in range(len(p.vertices) - 1):
        hull_points_2d[i, 0] = p.vertices[i].x
        hull_points_2d[i, 1] = p.vertices[i].y

    # Compute edges (x2-x1,y2-y1)
    edges = np.zeros((len(p.vertices) - 2, 2))  # empty 2 column array
    for i in range(len(edges)):
        edge_x = hull_points_2d[i + 1, 0] - hull_points_2d[i, 0]
        edge_y = hull_points_2d[i + 1, 1] - hull_points_2d[i, 1]
        edges[i] = [edge_x, edge_y]

    # Calculate edge angles   atan2(y/x)
    edge_angles = np.zeros((len(edges)))  # empty 1 column array
    for i in range(len(edge_angles)):
        edge_angles[i] = np.arctan2(edges[i, 1], edges[i, 0])
    # print "Edge angles: \n", edge_angles

    # Check for angles in 1st quadrant
    for i in range(len(edge_angles)):
        edge_angles[i] = abs(edge_angles[i] % (np.pi / 2))  # want strictly positive answers
    # print "Edge angles in 1st Quadrant: \n", edge_angles

    # Remove duplicate angles
    edge_angles = np.unique(edge_angles)
    # print "Unique edge angles: \n", edge_angles

    # Test each angle to find bounding box with smallest area
    min_bbox = (0, sys.maxsize, 0, 0, 0, 0, 0, 0)  # rot_angle, area, width, height, min_x, max_x, min_y, max_y
    # print("Testing", len(edge_angles), "possible rotations for bounding box... \n")
    for i in range(len(edge_angles)):

        # Create rotation matrix to shift points to baseline
        # R = [ cos(theta)      , cos(theta-PI/2)
        #       cos(theta+PI/2) , cos(theta)     ]
        R = np.array([[np.cos(edge_angles[i]), np.cos(edge_angles[i] - (np.pi / 2))],
                      [np.cos(edge_angles[i] + (np.pi / 2)), np.cos(edge_angles[i])]])
        # print "Rotation matrix for ", edge_angles[i], " is \n", R

        # Apply this rotation to convex hull points
        rot_points = np.dot(R, np.transpose(hull_points_2d))  # 2x2 * 2xn
        # print "Rotated hull points are \n", rot_points

        # Find min/max x,y points
        min_x = np.nanmin(rot_points[0], axis=0)
        max_x = np.nanmax(rot_points[0], axis=0)
        min_y = np.nanmin(rot_points[1], axis=0)
        max_y = np.nanmax(rot_points[1], axis=0)
        # print "Min x:", min_x, " Max x: ", max_x, "   Min y:", min_y, " Max y: ", max_y

        # Calculate height/width/area of this bounding rectangle
        width = max_x - min_x
        height = max_y - min_y
        area = width * height
        # print "Potential bounding box ", i, ":  width: ", width, " height: ", height, "  area: ", area

        # Store the smallest rect found first (a simple convex hull might have 2 answers with same area)
        if (area < min_bbox[1]):
            min_bbox = (edge_angles[i], area, width, height, min_x, max_x, min_y, max_y)
        # Bypass, return the last found rect
        # min_bbox = ( edge_angles[i], area, width, height, min_x, max_x, min_y, max_y )

    # Re-create rotation matrix for smallest rect
    angle = min_bbox[0]
    R = np.array(
        [[np.cos(angle), np.cos(angle - (np.pi / 2))], [np.cos(angle + (np.pi / 2)), np.cos(angle)]])
    # print "Projection matrix: \n", R

    # Project convex hull points onto rotated frame
    proj_points = np.dot(R, np.transpose(hull_points_2d))  # 2x2 * 2xn
    # print "Project hull points are \n", proj_points

    # min/max x,y points are against baseline
    min_x = min_bbox[4]
    max_x = min_bbox[5]
    min_y = min_bbox[6]
    max_y = min_bbox[7]
    # print "Min x:", min_x, " Max x: ", max_x, "   Min y:", min_y, " Max y: ", max_y

    # Calculate center point and project onto rotated frame
    center_x = (min_x + max_x) / 2
    center_y = (min_y + max_y) / 2
    center_point = np.dot([center_x, center_y], R)
    # print "Bounding box center point: \n", center_point

    # Calculate corner points and project onto rotated frame
    corner_points = np.zeros((4, 2))  # empty 2 column array
    corner_points[0] = np.dot([max_x, min_y], R)
    corner_points[1] = np.dot([min_x, min_y], R)
    corner_points[2] = np.dot([min_x, max_y], R)
    corner_points[3] = np.dot([max_x, max_y], R)
    # print "Bounding box corner points: \n", corner_points

    # print "Angle of rotation: ", angle, "rad  ", angle * (180/math.pi), "deg"

    return (angle, min_bbox[1], min_bbox[2], min_bbox[3], center_point,
            corner_points)  # rot_angle, area, width, height, center_point, corner_points


def compute_lines(p, w, theta, d):
    points, inter = [], []
    x_min, y_max = p.bounds[0], p.bounds[3]
    reached = False
    covered = False
    a = np.tan(theta)
    b = w + y_max
    while not covered:
        p1, p2 = [(x_min, a * x_min + b), (x_min + w, a * (x_min + w) + b)]
        inter = p.intersection(Line(p1, p2))
        if inter:
            reached = True
            points.extend(inter)
        elif reached:
            covered = True
        b -= d

    if isinstance(points[0], Point2D):
        del points[0]
    if isinstance(points[len(points)-1], Point2D):
        del points[len(points)-1]

    return points


def draw(p):
    for i in range(len(p.vertices) - 1):
        plt.plot([p.vertices[i].x, p.vertices[i+1].x], [p.vertices[i].y, p.vertices[i+1].y], color='black')
    plt.plot([p.vertices[len(p.vertices) - 1].x, p.vertices[0].x], [p.vertices[len(p.vertices) - 1].y, p.vertices[0].y], color='black')

# Press the green button in the gutter to run the script.
if __name__ == '__main__':
    p1, p2, p3, p4 = [(1, 1), (4, 1), (3, 2), (2, 2)]

    P = Polygon(p1, p2, p3, p4)
    info = convex_width(P)
    points = compute_lines(P, info[1], info[0], 0.1)
    print(points)

    plt.figure()
    draw(P)

    for i in range(len(points)):
        if isinstance(points[i], Point2D):
            plt.plot(points[i].x, points[i].y, '*r')
        elif isinstance(points[i], Segment2D):
            p1, p2 = points[i].points
            plt.plot(p1.x, p1.y, '*r')
            plt.plot(p2.x, p2.y, '*r')
    plt.show()

# See PyCharm help at https://www.jetbrains.com/help/pycharm/
