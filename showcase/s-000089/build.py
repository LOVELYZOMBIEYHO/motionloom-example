# =========================================
# =========================================
# showcase/s-000089/build.py
"""Build original, deterministic courtyard geometry; MotionLoom owns lighting."""
from pathlib import Path
import json
import math
import random
import struct
import zlib
import sys

ROOT = Path(__file__).resolve().parent
RNG = random.Random(8901)
TAU = math.tau
DETAIL = '--detail' in sys.argv

# Procedural technical maps are microstructure approximations, not scanned maps
# inferred from the generated albedo. All channels use the same tileable height field.
def technical_maps(kind, n=512):
    def height(x,y):
        u=x/n*TAU;v=y/n*TAU
        if kind=='wood':return .42*math.sin(u*43+.5*math.sin(v*2))+.13*math.sin(u*97+math.sin(v*3))
        if kind=='stone':return .20*math.sin(u*37+math.sin(v*23))+.12*math.sin(v*71+math.sin(u*59))
        return .08*math.sin(u*67+v*3)+.045*math.sin(v*83+u*41)
    def png(rows):
        def chunk(name,data):return struct.pack('>I',len(data))+name+data+struct.pack('>I',zlib.crc32(name+data)&0xffffffff)
        return b'\x89PNG\r\n\x1a\n'+chunk(b'IHDR',struct.pack('>IIBBBBB',n,n,8,2,0,0,0))+chunk(b'IDAT',zlib.compress(rows))+chunk(b'IEND',b'')
    normal=bytearray();mr=bytearray()
    for y in range(n):
        normal.append(0);mr.append(0)
        for x in range(n):
            dx=(height(x-1,y)-height(x+1,y))*.32
            dy=(height(x,y-1)-height(x,y+1))*.32
            length=math.sqrt(dx*dx+dy*dy+1)
            normal.extend(round((v/length*.5+.5)*255) for v in (dx,dy,1))
            base={'wood':.48,'stone':.61,'bronze':.37}[kind]
            rough=max(.15,min(.9,base+height(x,y)*.13))
            mr.extend((255,round(rough*255),255))
    return png(bytes(normal)),png(bytes(mr))

# Embedded procedural surface maps add grain without external asset dependencies.
def texture(kind):
    n = 256
    raw = bytearray()
    rng = random.Random(89)
    for y in range(n):
        raw.append(0)
        for x in range(n):
            noise = rng.uniform(-8, 8)
            if kind == 'wood':
                value = 180 + 25*math.sin(x*.35 + 2*math.sin(y*.024)) + 12*math.sin(x*1.7+y*.02) + noise
            elif kind == 'stone':
                value = 226 + 5*math.sin(x*.055+y*.027+3*math.sin(y*.04)) + noise*.45
            else:
                value = 234 + 6*math.sin(x*2) + 4*math.sin(y*2) + noise*.5
            v = int(max(0, min(255, value)))
            raw.extend((v,v,v))
    def chunk(name, data):
        return struct.pack('>I',len(data))+name+data+struct.pack('>I',zlib.crc32(name+data)&0xffffffff)
    return b'\x89PNG\r\n\x1a\n'+chunk(b'IHDR',struct.pack('>IIBBBBB',n,n,8,2,0,0,0))+chunk(b'IDAT',zlib.compress(bytes(raw)))+chunk(b'IEND',b'')

MATS = []
def material(name, color, rough=.7, metal=0, tex=None, glow=None):
    # Match the current MotionLoom shader's display-space factor convention.
    # These factors are calibrated for this renderer, not cross-DCC colour parity.
    rgb = [int(color[i:i+2],16)/255 for i in (1,3,5)]
    m = {'name':name,'pbrMetallicRoughness':{'baseColorFactor':rgb+[1],'roughnessFactor':rough,'metallicFactor':metal},'doubleSided':True}
    if tex is not None: m['pbrMetallicRoughness']['baseColorTexture']={'index':tex}
    if glow: m['emissiveFactor']=glow
    MATS.append(m)
    return len(MATS)-1

WOOD=material('weathered rosewood','#745144',.56,tex=0)
DARK=material('ink stained timber','#392F2D',.64,tex=0)
GOLD=material('aged champagne brass','#BBA16A',.38,.7)
STONE=[material('limestone '+str(i),c,.43,tex=1) for i,c in enumerate(['#A8ACA9','#BBBEB8','#C4C5BC','#969F9F'])]
ROOF=material('charcoal glazed tiles','#53646A',.45,.12,tex=1)
PAPER=material('warm lantern silk','#F4DBA5',.82,tex=2,glow=[1.3,.73,.27])
CLOTH=material('ivory hanging silk','#E4E1D3',.9,tex=2)
PINK=material('porcelain pink petals','#F1D7D2',.78)
WHITE=material('ivory blossom','#F3EBDB',.8)
LEAF=material('desaturated pine','#626E56',.94)
TRUNK=material('plum branches','#655146',.9,tex=0)
BLUE=material('celadon porcelain','#91A7A4',.23,.18)
MOUNTAIN=[material('mist rock '+str(i),c,.98,tex=1) for i,c in enumerate(['#84999F','#9CADB2','#B5C2C6'])]

if DETAIL:
    # White factors avoid double-tinting the generated colour maps.
    for ids,tex,normal,mr,factor,strength in [
        ([WOOD],0,4,5,[1,1,1,1],.7),
        ([DARK,TRUNK],0,4,5,[.58,.57,.56,1],.6),
        (STONE,1,6,7,[.94,.97,1,1],.55),
        ([GOLD],3,8,9,[1,1,1,1],.35),
    ]:
        for i in ids:
            pbr=MATS[i]['pbrMetallicRoughness']
            pbr['baseColorFactor']=factor
            pbr['baseColorTexture']={'index':tex}
            pbr['roughnessFactor']=1
            pbr['metallicRoughnessTexture']={'index':mr}
            MATS[i]['normalTexture']={'index':normal,'scale':strength}
    MATS[PAPER]['emissiveFactor']=[.32,.16,.045]

class Mesh:
    def __init__(self): self.parts={}
    def tri(self,m,a,b,c,uv=((0,0),(1,0),(1,1))):
        p,n,t=self.parts.setdefault(m,([],[],[]))
        u=[b[i]-a[i] for i in range(3)];v=[c[i]-a[i] for i in range(3)]
        normal=[u[1]*v[2]-u[2]*v[1],u[2]*v[0]-u[0]*v[2],u[0]*v[1]-u[1]*v[0]]
        length=math.sqrt(sum(x*x for x in normal)) or 1
        p.extend((a,b,c));n.extend([tuple(x/length for x in normal)]*3);t.extend(uv)
    def quad(self,m,a,b,c,d):
        self.tri(m,a,b,c);self.tri(m,a,c,d,((0,0),(1,1),(0,1)))
    def box(self,m,pos,size):
        if DETAIL and m in [WOOD,DARK,GOLD,*STONE,ROOF]:
            return self.beveled_box(m,pos,size,min(.045,min(size)*.13))
        x,y,z=pos;w,h,l=[v/2 for v in size]
        v=[(x+a*w,y+b*h,z+c*l) for a,b,c in [(-1,-1,-1),(1,-1,-1),(1,1,-1),(-1,1,-1),(-1,-1,1),(1,-1,1),(1,1,1),(-1,1,1)]]
        for a,b,c,d in [(0,3,2,1),(4,5,6,7),(0,4,7,3),(1,2,6,5),(3,7,6,2),(0,1,5,4)]:self.quad(m,v[a],v[b],v[c],v[d])
    def beveled_box(self,m,pos,size,r):
        # A rounded cube grid creates real edge highlights, not painted bevels.
        half=[s*.5 for s in size];inner=[h-r for h in half]
        for axis in range(3):
            a=(axis+1)%3;b=(axis+2)%3
            for sign in [-1,1]:
                aa=[-half[a],-inner[a],inner[a],half[a]]
                bb=[-half[b],-inner[b],inner[b],half[b]]
                def vertex(u,v):
                    p=[0,0,0];p[axis]=sign*half[axis];p[a]=u;p[b]=v
                    q=[max(-inner[k],min(inner[k],p[k])) for k in range(3)]
                    delta=[p[k]-q[k] for k in range(3)]
                    length=math.sqrt(sum(d*d for d in delta))
                    normal=tuple(d/length for d in delta)
                    return tuple(pos[k]+q[k]+normal[k]*r for k in range(3)),normal
                for i in range(3):
                    for j in range(3):
                        coords=[(aa[i],bb[j]),(aa[i+1],bb[j]),(aa[i+1],bb[j+1]),(aa[i],bb[j+1])]
                        if sign<0:coords.reverse()
                        verts=[vertex(*c) for c in coords]
                        self.quad(m,*(v[0] for v in verts))
                        self.parts[m][1][-6:]=[verts[k][1] for k in [0,1,2,0,2,3]]
                        # World-sized planar UVs keep texel scale stable across bevels.
                        uv=[((u+pos[a])*.7,(v+pos[b])*.7) for u,v in coords]
                        self.parts[m][2][-6:]=[uv[k] for k in [0,1,2,0,2,3]]
    def lathe(self,m,pos,rings,segments=16):
        x,y,z=pos
        for ring_index,((h,r),(hh,rr)) in enumerate(zip(rings,rings[1:])):
            for i in range(segments):
                a,b=i*TAU/segments,(i+1)*TAU/segments
                self.quad(m,(x+r*math.cos(a),y+h,z+r*math.sin(a)),(x+rr*math.cos(a),y+hh,z+rr*math.sin(a)),(x+rr*math.cos(b),y+hh,z+rr*math.sin(b)),(x+r*math.cos(b),y+h,z+r*math.sin(b)))
                # Continuous radial normals and UVs avoid faceted pots and striped pillars.
                slope=(r-rr)/max(.0001,hh-h);den=math.sqrt(1+slope*slope)
                na=(math.cos(a)/den,slope/den,math.sin(a)/den)
                nb=(math.cos(b)/den,slope/den,math.sin(b)/den)
                self.parts[m][1][-6:]=[na,na,nb,na,nb,nb]
                if DETAIL and m == BLUE:
                    def smooth_normal(index,angle):
                        lo=max(0,index-1);hi=min(len(rings)-1,index+1)
                        slope=(rings[lo][1]-rings[hi][1])/max(.0001,rings[hi][0]-rings[lo][0])
                        den=math.sqrt(1+slope*slope)
                        return (math.cos(angle)/den,slope/den,math.sin(angle)/den)
                    ns=[smooth_normal(ring_index,a),smooth_normal(ring_index+1,a),smooth_normal(ring_index+1,b),smooth_normal(ring_index,b)]
                    self.parts[m][1][-6:]=[ns[k] for k in [0,1,2,0,2,3]]
                u=i/segments;uu=(i+1)/segments
                self.parts[m][2][-6:]=[(u,h*.25),(u,hh*.25),(uu,hh*.25),(u,h*.25),(uu,hh*.25),(uu,h*.25)]
    def branch(self,m,a,b,r=.04):
        d=[b[i]-a[i] for i in range(3)];length=math.sqrt(sum(v*v for v in d));d=[v/length for v in d]
        ref=(0,1,0) if abs(d[1])<.95 else (1,0,0)
        u=[d[1]*ref[2]-d[2]*ref[1],d[2]*ref[0]-d[0]*ref[2],d[0]*ref[1]-d[1]*ref[0]]
        l=math.sqrt(sum(v*v for v in u));u=[v/l for v in u]
        v=[d[1]*u[2]-d[2]*u[1],d[2]*u[0]-d[0]*u[2],d[0]*u[1]-d[1]*u[0]]
        def p(o,t,rr):return tuple(o[j]+rr*(u[j]*math.cos(t)+v[j]*math.sin(t)) for j in range(3))
        segments=12 if DETAIL else 7
        for i in range(segments):
            aa=i*TAU/segments;bb=(i+1)*TAU/segments
            if DETAIL:
                self.quad(m,p(a,aa,r),p(a,bb,r),p(b,bb,r*.7),p(b,aa,r*.7))
                normals=[tuple(u[j]*math.cos(t)+v[j]*math.sin(t) for j in range(3)) for t in [aa,bb]]
                self.parts[m][1][-6:]=[normals[k] for k in [0,1,1,0,1,0]]
                self.parts[m][2][-6:]=[(i/segments,0),((i+1)/segments,0),((i+1)/segments,length), (i/segments,0),((i+1)/segments,length),(i/segments,length)]
            else:
                self.quad(m,p(a,aa,r),p(b,aa,r*.7),p(b,bb,r*.7),p(a,bb,r))
    def save(self,path):
        doc={'asset':{'version':'2.0','generator':'S89 original procedural courtyard'},'scene':0,'scenes':[{'nodes':[0]}],'nodes':[{'mesh':0}],'meshes':[{'primitives':[]}],'materials':MATS,'buffers':[{}],'bufferViews':[],'accessors':[],'images':[],'textures':[],'samplers':[{'magFilter':9729,'minFilter':9987,'wrapS':10497,'wrapT':10497}]}
        data=bytearray()
        def view(raw):
            data.extend(b'\0'*((-len(data))%4));start=len(data);data.extend(raw)
            doc['bufferViews'].append({'buffer':0,'byteOffset':start,'byteLength':len(raw)})
            return len(doc['bufferViews'])-1
        def accessor(values,size):
            index=view(b''.join(struct.pack('<'+'f'*size,*v) for v in values))
            doc['accessors'].append({'bufferView':index,'componentType':5126,'count':len(values),'type':'VEC'+str(size),'min':[min(v[i] for v in values) for i in range(size)],'max':[max(v[i] for v in values) for i in range(size)]})
            return len(doc['accessors'])-1
        textures=[texture(kind) for kind in ['wood','stone','paper']]
        if DETAIL:
            textures=[(ROOT/'assets/pbr/wood-base.png').read_bytes(),(ROOT/'assets/pbr/stone-base.png').read_bytes(),texture('paper'),(ROOT/'assets/pbr/bronze-base.png').read_bytes()]
            for kind in ['wood','stone','bronze']:
                maps=technical_maps(kind)
                for suffix,pixels in zip(['normal','roughness-metallic'],maps):
                    (ROOT/f'assets/pbr/{kind}-{suffix}.png').write_bytes(pixels)
                textures.extend(maps)
        for pixels in textures:
            doc['images'].append({'bufferView':view(pixels),'mimeType':'image/png'})
            doc['textures'].append({'sampler':0,'source':len(doc['images'])-1})
        for mat,(p,n,t) in self.parts.items():
            doc['meshes'][0]['primitives'].append({'attributes':{'POSITION':accessor(p,3),'NORMAL':accessor(n,3),'TEXCOORD_0':accessor(t,2)},'material':mat})
        data.extend(b'\0'*((-len(data))%4));doc['buffers'][0]['byteLength']=len(data)
        raw=json.dumps(doc,separators=(',',':')).encode();raw+=b' '*((-len(raw))%4)
        path.parent.mkdir(exist_ok=True)
        path.write_bytes(struct.pack('<III',0x46546c67,2,28+len(raw)+len(data))+struct.pack('<II',len(raw),0x4e4f534a)+raw+struct.pack('<II',len(data),0x004e4942)+data)
        print(path.name, sum(len(p)//3 for p,n,t in self.parts.values()), 'triangles')

world=Mesh()
# The foreground pavilion frames a sunlit stair and progressively paler mountain layers.
for iz in range(17):
    for ix in range(15):
        world.box(RNG.choice(STONE),(ix*1.12-7.84,-.13,-iz*1.13+8),(1.095,.25,1.105))
for i in range(10):world.box(STONE[i%4],(0,.12+i*.15,-8.1-i*.43),(6.8,.26+i*.3,.46))
world.box(STONE[1],(0,.7,-15),(17,1.5,7))

def column(x,z):
    world.box(STONE[1],(x,.25,z),(1,.5,1))
    world.box(STONE[2],(x,.53,z),(.82,.1,.82))
    world.lathe(WOOD,(x,0,z),[(.56,.30),(.6,.325),(1.25,.32),(5.9,.295),(6.35,.30),(6.4,.28)] if DETAIL else [(.56,.32),(6.4,.29)],64 if DETAIL else 24)
    for y in [.65,1.2,5.8,6.25]:
        world.lathe(GOLD,(x,0,z),[(y,.33),(y+.04,.33)],24)
    world.lathe(DARK,(x,0,z),[(.68,.335),(1.18,.335)],24)
    for k in range(8):
        a=k*TAU/8
        world.branch(GOLD,(x+.338*math.cos(a),.74,z+.338*math.sin(a)),(x+.338*math.cos(a+.23),1.1,z+.338*math.sin(a+.23)),.013)
for x in [-6.2,-3.9,4.9,7.1]:
    for z in [4.5,-1.9]:column(x,z)
for z in [4.5,-1.9]:
    world.box(WOOD,(.4,6.05,z),(15,.42,.46))
    world.box(GOLD,(.4,5.8,z),(15,.035,.49))
    for x in range(-7,8):
        world.box(DARK,(x,5.48,z),(.07,.7,.12))
        world.box(WOOD,(x,5.24,z),(.92,.06,.13))
        world.box(WOOD,(x,5.62,z),(.92,.06,.13))
        for xx in [-.28,.28]:world.box(WOOD,(x+xx,5.43,z),(.045,.4,.13))
for x in [-6.2,-3.9,4.9,7.1]:world.box(WOOD,(x,6.42,1.3),(.3,.25,7.4))
for z in [i*.55-2.4 for i in range(14)]:world.box(DARK,(.4,6.62,z),(15,.15,.12))
# Repeated carved rail frames cast readable small-scale shadows.
for side in [-1,1]:
    x=side*6.1
    for y in [.55,1.35]:world.box(WOOD,(x,y,1.2),(.16,.14,6))
    for j in range(12):
        z=-1.5+j*.5
        world.box(WOOD,(x,.95,z),(.12,.8,.055))

def lantern(x,y,z):
    world.branch(GOLD,(x,6.2,z),(x,y+.66,z),.018)
    world.lathe(PAPER,(x,y,z),[(-.62,.3),(-.52,.4),(.5,.4),(.62,.3)],8)
    for h in [-.58,.54]:world.lathe(GOLD,(x,y,z),[(h,.41),(h+.055,.41)],8)
    for k in range(8):
        a=k*TAU/8
        world.branch(DARK,(x+.4*math.cos(a),y-.53,z+.4*math.sin(a)),(x+.4*math.cos(a),y+.53,z+.4*math.sin(a)),.017)
    # A small brass rosette reads as ornament at preview resolution.
    for k in range(8):
        a=k*TAU/8;b=(k+1)*TAU/8
        world.branch(GOLD,(x+.13*math.cos(a),y+.13*math.sin(a),z+.405),(x+.13*math.cos(b),y+.13*math.sin(b),z+.405),.012)
    world.branch(GOLD,(x,y-.17,z+.41),(x,y+.17,z+.41),.013)
    world.branch(GOLD,(x,y-.65,z),(x,y-.93,z),.023)
    world.lathe(WOOD,(x,y,z),[(-1.25,.07),(-.91,.035)],8)
for pos in [(-3.3,4.3,3.5),(4,4.7,3.2),(-2.8,4.45,-1.9)]:lantern(*pos)
# A plain plaque retains the reference's silhouette without fabricated calligraphy.
world.box(DARK,(2.8,4.6,-1.9),(1.05,2.2,.12))
for x in [2.31,3.29]:world.box(GOLD,(x,4.6,-1.82),(.025,2.13,.025))
for y in [3.55,5.65]:world.box(GOLD,(2.8,y,-1.82),(1,.025,.025))

def roof(x,y,z,w,d):
    # Curved roof strips rise gently at the eaves and meet at a raised ridge.
    for side in [-1,1]:
        for i in range(12):
            t=i/12;tt=(i+1)/12
            def p(u,v):return (x+u,y+.82*(1-v)**2+.24*v**7+.45*(abs(u)/(w*.5))**6*v**3,z+side*d*.5*v)
            for j in range(16):
                a=-w*.5+j*w/16;b=a+w/16
                world.quad(ROOF,p(a,t),p(b,t),p(b,tt),p(a,tt))
                world.branch(ROOF,p(a,t),p(a,tt),.028)
                if DETAIL:
                    # Front lip and underside give each tile row a real thickness.
                    tile_c=p(a,tt);tile_d=p(b,tt)
                    world.quad(ROOF,tile_c,tile_d,(tile_d[0],tile_d[1]-.045,tile_d[2]),(tile_c[0],tile_c[1]-.045,tile_c[2]))
                if i==11:world.branch(GOLD,p(a,tt),p(b,tt),.025)
    world.branch(ROOF,(x-w*.5,y+.85,z),(x+w*.5,y+.85,z),.09)

def temple(x,y,z,s=1):
    world.box(STONE[1],(x,y-.15,z),(5*s,.3,3.6*s))
    world.box(DARK,(x,y+1.1*s,z),(3.6*s,2.2*s,2.4*s))
    for xx in [-1.8,-.6,.6,1.8]:
        world.lathe(WOOD,(x+xx*s,y,z+1.25*s),[(0,.10*s),(2.3*s,.10*s)],10)
        world.box(CLOTH,(x+xx*s,y+1.25*s,z+1.26*s),(.6*s,1.2*s,.03))
    roof(x,y+2.25*s,z,5.5*s,4.3*s)
    roof(x,y+3.05*s,z,3.6*s,2.7*s)
temple(0,3.6,-24,1.25)
temple(-10,4,-22,1.1)
temple(11,5,-28,1.3)

# Stone balustrade and a bronze censer establish scale in the bright middle ground.
for x in [-7,-5,-3.8,3.8,5,7]:
    world.box(STONE[1],(x,2.05,-12.8),(.3,1.4,.3))
    world.lathe(STONE[2],(x,2.8,-12.8),[(0,.22),(.18,.12),(.28,0)],12)
for x in [-5.5,5.5]:world.box(STONE[2],(x,2.35,-12.8),(3.8,.2,.18))
world.lathe(GOLD,(.5,1.5,-14.5),[(0,.7),(.15,.85),(.3,.5),(.55,.65),(1.05,.65),(1.15,.82),(1.26,.62),(1.6,.22),(1.85,.12),(2,0)],20)
for x in [-.1,1.1]:world.branch(DARK,(x,1.55,-14.5),(x,2.05,-14.5),.09)
for x,z in [(-3.7,-11),(3.6,-12),(-5.7,-16),(6.5,-17)]:
    world.branch(GOLD,(x,1.5,z),(x,5.3,z),.025)
    world.branch(GOLD,(x,5.18,z),(x+1.15,5.18,z),.025)
    for i in range(12):
        yy=5.12-i*.22
        world.quad(CLOTH,(x+.06,yy,z+math.sin(i*.6)*.055),(x+1.07,yy,z+.08+math.sin(i*.6)*.055),(x+1.07,yy-.22,z+.08+math.sin((i+1)*.6)*.055),(x+.06,yy-.22,z+math.sin((i+1)*.6)*.055))

def blossom(pos,r):
    x,y,z=pos
    if DETAIL:
        # Curved petal surfaces replace the flat diamond cards in the close-up.
        for petal in range(5):
            angle=petal*TAU/5
            def point(t,s):
                length=r*1.45*t;width=r*.46*math.sin(math.pi*t)*s
                return (x+math.cos(angle)*length-math.sin(angle)*width,
                        y+math.sin(angle)*length+math.cos(angle)*width,
                        z+r*(.22*t*t+.20*s*s*math.sin(math.pi*t)))
            for i in range(5):
                for j in range(3):
                    t=i/5;tt=(i+1)/5;s=-1+j*2/3;ss=s+2/3
                    world.quad(WHITE if petal%3 else PINK,point(t,s),point(tt,s),point(tt,ss),point(t,ss))
        world.lathe(GOLD,(x,y-.018,z+.012),[(0,.024),(.035,0)],10)
        return
    for i in range(5):
        a=i*TAU/5
        center=(x+math.cos(a)*r*.55,y+math.sin(a)*r*.55,z)
        u=(math.cos(a)*r*.7,math.sin(a)*r*.7,.015)
        v=(-math.sin(a)*r*.37,math.cos(a)*r*.37,.025)
        world.quad(WHITE if i%3 else PINK,tuple(center[j]-u[j] for j in range(3)),tuple(center[j]+v[j] for j in range(3)),tuple(center[j]+u[j] for j in range(3)),tuple(center[j]-v[j] for j in range(3)))
    world.lathe(GOLD,(x,y-.018,z+.012),[(0,.024),(.035,0)],5)

def plum(x,y,z,s):
    rings=[(0,.25*s),(.1*s,.34*s),(.4*s,.42*s),(.6*s,.22*s),(.66*s,.27*s)]
    if DETAIL:
        rings=[(h*s,r*s) for h,r in [(0,.24),(.025,.27),(.07,.30),(.14,.36),(.23,.40),(.32,.415),(.40,.40),(.46,.36),(.52,.29),(.57,.23),(.61,.22),(.63,.25),(.66,.27),(.68,.265)]]
    world.lathe(BLUE,(x,y,z),rings,64 if DETAIL else 20)
    origin=(x,y+.55*s,z)
    for k in range(7):
        a=RNG.uniform(0,TAU);end=(x+math.cos(a)*s*.9,y+s*RNG.uniform(1.5,2.7),z+math.sin(a)*s*.55)
        world.branch(TRUNK,origin,end,.035*s)
        for j in range(8):
            t=.35+j*.085
            p=tuple(origin[i]+(end[i]-origin[i])*t for i in range(3))
            tip=(p[0]+RNG.uniform(-.25,.25)*s,p[1]+RNG.uniform(0,.2)*s,p[2]+RNG.uniform(-.12,.12)*s)
            world.branch(TRUNK,p,tip,.012*s);blossom(tip,RNG.uniform(.075,.12)*s)
for x,y,z,s in [(-4.5,.2,3.3,1.05),(-5.4,.2,-1,1.25),(5.2,.2,-2,1.1),(-3.9,.8,-6,1),(4.5,1.55,-13,1),(-6,1.55,-16,1.2)]:plum(x,y,z,s)
for i in range(85):
    x=RNG.uniform(-6,6);z=RNG.uniform(-7,7)
    world.quad(PINK,(x,.013,z),(x+.07,.018,z-.015),(x+.10,.013,z+.065),(x+.02,.012,z+.07))

mountains=Mesh()
for layer in range(3):
    for k in range(9):
        x=(k-4)*8+RNG.uniform(-2,2);z=-36-layer*16-RNG.uniform(0,5)
        height=RNG.uniform(9,18)+layer*2;r=RNG.uniform(3,5)
        rings=[]
        for j in range(10):
            t=j/9;rr=r*(1-t*.8)
            rings.append([(x+math.cos(a*TAU/13)*rr*(1+RNG.uniform(-.17,.17))+math.sin(t*5)*.8,-1+t*height,z+math.sin(a*TAU/13)*rr) for a in range(13)])
        for j in range(9):
            for a in range(13):mountains.quad(MOUNTAIN[layer],rings[j][a],rings[j+1][a],rings[j+1][(a+1)%13],rings[j][(a+1)%13])
        for a in range(13):mountains.tri(MOUNTAIN[layer],rings[-1][a],(x+.1,height-.5,z),rings[-1][(a+1)%13])
        # Sparse dark crowns break the skyline without dense leaf geometry.
        if layer==0:
            for j in range(3):
                xx=x+RNG.uniform(-1,1);yy=height-1+j*.25
                mountains.branch(TRUNK,(xx,yy-1,z),(xx+.12,yy+.45,z),.055)
                mountains.lathe(LEAF,(xx,yy,z),[(0,.9),(.24,.7),(.38,.1)],9)
world.save(ROOT/('assets/courtyard-detail.glb' if DETAIL else 'assets/courtyard.glb'))
mountains.save(ROOT/('assets/mountains-detail.glb' if DETAIL else 'assets/mountains.glb'))

# A small original equirectangular sky supplies broad diffuse light and reflections.
raw=bytearray()
for y in range(256):
    raw.append(0)
    for x in range(512):
        t=y/255
        haze=math.exp(-((t-.48)/.18)**2)
        cloud=max(0,math.sin(x*.039+math.sin(y*.05))*math.sin(y*.09+x*.013))**2
        sky=[165+61*haze+22*cloud,188+43*haze+18*cloud,205+29*haze+14*cloud]
        if t>.55:sky=[130,139,143]
        raw.extend(int(min(255,v)) for v in sky)
def png_chunk(name,data):return struct.pack('>I',len(data))+name+data+struct.pack('>I',zlib.crc32(name+data)&0xffffffff)
(ROOT/('assets/sky-detail.png' if DETAIL else 'assets/sky.png')).write_bytes(b'\x89PNG\r\n\x1a\n'+png_chunk(b'IHDR',struct.pack('>IIBBBBB',512,256,8,2,0,0,0))+png_chunk(b'IDAT',zlib.compress(bytes(raw)))+png_chunk(b'IEND',b''))
