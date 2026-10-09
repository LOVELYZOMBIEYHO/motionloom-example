"""Deterministic native MeshAsset planting; no external model files.

Leaves are attached to petioles and swept, tapered branches. Each leaf is a
curved, pointed surface with a raised midrib, rather than a canopy-sized disk.
Meshes are batched by material below MotionLoom's 30,000-vertex cage limit.
"""
import math
import random
from collections import defaultdict

MATERIALS_XML = '''
    <MaterialAsset id="s99_foliage_deep" shading="pbr" baseColor="#344B2D" roughness=".72" specular=".27" doubleSided="true" />
    <MaterialAsset id="s99_foliage_green" shading="pbr" baseColor="#496137" roughness=".68" specular=".30" doubleSided="true" />
    <MaterialAsset id="s99_foliage_mid" shading="pbr" baseColor="#5B7142" roughness=".71" specular=".28" doubleSided="true" />
    <MaterialAsset id="s99_foliage_tip" shading="pbr" baseColor="#70804B" roughness=".75" specular=".23" doubleSided="true" />
    <MaterialAsset id="s99_leaf_rib" shading="pbr" baseColor="#76804D" roughness=".8" />
    <MaterialAsset id="s99_tree_bark" shading="pbr" baseColor="#655442" roughness=".96" specular=".14" />
    <MaterialAsset id="s99_young_bark" shading="pbr" baseColor="#635F3D" roughness=".91" specular=".17" />
    <MaterialAsset id="s99_pot_clay" shading="pbr" baseColor="#A77558" roughness=".9" />
'''


def add(a, b):
    return tuple(x+y for x, y in zip(a, b))


def sub(a, b):
    return tuple(x-y for x, y in zip(a, b))


def mul(a, scale):
    return tuple(x*scale for x in a)


def unit(a):
    length = math.sqrt(sum(x*x for x in a))
    return mul(a, 1/max(length, 1e-12))


def cross(a, b):
    return (a[1]*b[2]-a[2]*b[1], a[2]*b[0]-a[0]*b[2], a[0]*b[1]-a[1]*b[0])


def mix(a, b, t):
    return add(mul(a, 1-t), mul(b, t))


def polar(angle, radius, y):
    return (math.cos(angle)*radius, y, math.sin(angle)*radius)


def on_path(points, knots, t):
    for i in range(len(knots)-1):
        if t <= knots[i+1]:
            return mix(points[i], points[i+1], (t-knots[i])/(knots[i+1]-knots[i]))
    return points[-1]


class Mesh:
    def __init__(self):
        self.vertices = []
        self.faces = []

    def vertex(self, position, uv=(0, 0)):
        self.vertices.append((position, uv))
        return len(self.vertices)-1

    def tube(self, points, radii, sides=8, grooves=False):
        offset = len(self.vertices)
        for j, (p, radius) in enumerate(zip(points, radii)):
            tangent = unit(sub(points[min(j+1, len(points)-1)], points[max(0, j-1)]))
            right = unit(cross(tangent, (0, 0, 1) if abs(tangent[2]) < .85 else (1, 0, 0)))
            forward = unit(cross(right, tangent))
            for k in range(sides):
                angle = 2*math.pi*k/sides
                r = radius*(1+(.075*math.sin(k*2.7+j*.9) if grooves else 0))
                self.vertex(add(p, add(mul(right, r*math.cos(angle)), mul(forward, r*math.sin(angle)))), (k/sides, j/(len(points)-1)))
        for j in range(len(points)-1):
            for k in range(sides):
                a = offset+j*sides+k
                b = offset+j*sides+(k+1)%sides
                self.faces.append((a, a+sides, b+sides, b))
        # Opposite winding at the two ends maintains a manifold component.
        for k in range(1, sides-1):
            self.faces.append((offset, offset+k, offset+k+1))
            last = offset+(len(points)-1)*sides
            self.faces.append((last, last+k+1, last+k))

    def leaf(self, base, direction, length, width, roll, droop, rib=None):
        axis = unit(direction)
        side = unit(cross((0, 1, 0), axis))
        if sum(x*x for x in side) < .1:
            side = (1, 0, 0)
        normal = unit(cross(axis, side))
        side, normal = add(mul(side, math.cos(roll)), mul(normal, math.sin(roll))), add(mul(normal, math.cos(roll)), mul(side, -math.sin(roll)))
        rows = (0, .10, .22, .38, .54, .70, .84, .94, 1) if rib is not None else (0, .16, .36, .59, .81, 1)
        offset = len(self.vertices)
        centers = []
        for t in rows:
            half = width*.5*max(.013, math.sin(math.pi*t)**.72)*(1-.18*t)
            center = add(base, add(mul(axis, length*t), mul(normal, length*(.105*math.sin(math.pi*t)-droop*t*t))))
            centers.append(add(center, mul(normal, half*.12+width*.018)))
            for side_index in (-1, 0, 1):
                # Cupped blade and slightly twisted margins catch light naturally.
                fold = half*(.12 if side_index == 0 else -.10)+side_index*half*.05*math.sin(t*5+roll)
                self.vertex(add(center, add(mul(side, side_index*half), mul(normal, fold))), ((side_index+1)*.5, t))
        for j in range(len(rows)-1):
            for k in range(2):
                a = offset+j*3+k
                self.faces.append((a, a+3, a+4, a+1))
        if rib is not None:
            rib.tube(centers, [max(.0004, width*.013*(1-t*.75)) for t in rows], 4)

    def xml(self, identity, material):
        def v(values):
            return '{['+','.join(f'{x:.6f}' for x in values)+']}'
        geometry = identity+'_geometry'
        lines = [f'    <GeometryAsset id="{geometry}">', '      <Mesh>']
        lines.extend(f'      <Vertex position={v(p)} uv={v(uv)} />' for p, uv in self.vertices)
        lines.extend('      <Face indices={['+','.join(str(x) for x in face)+']} />' for face in self.faces)
        return '\n'.join(lines+['      </Mesh>', '    </GeometryAsset>',
                                f'    <MeshAsset id="{identity}" material="{material}" geometry="{geometry}" />'])


class Planting:
    def __init__(self, assets, model):
        self.assets = assets
        self.model = model
        self.report = []

    def emit(self, name, meshes, position, leaves, rotation=None):
        for material, mesh in meshes.items():
            if not mesh.vertices:
                continue
            assert len(mesh.vertices) <= 30000 and len(mesh.faces) <= 30000, (name, material)
            identity = 's99_'+name+'_'+material.removeprefix('s99_')+'_mesh'
            self.assets.append(mesh.xml(identity, material))
            self.model(name+'_'+material.removeprefix('s99_'), identity, position, rotation=rotation)
        positions = [p for mesh in meshes.values() for p, _ in mesh.vertices]
        self.report.append(dict(name=name, position=position, rotation=rotation, leaves=leaves,
                                vertices=sum(len(m.vertices) for m in meshes.values()),
                                faces=sum(len(m.faces) for m in meshes.values()),
                                local_bounds=[[min(p[i] for p in positions), max(p[i] for p in positions)] for i in range(3)]))

    @staticmethod
    def palette(rng):
        return rng.choices(['s99_foliage_deep', 's99_foliage_green', 's99_foliage_mid', 's99_foliage_tip'], [2, 5, 4, 1])[0]

    @staticmethod
    def pot(meshes, radius=.19, height=.3):
        mesh = meshes['s99_pot_clay']
        profile = [(radius*.69, 0), (radius*.72, .025), (radius*.96, height-.027),
                   (radius, height-.024), (radius, height), (radius*.89, height),
                   (radius*.88, height-.034), (radius*.68, .038)]
        sides = 36
        for j, (r, y) in enumerate(profile):
            for i in range(sides):
                a = i*math.tau/sides
                mesh.vertex((r*math.cos(a), y, r*math.sin(a)), (i/sides, j/len(profile)))
        for j in range(len(profile)-1):
            for i in range(sides):
                a = j*sides+i
                b = j*sides+(i+1)%sides
                mesh.faces.append((a, a+sides, b+sides, b))
        # Dark soil closes the opening, while the rim remains hollow and visible.
        soil = meshes['soil']
        center = soil.vertex((0, height-.035, 0))
        for i in range(sides):
            a = i*math.tau/sides
            soil.vertex((radius*.87*math.cos(a), height-.035, radius*.87*math.sin(a)))
        for i in range(sides):
            soil.faces.append((center, 1+(i+1)%sides, 1+i))

    def plant(self, name, x, z, height=1.1):
        rng = random.Random(99+sum((i+1)*ord(c) for i, c in enumerate(name)))
        meshes = defaultdict(Mesh)
        self.pot(meshes)
        bark, rib = meshes['s99_young_bark'], meshes['s99_leaf_rib']
        count = 0
        # Three unequal, leaning stems with alternate leaves, no radial tiers.
        for branch in range(3):
            angle = branch*2.28+rng.uniform(-.3, .3)
            stem_height = (height-.3)*(1-branch*.13)
            root = polar(angle, .035, .265)
            tip = polar(angle, .14+branch*.035, .3+stem_height-.065)
            points = [mix(root, tip, t) for t in (0, .2, .45, .7, 1)]
            points[2] = add(points[2], polar(angle+.7, .025, 0))
            bark.tube(points, [.014, .012, .009, .006, .003], 10)
            for i in range(11+branch):
                t = .20+.77*i/(10+branch)
                attachment = on_path(points, (0, .2, .45, .7, 1), t)
                leaf_angle = angle+i*2.42+rng.uniform(-.35, .35)
                direction = polar(leaf_angle, 1, rng.uniform(.03, .45))
                petiole = add(attachment, mul(unit(direction), rng.uniform(.035, .065)))
                bark.tube([attachment, petiole], [.0028, .0017], 5)
                length = rng.uniform(.18, .255)*(height/1.5)**.35*(.76 if t>.88 else 1)
                meshes[self.palette(rng)].leaf(petiole, direction, length, length*rng.uniform(.50, .63), rng.uniform(-.4, .4), rng.uniform(.18, .38), rib)
                count += 1
        self.emit(name, meshes, [x, 0, z], count)

    def tree(self, name, x, z, seed, rotation=None):
        rng = random.Random(seed)
        meshes = defaultdict(Mesh)
        wood, twigs = meshes['s99_tree_bark'], meshes['s99_young_bark']
        # Asymmetric tapered leader and short root flares in the ground plane.
        trunk = [(0, -.22, 0), (.025, .22, .012), (-.02, .8, .035),
                 (.015, 1.35, .055), (.085, 1.92, .02), (.12, 2.4, .09), (.17, 3.25, .08), (.21, 3.8, .12)]
        wood.tube(trunk, [.175, .135, .118, .100, .08, .058, .026, .007], 18, True)
        for i in range(5):
            a = i*math.tau/5+.35
            wood.tube([polar(a, .35, -.23), polar(a, .19, -.16), (0, .28, 0)], [.012, .04, .075], 8, True)
        leaves = 0
        for branch in range(11):
            angle = branch*2.399+rng.uniform(-.3, .3)
            start = on_path(trunk[3:7], (0, .32, .56, 1), branch/13)
            radial = rng.uniform(1.12, 1.58) if branch < 8 else rng.uniform(.55, .83)
            crown_y = 3.10+rng.uniform(-.27, .31) if branch < 8 else 3.90+rng.uniform(-.10, .15)
            tip = polar(angle, radial, crown_y)
            points = [start, mix(start, tip, .32), mix(start, tip, .68), tip]
            points[1] = add(points[1], (0, .16, 0))
            wood.tube(points, [.048*(1-branch*.04), .028, .016, .006], 10, True)
            for secondary in range(5):
                t = .25+secondary*.15
                origin = on_path(points, (0, .32, .68, 1), t)
                a = angle+(-1 if secondary%2 else 1)*rng.uniform(.48, .95)
                endpoint = add(origin, polar(a, rng.uniform(.42, .68), rng.uniform(.15, .39)))
                twigs.tube([origin, mix(origin, endpoint, .55), endpoint], [.011, .006, .0025], 7)
                for twig in range(5):
                    joint = mix(origin, endpoint, .25+twig*.17)
                    ta = a+(-1 if twig%2 else 1)*rng.uniform(.62, 1.3)
                    end = add(joint, polar(ta, rng.uniform(.20, .36), rng.uniform(-.08, .23)))
                    twigs.tube([joint, mix(joint, end, .55), end], [.0035, .002, .0009], 5)
                    for leaf_index in range(8):
                        lt = .16+leaf_index*.115
                        attachment = mix(joint, end, lt)
                        la = ta+(-1 if leaf_index%2 else 1)*rng.uniform(.75, 1.4)
                        direction = polar(la, 1, rng.uniform(-.1, .7))
                        petiole = add(attachment, mul(unit(direction), rng.uniform(.016, .03)))
                        twigs.tube([attachment, petiole], [.0013, .0007], 4)
                        length = rng.uniform(.115, .185)
                        meshes[self.palette(rng)].leaf(petiole, direction, length, length*rng.uniform(.39, .53), rng.uniform(-.65, .65), rng.uniform(.14, .30))
                        leaves += 1
        self.emit(name, meshes, [x, 0, z], leaves, rotation)

    def shrub(self, name, x, z, height=.7):
        # Four deterministic forms repeat once each across the eight planters.
        # Sharing whole material batches retains the low draw-call count.
        rng = random.Random(300+int(name.removeprefix('garden')) % 4)
        meshes = defaultdict(Mesh)
        bark = meshes['s99_young_bark']
        leaves = 0
        # Low branched shrubs grow directly from the existing stone planters.
        soil = meshes['soil']
        corners = [(-.30,.257,-.335),(-.30,.257,.335),(.30,.257,.335),(.30,.257,-.335)]
        for p in corners:
            soil.vertex(p)
        soil.faces.append((0,1,2,3))
        for i in range(9):
            a = i*2.399+rng.uniform(-.3, .3)
            root = (0, .257, 0)
            top = polar(a, rng.uniform(.13, .24), height*rng.uniform(.88, 1.20))
            bark.tube([root, mix(root,top,.5), top], [.006, .004, .0015], 6)
            for j in range(16):
                t = .2+j*.05
                attach = mix(root, top, t)
                la = a+j*2.41
                direction = polar(la, 1, rng.uniform(.15, .6))
                petiole = add(attach, mul(unit(direction), .018))
                bark.tube([attach,petiole],[.0013,.0006],4)
                length = rng.uniform(.06,.10)
                meshes[self.palette(rng)].leaf(petiole, direction, length, length*.42, rng.uniform(-.4,.4), .16)
                leaves += 1
        self.emit(name, meshes, [x, 0, z], leaves)

    def sprigs(self, x, y, z):
        rng = random.Random(819)
        meshes = defaultdict(Mesh)
        stems = meshes['s99_young_bark']
        for i in range(5):
            a = i*2.399
            start = polar(a,.018,0)
            tip = polar(a,.11,.29+rng.uniform(-.06,.06))
            stems.tube([start,mix(start,tip,.5),tip],[.002,.0014,.0007],5)
            for j in range(6):
                base = mix(start,tip,.3+j*.12)
                direction = polar(a+j*2.4,1,.35)
                meshes[self.palette(rng)].leaf(base,direction,.055,.022,.12,.14)
        self.emit('vase_sprigs',meshes,[x,y,z],30)
