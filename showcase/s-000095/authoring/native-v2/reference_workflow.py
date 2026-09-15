# =========================================
# =========================================
# showcase/s-000095/authoring/native-v2/reference_workflow.py
"""Prepare native API requests; no third-party geometry or image packages."""
import json, pathlib, uuid, subprocess, math
import build_native as b
ROOT=b.ROOT; SHOW=b.SHOW
REPO=SHOW.parents[2]; BIN=REPO/'anica/target/debug/examples'
def dump(p,x):p.parent.mkdir(parents=True,exist_ok=True);p.write_text(json.dumps(x,indent=2))
# A neutral aggregate proxy measures the complete skin silhouette. The visible scene remains a native part assembly.
keys=['shark_head','shark_body','dorsal','pectoral_left','pectoral_right','pelvic_left','pelvic_right','dorsal_second','anal','tail_upper','tail_lower']
v=[];f=[];offsets={}
for key in keys:
    offsets[key]=len(v);m=b.MESHES[key];v.extend(m['vertices']);f.extend([[i+offsets[key] for i in face] for face in m['faces']])
def near(key,pos):
    pts=b.MESHES[key]['vertices'];return offsets[key]+min(range(len(pts)),key=lambda i:sum((pts[i][k]-pos[k])**2 for k in range(3)))
def feature(name,key,pos,xy):return {'id':name,'kind':'point','points':[xy],'semanticLabel':name,'binding':{'type':'vertex','vertex':near(key,pos)},'confidence':.8,'snapRadius':3}
FEATURES={
'left':[feature('snout','shark_head',(-3.68,.03,0),[11,226]),feature('dorsal_tip','dorsal',(.35,1.61,0),[419,65]),feature('pectoral_tip','pectoral_left',(.13,-1.1,2.14),[370,390]),feature('tail_upper','tail_upper',(4.04,1.49,0),[808,90]),feature('tail_lower','tail_lower',(3.89,-1.035,0),[790,334])],
'front':[feature('snout','shark_head',(-3.68,.03,0),[372,204]),feature('dorsal_tip','dorsal',(.35,1.61,0),[372,10]),feature('pectoral_left','pectoral_left',(.13,-1.1,2.14),[629,399]),feature('pectoral_right','pectoral_right',(.13,-1.1,-2.14),[113,399])],
# The two lateral fins in the top panel are pectorals, not a dorsal fin.
 'top':[feature('snout','shark_head',(-3.68,.03,0),[46,204]),feature('pectoral_upper','pectoral_right',(.13,-1.1,-2.14),[358,12]),feature('pectoral_lower','pectoral_left',(.13,-1.1,2.14),[342,414])],
'bottom':[feature('snout','shark_head',(-3.68,.03,0),[44,213]),feature('pectoral_upper','pectoral_left',(.13,-1.1,2.14),[333,14]),feature('pectoral_lower','pectoral_right',(.13,-1.1,-2.14),[341,414])]}
# Calibrated, weak-perspective camera configurations are frozen before the baseline measurement.
head='''<Graph fps={24} duration="8s" size={[900,500]}>
<Assets>
<MaterialAsset id="clay" baseColor="#89949E" />
<MeshAsset id="fit_skin" material="clay" subdivision="0">\n'''
source=head+'\n'.join(f'<Vertex position={b.vec(p)} />' for p in v)+'\n'+'\n'.join('<Face indices={['+','.join(map(str,p))+']} />' for p in f)+'''
</MeshAsset>
</Assets>
<Background color="#B0B0B0" />
<Scene id="Fit">
<Timeline>
<Track space="3d">
<Sequence duration="8s">
<CompositeGroup id="fit_stage" space="3d" depth="true">
<Camera3D id="fit_camera" position={[0,0,12]} target={[0,0,0]} fov="21.2" depthOfField="false" />
<Model id="fit_model" asset="fit_skin" />
</CompositeGroup>
</Sequence>
</Track>
</Timeline>
</Scene>
<AnimationTarget node="fit_model" property="rotationX">
<Key time="0s" value="0" />
<Key time="2s" value="0" />
<Key time="4s" value="90" />
<Key time="6s" value="-90" />
</AnimationTarget>
<AnimationTarget node="fit_model" property="rotationY">
<Key time="0s" value="0" />
<Key time="2s" value="90" />
<Key time="4s" value="0" />
<Key time="6s" value="0" />
</AnimationTarget>
<AnimationTarget node="fit_camera" property="fov">
<Key time="0s" value="21.2" />
<Key time="2s" value="16.15" />
<Key time="4s" value="22.62" />
<Key time="6s" value="22.62" />
</AnimationTarget>
<Present from="Fit" />
</Graph>'''
(ROOT/'fit-baseline.motionloom').write_text(source)
dump(ROOT/'fit-index.json',{'offsets':offsets,'count':len(v),'scope':'body and all major fins; primitive facial details are inspected in GPU renders'})
for view in FEATURES:
    old=SHOW/'authoring/analyses'/view
    request=json.loads((old/'request.json').read_text())
    request['imageId']='native-'+str(uuid.uuid5(uuid.NAMESPACE_URL,'s95/native-v2/'+view))
    request['featureHints']=FEATURES[view];request['depthHints']=[];request.pop('analysisProfile',None)
    if view=='bottom':
        request['segmentation']['mode']='mask';request['segmentation']['suppliedMask']=json.loads((old/'analysis.json').read_text())['foregroundMask']
    out=ROOT/'analyses-r3'/view;dump(out/'request.json',request)
    if not (out/'analysis.json').exists():subprocess.run([str(BIN/'analyze_image_reference'),str(SHOW/'authoring/references'/f'{view}-padded.png'),str(out/'request.json'),str(out)],check=True)
request={'schemaVersion':'1.0','targetAssetId':'fit_skin','targetModelId':'fit_model','references':[{'id':view,'frame':i*48,'analysis':json.loads((ROOT/'analyses-r3'/view/'analysis.json').read_text())} for i,view in enumerate(FEATURES)],'options':{'cameraPolicy':'frozen','allowBoundary':True,'allowMultipleComponents':True,'maxVertexResiduals':128,'metricWeights':{'silhouette':.3,'boundary':.25,'landmarks':.15,'features':.25,'depth':.05},'qualityGates':{'minimumMaskIou':.92,'maximumP95EdgeDistancePx':18,'maximumLandmarkMeanDistancePx':8,'maximumFeatureMeanDistancePx':10,'maximumDepthViolations':0}}}
dump(ROOT/'references.json',request)
