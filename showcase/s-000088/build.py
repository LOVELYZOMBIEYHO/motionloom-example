# =========================================
# =========================================
# showcase/s-000088/build.py
"""Build a continuous canyon course and a shot-driven MotionLoom racing previz."""
from pathlib import Path
import math, json, struct, random

ROOT = Path(__file__).resolve().parent
ASSETS = ROOT / 'assets'
ASSETS.mkdir(exist_ok=True)

# One shared route controls road edges, vehicle tangents and camera rails.
def route(s, lane=0, height=0):
    x=18*math.sin(s/62)+9*math.sin(s/29)
    slope=18/62*math.cos(s/62)+9/29*math.cos(s/29)
    norm=math.sqrt(1+slope*slope)
    return (x+lane/norm, height, -s+lane*slope/norm)

def yaw(s):
    a,b=route(s-.05),route(s+.05)
    return math.degrees(math.atan2(-(b[0]-a[0]),-(b[2]-a[2])))

def mix(a,b,t): return tuple(x+(y-x)*t for x,y in zip(a,b))
def smooth(t): return max(0,min(1,t))**2*(3-2*max(0,min(1,t)))

class Mesh:
    def __init__(self): self.parts={}
    def tri(self,mat,a,b,c):
        p,n=self.parts.setdefault(mat,([],[]))
        u=[b[i]-a[i] for i in range(3)];v=[c[i]-a[i] for i in range(3)]
        normal=[u[1]*v[2]-u[2]*v[1],u[2]*v[0]-u[0]*v[2],u[0]*v[1]-u[1]*v[0]]
        length=math.sqrt(sum(x*x for x in normal)) or 1
        p.extend((a,b,c)); n.extend([tuple(x/length for x in normal)]*3)
    def quad(self,mat,a,b,c,d): self.tri(mat,a,b,c);self.tri(mat,a,c,d)
    def box(self,mat,pos,size):
        x,y,z=pos;w,h,l=[v/2 for v in size]
        v=[(x+a*w,y+b*h,z+c*l) for a,b,c in [(-1,-1,-1),(1,-1,-1),(1,1,-1),(-1,1,-1),(-1,-1,1),(1,-1,1),(1,1,1),(-1,1,1)]]
        for a,b,c,d in [(0,3,2,1),(4,5,6,7),(0,4,7,3),(1,2,6,5),(3,7,6,2),(0,1,5,4)]:self.quad(mat,v[a],v[b],v[c],v[d])
    def rock(self,mat,pos,radius,height,seed):
        rng=random.Random(seed);rings=[]
        for level,scale in [(0,1.18),(.22,1.05),(.58,.88),(.82,.78),(1,.64)]:
            rings.append([(pos[0]+math.cos(i*math.tau/7)*radius*scale*(.9+rng.random()*.2),pos[1]+height*level,pos[2]+math.sin(i*math.tau/7)*radius*scale*(.9+rng.random()*.2)) for i in range(7)])
        for j in range(4):
            for i in range(7):self.quad(mat if j%2==0 else mat+1,rings[j][i],rings[j+1][i],rings[j+1][(i+1)%7],rings[j][(i+1)%7])
        for i in range(1,6):self.tri(mat,rings[-1][0],rings[-1][i+1],rings[-1][i])
    def wheel(self,pos):
        x,y,z=pos
        for i in range(12):
            a,b=i*math.tau/12,(i+1)*math.tau/12
            def p(dx,t):return (x+dx,y+.36*math.cos(t),z+.36*math.sin(t))
            self.quad(7,p(-.14,a),p(-.14,b),p(.14,b),p(.14,a))
            self.tri(7,(x+.14,y,z),p(.14,a),p(.14,b))
            self.tri(7,(x-.14,y,z),p(-.14,b),p(-.14,a))
    def save(self,path):
        colors=['#343B3D','#E5CF91','#C38F60','#BA7550','#D29A6A','#935438','#AF7350','#181D22','#E44132','#267EDB','#273744','#F2D69C']
        materials=[]
        for c in colors:
            rgb=[int(c[i:i+2],16)/255 for i in (1,3,5)]
            materials.append({'pbrMetallicRoughness':{'baseColorFactor':rgb+[1],'metallicFactor':0,'roughnessFactor':.8},'doubleSided':True})
        doc={'asset':{'version':'2.0','generator':'S88 deterministic blockout'},'scene':0,'scenes':[{'nodes':[0]}],'nodes':[{'mesh':0}],'meshes':[{'primitives':[]}],'materials':materials,'buffers':[{}],'bufferViews':[],'accessors':[]}
        data=bytearray()
        def accessor(values):
            start=len(data)
            for v in values:data.extend(struct.pack('<3f',*v))
            view=len(doc['bufferViews']);doc['bufferViews'].append({'buffer':0,'byteOffset':start,'byteLength':len(data)-start})
            index=len(doc['accessors']);doc['accessors'].append({'bufferView':view,'componentType':5126,'count':len(values),'type':'VEC3','min':[min(v[i] for v in values) for i in range(3)],'max':[max(v[i] for v in values) for i in range(3)]})
            return index
        for mat,(positions,normals) in self.parts.items():
            doc['meshes'][0]['primitives'].append({'attributes':{'POSITION':accessor(positions),'NORMAL':accessor(normals)},'material':mat})
        doc['buffers'][0]['byteLength']=len(data)
        raw=json.dumps(doc,separators=(',',':')).encode();raw+=b' '*((-len(raw))%4)
        path.write_bytes(struct.pack('<III',0x46546c67,2,28+len(raw)+len(data))+struct.pack('<II',len(raw),0x4e4f534a)+raw+struct.pack('<II',len(data),0x004e4942)+data)

world=Mesh()
# Joined ribbon quads have shared edge coordinates: no slab gaps or overlap flicker.
for s in range(-60,721,2):
    for lo,hi,mat,h in [(-6,6,0,.02),(-13,-6,2,0),(6,13,2,0),(-6,-5.82,1,.025),(5.82,6,1,.025)]:
        world.quad(mat,route(s,lo,h),route(s,hi,h),route(s+2,hi,h),route(s+2,lo,h))
    if s%12<5:
        world.quad(1,route(s,-.07,.028),route(s,.07,.028),route(s+2,.07,.028),route(s+2,-.07,.028))
world.box(2,(0,-1,-330),(300,1.9,920))
rng=random.Random(8808)
for side in [-1,1]:
    for i,s in enumerate(range(-45,735,17)):
        radius=rng.uniform(7,11);lane=side*(18+radius*.6+rng.uniform(0,5))
        world.rock(3 if i%3 else 5,route(s,lane,-.6),radius,rng.uniform(14,29),8800+i+100*(side+1))
    for i,s in enumerate(range(-15,760,57)):
        world.rock(3,route(s,side*48,-1),rng.uniform(13,20),rng.uniform(28,43),9800+i+100*(side+1))
world.save(ASSETS/'canyon.glb')
for name,mat in [('red',8),('blue',9)]:
    car=Mesh();car.box(mat,(0,.53,0),(1.96,.50,4.35));car.box(mat,(0,.79,-1.18),(1.82,.16,1.65))
    car.box(10,(0,1.03,.25),(1.60,.55,1.82));car.box(mat,(0,1.33,.3),(1.68,.08,1.64))
    car.box(7,(0,.42,2.21),(1.68,.18,.12));car.box(7,(0,.4,-2.21),(1.65,.12,.10))
    for x in [-.66,.66]:car.box(8,(x,.68,2.19),(.47,.14,.04));car.box(11,(x,.70,-2.19),(.45,.12,.04))
    for x in [-1,1]:
        for z in [-1.38,1.38]:car.wheel((x,.38,z))
    car.box(7,(0,.98,1.85),(2.10,.08,.38))
    car.save(ASSETS/f'{name}-car.glb')

# Road distance advances continuously; passing happens longitudinally in separate lanes.
def cars(t):
    base=22+19*t
    lead=3.8*math.cos(t*math.tau/24)
    return (base-lead,-2.05),(base+lead,2.05)

shots=[('entry',0,4),('front',4,8),('left_side',8,11),('quarter',11,14),('overhead',14,18),('right_side',18,22),('bumper',22,26),('runout',26,30)]
def camera(name,t):
    r,b=cars(t);s=(r[0]+b[0])/2
    if name=='entry':
        q=smooth(t/4);return route(s-17+5*q,-2+2*q,8-5.8*q),route(s+1,0,.8),54
    # Front and side tracking establish genuinely different viewing directions.
    # Keep lateral rigs inside the canyon's clear shoulder corridor.
    if name=='front':return route(s+15,0,2.1),route(s,0,.65),60
    if name=='left_side':return route(s-1,-11,3.2),route(s,0,.7),76
    if name=='bumper':return route(r[0]-8,.8,1.7),route(s+1,0,.8),62
    # Track from inside the two lanes so blue stays large in the foreground
    # without hiding the leading red car along the same sightline.
    if name=='quarter':return route(b[0]-7,-.8,1.6),route(s+1,0,.85),64
    # The overhead shot re-establishes geography before crossing the race axis.
    if name=='overhead':return route(s-3,0,23),route(s+1,0,0),57
    if name=='right_side':return route(s+1,11,5),route(s,0,.7),76
    q=smooth((t-26)/4);return route(s+14+8*q,-8-2*q,6+7*q),route(s,0,.7),58

def vec(v):return '['+','.join(f'{x:.4f}' for x in v)+']'
lines=['<!-- S88 / CANYON DUEL / 30-second cinematic blocking reference -->','<Graph fps={24} duration="30s" size={[1280,720]}>',
'<Assets><ModelAsset id="canyon" src="https://raw.githubusercontent.com/LOVELYZOMBIEYHO/motionloom-example/refs/heads/main/showcase/s-000088/assets/canyon.glb" /><ModelAsset id="red_asset" src="https://raw.githubusercontent.com/LOVELYZOMBIEYHO/motionloom-example/refs/heads/main/showcase/s-000088/assets/red-car.glb" /><ModelAsset id="blue_asset" src="https://raw.githubusercontent.com/LOVELYZOMBIEYHO/motionloom-example/refs/heads/main/showcase/s-000088/assets/blue-car.glb" /></Assets>',
'<Background color="#BCD0D5" />','<Scene id="S88CanyonDuel"><Timeline><Track id="world" space="3d"><Sequence from="0s" duration="30s" out="hold"><CompositeGroup id="stage" space="3d" depth="true">']
for name,start,end in shots:
    pos,target,fov=camera(name,start);lines.append(f'<Camera3D id="{name}" position={{{vec(pos)}}} target={{{vec(target)}}} fov="{fov}" />')
lines+=['<DirectionalLight direction={[-.55,-1,.35]} color="#FFE1B5" intensity="2.2" castShadow="true" shadowStrength="0.62" />','<DirectionalLight direction={[.4,-.35,-.7]} color="#CADDE9" intensity="0.9" />','<AmbientOcclusion radius="0.6" intensity="0.35" />','<ContactShadow distance="0.3" softness="0.4" intensity="0.6" />','<ColorManagement toneMapping="aces" exposure="1.15" />','<Model id="course" asset="canyon" scaleMode="none" scale="1" receiveShadow="true" castShadow="true" />']
for name,index in [('red',0),('blue',1)]:
    s,lane=cars(0)[index];lines.append(f'<Model id="{name}" asset="{name}_asset" position={{{vec(route(s,lane,.025))}}} scaleMode="none" scale="1" castShadow="true" receiveShadow="true" />')
lines+=['</CompositeGroup></Sequence></Track>', '<Track id="slate" space="screen" compositeOrder="90"><Sequence from="0s" duration="30s" out="hold"><Layer space="screen">', '<Rect x="0" y="0" width="1280" height="50" color="#080C10" /><Rect x="0" y="670" width="1280" height="50" color="#080C10" />', '<Text x="32" y="30" value="CANYON DUEL   /   CAMERA BLOCKING" fontSize="15" tracking="2" color="#ECE8DC" /><Text x="32" y="700" value="PREVIZ — NOT FINAL ANIMATION" fontSize="13" tracking="2" color="#D4B488" />','</Layer></Sequence></Track></Timeline></Scene>']
def channel(node,prop,samples):
    lines.append(f'<AnimationTarget node="{node}" property="{prop}">')
    for t,v in samples:lines.append(f'  <Key time="{t:.4f}s" value="{vec(v) if isinstance(v,tuple) else v}" />')
    lines.append('</AnimationTarget>')
times=[i/8 for i in range(241)]
for name,index in [('red',0),('blue',1)]:
    channel(name,'position',[(t,route(*cars(t)[index],height=.025)) for t in times])
    channel(name,'rotationY',[(t,f'{yaw(cars(t)[index][0]):.4f}') for t in times])
channel('S88CanyonDuel','activeCamera',[(start,name) for name,start,end in shots])
for name,start,end in shots:
    ts=[t for t in times if start<=t<=end]
    channel(name,'position',[(t,camera(name,t)[0]) for t in ts])
    channel(name,'target',[(t,camera(name,t)[1]) for t in ts])
lines+=['<Present from="S88CanyonDuel" />','</Graph>']
script='\n'.join(lines).replace('><','>\n<')+'\n';(ROOT/'main.motionloom').write_text(script)
(ROOT/'shots.json').write_text(json.dumps([{'camera':n,'start':a,'end':b} for n,a,b in shots],indent=2)+'\n')
print('Built continuous canyon course, two low-poly cars, eight multi-angle shots and 30 s of 8 Hz transform keys.')
