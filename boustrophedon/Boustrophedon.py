import matplotlib.pyplot as plt
from sympy import Polygon, Line, Point2D, Segment2D, Segment
from seidel.point import Point
import seidel.trapezoidal_map as tz
import numpy as np
import sys


class Poly:
    def __init__(self, points, ecart_fauchee):
        self.p = Polygon(*points)
        self.d = ecart_fauchee
        if self.p.is_convex():
            info = self.convex_width()
            self.w, self.a = max(info[2], info[3]), info[0]

    def __str__(self):
        res = '['
        for p in self.p.vertices:
            res += '(' + str(p.x) + ',' + str(p.y) + ')'

        return res + ']'

    def convex_width(self):
        # function found at https://github.com/dbworth/minimum-area-bounding-rectangle/
        hull_points_2d = np.zeros((len(self.p.vertices) - 1, 2))
        # transfor into array fitting the function
        for i in range(len(self.p.vertices) - 1):
            hull_points_2d[i, 0] = self.p.vertices[i].x
            hull_points_2d[i, 1] = self.p.vertices[i].y

        # Compute edges (x2-x1,y2-y1)
        edges = np.zeros((len(self.p.vertices) - 2, 2))  # empty 2 column array
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

    def compute_lines(self):
        points, inter = [], []
        x_min, y_max = self.p.bounds[0], self.p.bounds[3]
        reached = False
        covered = False
        a = np.tan(self.a)
        b = self.w + y_max
        while not covered:
            p1, p2 = [(x_min, a * x_min + b), (x_min + self.w, a * (x_min + self.w) + b)]
            inter = self.p.intersection(Line(p1, p2))
            if inter:
                reached = True
                points.extend(inter)
            elif reached:
                covered = True
            b -= self.d

        dim = len(points)
        if isinstance(points[0], Point2D):
            del points[0]
            dim-=1
        if isinstance(points[dim-1], Point2D):
            del points[dim-1]
            dim -= 1
        if isinstance(points[0], Segment2D):
            p1, p2 = points[0].points
            del points[0]
            points.insert(0, p1)
            points.insert(1, p2)
        if isinstance(points[dim-1], Segment2D):
            p1, p2 = points[dim-1].points
            del points[dim-1]
            points.append(p1)
            points.append(p2)

        return points

    def classify(self, obstacle=False):
        classes = []
        n = len(self.p.vertices)

        for i in range(n):
            v = self.p.vertices[i]
            v_prev = self.p.vertices[i-1]
            v_next = self.p.vertices[(i+1)%n]
            angle = self.p.angles[v]

            if (v.x <= v_prev.x and v.x <= v_next.x):
                if angle < np.pi:
                    if not obstacle:
                        classes.append('OPEN')
                    else:
                        classes.append('SPLIT')
            elif (v.x >= v_prev.x and v.x >= v_next.x):
                if angle < np.pi:
                    if not obstacle:
                        classes.append('CLOSE')
                    else:
                        classes.append('MERGE')
            elif (v.x <= v_prev.x and v.x >= v_next.x):
                if angle < np.pi:
                    if not obstacle:
                        classes.append('CEIL_CONVEX')
                    else:
                        classes.append('FLOOR_CONCAVE')
                else:
                    if not obstacle:
                        classes.append('CEIL_CONCAVE')
                    else:
                        classes.append('FLOOR_CONVEXE')
            elif (v.x >= v_prev.x and v.x <= v_next.x):
                if angle < np.pi:
                    if not obstacle:
                        classes.append('FLOOR_CONVEX')
                    else:
                        classes.append('CEIL_CONCAVE')
                else:
                    if not obstacle:
                        classes.append('FLOOR_CONCAVE')
                    else:
                        classes.append('CEIL_CONVEX')
            else:
                raise Exception("Unusual issue occured whille classing vertices")

        return classes

    def draw(self, color='k'):
        for i in range(len(self.p.vertices) - 1):
            plt.plot([self.p.vertices[i].x, self.p.vertices[i+1].x], [self.p.vertices[i].y, self.p.vertices[i+1].y], color=color)
        plt.plot([self.p.vertices[len(self.p.vertices) - 1].x, self.p.vertices[0].x], [self.p.vertices[len(self.p.vertices) - 1].y, self.p.vertices[0].y], color=color)


class Cell:
    def __init__(self):
        self.Lc = []
        self.Lf = []
        self.closed = False


class Boustrophedon:
    def __init__(self, boundary_points, ecart_fauchee, obstacles=[]):
        self.outer = Poly(boundary_points, ecart_fauchee)
        self.obstacles = [Poly(obstacle, ecart_fauchee) for obstacle in obstacles]
        self.Lcll = []
        self.d = ecart_fauchee

    def decomposition(self):
        def find_cell(vf, vc, Lcll, obstacles):
            polygons = []
            cell_index = -1
            for cell in Lcll:
                if not cell.closed:
                    if not vf.equals(vc):
                        points = tuple(cell.Lf.copy() + cell.Lc.copy() + [vf, vc])
                    else:
                        points = tuple(cell.Lf.copy() + cell.Lc.copy() +[vf])
                    p = Polygon(*points)
                    polygons.append(p)
                else:
                    polygons.append([])

            for i in range(len(polygons)):
                empty = True
                polygon = polygons[i]
                if polygon != []:
                    for j in range(len(obstacles)):
                        test = obstacles[j].p
                        inter = polygon.intersection(test)
                        count=0
                        for p in inter:
                            if isinstance(p, Point2D):
                                count+= 1
                            elif isinstance(p, Segment2D):
                                count+= 2
                            else:
                                count+= len(p.vertices)
                        if count > 2:
                            empty = False

                    if empty:
                        cell_index = i
                        break
            return cell_index

        ymin, ymax = self.outer.p.bounds[1], self.outer.p.bounds[3]
        Le = []
        Lcll = []

        classes = self.outer.classify()
        Lv = [(self.outer.p.vertices[i], classes[i], 0) for i in range(len(self.outer.p.vertices))]

        for i in range(len(self.obstacles)):
            obstacle = self.obstacles[i]
            classes = obstacle.classify(True)
            Lv.extend([(obstacle.p.vertices[j], classes[j], i+1) for j in range(len(obstacle.p.vertices))])

        Lv.sort(key=lambda p:p[0].x)

        while Lv:
            v = Lv[0]
            sweep_line = Segment2D((v[0].x, ymin), (v[0].x, ymax))

            if v[2] == 0:
                index = self.outer.p.vertices.index(v[0])
                v_prev = self.outer.p.vertices[index - 1]
                v_next = self.outer.p.vertices[(index + 1)%len(self.outer.p.vertices)]
                edge_left = Segment2D(v_prev, v[0])
                edge_right = Segment2D(v[0], v_next)
            else:
                index = self.obstacles[v[2]-1].p.vertices.index(v[0])
                v_prev = self.obstacles[v[2]-1].p.vertices[index - 1]
                v_next = self.obstacles[v[2]-1].p.vertices[(index + 1) % len(self.obstacles[v[2]-1].p.vertices)]
                edge_left = Segment2D(v[0], v_next)
                edge_right = Segment2D(v_prev, v[0])

            if v[1] == 'OPEN':
                Le.extend([edge_left, edge_right])
                c = Cell()
                c.Lf.append(v[0])
                Lcll.append(c)

            elif v[1] == 'SPLIT':
                Lv_inter = list(filter(([]).__ne__, [sweep_line.intersection(edge) for edge in Le]))
                Lv_inter.sort(key=lambda x:x[0].y)
                vf, vc = Lv_inter[0][0], Lv_inter[-1][0]
                for v_inter in Lv_inter:
                    v_inter = v_inter[0]
                    if vf.y < v_inter.y < v[0].y:
                        vf = v_inter
                    if v[0].y < v_inter.y < vc.y:
                        vc = v_inter
                c = Lcll[find_cell(vf, vc, Lcll, self.obstacles)]
                c.Lf.append(vf)
                c.Lc.append(vc)
                c.closed = True

                cf, cc = Cell(), Cell()
                cf.Lf.append(vf)
                cf.Lc.append(v[0])
                cc.Lf.append(v[0])
                cc.Lc.append(vc)
                Lcll.extend([cc, cf])

                Le.extend([edge_left, edge_right])

            elif v[1] == 'CEIL_CONVEX':
                Le.remove(edge_right)
                Le.append(edge_left)

                Lv_inter = list(filter(([]).__ne__, [sweep_line.intersection(edge) for edge in Le]))
                Lv_inter.sort(key=lambda x: x[0].y)
                vf = Lv_inter[0][0]
                for v_inter in Lv_inter:
                    v_inter = v_inter[0]
                    if vf.y < v_inter.y < v[0].y:
                        vf = v_inter
                c = Lcll[find_cell(vf, v[0], Lcll, self.obstacles)]
                c.Lc.append(v[0])

            elif v[1] == 'FLOOR_CONVEX':
                Le.remove(edge_left)
                Le.append(edge_right)

                Lv_inter = list(filter(([]).__ne__, [sweep_line.intersection(edge) for edge in Le]))
                Lv_inter.sort(key=lambda x: x[0].y)
                vc = Lv_inter[-1][0]
                for v_inter in Lv_inter:
                    v_inter = v_inter[0]
                    if v[0].y < v_inter.y < vc.y:
                        vc = v_inter
                c = Lcll[find_cell(v[0], vc, Lcll, self.obstacles)]
                c.Lf.append(v[0])

            elif v[1] == 'CEIL_CONCAVE':
                Le.remove(edge_right)
                Le.append(edge_left)

                Lv_inter = list(filter(([]).__ne__, [sweep_line.intersection(edge) for edge in Le]))
                Lv_inter.sort(key=lambda x: x[0].y)
                vf= Lv_inter[0][0]
                for v_inter in Lv_inter:
                    v_inter = v_inter[0]
                    if vf.y < v_inter.y < v[0].y:
                        vf = v_inter
                c = Lcll[find_cell(vf, v[0], Lcll, self.obstacles)]
                c.Lc.append(v[0])
                c.Lf.append(vf)
                c.closed = True
                c_new = Cell()
                c_new.Lc.append(v[0])
                c_new.Lf.append(vf)
                Lcll.append(c_new)

            elif v[1] == 'FLOOR_CONCAVE':
                Le.remove(edge_left)
                Le.append(edge_right)

                Lv_inter = list(filter(([]).__ne__, [sweep_line.intersection(edge) for edge in Le]))
                Lv_inter.sort(key=lambda x: x[0].y)
                vc = Lv_inter[-1][0]
                for v_inter in Lv_inter:
                    v_inter = v_inter[0]
                    if v[0].y < v_inter.y < vc.y:
                        vc = v_inter
                c = Lcll[find_cell(v[0], vc, Lcll, self.obstacles)]
                c.Lf.append(v[0])
                c.Lc.append(vc)
                c.closed = True
                c_new = Cell()
                c_new.Lf.append(v[0])
                c_new.Lc.append(vc)
                Lcll.append(c_new)

            elif v[1] == 'MERGE':
                Le.remove(edge_left)
                Le.remove(edge_right)

                Lv_inter = list(filter(([]).__ne__, [sweep_line.intersection(edge) for edge in Le]))
                Lv_inter.sort(key=lambda x: x[0].y)
                vf, vc = Lv_inter[0][0], Lv_inter[-1][0]
                for v_inter in Lv_inter:
                    v_inter = v_inter[0]
                    if vf.y < v_inter.y < v[0].y:
                        vf = v_inter
                    if v[0].y < v_inter.y < vc.y:
                        vc = v_inter
                cc = Lcll[find_cell(v[0], vc, Lcll, self.obstacles)]
                cc.Lf.append(v[0])
                cc.Lc.append(vc)
                cc.closed = True
                cf = Lcll[find_cell(vf, v[0], Lcll, self.obstacles)]
                cf.Lf.append(vf)
                cf.Lc.append(v[0])
                cf.closed = True
                c_new = Cell()
                c_new.Lc.append(vc)
                c_new.Lf.append(vf)
                Lcll.append(c_new)

            elif v[1] == 'CLOSE':
                Le.remove(edge_left)
                Le.remove(edge_right)
                c = Lcll[find_cell(v[0], v[0], Lcll, self.obstacles)]
                c.Lf.append(v[0])
                c.closed = True

            else:
                raise Exception("Incorrect class encountered")

            Lv.remove(v)

        self.Lcll = [Poly(cell.Lf + cell.Lc[::-1], self.d) for cell in Lcll]