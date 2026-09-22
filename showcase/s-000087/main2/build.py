# =========================================
# =========================================
# showcase/s-000087/main2/build.py
"""Build original procedural assets and animation for native MotionLoom playback."""
from pathlib import Path
import math, json, struct, random, hashlib
P=Path(__file__).resolve().parent
TAU=math.tau
rng=random.Random(88022)
def add(a,b):return tuple(x+y for x,y in zip(a,b))
def sub(a,b):return tuple(x-y for x,y in zip(a,b))
def mul(a,b):return tuple(x*b for x in a)
def dot(a,b):return sum(x*y for x,y in zip(a,b))
def cross(a,b):return (a[1]*b[2]-a[2]*b[1],a[2]*b[0]-a[0]*b[2],a[0]*b[1]-a[1]*b[0])
def length(a):return math.sqrt(dot(a,a))
def norm(a):return mul(a,1/max(length(a),1e-9))
def lerp(a,b,t):return tuple(x+(y-x)*t for x,y in zip(a,b))
def clamp(x):return max(0,min(1,x))
def smooth(x):x=clamp(x);return x*x*(3-2*x)
def qaxis(a,t):return (*mul(norm(a),math.sin(t/2)),math.cos(t/2))
def qmul(a,b):return (*add(add(mul(b[:3],a[3]),mul(a[:3],b[3])),cross(a[:3],b[:3])),a[3]*b[3]-dot(a[:3],b[:3]))
def quat(x=0,y=0,z=0):return qmul(qmul(qaxis((0,0,1),z),qaxis((0,1,0),y)),qaxis((1,0,0),x))
def rotate(v,q):t=mul(cross(q[:3],v),2);return add(v,add(mul(t,q[3]),cross(q[:3],t)))
def between(a,b):
 a=norm(a);b=norm(b);d=dot(a,b)
 if d<-.99999:return qaxis((1,0,0),math.pi)
 return norm((*cross(a,b),1+d))
def rgb(s):return [((int(s[i:i+2],16)/255+.055)/1.055)**2.4 if int(s[i:i+2],16)/255>.04045 else int(s[i:i+2],16)/255/12.92 for i in (1,3,5)]
class GLB:
 def __init__(self):self.doc={'asset':{'version':'2.0','generator':'MotionLoom S87 MAIN2 original procedural authoring'},'scene':0,'scenes':[{'nodes':[]}],'nodes':[],'meshes':[],'materials':[],'buffers':[{}],'bufferViews':[],'accessors':[]};self.bin=bytearray();self.anim=[];self.cache={};self.values=[]
 def material(self,name,color,emission=0,double=False):
  c=rgb(color);m={'name':name,'pbrMetallicRoughness':{'baseColorFactor':c+[1],'metallicFactor':0,'roughnessFactor':.92},'doubleSided':double}
  if emission:m['emissiveFactor']=[v*emission for v in c]
  self.doc['materials'].append(m);return len(self.doc['materials'])-1
 def acc(self,values,kind,component=5126):
  dims={'SCALAR':1,'VEC2':2,'VEC3':3,'VEC4':4,'MAT4':16}[kind];flat=[x for v in values for x in (v if isinstance(v,(tuple,list)) else (v,))]
  while len(self.bin)%4:self.bin.append(0)
  off=len(self.bin);self.bin.extend(struct.pack('<'+('f' if component==5126 else 'H' if component==5123 else 'I')*len(flat),*flat));vi=len(self.doc['bufferViews']);self.doc['bufferViews'].append({'buffer':0,'byteOffset':off,'byteLength':len(self.bin)-off});a={'bufferView':vi,'componentType':component,'count':len(values),'type':kind}
  if kind=='VEC3':a.update(min=[min(v[j] for v in values) for j in range(3)],max=[max(v[j] for v in values) for j in range(3)])
  if kind=='SCALAR':a.update(min=[min(values)],max=[max(values)])
  self.values.append(values);self.doc['accessors'].append(a);return len(self.doc['accessors'])-1
 def mesh(self,geo,mat,name='mesh'):
  pos,normal,indices=geo;pr={'attributes':{'POSITION':self.acc(pos,'VEC3'),'NORMAL':self.acc(normal,'VEC3')},'indices':self.acc(indices,'SCALAR',5125),'material':mat}
  self.doc['meshes'].append({'name':name,'primitives':[pr]});return len(self.doc['meshes'])-1
 def node(self,name,mesh=None,parent=None,pos=(0,0,0),rot=(0,0,0,1),scale=(1,1,1)):
  n={'name':name+'_'+str(len(self.doc['nodes'])),'translation':list(pos),'rotation':list(rot),'scale':list(scale)}
  if mesh is not None:n['mesh']=mesh
  i=len(self.doc['nodes']);self.doc['nodes'].append(n)
  if parent is None:self.doc['scenes'][0]['nodes'].append(i)
  else:self.doc['nodes'][parent].setdefault('children',[]).append(i)
  return i
 def channel(self,node,path,values,times,step=False):
  if all(v==values[0] for v in values):self.doc['nodes'][node][path]=list(values[0]);return
  self.anim.append((node,path,values,times,step))
 def save(self,name):
  # The current importer associates one node per mesh. Give each instance its own
  # mesh record while sharing vertex accessors; no renderer changes are needed.
  seen=set()
  for node in self.doc['nodes']:
   if 'mesh' not in node:continue
   mi=node['mesh']
   if mi in seen:
    node['mesh']=len(self.doc['meshes']);self.doc['meshes'].append(json.loads(json.dumps(self.doc['meshes'][mi])))
   seen.add(mi)
  if self.anim:
   # Bake vertices into a common bind space and retain rigid one-joint weights.
   # This is a standard single-mesh skin with inverse bind matrices, avoiding
   # ambiguous per-primitive bind spaces in native skinning strategy selection.
   parents={child:i for i,n in enumerate(self.doc['nodes']) for child in n.get('children',[])}
   cache={}
   def local(i):
    n=self.doc['nodes'][i];q=n['rotation'];sc=n['scale'];tr=n['translation']
    cols=[mul(rotate(axis,q),scale) for axis,scale in zip([(1,0,0),(0,1,0),(0,0,1)],sc)]
    return [[cols[c][r] for c in range(3)]+[tr[r]] for r in range(3)]+[[0,0,0,1]]
   def mm(a,b):return [[sum(a[r][k]*b[k][c] for k in range(4)) for c in range(4)] for r in range(4)]
   def world(i):
    if i not in cache:cache[i]=mm(world(parents[i]),local(i)) if i in parents else local(i)
    return cache[i]
   def inverse(m):
    a=[list(row)+[float(i==j) for j in range(4)] for i,row in enumerate(m)]
    for j in range(4):
     pivot=max(range(j,4),key=lambda i:abs(a[i][j]));a[j],a[pivot]=a[pivot],a[j];v=a[j][j];a[j]=[x/v for x in a[j]]
     for i in range(4):
      if i!=j:v=a[i][j];a[i]=[x-v*y for x,y in zip(a[i],a[j])]
    return [row[4:] for row in a]
   meshjoints=[i for i,n in enumerate(self.doc['nodes']) if 'mesh' in n];joints=meshjoints+paper_bends;merged={};ib=[]
   for j,ni in enumerate(joints):
    node=self.doc['nodes'][ni];m=world(ni);inv=inverse(m);ib.append(tuple(inv[r][c] for c in range(4) for r in range(4)))
    if 'mesh' not in node:continue
    ancestor=ni
    while ancestor in parents and ancestor!=paper:ancestor=parents[ancestor]
    is_paper=ancestor==paper
    for prim in self.doc['meshes'][node.pop('mesh')]['primitives']:
     pos=self.values[prim['attributes']['POSITION']];nor=self.values[prim['attributes']['NORMAL']];inds=self.values[prim['indices']]
     bp,bn,bi,bj,bw=merged.setdefault(prim['material'],([],[],[],[],[]));offset=len(bp)
     bp.extend(tuple(sum(m[r][k]*v[k] for k in range(3))+m[r][3] for r in range(3)) for v in pos)
     bn.extend(norm(tuple(sum(inv[k][r]*v[k] for k in range(3)) for r in range(3))) for v in nor)
     bi.extend(i+offset for i in inds)
     for v in bp[offset:]:
      if is_paper:
       row=clamp((v[1]+.37)/.74)*8;lo=min(7,int(row));f=row-lo
       bj.append((len(meshjoints)+lo,len(meshjoints)+lo+1,0,0));bw.append((1-f,f,0,0))
      else:bj.append((j,0,0,0));bw.append((1,0,0,0))
   self.doc['meshes']=[];prims=[]
   for mat,(pos,nor,inds,js,ws) in merged.items():
    prims.append({'attributes':{'POSITION':self.acc(pos,'VEC3'),'NORMAL':self.acc(nor,'VEC3'),'JOINTS_0':self.acc(js,'VEC4',5123),'WEIGHTS_0':self.acc(ws,'VEC4')},'indices':self.acc(inds,'SCALAR',5125),'material':mat})
   self.doc['meshes']=[{'name':'original_rigid_character_mesh','primitives':prims}]
   meshnode=self.node('skinned_geometry',0);self.doc['nodes'][meshnode]['skin']=0
   self.doc['skins']=[{'joints':joints,'inverseBindMatrices':self.acc(ib,'MAT4')}]
   a={'name':'film','samplers':[],'channels':[]};tc={}
   for node,path,vals,times,step in self.anim:
    key=tuple(times)
    if key not in tc:tc[key]=self.acc(times,'SCALAR')
    out=self.acc(vals,'VEC4' if path=='rotation' else 'VEC3');a['channels'].append({'sampler':len(a['samplers']),'target':{'node':node,'path':path}});a['samplers'].append({'input':tc[key],'output':out,'interpolation':'STEP' if step else 'LINEAR'})
   self.doc['animations']=[a]
  self.doc['buffers'][0]['byteLength']=len(self.bin);js=json.dumps(self.doc,separators=(',',':')).encode();js+=b' '*((-len(js))%4);self.bin+=b'\0'*((-len(self.bin))%4)
  (P/name).write_bytes(struct.pack('<III',0x46546c67,2,28+len(js)+len(self.bin))+struct.pack('<II',len(js),0x4e4f534a)+js+struct.pack('<II',len(self.bin),0x004e4942)+self.bin)
# Smooth lathed surfaces and indexed triangles keep the native renderer efficient.
def loft(rows,n=32):
 pos=[];ind=[]
 for y,rx,rz,cz in rows:
  for j in range(n):a=j/n*TAU;pos.append((math.sin(a)*rx,y,cz+math.cos(a)*rz))
 for i in range(len(rows)-1):
  for j in range(n):a=i*n+j;b=i*n+(j+1)%n;c=b+n;d=a+n;ind.extend([a,b,c,a,c,d])
 return normals(pos,ind)
def normals(pos,ind):
 ns=[(0,0,0) for _ in pos]
 for i in range(0,len(ind),3):
  a,b,c=ind[i:i+3];n=cross(sub(pos[b],pos[a]),sub(pos[c],pos[a]))
  for j in (a,b,c):ns[j]=add(ns[j],n)
 return (pos,[norm(n) for n in ns],ind)
def ell(rx=1,ry=1,rz=1,n=24,rings=16):
 return loft([(-math.cos(i/rings*math.pi)*ry,max(.0001,math.sin(i/rings*math.pi))*rx,max(.0001,math.sin(i/rings*math.pi))*rz,0) for i in range(rings+1)],n)
def cube():
 p=[];ns=[];idx=[]
 for normal,u,v in [((1,0,0),(0,1,0),(0,0,1)),((-1,0,0),(0,0,1),(0,1,0)),((0,1,0),(0,0,1),(1,0,0)),((0,-1,0),(1,0,0),(0,0,1)),((0,0,1),(1,0,0),(0,1,0)),((0,0,-1),(0,1,0),(1,0,0))]:
  base=len(p)
  for a,b in [(-1,-1),(1,-1),(1,1),(-1,1)]:p.append(mul(add(normal,add(mul(u,a),mul(v,b))),.5));ns.append(normal)
  idx.extend([base,base+1,base+2,base,base+2,base+3])
 return p,ns,idx
def tube(points,r=.008,n=7):
 pos=[];idx=[]
 for i,p in enumerate(points):
  tangent=norm(sub(points[min(i+1,len(points)-1)],points[max(0,i-1)]));u=norm(cross(tangent,(0,0,1)))
  if length(u)<.1:u=(1,0,0)
  v=cross(tangent,u)
  for j in range(n):pos.append(add(p,add(mul(u,r*math.cos(j/n*TAU)),mul(v,r*math.sin(j/n*TAU)))))
 for i in range(len(points)-1):
  for j in range(n):a=i*n+j;b=i*n+(j+1)%n;idx.extend([a,b,b+n,a,b+n,a+n])
 return normals(pos,idx)
def strand(points,width=.1,depth=.04):
 pos=[];idx=[];n=10
 for i,p in enumerate(points):
  f=i/(len(points)-1);w=max(.001,width*(math.sin((.15+f*.85)*math.pi)**.6));d=max(.002,depth*(1-f*.8))
  for j in range(n):a=j/n*TAU;pos.append(add(p,(math.cos(a)*w,0,math.sin(a)*d)))
 for i in range(len(points)-1):
  for j in range(n):a=i*n+j;b=i*n+(j+1)%n;idx.extend([a,b,b+n,a,b+n,a+n])
 return normals(pos,idx)
G=GLB();M={}
for name,color,e in [('skin','#F5D6BE',.16),('skinshade','#D5A58D',.12),('blush','#E9B5A5',.2),('hair','#45413F',.06),('hairlit','#655852',.08),('ink','#383A40',.1),('white','#FFF6E7',.45),('iris','#777DA4',.3),('pupil','#333446',.2),('cream','#EEE9D8',.1),('teal','#548D88',.05),('pants','#53616A',.05),('skirt','#4F686C',.05),('sole','#BAC1B8',.05),('gold','#D5AD68',.1),('book','#367B7B',.12),('paper','#FFF4DC',.45)]:M[name]=G.material(name,color,e)
unit_sphere={};unit_box={}
def ball(parent,name,mat,pos,size):
 if mat not in unit_sphere:unit_sphere[mat]=G.mesh(ell(),M[mat],mat+'_ell')
 return G.node(name,unit_sphere[mat],parent,pos,scale=size)
def boxnode(parent,name,mat,pos,size,rot=(0,0,0,1)):
 if mat not in unit_box:unit_box[mat]=G.mesh(cube(),M[mat],mat+'_box')
 return G.node(name,unit_box[mat],parent,pos,rot,size)
def geom(parent,name,mat,geo,pos=(0,0,0),rot=(0,0,0,1)):return G.node(name,G.mesh(geo,M[mat],name),parent,pos,rot)
def curve(parent,name,mat,pts,r=.008):return geom(parent,name,mat,tube(pts,r))
def make_character(role,girl):
 root=G.node(role);body=G.node(role+'_body',parent=root);head=G.node(role+'_head',parent=body,pos=(0,2.25,0))
 geom(body,role+'_shirt','cream',loft([(1.18,.25,.16,0),(1.32,.29,.18,0),(1.70,.31,.19,0),(1.90,.33,.16,0),(1.96,.19,.12,0)]))
 ball(body,role+'_neck','skin',(0,2.0,0),(.105,.15,.10))
 geom(head,role+'_face','skin',loft([(-.38,.016,.055,.08),(-.33,.115,.125,.025),(-.24,.22,.205,0),(-.12,.29,.255,0),(.02,.305,.265,0),(.17,.315,.267,-.01),(.30,.27,.24,-.025),(.39,.17,.16,-.03),(.425,.003,.005,-.03)],48))
 for s in (-1,1):
  ball(head,role+'_ear','skin',(s*.302,-.025,-.015),(.053,.083,.039));ball(head,role+'_earinner','skinshade',(s*.32,-.02,.015),(.024,.048,.01))
 eyes=[]
 for s in (-1,1):
  eye=G.node(role+f'_eye{s}',parent=head,pos=(s*.133,.008,.246),rot=quat(0,s*.23,0));eyes.append(eye)
  ball(eye,'sclera','white',(0,0,0),(.091,.074,.022));ball(eye,'iris','iris',(0,-.004,.021),(.041,.062,.012));ball(eye,'pupil','pupil',(0,-.005,.032),(.014,.04,.003));ball(eye,'glint','white',(-.012,.023,.036),(.011,.014,.004));ball(eye,'glint_small','white',(.016,-.03,.036),(.005,.007,.003))
  curve(eye,'upper_lash','ink',[(x,.047+.024*math.sin(i/12*math.pi),.012) for i,x in enumerate([-.089+j*.178/12 for j in range(13)])],.009)
  curve(eye,'lower_lash','skinshade',[(x,-.052-.012*math.sin(i/10*math.pi),.014) for i,x in enumerate([-.075+j*.15/10 for j in range(11)])],.003)
  curve(head,'brow','hair',[(s*.133-.075+i*.015,.14+.012*math.sin(i/10*math.pi),.252-abs(s*.133-.075+i*.015)*.12) for i in range(11)],.005)
  ball(head,'cheek','blush',(s*.213,-.105,.19),(.046,.013,.007))
 ball(head,'nose','skin',(0,-.09,.255),(.026,.033,.035))
 mouth=curve(head,'mouth','skinshade',[(-.036,-.235,.196),(0,-.239,.204),(.036,-.235,.196)],.004)
 hair=G.node(role+'_hair',parent=head)
 # The cap stops above the eyes; individually tapered locks define the silhouette.
 geom(hair,'cap','hair',loft([(.07,.327,.287,-.026),(.19,.332,.28,-.025),(.31,.287,.245,-.025),(.40,.18,.164,-.025),(.447,.003,.004,-.025)],40))
 for i in range(11 if girl else 9):
  a=math.pi*.38+i/(10 if girl else 8)*math.pi*1.24;x=math.sin(a)*.295;z=math.cos(a)*.268-.035;end=-.61 if girl else -.26
  pts=[(x*(.72+.34*f),.31+(end-.31)*f,z+.04*f) for f in [j/12 for j in range(13)]]
  geom(hair,'back_lock','hair' if i%3 else 'hairlit',strand(pts,.085,.075))
 for i in range(7):
  x=-.25+i*.083;end=.025+(.07 if i%3==0 else 0)+(abs(i-3)*.008)
  pts=[(x+.04*math.sin(f*math.pi),.35+(end-.35)*f,.18+.106*math.sin(f*math.pi*.7)) for f in [j/12 for j in range(13)]]
  geom(hair,'fringe','hair' if i%3 else 'hairlit',strand(pts,.065,.026))
 for s in (-1,1):
  geom(hair,'side_lock','hair',strand([(s*(.29+.024*math.sin(f*math.pi)),.27-f*(.62 if girl else .45),.055+.06*math.sin(f*math.pi)) for f in [j/12 for j in range(13)]],.055,.052))
 if girl:
  boxnode(head,'gold_barrette','gold',(.292,.125,.19),(.088,.02,.025),quat(0,.4,-.35));boxnode(head,'gold_barrette2','gold',(.30,.085,.185),(.074,.015,.023),quat(0,.4,-.35))
  geom(body,'pleated_skirt','skirt',loft([(.75,.42,.29,0),(.83,.42,.29,0),(1.16,.26,.175,0),(1.22,.25,.17,0)],32))
  for i in range(12):
   a=i/12*TAU;curve(body,'pleat','pants',[(math.sin(a)*r,y,math.cos(a)*r*.7) for y,r in [(.77,.423),(.95,.34),(1.16,.263)]],.003)
 else:
  for s in (-1,1):boxnode(body,'backpack_strap','pants',(s*.215,1.62,.18),(.036,.60,.021),quat(0,0,s*.12))
  ball(body,'backpack','teal',(0,1.55,-.23),(.28,.33,.11))
 for s in (-1,1):curve(body,'collar','sole',[(s*.18,1.94,.13),(s*.095,1.84,.18),(0,1.86,.20)],.011)
 arms=[];legs=[]
 for s in (-1,1):
  upper=G.node(role+f'_arm{s}',parent=body);ball(upper,'sleeve','cream',(0,-.13,0),(.116,.205,.125));ball(upper,'upperarm','skin',(0,-.28,0),(.067,.15,.071))
  lower=G.node(role+f'_forearm{s}',parent=body);ball(lower,'forearm','skin',(0,-.16,0),(.062,.195,.065));hand=G.node(role+f'_hand{s}',parent=body);ball(hand,'palm','skin',(0,0,0),(.062,.075,.027))
  for j in range(4):ball(hand,'finger','skin',(-.037+j*.024,-.066,.005),(.012,.038-(abs(j-1)*.004),.012))
  ball(hand,'thumb','skin',(s*.058,-.012,.014),(.017,.038,.017));arms.append((upper,lower,hand))
  thigh=G.node(role+f'_thigh{s}',parent=body,pos=(s*.16,1.16,0));ball(thigh,'thigh','skin' if girl else 'pants',(0,-.25,0),(.115,.285,.12));shin=G.node(role+f'_shin{s}',parent=thigh,pos=(0,-.50,0));ball(shin,'shin','skin' if girl else 'pants',(0,-.23,0),(.079,.255,.084));foot=G.node(role+f'_foot{s}',parent=shin,pos=(0,-.47,.04));ball(foot,'sock','pants',(0,.04,0),(.081,.09,.08));ball(foot,'shoe','cream',(0,-.025,.08),(.112,.09,.20));boxnode(foot,'sole','sole',(0,-.092,.08),(.214,.034,.34))
  for j in range(3):boxnode(foot,'lace','white',(0,.04,.08+j*.032),(.11,.008,.009))
  legs.append((thigh,shin,foot))
 return dict(root=root,body=body,head=head,hair=hair,eyes=eyes,mouth=mouth,arms=arms,legs=legs,girl=girl)
A=make_character('artist',False);B=make_character('reader',True)
# Props have a shared transform used by the hand solver and the drawing surface.
book=G.node('reader_book');boxnode(book,'book_cover','book',(0,0,0),(.59,.034,.42));boxnode(book,'book_pages','paper',(0,.03,0),(.56,.03,.39))
board=G.node('artist_board');boxnode(board,'board_cover','teal',(0,0,-.014),(.63,.77,.022))
paper=G.node('flying_drawing')
paper_bends=[G.node('paper_bend_'+str(i),parent=paper,pos=(0,-.37+i*.74/8,0)) for i in range(9)]
# A recognizable drawn portrait is authored from the same head, fringe and barrette landmarks.
def drawing(parent,prefix):
 pos=[(-.30+i*.60/10,-.37+j*.74/18,0) for j in range(19) for i in range(11)];idx=[]
 for j in range(18):
  for i in range(10):a=j*11+i;idx.extend([a,a+1,a+12,a,a+12,a+11])
 geo=(pos,[(0,0,1)]*len(pos),idx);geom(parent,prefix+'_sheet','paper',geo)
 G.doc['materials'][M['paper']]['doubleSided']=True
 def ln(pts,r=.0018,mat='ink'):return curve(parent,prefix+'_pencil',mat,[(x,y,.0045) for x,y in pts],r)
 outline=[(-.095,.22),(-.117,.18),(-.12,.08),(-.095,.0),(-.04,-.055),(0,-.068),(.055,-.025),(.094,.03),(.11,.12),(.09,.20),(.04,.24),(-.03,.25),(-.095,.22)]
 ln(outline);ln([(-.11,.18),(-.115,-.085),(-.075,-.13),(-.06,.06)]);ln([(.085,.20),(.12,.06),(.10,-.11),(.055,-.085)])
 for i in range(5):x=-.087+i*.037;ln([(x,.215),(x+.018,.155),(x+.005,.115)])
 for s in (-1,1):
  ln([(s*.046-.025,.065),(s*.046,.076),(s*.046+.022,.068)],.0025);ln([(s*.046,.07),(s*.046,.043)],.003)
 ln([(-.017,-.013),(.008,-.02),(.025,-.01)])
 ln([(.08,.13),(.116,.15)],.003,'gold');ln([(-.055,-.071),(-.13,-.12),(-.15,-.26),(.14,-.26),(.11,-.12),(.04,-.07)])
 boxnode(parent,prefix+'_drawn_book','book',(0,-.176,.005),(.17,.078,.002),quat(0,0,-.12))
 for s in (-1,1):ln([(s*.115,-.13),(s*.095,-.19),(s*.04,-.18)])
 for i in range(11):x=-.11+i*.022;ln([(x,-.23),(x+.015,-.25)],.0007)
 for y in [-.29,-.31]:ln([(-.20,y),(.20,y)],.001)
 return parent
drawing(board,'sketchbook');drawing(paper,'flight')
pencil=G.node('pencil');geom(pencil,'pencil_wood','gold',loft([(-.11,.004,.004,0),(-.08,.008,.008,0),(.11,.008,.008,0)],8));geom(pencil,'pencil_tip','ink',loft([(-.125,.0005,.0005,0),(-.11,.004,.004,0)],8))
# Cubic interpolation preserves a gently curved flight instead of corner-to-corner travel.
flight_pts=[(-5,1.0,2.25),(-4.2,2.05,2.9),(-2.3,2.65,3.7),(0,1.65,4),(2.2,2.20,3.9),(4.1,.68,3.1),(5,.075,2.65)]
def catmull(u):
 u=clamp(u)*(len(flight_pts)-1);i=min(int(u),len(flight_pts)-2);f=u-i;p0=flight_pts[max(0,i-1)];p1=flight_pts[i];p2=flight_pts[i+1];p3=flight_pts[min(i+2,len(flight_pts)-1)]
 return tuple(.5*((2*b)+(-a+c)*f+(2*a-5*b+4*c-d)*f*f+(-a+3*b-3*c+d)*f*f*f) for a,b,c,d in zip(p0,p1,p2,p3))
def paper_pose(t):
 if t<12.5:return (-5,.96,2.15),quat(-math.pi/2,0,0)
 if t<21:
  u=smooth((t-12.5)/8.5);return catmull(u),quat(-1.2+math.sin(t*2.6)*.45,math.sin(t*1.7)*.5,math.sin(t*2.1)*.4)
 if t<22.7:return (5,.075,2.65),quat(-math.pi/2,0,.12)
 f=smooth((t-22.7)/1.3);return lerp((5,.075,2.65),(5,1.32,2.34),f),quat(-math.pi/2+(math.pi/2-.18)*f,0,.12-.16*f)
def arm_pose(shoulder,target,side):
 d=sub(target,shoulder);dist=min(length(d),.705);axis=norm(d);a=.36;b=.36;x=(a*a-b*b+dist*dist)/(2*max(.001,dist));h=math.sqrt(max(0,a*a-x*x));pole=(side*.85,-.75,-.15);perp=norm(sub(pole,mul(axis,dot(pole,axis))));elbow=add(shoulder,add(mul(axis,x),mul(perp,h)));return elbow,between((0,-1,0),sub(elbow,shoulder)),between((0,-1,0),sub(target,elbow))
times=[i/12 for i in range(361)];channels={}
def key(node,path,value):channels.setdefault((node,path),[]).append(value)
for t in times:
 for i,node in enumerate(paper_bends):
  amp=.06 if 13<t<21 else .004
  key(node,'rotation',quat(math.sin(t*6+i*.45)*amp,0,0))
 pp,pq=paper_pose(t);key(paper,'translation',pp);key(paper,'rotation',pq);key(paper,'scale',(1,1,1) if t>=12.5 else (.001,.001,.001))
 boardpos=(-5,.96,2.15);boardq=quat(-math.pi/2,0,.06);key(board,'translation',boardpos);key(board,'rotation',boardq)
 key(book,'translation',(5,.97,2.17));key(book,'rotation',quat(.1,0,0));key(book,'scale',(1,1,1) if t<21.5 else (.001,.001,.001))
 for c in (A,B):
  girl=c['girl'];stand=smooth((t-(21.5 if girl else 15.1))/(1.1 if girl else .85));run=(smooth((t-15.7)/.5)*(1-smooth((t-25.9)/1.1))) if not girl else 0
  x=5 if girl else -5+8.1*smooth((t-16)/11)
  z=1.65+(.45 if girl else 1.45)*stand;ang=(-.50*smooth((t-26)/1)) if girl else (math.pi/2*stand if t<26 else 1.0)
  rootpos=(x,0,z);rq=quat(0,ang,0);key(c['root'],'translation',rootpos);key(c['root'],'rotation',rq)
  dy=-.29*(1-stand)+abs(math.sin(t*11))*run*.045;key(c['body'],'translation',(0,dy,0))
  headturn=(-.2 if girl else (.32 if t%3<.65 else 0));headbend=.10
  if t>=24 and girl:headturn=-.25*smooth((t-25)/1.5);headbend=.13-.16*smooth((t-25)/2)
  if t>=27 and not girl:headturn=.10;headbend=.05
  key(c['head'],'rotation',quat(headbend,headturn,0));key(c['hair'],'rotation',quat(.007*math.sin(t*2),0,.01*math.sin(t*2.3)*(2 if 12<t<21 else 1)))
  blink=.13 if t%4.3>4.16 else 1
  for e in c['eyes']:key(e,'scale',(1,blink,1))
  key(c['mouth'],'scale',(1,1+.4*smooth((t-25)/2) if girl else 1,1))
  for i,(thigh,shin,foot) in enumerate(c['legs']):
   phase=t*11+i*math.pi;hip=-1.48*(1-stand)+math.sin(phase)*.66*run;knee=1.52*(1-stand)+max(0,-math.sin(phase))*.9*run
   key(thigh,'rotation',quat(hip,0,0));key(shin,'rotation',quat(knee,0,0));key(foot,'rotation',quat(-hip-knee if not run else -.1,0,0))
  for i,(upper,lower,hand) in enumerate(c['arms']):
   side=-1 if i==0 else 1;shoulder=(side*.345,1.83,0)
   if girl and t>=22.7:
    wp=add(pp,rotate((side*.255,-.22,.02),pq));target=rotate(sub(wp,add(rootpos,(0,dy,0))),quat(0,-ang,0))
   elif t<(21.5 if girl else 12.5):
    wp=(x+side*.25,.98,2.12) if girl else (x+side*.21,1.005,2.13+(.025*math.sin(t*13) if i else 0));target=rotate(sub(wp,add(rootpos,(0,dy,0))),quat(0,-ang,0))
   elif girl and t<24:
    target=(side*.22,1.1-.45*math.sin(smooth((t-21.5)/2.5)*math.pi),.5)
   elif run and i==1:target=(.27,1.60,.58)
   else:target=(side*.39,1.18+run*.13*math.sin(t*11+i*math.pi),.1+run*.24*math.sin(t*11+i*math.pi))
   elbow,uq,lq=arm_pose(shoulder,target,side);key(upper,'translation',shoulder);key(upper,'rotation',uq);key(lower,'translation',elbow);key(lower,'rotation',lq);key(hand,'translation',target);key(hand,'rotation',quat(-.8 if t<12.5 or girl and t>=22.7 else 0,0,0))
   if not girl and i==1:
    tip=add(add(rootpos,(0,dy,0)),rotate(target,rq));key(pencil,'translation',add(tip,(0,.06,.005)));key(pencil,'rotation',quat(.18,0,-.15));key(pencil,'scale',(1,1,1) if t<12.5 else (.001,.001,.001))
for (node,path),values in channels.items():G.channel(node,path,values,times,step=node!=paper and node not in paper_bends)
G.save('actors.glb')
print('actors',len(G.doc['nodes']),len(G.bin))
# Static scenery is merged by material, rather than thousands of runtime draw calls.
E=GLB();em={};batches={}
for name,color,emission in [('grass','#A6B184',.2),('path','#E1D8BF',.18),('tile1','#D3CBB5',.16),('tile2','#E8DEC7',.18),('bark','#81705B',.12),('wood','#AE8B62',.13),('iron','#4B5F58',.1),('lamp','#FFF0B7',.55),('leaf0','#728960',.18),('leaf1','#8FA66C',.18),('leaf2','#AEC17D',.18),('leaf3','#CBD291',.2),('leaf4','#D9DBA0',.2),('flower','#FFF7DF',.3),('city0','#CCDAD5',.4),('city1','#D5DFD8',.4),('dapple','#B9BEA1',.18)]:em[name]=E.material(name,color,emission)
def static(mat,geo,pos=(0,0,0),scale=(1,1,1),q=(0,0,0,1)):
 p,n,ind=geo;bp,bn,bi=batches.setdefault(mat,([],[],[]));off=len(bp)
 bp.extend(add(pos,rotate(tuple(a*b for a,b in zip(v,scale)),q)) for v in p);bn.extend(norm(rotate(tuple(a/b for a,b in zip(v,scale)),q)) for v in n);bi.extend(i+off for i in ind)
C=cube();leafgeo=ell(n=7,rings=4);shrubgeo=ell(n=9,rings=6)
def eb(mat,pos,size,q=(0,0,0,1)):static(mat,C,pos,size,q)
def branch(a,b,r1,r2,mat='bark'):
 l=length(sub(b,a));static(mat,loft([(-l/2,r1,r1,0),(l/2,r2,r2,0)],8),lerp(a,b,.5),q=between((0,1,0),sub(b,a)))
eb('grass',(0,-.19,-6),(100,.30,90));eb('path',(0,-.06,3.8),(64,.12,6.4))
for i in range(-25,26):
 for j in range(8):
  if rng.random()<.63:eb('tile1' if rng.random()<.55 else 'tile2',(i*1.2+(j%2)*.6,.012,.80+j*.76),(1.175,.014,.735))
for z in [.40,7.05]:eb('tile1',(0,.06,z),(64,.12,.16))
for x in [-5,5,-17,17]:
 for j in range(4):eb('wood',(x,.85,1.43+j*.16),(3.25,.075,.125))
 for j in range(4):eb('wood',(x,1.14+j*.15,1.20),(3.25,.09,.09))
 for s in (-1,1):
  xx=x+s*1.31
  for z in [1.37,1.86]:branch((xx,.04,z),(xx,.86,z),.037,.037,'iron')
  branch((xx,.68,1.18),(xx,1.72,1.18),.032,.032,'iron');branch((xx,1.28,1.2),(xx,1.28,1.95),.03,.03,'iron')
for i in range(20):
 x=(i-10)*3.3;h=rng.uniform(3.5,7.5);eb('city'+str(i%2),(x,h/2,-35-rng.random()*8),(rng.uniform(1.3,2.4),h,1.4))
for i,(x,z) in enumerate([(x,-3.5+rng.uniform(-1,1)) for x in [-15,-10,-5,0,5,10,15,20]]+[(x,9.5) for x in [-14,-8,0,8,15]]+[(x,-12) for x in [-18,-9,1,10,19]]):
 h=rng.uniform(3.6,4.7);top=(x+.18,h,z);branch((x,0,z),top,.19,.075)
 for b in range(5):
  a=b/5*TAU+rng.random();tip=(x+math.sin(a)*1.7,h+.2+rng.random(),z+math.cos(a)*1.5);branch((x,h*.65,z),tip,.065,.015)
  for j in range(54):
   p=add(tip,(rng.uniform(-1.65,1.65),rng.uniform(-.6,.65),rng.uniform(-1.4,1.4)));size=(rng.uniform(.13,.32),rng.uniform(.035,.085),rng.uniform(.13,.3))
   static('leaf'+str(rng.randrange(5)),leafgeo,p,size,quat(rng.uniform(-.7,.7),rng.random()*TAU,rng.uniform(-.8,.8)))
# Mid-distance understory closes the empty horizon with layered small leaves.
for i in range(130):
 x=rng.uniform(-29,29);z=rng.uniform(-13,-8);y=rng.uniform(.8,2.7)
 static('leaf'+str(rng.randrange(4)),shrubgeo,(x,y,z),(rng.uniform(.4,.9),rng.uniform(.3,.6),rng.uniform(.4,.8)))
 for j in range(14):static('leaf'+str(rng.randrange(5)),leafgeo,(x+rng.uniform(-.8,.8),y+rng.uniform(-.5,.6),z+rng.uniform(-.5,.5)),(.17,.048,.19),quat(.4,rng.random()*TAU,.4))
for i in range(410):
 x=rng.uniform(-28,28);z=rng.choice([-.30,-1.0,-6,7.8])+rng.uniform(-.4,.4);static('leaf'+str(rng.randrange(4)),shrubgeo,(x,rng.uniform(.18,.44),z),(rng.uniform(.25,.65),rng.uniform(.20,.43),rng.uniform(.25,.50)))
 if i%3==0:
  for j in range(3):static('flower',leafgeo,(x+rng.uniform(-.3,.3),.65+rng.uniform(-.1,.1),z+rng.uniform(-.25,.25)),(.043,.025,.043))
for i in range(430):
 # Painted irregular dapple patches supplement directional shadows at animatic cost.
 x=rng.uniform(-27,27);z=rng.uniform(.7,6.8);static('dapple',leafgeo,(x,.025,z),(rng.uniform(.05,.18),.001,rng.uniform(.05,.21)),quat(0,rng.random()*TAU,0))
for x in [-12,-1,11,23]:
 branch((x,0,.12),(x,3.7,.12),.047,.027,'iron');eb('lamp',(x,3.77,.12),(.22,.40,.22));eb('iron',(x,4.0,.12),(.33,.06,.33))
 for s in (-1,1):
  for r in (-1,1):branch((x+s*.115,3.56,.12+r*.115),(x+s*.115,3.98,.12+r*.115),.008,.008,'iron')
for mat,geo in batches.items():E.node(mat,E.mesh(geo,em[mat],mat))
E.save('park.glb');print('park triangles',sum(len(v[2])//3 for v in batches.values()))
# MotionLoom owns the camera cuts, lighting, CEL pass, atmosphere and video export.
shots=[('S01',0,3,(-11,3.6,12),(0,1.65,.2),48),('S02',3,6,(-7.6,2.35,6.0),(-5,1.53,1.9),34),('S03',6,9,(7.0,2.25,5.6),(5,1.6,1.75),32),('S04',9,12,(-4.7,2.30,2.9),(-5,.96,2.15),34),('S05',12,14,(-4.0,1.72,3.4),(-4.85,1.15,2.25),36),('S06',14,16,(-2.3,3.1,6),(-2.4,2.2,3.3),35),('S07A',16,18,(-4.4,2.0,8.3),(-3.7,1.35,3.0),42),('S07B',18,19.5,(1.2,1.1,6.3),(-2.8,1.5,3.1),45),('S07C',19.5,21,(4,8,7),(3,1,2.6),43),('S08',21,24,(6.3,.5,4.4),(5,.3,2.5),38),('S09A',24,25.2,(5,1.65,4.1),(5,1.34,2.34),32),('S09B',25.2,27,(4.45,2.34,4.1),(5,2.25,2.0),28),('S10',27,30,(4,2.2,8.3),(4.05,1.70,2.55),36)]
cam=[];an=[]
def ak(node,prop,values):
 an.append(f'<AnimationTarget node="{node}" property="{prop}">')
 for t,v in values:an.append(f'<Key time="{t:g}s" value="{json.dumps(v,separators=(",",":")) if isinstance(v,(tuple,list)) else v}" />')
 an.append('</AnimationTarget>')
for n,s,e,pos,target,fov in shots:
 dist=length(sub(pos,target));cam.append(f'<Camera3D id="{n}" position={{{json.dumps(pos)}}} target={{{json.dumps(target)}}} fov="{fov}" depthOfField="true" focusDistance="{dist:.4f}" fStop="4.5" maxBlur="1.0" />')
ak('MAIN2','activeCamera',[(s,n) for n,s,*_ in shots]);ak('S01','position',[(0,(-11,3.6,12)),(3,(-10.4,3.5,11.4))]);ak('S02','position',[(3,(-7.6,2.35,6)),(6,(-7.4,2.32,5.8))])
for n,s,e,*_ in shots:
 if n=='S06':
  ts=[14+i/12 for i in range(25)];ak(n,'position',[(t,add(paper_pose(t)[0],(.3,.85,2.4))) for t in ts]);ak(n,'target',[(t,paper_pose(t)[0]) for t in ts])
 if n=='S07A':
  ts=[16,17,18];ak(n,'position',[(t,(-5+8.1*smooth((t-16)/11)-1,2,8.3)) for t in ts]);ak(n,'target',[(t,(-5+8.1*smooth((t-16)/11)+.7,1.35,3)) for t in ts])
ak('S08','position',[(21,(6.3,.5,4.4)),(22.5,(6.3,.5,4.4)),(24,(6.3,1.8,4.4))]);ak('S08','target',[(21,(5,.3,2.5)),(22.5,(5,.3,2.5)),(24,(5,1.35,2.2))]);ak('S10','position',[(27,(4,2.2,8.3)),(30,(4,2.2,8.0))])
script='''<!-- MAIN2: original procedural characters, native MotionLoom CEL; MAIN is untouched. -->
<Graph fps={24} duration="30s" size={[1280,720]}>
<RenderStyle id="film_cel">
<SurfaceStyle shading="cel" shadingSteps="3" shadowColor="#BBC3B3" specular="0.025" />
<OutlineStyle enabled="true" color="#464A46" width="0.45" method="geometry" distanceMode="screen" />
<LightingStyle ambientIntensity="0.85" ambientColor="#F2EBCF" shadowStyle="soft" />
<PostStyle toneMapping="aces" exposure="1.20" saturation="1.04" contrast="1.01" bloomThreshold="1.15" bloomIntensity="0.07" />
</RenderStyle>
<Assets>
<ModelAsset id="park_asset" src="main2/park.glb" />
<ModelAsset id="actors_asset" src="main2/actors.glb" />
</Assets>
<Background color="#C4DFE8" />
<Scene id="MAIN2" renderStyle="film_cel">
<Timeline>
<Track id="film" space="3d">
<Sequence from="0s" duration="30s">
<CompositeGroup id="stage" space="3d" depth="true">
'''+ '\n'.join(cam)+'''
<DirectionalLight direction={[.55,-1,.3]} color="#FFF0BC" intensity="2.7" castShadow="true" shadowStrength="0.45" />
<DirectionalLight direction={[-.4,-.15,-1]} color="#E1F0E8" intensity="0.65" />
<AtmosphereFog id="morning_air" scatteringColor="#DAE5DE" density="0.022" affectEnvironment="false" />
<Model id="park" asset="park_asset" castShadow="true" receiveShadow="true" />
<Model id="actors" asset="actors_asset" castShadow="true" receiveShadow="true">
<Play clip="film" loop="false" speed="1" />
</Model>
</CompositeGroup>
</Sequence>
</Track>
</Timeline>
</Scene>
'''+ '\n'.join(an)+'''
<Present from="MAIN2" />
</Graph>
'''
(P.parent/'main2.motionloom').write_text(script)
(P/'shots.json').write_text(json.dumps([dict(id=n,start=s,end=e,camera=pos,target=target,fov=fov,frame=round((s+e)/2*24)) for n,s,e,pos,target,fov in shots],indent=2))
