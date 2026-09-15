# =========================================
# =========================================
# showcase/s-000095/authoring/native-v2/build_native.py
"""Author native MotionLoom DSL with Python standard-library arithmetic only.
No imported geometry, Blender, mesh libraries, or external renderer is used.
"""
import math, json, pathlib, collections
from math import sin, cos, pi, sqrt
ROOT=pathlib.Path(__file__).resolve().parent
SHOW=ROOT.parent.parent
ASSETS=[]; MODELS=[]; MESHES={}
def vec(v): return '{['+','.join(f'{x:.7f}' for x in v)+']}'
def mesh(name,vs,fs,uv=None,material='skin',sub=1):
    # Weld coincident fin-edge vertices and omit collapsed seam faces.
    unique={}; newvs=[]; newuv=[]; remap={}
    for i,pos in enumerate(vs):
        key=tuple(round(x,7) for x in pos)
        if key not in unique:
            unique[key]=len(newvs);newvs.append(pos);newuv.append(uv[i] if uv else (.25,.25))
        remap[i]=unique[key]
    cleaned=[]
    for face in fs:
        f=list(dict.fromkeys(remap[i] for i in face))
        if len(f)>=3:cleaned.append(f)
    vs,fs,uv=newvs,cleaned,newuv
    # Enforce consistent winding across shared edges without a mesh library.
    edges=collections.defaultdict(list)
    for i,f in enumerate(fs):
        for a,b in zip(f,f[1:]+f[:1]):edges[tuple(sorted((a,b)))].append((i,a,b))
    flips={}
    for start in range(len(fs)):
        if start in flips:continue
        flips[start]=False; todo=[start]
        while todo:
            i=todo.pop(); f=fs[i]
            for a,b in zip(f,f[1:]+f[:1]):
                for j,c,d in edges[tuple(sorted((a,b)))]:
                    if j not in flips:flips[j]=flips[i] ^ (a==c); todo.append(j)
    fs=[list(reversed(f)) if flips[i] else list(f) for i,f in enumerate(fs)]
    volume=0.0
    for f in fs:
        a=vs[f[0]]
        for i in range(1,len(f)-1):
            b=vs[f[i]];c=vs[f[i+1]]
            volume+=a[0]*(b[1]*c[2]-b[2]*c[1])+a[1]*(b[2]*c[0]-b[0]*c[2])+a[2]*(b[0]*c[1]-b[1]*c[0])
    if volume<0:fs=[f[::-1] for f in fs]
    MESHES[name]={'vertices':vs,'faces':fs,'uv':uv,'material':material}
    lines=[f'<MeshAsset id="{name}" material="{material}" subdivision="{sub}" subdivisionScheme="catmullClark">']
    for i,v in enumerate(vs):lines.append(f'  <Vertex position={vec(v)} uv={vec(uv[i] if uv else (.25,.25))} />')
    lines.extend('  <Face indices={['+','.join(map(str,f))+']} />' for f in fs); lines.append('</MeshAsset>'); ASSETS.append('\n'.join(lines))
    MODELS.append(f'<Model id="{name}_model" asset="{name}" castShadow="true" />')
def ellipsoid(name,pos,radii,material):
    ASSETS.append(f'<PrimitiveAsset id="{name}" shape="ellipsoid" radii={vec(radii)} segments="48" rings="24" material="{material}" />')
    MODELS.append(f'<Model id="{name}_model" asset="{name}" position={vec(pos)} castShadow="true" />')
def photo(px,py):return (px/1448,py/1086)
# X is longitudinal, Y is dorsal and Z is the left flank. The photograph is a UV reference, not geometry.
S=[(-3.68,.010,.014,.030,219,225),(-3.55,.15,.14,.01,207,243),(-3.32,.32,.31,-.035,198,267),(-3.0,.46,.42,-.035,186,296),(-2.6,.59,.51,0,170,307),(-2.1,.69,.64,-.005,156,318),(-1.55,.75,.735,-.01,145,323),(-1.0,.745,.735,-.015,145,318),(-.4,.68,.66,-.015,158,307),(.2,.57,.555,-.005,173,292),(.85,.425,.415,0,191,275),(1.5,.285,.28,0,208,258),(2.1,.18,.18,0,217,246),(2.65,.105,.102,0,220,240),(3.06,.085,.087,0,223,236),(3.20,.073,.095,0,219,241)]
def interp(x,k):
    for a,b in zip(S,S[1:]):
        if a[0]<=x<=b[0]:t=(x-a[0])/(b[0]-a[0]); return a[k]*(1-t)+b[k]*t
    return S[0 if x<S[0][0] else -1][k]
def catmull(rows,steps=5):
    out=[]
    for j in range(len(rows)-1):
        for it in range(steps):
            t=it/steps; vals=[]
            for k in range(len(rows[0])):
                a,b,c,d=[rows[max(0,min(len(rows)-1,j+off))][k] for off in [-1,0,1,2]]
                vals.append(.5*(2*b+(-a+c)*t+(2*a-5*b+4*c-d)*t*t+(-a+3*b-3*c+d)*t*t*t))
            out.append(vals)
    return out+[rows[-1]]
# Dense, explicit body rings are smooth in the native renderer even without fitting-time subdivision.
vs=[]; uv=[]; fs=[]; rings=catmull([s[:4] for s in S],6); N=64
for x,w,h,c in rings:
    for j in range(N):
        a=2*pi*j/N; y=c+h*cos(a); z=w*sin(a); vs.append((x,y,z))
        # Sampling inside the silhouette avoids projecting the reference's background onto the back.
        top=interp(x,4)+10; bottom=interp(x,5)-5; py=(top+bottom)/2-(bottom-top)/2*cos(a)
        px=14+(x+3.68)/7.83*800
        if x < -1.85:
            # A clean skin patch prevents photograph eyes/mouth from duplicating the explicit anatomy.
            weight=min(1.0,(-1.85-x)/.35)
            px=px*(1-weight)+(305+12*(x+3.68))*weight
            clean_y=235-100*y
            py=py*(1-weight)+clean_y*weight
        if cos(a)<-.45:
            px=470+15*sin(a)**2;py=293+3*sin(x*2)
        uv.append(photo(px,py))
for r in range(len(rings)-1):
    for j in range(N):
        f=[r*N+j,(r+1)*N+j,(r+1)*N+(j+1)%N,r*N+(j+1)%N]
        cx,cy,cz=[sum(vs[i][k] for i in f)/4 for k in range(3)]
        # Omit a narrow set of lower snout faces; the dark recessed shell closes the visible mouth.
        cut=((cx+3.24)/.66)**2+((cy+.265)/.087)**2+(cz/.41)**2 < 1
        if not cut:fs.append(f)
# Tiny end rings are capped with fans; all authored faces remain triangles or quads.
for r in [0,len(rings)-1]:
    pole=len(vs); x,w,h,c=rings[r];vs.append((x,c,0));uv.append(photo(305,235-100*c) if r==0 else photo(715,226))
    for j in range(N):fs.append([pole,r*N+j,r*N+(j+1)%N])
# Separate UV islands prevent the side photograph from pinching into a polar pattern on the nose.
for label,front in [('shark_head',True),('shark_body',False)]:
    selected=[f for f in fs if (sum(vs[i][0] for i in f)/len(f)<-1.85)==front]
    indices=sorted({i for f in selected for i in f}); index={old:new for new,old in enumerate(indices)}
    coords=[vs[i] for i in indices]
    mapped=[photo(1139-160*vs[i][2],250-160*vs[i][1]) if front else uv[i] for i in indices]
    mesh(label,coords,[[index[i] for i in f] for f in selected],mapped)
# Native loft primitives add mouth lining and embedded eye surfaces.
ellipsoid('oral_shadow',(-3.10,-.266,0),(.23,.068,.35),'oral')
# Fins are independent lenticular surfaces, with a narrow leading and trailing seam.
def fin(name,rows,plane='dorsal',sign=1,tex='dorsal'):
    rows=catmull(rows,3); v=[]; uvs=[]; faces=[]; K=12
    for side in [1,-1]:
        for r,(lead,trail,span,height,thick) in enumerate(rows):
            for k in range(K+1):
                t=k/K; x=lead+(trail-lead)*t; bulge=sin(pi*t)**.75*thick*side
                if plane=='lateral':p=(x,height+bulge,sign*span)
                else:p=(x,span,bulge)
                v.append(p)
                if tex=='pectoral':px=255+115*(span-.6)/1.55+35*(t-.5);py=278+104*(span-.6)/1.55
                elif tex=='tail':px=14+(x+3.68)/7.83*800;py=228-span*98
                else:px=354+60*t+20*r/(len(rows)-1);py=145-75*r/(len(rows)-1)
                if plane=='lateral' and side<0:px=470+15*t;py=293+3*sin(pi*t)
                uvs.append(photo(px,py))
    R=len(rows); stride=K+1; half=R*stride
    for layer in range(2):
        for r in range(R-1):
            for k in range(K):
                a=layer*half+r*stride+k;f=[a,a+1,a+stride+1,a+stride];faces.append(f if layer==0 else f[::-1])
    for r in range(R-1):
        for k in [0,K]:a=r*stride+k;b=(r+1)*stride+k;faces.append([a,b,b+half,a+half])
    for r in [0,R-1]:
        for k in range(K):a=r*stride+k;faces.append([a,a+half,a+half+1,a+1])
    mesh(name,v,faces,uvs)
fin('dorsal',[(-.68,.65,.55,0,.12),(-.57,.60,.78,0,.12),(-.35,.43,1.06,0,.085),(-.13,.36,1.34,0,.05),(.09,.35,1.53,0,.025),(.26,.36,1.61,0,.007),(.345,.36,1.615,0,.001)])
for sign,label in [(1,'left'),(-1,'right')]:
    fin('pectoral_'+label,[(-1.48,-.50,.57,-.35,.10),(-1.45,-.47,.77,-.40,.115),(-1.31,-.42,1.04,-.49,.09),(-1.08,-.29,1.40,-.66,.064),(-.78,-.12,1.73,-.86,.038),(-.44,.06,1.99,-1.03,.016),(-.11,.14,2.12,-1.10,.004),(.105,.14,2.14,-1.105,.001)],'lateral',sign,'pectoral')
    fin('pelvic_'+label,[(1.05,1.55,.23,-.20,.045),(1.15,1.67,.40,-.27,.04),(1.48,1.82,.65,-.36,.015),(1.79,1.84,.72,-.39,.002)],'lateral',sign,'pectoral')
fin('dorsal_second',[(1.90,2.33,.15,0,.036),(2.02,2.22,.30,0,.025),(2.16,2.23,.40,0,.007),(2.22,2.23,.415,0,.001)])
fin('anal',[(2.04,2.44,-.13,0,.025),(2.20,2.39,-.30,0,.02),(2.38,2.43,-.36,0,.002)])
fin('tail_upper',[(2.85,3.38,-.015,0,.085),(2.94,3.46,.24,0,.073),(3.09,3.48,.55,0,.060),(3.28,3.58,.88,0,.044),(3.51,3.79,1.19,0,.028),(3.78,3.92,1.40,0,.012),(4.02,4.04,1.49,0,.001)],tex='tail')
fin('tail_lower',[(2.90,3.39,.055,0,.08),(3.04,3.43,-.25,0,.067),(3.22,3.50,-.51,0,.046),(3.44,3.65,-.79,0,.026),(3.69,3.85,-.99,0,.01),(3.87,3.89,-1.035,0,.001)],tex='tail')
# Tube meshes are generated directly as ordinary MeshAsset rings, not external curves.
def tube(name,points,radius,material):
    v=[]; f=[]; K=8
    for i,p in enumerate(points):
        before=points[max(0,i-1)]; after=points[min(len(points)-1,i+1)]; d=[after[k]-before[k] for k in range(3)]; norm=sqrt(sum(x*x for x in d));d=[x/norm for x in d]
        ref=[0,0,1] if abs(d[2])<.9 else [0,1,0]
        a=[d[1]*ref[2]-d[2]*ref[1],d[2]*ref[0]-d[0]*ref[2],d[0]*ref[1]-d[1]*ref[0]]; norm=sqrt(sum(x*x for x in a));a=[x/norm for x in a]
        b=[d[1]*a[2]-d[2]*a[1],d[2]*a[0]-d[0]*a[2],d[0]*a[1]-d[1]*a[0]]
        for j in range(K):v.append(tuple(p[k]+radius*(cos(2*pi*j/K)*a[k]+sin(2*pi*j/K)*b[k]) for k in range(3)))
    for i in range(len(points)-1):
        for j in range(K):a=i*K+j;f.append([a,i*K+(j+1)%K,(i+1)*K+(j+1)%K,a+K])
    mesh(name,v,f,material=material,sub=1)
for sign,label in [(1,'left'),(-1,'right')]:
    ellipsoid('socket_'+label,(-2.99,.205,sign*.389),(.078,.075,.025),'rim')
    ellipsoid('eye_'+label,(-2.996,.206,sign*.407),(.056,.055,.024),'eye')
    ellipsoid('nostril_'+label,(-3.36,-.065,sign*.264),(.031,.015,.009),'oral')
    for j in range(5):
        points=[]
        for i in range(18):
            t=i/17;x=-1.79+j*.115-.045*sin(pi*t)+.065*t*t;y=.30-.78*t;h=interp(x,2);w=interp(x,1);c=interp(x,3)
            z=sign*(w*sqrt(max(.02,1-((y-c)/h)**2))+.004);points.append((x,y,z))
        tube('gill_'+label+'_'+str(j+1),points,.007,'gill')
# Two curved gumlines and individually pointed teeth remain native polygon assets.
for upper in [True,False]:
    pts=[]
    for i in range(39):
        t=-1.43+2.86*i/38;pts.append((-2.94-.362*cos(t),(-.198-.030*cos(t) if upper else -.283-.063*cos(t)),.382*sin(t)))
    tube('gum_'+str(upper).lower(),pts,.010,'gum')
    for i in range(23):
        t=-1.38+2.76*i/22;x=-2.94-.359*cos(t);z=.371*sin(t);y=(-.198-.030*cos(t) if upper else -.283-.063*cos(t));h=(.059 if upper else .052)*(1-.25*abs(sin(t)));w=.038;direction=-1 if upper else 1
        tangent=(sin(t),0,cos(t)); normal=(-cos(t),0,sin(t));c=(x,y,z)
        v=[tuple(c[k]+sgn*w/2*tangent[k]+dep*normal[k] for k in range(3)) for sgn,dep in [(-1,-.007),(1,-.007),(-1,.009),(1,.009)]]
        v.append((x+.009,y+direction*h,z));mesh(('upper' if upper else 'lower')+'_tooth_'+str(i),v,[[0,1,4],[3,2,4],[2,0,4],[1,3,4],[0,2,3,1]],material='enamel',sub=0)
# Cameras and lights use only existing scene API nodes. A turntable moves the camera around the assembled shark.
MATERIALS='''<ImageAsset id="shark_reference" src="texture/source-composite.png" colorSpace="srgb" />
<MaterialAsset id="skin" shading="pbr" baseColor="#F0F1F2" baseColorTexture="shark_reference" roughness="0.57" specular="0.22" metallic="0" />
<MaterialAsset id="eye" shading="pbr" baseColor="#050708" roughness="0.16" specular="0.50" />
<MaterialAsset id="rim" shading="pbr" baseColor="#313A40" roughness="0.50" />
<MaterialAsset id="oral" shading="pbr" baseColor="#130909" roughness="0.85" />
<MaterialAsset id="gill" shading="pbr" baseColor="#252A29" roughness="0.75" />
<MaterialAsset id="gum" shading="pbr" baseColor="#845F57" roughness="0.63" />
<MaterialAsset id="enamel" shading="pbr" baseColor="#E2DDC9" roughness="0.38" />'''
CAMS={'side':((0,0,16),(.1,.15,0)), 'beauty':((-8,3.0,15),(-.1,.1,0)), 'front':((-11,0,0),(0,0,0)), 'top':((0,16,.0001),(.1,0,0)), 'bottom':((0,-16,.0001),(.1,0,0))}
def scene(view='beauty',texture=True):
    pos,target=CAMS[view]
    up=(0,0,-1) if view=='top' else ((0,0,1) if view=='bottom' else (0,1,0))
    materials=MATERIALS if texture else MATERIALS.replace(' baseColorTexture="shark_reference"','')
    return '''<!-- ========================================= -->
<!-- ========================================= -->
<!-- showcase/s-000095/main.motionloom -->
<Graph fps={24} duration="8s" size={[1200,800]} renderSize={[1200,800]}>
<RenderStyle id="native_studio">
 <SurfaceStyle shading="physical" specular="0.30" />
 <LightingStyle ambientIntensity="0.65" ambientColor="#D5DFE9" shadowStyle="soft" />
 <PostStyle toneMapping="aces" exposure="1.0" saturation="0.9" contrast="1.0" bloomIntensity="0" />
 <AntiAliasingStyle method="msaa" quality="high" fallback="smaa" />
</RenderStyle>
<Assets>\n'''+materials+'\n'+'\n'.join(ASSETS)+'''\n</Assets>
<Background color="#A7ACB1" />
<Scene id="S95Shark" renderStyle="native_studio">
<Timeline>
<Track id="world" space="3d">
<Sequence from="0s" duration="8s" out="hold">
<CompositeGroup id="stage" space="3d" depth="true" format="rgba16f">
'''+f'<Camera3D id="camera" position={vec(pos)} target={vec(target)} up={vec(up)} fov="22" depthOfField="false" />'+'''
<RectAreaLight position={[-4,6,5]} direction={[0.4,-0.6,-0.7]} width="7" height="7" color="#F1F4F7" intensity="3.0" />
<RectAreaLight position={[-2,-4,3]} direction={[0.1,0.7,-0.6]} width="5" height="5" color="#E9ECF3" intensity="1.6" />
<DirectionalLight direction={[-0.3,-0.6,-0.5]} color="#FFFFFF" intensity="0.9" castShadow="true" shadowStrength="0.35" />
<DirectionalLight direction={[0,1,-0.2]} color="#F2F0EA" intensity="1.0" castShadow="false" />
<AmbientOcclusion radius="0.12" intensity="0.18" />
'''+ '\n'.join(MODELS)+'''\n</CompositeGroup>
</Sequence>
</Track>
</Timeline>
</Scene>
<Present from="S95Shark" />
</Graph>\n'''
if __name__=='__main__':
    # Preview scripts live beside main so the relative reference asset resolves identically.
    for name in CAMS:(SHOW/f'preview-{name}.motionloom').write_text(scene(name))
    (SHOW/'preview-clay.motionloom').write_text(scene('beauty',False))
    (SHOW/'main.motionloom').write_text(scene('beauty'))
    (ROOT/'mesh-index.json').write_text(json.dumps({k:{'vertices':len(v['vertices']),'faces':len(v['faces'])} for k,v in MESHES.items()},indent=2))
    print('Native MotionLoom assets:',len(ASSETS),'mesh vertices:',sum(len(m['vertices']) for m in MESHES.values()))
