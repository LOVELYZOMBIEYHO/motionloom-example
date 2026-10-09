#!/usr/bin/env python3
"""Rebuild HOUSE 99 as native MotionLoom geometry; metres, +Y up, south +Z."""
from pathlib import Path
import hashlib
import json
import math
from vegetation import Planting, MATERIALS_XML as VEGETATION_MATERIALS
from compact_dsl import compact
import city_context
from material_upgrade import material_assets, surface_material, uv_xml

ROOT = Path(__file__).resolve().parents[1]
assets, models, roof, architecture = [], [], [], []
cache = {}


def vec(values):
    return '{[' + ','.join(f'{v:.5g}' for v in values) + ']}'


def primitive(shape, material, **params):
    if material == 'linen' and shape == 'frustum':
        material = 'shade_fabric'
    key = (shape, material, tuple((k, str(v)) for k, v in params.items()))
    if key not in cache:
        name = f's99_p{len(cache):03d}'
        attrs = ' '.join(f'{k}={vec(v)}' if isinstance(v, (list, tuple)) else f'{k}="{v}"' for k, v in params.items())
        geometry = name+'_geometry'
        uv = uv_xml(shape, material, params)
        assets.append(f'    <GeometryAsset id="{geometry}">\n'
                      f'      <Primitive shape="{shape}" {attrs} />{uv}\n'
                      f'    </GeometryAsset>\n'
                      f'    <MeshAsset id="{name}" material="{material}" geometry="{geometry}" />')
        cache[key] = name
    return cache[key]


def model(name, asset, pos, rotation=None, stage='body', shadow=True):
    attrs = f'position={vec(pos)}'
    if rotation:
        attrs += f' rotation={vec(rotation)}'
    # The assembly rises through the slab. Each opening retains its dimensions.
    if stage == 'wall':
        attrs += f' positionY={{curve("0:{pos[1]-3.3:.4f}, 6.5:{pos[1]-3.3:.4f}, 10.5:{pos[1]:.4f}:ease_in_out")}}'
    line = f'            <Model id="s99_{name}" asset="{asset}" {attrs} castShadow="{str(shadow).lower()}" receiveShadow="true" />'
    (roof if stage == 'roof' else models).append(line)


def box(name, size, pos, material='plaster', bevel=0, rotation=None, stage='body', shadow=True):
    material = surface_material(name, material)
    params = dict(size=size)
    if bevel:
        params.update(bevelRadius=min(bevel, min(size)*.35), bevelSegments=2)
    model(name, primitive('box', material, **params), pos, rotation, stage, shadow)


def cylinder(name, radius, height, pos, material, rotation=None, stage='body'):
    model(name, primitive('cylinder', material, radius=radius, height=height, segments=20), pos, rotation, stage)


def ellipsoid(name, radii, pos, material, rotation=None):
    model(name, primitive('ellipsoid', material, radii=radii, segments=16, rings=8), pos, rotation)


def wall(name, axis, fixed, start, end, openings=(), thickness=.18, material='plaster'):
    """Split wall solids around real door/window voids instead of painting on glass."""
    cursor = start
    sections = []
    for a, b, sill, head in sorted(openings):
        if a > cursor:
            sections.append((cursor, a, 0, 3))
        if sill > 0:
            sections.append((a, b, 0, sill))
        if head < 3:
            sections.append((a, b, head, 3))
        cursor = b
    if cursor < end:
        sections.append((cursor, end, 0, 3))
    for i, (a, b, lo, hi) in enumerate(sections):
        size = [b-a, hi-lo, thickness] if axis == 'x' else [thickness, hi-lo, b-a]
        pos = [(a+b)/2, (lo+hi)/2, fixed] if axis == 'x' else [fixed, (lo+hi)/2, (a+b)/2]
        box(f'{name}_{i}', size, pos, material, .008, stage='wall')
        architecture.append(dict(id=f's99_{name}_{i}', axis=axis, fixed=fixed, along=[a,b], vertical=[lo,hi], thickness=thickness))


def window(name, axis, fixed, a, b, sill, head, panels=2, sliding=False):
    for i in range(panels+1):
        t = a+(b-a)*i/panels
        size = [.045,head-sill,.09] if axis=='x' else [.09,head-sill,.045]
        pos = [t,(sill+head)/2,fixed] if axis=='x' else [fixed,(sill+head)/2,t]
        box(f'{name}_jamb{i}',size,pos,'metal',.008,stage='wall')
    for label,y in [('sill',sill),('head',head)]:
        size=[b-a,.045,.09] if axis=='x' else [.09,.045,b-a]
        pos=[(a+b)/2,y,fixed] if axis=='x' else [fixed,y,(a+b)/2]
        box(f'{name}_{label}',size,pos,'metal',.005,stage='wall')
    for i in range(panels):
        # One open sliding bay connects the lounge to the terrace.
        if sliding and i==panels-1:
            continue
        t=a+(b-a)*(i+.5)/panels
        size=[(b-a)/panels-.055,head-sill-.06,.012] if axis=='x' else [.012,head-sill-.06,(b-a)/panels-.055]
        pos=[t,(sill+head)/2,fixed] if axis=='x' else [fixed,(sill+head)/2,t]
        box(f'{name}_glass{i}',size,pos,'glass',stage='wall',shadow=False)


def chair(name,x,z,rotation=0):
    # A small compound keeps the seat, curved-looking back and tapered legs together.
    seat=primitive('box','oak',size=[.48,.07,.48],bevelRadius=.024,bevelSegments=3)
    back=primitive('box','oak',size=[.48,.3,.065],bevelRadius=.022,bevelSegments=3)
    leg=primitive('cylinder','oak',radius=.022,height=.44,segments=12)
    compound=[f'    <CompoundAsset id="s99_{name}_asset">',f'      <Instance asset="{seat}" position={{[0,.47,0]}} />',f'      <Instance asset="{back}" position={{[0,.7,-.2]}} rotation={{[-8,0,0]}} />']
    for dx in [-.19,.19]:
        for dz in [-.18,.18]:
            compound.append(f'      <Instance asset="{leg}" position={vec([dx,.22,dz])} />')
    assets.extend(compound+['    </CompoundAsset>'])
    model(name,f's99_{name}_asset',[x,0,z],[0,rotation,0])


planting = Planting(assets, model)
plant = planting.plant


# Finish-specific materials retain shared map data and physical texture scale.
material_xml = material_assets()
material_xml += VEGETATION_MATERIALS
material_xml += city_context.MATERIALS_XML

# Site, terrace and quiet urban context establish the building's street frontage.
box('site',[32,.3,26],[0,-.38,0],'grass')
box('street',[32,.04,4],[0,-.2,10.1],'road')
box('sidewalk',[32,.06,1.7],[0,-.16,7.2],'stone')
box('slab',[12.2,.22,8.2],[0,-.11,0],'stone',.04)
box('terrace',[8.5,.14,2.6],[-1.55,-.07,5.4],'stone',.02)
for i in range(6):
    box(f'path{i}',[1.5,.055,.58],[.7,-.022,5.0+i*.61],'stone',.01)
for i in range(13):
    box(f'deck_joint{i}',[.009,.003,2.6],[-5.8+i*.6,.004,5.4],'walnut',shadow=False)
assets.append(city_context.build_city(box, cylinder, model, primitive, batch_boxes=True))

# The floor and wall layout share the exact coordinates used by the plan overlay.
for i in range(23):
    box(f'floor_plank{i}',[.315,.018,7.78],[-5.73+i*.323,.012,0],'oak',.002)
box('hall_floor',[1.04,.022,7.8],[2.1,.015,0],'stone')
box('guest_floor',[3.1,.022,2.46],[4.35,.015,-2.65],'oak')
box('bath_floor',[3.1,.024,2.22],[4.35,.017,-.1],'stone')
box('primary_floor',[3.1,.022,2.68],[4.35,.015,2.55],'oak')
wall('south','x',4,-6,6,[(-5.3,-.8,0,2.6),(.15,1.25,0,2.4),(3.25,5.5,.85,2.5)])
wall('north','x',-4,-6,6,[(-5.3,-1.6,1.25,2.5),(3.3,5.5,1.0,2.5)])
wall('west','z',-6,-3.91,3.91,[(-.7,2.1,.65,2.6)])
wall('east','z',6,-3.91,3.91,[(-.8,.6,1.65,2.5),(1.7,3.3,.85,2.5)])
wall('privacy','z',1.5,-3.91,3.91,[(-.5,.6,0,2.4)],.14)
wall('hall','z',2.7,-3.91,3.91,[(-3,-2.1,0,2.25),(-.65,.25,0,2.25),(1.5,2.4,0,2.25)],.14)
wall('guest_bath','x',-1.3,2.77,5.91,thickness=.14)
wall('bath_primary','x',1.1,2.77,5.91,thickness=.14)
window('living_slider','x',4,-5.3,-.8,.03,2.6,4,True)
window('south_primary','x',4,3.25,5.5,.85,2.5)
window('kitchen','x',-4,-5.3,-1.6,1.25,2.5,3)
window('guest','x',-4,3.3,5.5,1,2.5)
window('living_west','z',-6,-.7,2.1,.65,2.6,3)
window('bath_high','z',6,-.8,.6,1.65,2.5)
window('primary_east','z',6,1.7,3.3,.85,2.5)

# Door leaves are held open at the same measured openings; all rooms are connected.
for name,x,z,width,angle in [('entry',.16,4,1.06,-90),('guest_door',2.7,-3,.86,80),('bath_door',2.7,-.65,.86,80),('primary_door',2.7,1.5,.86,80)]:
    if name=='entry':
        dx=math.cos(math.radians(angle))*width/2; dz=-math.sin(math.radians(angle))*width/2
        box(name,[width,2.23,.045],[x+dx,1.115,z+dz],'walnut',.009,[0,angle,0],stage='wall')
    else:
        dx=math.sin(math.radians(angle))*width/2; dz=math.cos(math.radians(angle))*width/2
        box(name,[.045,2.2,width],[x+dx,1.1,z+dz],'oak',.009,[0,angle,0],stage='wall')
    for y in [.04,2.27]:
        if name!='entry':
            box(name+'_trim'+str(y),[.17,.045,.96],[x,y,z+.45],'walnut',stage='wall')

# Flat roofs are one native compound so their lift never alters the house body.
box('public_roof',[7.95,.22,8.6],[-2.25,3.12,0],'stone',.025,stage='roof')
box('ceiling',[7.7,.025,8.02],[-2.25,2.99,0],'ceiling',stage='roof')
box('private_roof',[4.62,.26,8.48],[3.76,3.23,0],'plaster',.018,stage='roof')
box('canopy',[7.6,.16,1.2],[-2.3,2.98,4.52],'stone',.012,stage='roof')
for i in range(23):
    box(f'canopy_slat{i}',[.045,.1,1.06],[-5.85+i*.32,2.86,4.58],'oak',.006,stage='roof')
for x in [-5.8,1.2]:
    box(f'porch_post{x}',[.085,2.9,.085],[x,1.45,5.02],'metal',.007)
for i in range(15):
    box(f'entry_slat{i}',[.055,2.9,.055],[1.68+i*.094,1.45,4.13],'walnut',.005,stage='wall')
box('entry_light',[.025,.72,.055],[1.46,1.7,4.13],'light',stage='wall')

# Kitchen: joinery, hardware, real countertop objects and under-cabinet light.
for i in range(7):
    x=-5.45+i*.59
    box(f'cabinet{i}',[.568,.83,.65],[x,.435,-3.55],'sage',.013)
    box(f'cabinet_handle{i}',[.26,.013,.015],[x,.81,-3.211],'brass',.004)
box('counter',[4.26,.07,.74],[-3.68,.9,-3.55],'worktop',.018)
box('backsplash',[4.4,.42,.02],[-3.6,1.17,-3.895],'worktop')
for i in range(5):
    box(f'upper{i}',[.8,.45,.29],[-5.24+i*.85,2.72,-3.76],'oak',.01)
box('kitchen_strip',[4.2,.015,.022],[-3.64,2.48,-3.6],'light')
box('fridge',[.66,2.3,.7],[-1.17,1.15,-3.53],'metal',.025)
box('fridge_seam',[.62,.009,.009],[-1.17,.78,-3.174],'brass')
box('sink_rim',[.64,.025,.42],[-4.7,.947,-3.53],'metal',.045)
box('sink_basin',[.52,.015,.31],[-4.7,.953,-3.53],'road',.05)
cylinder('tap',.022,.28,[-4.7,1.095,-3.82],'brass')
cylinder('tap_spout',.022,.22,[-4.7,1.225,-3.73],'brass',[90,0,0])
box('hob',[.66,.025,.46],[-2.6,.95,-3.54],'metal',.012)
for i in range(2):
    cylinder(f'hob_ring{i}',.105,.008,[-2.78+i*.34,.97,-3.53],'road')
box('cutting_board',[.48,.025,.3],[-3.61,.955,-3.54],'oak',.03)
ellipsoid('bread',[.17,.08,.09],[-3.6,1.02,-3.54],'terracotta')
box('island',[2.5,.9,1],[-3.8,.45,-1.85],'oak',.022)
box('island_top',[2.6,.07,1.09],[-3.8,.935,-1.85],'worktop',.02)
for i in range(14):
    box(f'island_flute{i}',[.018,.8,.017],[-4.96+i*.18,.46,-1.336],'walnut',.004)
for i in range(2):
    chair(f'stool{i}',-4.3+i*1.0,-.93,0)
    cylinder(f'pendant_cord{i}',.009,.85,[-4.3+i,2.55,-1.85],'metal')
    model(f'pendant_shade{i}',primitive('cone','terracotta',radius=.24,height=.22,segments=32),[-4.3+i,2.1,-1.85],[180,0,0])
    cylinder(f'pendant_glow{i}',.19,.018,[-4.3+i,2.0,-1.85],'light')

# Dining: four chairs, ceramic place settings and a vase with stems.
box('dining_table',[1.65,.08,.88],[-.4,.76,-2.05],'oak',.05)
for dx in [-.6,.6]:
    for dz in [-.28,.28]:
        cylinder(f'table_leg{dx}{dz}',.035,.72,[-.4+dx,.36,-2.05+dz],'oak')
for i,(x,z,rot) in enumerate([(-.91,-2.78,0),(.11,-2.78,0),(-.91,-1.32,180),(.11,-1.32,180)]):
    chair(f'dining_chair{i}',x,z,rot)
    cylinder(f'plate{i}',.14,.017,[x,.81,-2.05+(-.22 if i<2 else .22)],'ceramic')
cylinder('table_vase',.075,.22,[-.4,.91,-2.05],'terracotta')
planting.sprigs(-.4, 1.02, -2.05)

# Lounge: low upholstered furniture, reading light, books and a folded throw.
box('rug',[3.8,.015,3.0],[-3.55,.038,2.0],'linen',.03)
box('sofa_base',[2.9,.22,.99],[-3.85,.24,1.5],'walnut',.045)
for i in range(3):
    box(f'sofa_seat{i}',[.85,.22,.81],[-4.72+i*.87,.49,1.58],'linen',.06)
    box(f'sofa_back{i}',[.89,.56,.2],[-4.72+i*.87,.8,1.08],'linen',.065,[-8,0,0])
for x in [-5.22,-2.48]:
    box(f'sofa_arm{x}',[.2,.49,1.0],[x,.58,1.51],'linen',.06)
box('pillow_sage',[.46,.42,.18],[-4.8,.83,1.36],'sage',.06,[-12,0,-12])
box('pillow_clay',[.43,.39,.17],[-2.94,.81,1.35],'clay',.065,[-14,0,12])
box('folded_throw',[.57,.035,.68],[-3.1,.623,1.62],'sage',.015)
box('coffee_top',[1.27,.075,.66],[-3.9,.38,2.8],'walnut',.08)
for x in [-4.35,-3.45]:
    box(f'coffee_leg{x}',[.13,.31,.44],[x,.18,2.8],'walnut',.035)
box('coffee_book',[.31,.03,.22],[-4.2,.44,2.77],'bookblue',.007,[0,-8,0])
cylinder('coffee_cup',.044,.08,[-3.76,.468,2.8],'ceramic')
cylinder('coffee_inside',.033,.004,[-3.76,.51,2.8],'walnut')
box('side_table',[.5,.045,.5],[-2.07,.55,1.5],'oak',.04)
cylinder('floorlamp_stem',.016,1.45,[-5.5,.73,.52],'brass')
cylinder('floorlamp_base',.17,.03,[-5.5,.025,.52],'metal')
model('floorlamp_shade',primitive('frustum','linen',topSize=[.34,.34],bottomSize=[.5,.5],height=.32),[-5.5,1.46,.52])
cylinder('floorlamp_bulb',.07,.08,[-5.5,1.37,.52],'light')
box('bookshelf_back',[.24,2.3,2.3],[-5.74,1.18,2.7],'oak',.01)
for i in range(5):
    box(f'shelf{i}',[.4,.04,2.3],[-5.68,.28+i*.43,2.7],'walnut')
    for j in range(5):
        box(f'book{i}_{j}',[.18,.21+j%2*.07,.04],[-5.46,.41+i*.43,1.79+j*.093],['linen','clay','sage','bookblue'][j%4],.003)
plant('lounge_plant',-1.65,3.18,1.5)

# Primary bedroom: east headboard, west foot aisle and real reading lamps.
box('primary_rug',[2.82,.015,2.2],[4.3,.038,2.75],'linen',.03)
box('bed_base',[2.14,.28,1.68],[4.55,.25,2.85],'walnut',.04)
box('mattress',[2.08,.21,1.6],[4.55,.49,2.85],'linen',.09)
box('duvet',[1.45,.12,1.56],[4.25,.64,2.85],'linen',.07)
box('bed_throw',[.48,.03,1.58],[3.85,.715,2.85],'sage',.02)
box('headboard',[.1,1.0,2.1],[5.68,.75,2.8],'oak',.018)
for z in [2.47,3.24]:
    box(f'bed_pillow{z}',[.48,.17,.57],[5.23,.68,z],'linen',.065,[0,0,8])
for z in [1.6,3.7]:
    box(f'bed_side{z}',[.46,.045,.34],[5.46,.59,z],'walnut',.03)
    cylinder(f'bed_lamp_stem{z}',.015,.28,[5.46,.75,z],'brass')
    model(f'bed_lamp_shade{z}',primitive('frustum','linen',topSize=[.18,.18],bottomSize=[.28,.28],height=.18),[5.46,.91,z])
    ellipsoid(f'bed_light{z}',[.06,.055,.06],[5.46,.84,z],'light')
box('wardrobe',[1.3,2.5,.36],[4.5,1.25,1.36],'sage',.012)
box('wardrobe_pull',[.022,.37,.022],[4.5,1.25,1.56],'brass',.007)
box('primary_art_frame',[.68,.53,.035],[4.05,1.86,1.195],'walnut',.007)
box('primary_art',[.6,.45,.015],[4.05,1.86,1.218],'linen')
ellipsoid('primary_art_relief',[.21,.12,.025],[4.05,1.89,1.238],'clay')

# Guest study, bathroom and arrival storage make the interior usable beyond a shell.
box('guest_bed',[1.15,.27,1.9],[4.64,.25,-2.85],'oak',.04)
box('guest_mattress',[1.1,.21,1.87],[4.64,.49,-2.85],'linen',.08)
box('guest_cover',[1.08,.07,1.24],[4.64,.63,-2.57],'sage',.045)
box('guest_pillow',[.65,.16,.4],[4.64,.67,-3.44],'linen',.06)
box('desk',[.56,.065,1.35],[3.25,.75,-1.99],'oak',.025)
chair('desk_chair',3.75,-1.99,90)
box('laptop',[.31,.018,.22],[3.25,.802,-1.99],'metal',.008)
box('laptop_screen',[.015,.22,.3],[3.07,.91,-1.99],'bookblue',.008,[0,0,-10])
box('bath_vanity',[.7,.75,.4],[3.35,.41,-.95],'walnut',.02)
box('basin',[.72,.12,.42],[3.35,.86,-.95],'ceramic',.055)
box('basin_inner',[.52,.006,.27],[3.35,.927,-.95],'ceramic',.045)
box('mirror',[.012,.75,.42],[2.795,1.57,-.95],'mirror',.006)
box('mirror_light',[.028,.018,.48],[2.82,2.01,-.95],'light')
ellipsoid('toilet_base',[.19,.23,.26],[4.3,.25,.53],'ceramic')
ellipsoid('toilet_seat',[.21,.045,.3],[4.3,.51,.5],'ceramic')
box('toilet_tank',[.41,.48,.19],[4.3,.73,.83],'ceramic',.045)
box('shower_tray',[1.1,.055,1.04],[5.3,.064,-.65],'ceramic',.018)
box('shower_screen',[.012,2.18,1.05],[4.77,1.16,-.66],'shower_glass',shadow=False)
cylinder('shower_riser',.015,1.16,[5.72,1.58,-1.205],'brass')
cylinder('shower_head',.11,.025,[5.56,2.22,-1.06],'brass',[0,0,0])
box('towel',[.012,.53,.37],[2.803,1.22,.66],'linen',.008)
box('entry_bench',[.4,.075,1.1],[1.13,.42,2.54],'oak',.025)
box('entry_shoes',[.24,.1,.28],[1.15,.1,2.24],'metal',.03)
box('entry_coat',[.07,.8,.28],[1.39,1.84,2.89],'sage',.02)

# Terrace furniture and leaf-based vegetation give the exterior daily use and scale.
box('outdoor_bench',[2.2,.12,.53],[-3.85,.43,5.35],'oak',.02)
for x in [-4.7,-3.0]:
    box(f'outdoor_leg{x}',[.1,.42,.5],[x,.21,5.35],'metal',.009)
for i in range(8):
    box(f'bench_slat{i}',[2.2,.02,.046],[-3.85,.502,5.13+i*.061],'walnut',.006)
plant('terrace_plant',-5.3,5.87,1.4)
plant('entry_plant',2.4,5.55,1.05)
# The east tree reuses the west tree's material-batched MeshAssets at a
# different orientation. Distinct placement and lighting keep the pair natural.
for name,x,z,seed,rotation in [('tree_west',-8.35,2,991,None),('tree_east',8,-1,991,[0,137,0])]:
    planting.tree(name,x,z,seed,rotation)
for i in range(8):
    box(f'planter{i}',[.68,.35,.75],[-8.0+i*.82,.08,-5.5],'stone',.025)
    planting.shrub(f'garden{i}',-8.0+i*.82,-5.5,.7)

# Build a dedicated roof asset from its authored primitive model instances.
import re
roof_parts=[]
for line in roof:
    roof_parts.append('      <Instance '+re.sub(r'id="[^"]+" ', '', line.strip().removeprefix('<Model ')).replace(' castShadow="true" receiveShadow="true"',''))
assets.extend(['    <CompoundAsset id="s99_roof_asset">']+roof_parts+['    </CompoundAsset>'])
models.append('            <Model id="s99_roof" asset="s99_roof_asset" scale={curve("0:0, 11:0, 11.04:1, 44:1")} positionY={curve("0:3, 11:3, 12.8:0:ease_in_out, 44:0")} />')

lighting='''
            <EnvironmentLight id="s99_ibl" asset="s99_environment" intensity={curve("0:.75, 37:.75, 40:.2:ease_in_out, 44:.2")} visible="false" diffuseIntensity=".85" specularIntensity=".4" rotationY="-90.33" />
            <DirectionalLight id="s99_sun" direction={[.5,-.8,-.65]} color="#FFE6C5" intensity={curve("0:3.2, 37:3.2, 40:.28:ease_in_out, 44:.28")} castShadow="true" shadowStrength=".75" />
            <BakedLighting id="s99_bounce" src="assets/lighting-v3/s99-lighting.json" blend={curve("0:0,37:0,40:1:ease_in_out,44:1")} intensity={curve("0:0,12.8:0,13.6:1:ease_in_out,44:1")} specularIntensity={curve("0:0,12.8:0,13.6:1:ease_in_out,44:1")} />
            <PlanarReflection id="s99_bath_mirror" target="s99_mirror" resolutionScale=".5" clipBias=".005" />
            <PointLight id="s99_pendant_left" position={[-4.3,1.98,-1.85]} color="#FFD6A3" intensity={curve("0:4,37:4,40:6:ease_in_out,44:6")} range="5" />
            <PointLight id="s99_pendant_right" position={[-3.3,1.98,-1.85]} color="#FFD6A3" intensity={curve("0:4,37:4,40:6:ease_in_out,44:6")} range="5" />
            <PointLight id="s99_living_lamp" position={[-5.41,1.28,.52]} color="#FFD4A0" intensity={curve("0:4.6,37:4.6,40:7:ease_in_out,44:7")} range="4" />
            <PointLight id="s99_primary_lamp_left" position={[5.52,.80,1.6]} color="#FFD4A0" intensity={curve("0:2.6,37:2.6,40:4:ease_in_out,44:4")} range="3" />
            <PointLight id="s99_primary_lamp_right" position={[5.52,.80,3.7]} color="#FFD4A0" intensity={curve("0:2.6,37:2.6,40:4:ease_in_out,44:4")} range="3" />
            <PointLight id="s99_bath_fixture" position={[2.85,2.01,-.95]} color="#FFD4A0" intensity={curve("0:4,37:4,40:6:ease_in_out,44:6")} range="4" />
            <AmbientOcclusion intensity=".72" radius=".35" />
            <ContactShadow intensity=".85" distance=".18" softness=".55" />
            <Camera3D id="s99_axo" position={[-13,13,17]} target={[0,.1,0]} fov="43" />
            <Camera3D id="s99_exterior" position={[-13.5,6.2,18]} target={[-.2,1.2,.3]} fov="43" />
            <Camera3D id="s99_living" position={[.55,1.65,3.35]} target={[-3.85,1.0,1.2]} fov="68" />
            <Camera3D id="s99_kitchen" position={[-1,1.75,.85]} target={[-3.5,1.2,-2.75]} fov="66" />
            <Camera3D id="s99_primary" position={[3.2,1.55,1.9]} target={[4.77,.98,2.95]} fov="74" />
            <Camera3D id="s99_bath" position={[3.06,1.65,.69]} target={[5.0,1.12,-.45]} fov="80" />
            <Camera3D id="s99_dusk" position={[-12,5.5,17]} target={[-.2,1.1,.8]} fov="45" />
'''

# Camera cuts use the public Scene activeCamera channel; motion is local to each shot.
camera_keys=[(0,'axo'),(13,'exterior'),(19,'living'),(26,'kitchen'),(32,'primary'),(36,'bath'),(39,'dusk')]
animations=['  <AnimationTarget node="SHOWCASE99" property="activeCamera">']+[f'    <Key time="{t}s" value="s99_{cam}" />' for t,cam in camera_keys]+['  </AnimationTarget>']
for cam,start,end,p0,p1 in [('axo',6.5,12.8,[-13,13,17],[-12,11.8,15.7]),('exterior',13,18.9,[-13.5,6.2,18],[-11.5,5.4,16.7]),('living',19,25.9,[.55,1.65,3.35],[.05,1.6,3.2]),('kitchen',26,31.9,[-1,1.75,.85],[-1.25,1.68,.58]),('primary',32,35.9,[3.2,1.55,1.9],[3.28,1.5,1.97]),('dusk',39,44,[-12,5.5,17],[-10.5,4.8,15.3])]:
    animations.extend([f'  <AnimationTarget node="s99_{cam}" property="position">',f'    <Key time="{start}s" value="{vec(p0)[1:-1]}" />',f'    <Key time="{end}s" value="{vec(p1)[1:-1]}" ease="ease_in_out" />','  </AnimationTarget>'])

plan_path=ROOT/'scripts/plan.motionloom.fragment'
if not plan_path.exists():
    plan_path=Path('/private/tmp/s99-plan.motionloom.fragment')
plan=plan_path.read_text() if plan_path.exists() else '<Layer space="screen"><Rect width="1920" height="1080" color="#F3EFE6" /></Layer>'
overlays=[]
for start,end,num,title,detail in [(6.5,13,'02','FROM PLAN TO VOLUME','ONE FLOOR PLAN / REAL OPENINGS / 3.0 M WALLS'),(13,19,'03','THE CITY, AT HOME','LIMESTONE / OAK / A SOUTH-FACING TERRACE'),(19,26,'04','A ROOM FOR EVERYDAY','READING LIGHT / LINEN / BOOKS / OPEN GARDEN BAY'),(26,32,'05','COOK. GATHER. STAY.','WORKTOP / ISLAND / FOUR PLACES AT THE TABLE'),(32,36,'06','THE QUIET WING','SEPARATE HALL / TWO BEDROOMS / WARM READING LIGHT'),(36,39,'07','DAILY RITUALS','SHOWER / VANITY / HIGH PRIVACY WINDOW'),(39,44,'08','HOME AFTER DARK','THE SAME HOUSE / A DIFFERENT HOUR')]:
    overlays.extend([f'        <Sequence from="{start}s" duration="{end-start}s">','          <Layer space="screen">','            <Rect x="0" y="944" width="1920" height="136" color="#1E2927EF" />',f'            <Text x="76" y="990" value="{num} / HOUSE 99" fontFamily="Arial" fontSize="16" tracking="3" color="#C2B594" />',f'            <Text x="76" y="1031" value="{title}" fontFamily="Arial" fontSize="30" tracking="1.5" fontWeight="700" color="#F5F0E4" />',f'            <Text x="935" y="1026" value="{detail}" fontFamily="Arial" fontSize="15" tracking="1.3" color="#DDD6C6" />','          </Layer>','        </Sequence>'])

document='''<!-- S99 / HOUSE 99 / Native MotionLoom architecture, furniture and cameras. -->
<Graph fps={24} duration="44s" size={[3840,2160]} renderSize={[1920,1080]}>
  <RenderStyle id="s99_architecture">
    <SurfaceStyle shading="physical" />
    <LightingStyle ambientIntensity=".16" ambientColor="#FFF0DB" shadowStyle="soft" />
    <PostStyle toneMapping="aces" exposure="1.08" contrast="1.035" saturation=".92" />
    <AntiAliasingStyle method="taa" quality="high" fallback="smaa" sharpness=".04" />
  </RenderStyle>
  <Assets>
'''+material_xml+'\n'.join(assets)+'''
  </Assets>
  <Background color="#DCE2D6" />
  <Scene id="SHOWCASE99" renderStyle="s99_architecture">
    <Timeline>
      <Track id="s99_dusk_sky" space="screen" compositeOrder="0">
        <Sequence from="39s" duration="5s">
          <Layer space="screen">
            <Rect x="0" y="0" width="1920" height="1080" color="#2D3B46" opacity={curve("0:0, 1:1:ease_in_out, 5:1")} />
          </Layer>
        </Sequence>
      </Track>
      <Track id="s99_house" space="3d" compositeOrder="10">
        <Sequence from="0s" duration="44s" out="hold">
          <CompositeGroup id="s99_house_stage" space="3d" depth="true" format="rgba16f">
'''+lighting+'\n'.join(models)+'''
          </CompositeGroup>
        </Sequence>
      </Track>
      <Track id="s99_plan" space="screen" compositeOrder="30">
        <Sequence from="0s" duration="6.5s">
'''+plan+'''
        </Sequence>
      </Track>
      <Track id="s99_editorial" space="screen" compositeOrder="40">
'''+ '\n'.join(overlays)+'''
      </Track>
    </Timeline>
  </Scene>
'''+ '\n'.join(animations)+'''
  <Present from="SHOWCASE99" />
</Graph>
'''
# Style values are JSON numbers as well as DSL expressions, so keep leading zeros.
# Keep the logical 4K canvas and the authored 1080p screen artwork coordinates;
# the renderer fits the 3D island to renderSize without changing the layout.
document=document.replace('<Layer space="screen"', '<Layer scale="2" space="screen"')
document=re.sub(r'(?<![\w\d])(-?)\.(?=\d)',r'\g<1>0.',document)
document=compact(document)
ROOT.joinpath('main.motionloom').write_text(document)
ROOT.joinpath('evidence/planting-geometry.json').write_text(json.dumps(dict(source_sha256=hashlib.sha256(document.encode()).hexdigest(), plants=planting.report),indent=2)+'\n')
ROOT.joinpath('scripts/layout.json').write_text(json.dumps(dict(units='metres',footprint=[12,8],height=3,wall_segments=architecture,doors=[dict(wall='hall',fixed=2.7,along=[a,a+.9],height=2.25) for a in [-3,-.65,1.5]],rooms=dict(public=[-6,1.5,-4,4],hall=[1.5,2.7,-4,4],guest=[2.7,6,-4,-1.3],bath=[2.7,6,-1.3,1.1],primary=[2.7,6,1.1,4])),indent=2)+'\n')
print(f'Generated {len(models)} native models / {len(cache)} primitive assets; SHA256 {hashlib.sha256(document.encode()).hexdigest()}')
