"""Native, recessed urban facades for HOUSE 99.

Import this module from build_showcase.py and replace its original city loop:

    material_xml += city_context.MATERIALS_XML
    assets.append(city_context.build_city(box, cylinder, model, primitive))

Supplying model and primitive makes one CompoundAsset/Model per building.
With batch_boxes=True, ordinary facade boxes are additionally combined into
material-bound native meshes; rounded, rotated and cylindrical parts remain
in the residual CompoundAsset.
The two-callback fallback emits the same boxes and cylinders directly.
No scene, house, furniture, lighting, camera or existing material is modified.
"""
from html import escape


BUILDINGS = (
    (-12, -6, 5, 7, 6.5),
    (12, -8, 5, 7, 8),
    (-3, -12, 6, 5, 6),
    (5, -13, 5, 5, 9),
)
GROUND_Y = -.2

# Windows are fully opaque PBR surfaces with distinct reflection/roughness.
# Their depth comes from actual facade piers, lintels, sills and recessed panes.
MATERIALS_XML = '''
    <MaterialAsset id="city_limestone" shading="pbr" baseColor="#BEBCAF" roughness="0.83" specular="0.2" />
    <MaterialAsset id="city_warm_plaster" shading="pbr" baseColor="#BDB4A6" roughness="0.87" specular="0.16" />
    <MaterialAsset id="city_stonegray" shading="pbr" baseColor="#A7B0A6" roughness="0.88" specular="0.18" />
    <MaterialAsset id="city_graphite" shading="pbr" baseColor="#87948E" roughness="0.82" specular="0.22" />
    <MaterialAsset id="city_recess" shading="pbr" baseColor="#627069" roughness="0.94" specular="0.12" />
    <MaterialAsset id="city_trim" shading="pbr" baseColor="#DBD9CE" roughness="0.69" specular="0.25" />
    <MaterialAsset id="city_sill" shading="pbr" baseColor="#949B8F" roughness="0.71" specular="0.22" />
    <MaterialAsset id="city_frame" shading="pbr" baseColor="#35443F" metallic="0.68" roughness="0.38" />
    <MaterialAsset id="city_window_blue" shading="pbr" baseColor="#344F5A" metallic="0.15" roughness="0.23" specular="0.65" />
    <MaterialAsset id="city_window_green" shading="pbr" baseColor="#3E5651" metallic="0.13" roughness="0.27" specular="0.6" />
    <MaterialAsset id="city_window_dim" shading="pbr" baseColor="#273E41" metallic="0.12" roughness="0.3" specular="0.5" />
    <MaterialAsset id="city_sky_reflection" shading="pbr" baseColor="#637B7D" metallic="0.18" roughness="0.26" specular="0.6" />
    <MaterialAsset id="city_roof" shading="pbr" baseColor="#777E76" roughness="0.94" specular="0.12" />
    <MaterialAsset id="city_equipment" shading="pbr" baseColor="#B1B9B1" metallic="0.42" roughness="0.52" />
    <MaterialAsset id="city_solar" shading="pbr" baseColor="#253D4A" metallic="0.3" roughness="0.22" specular="0.62" />
'''


def _vec(values):
    return '{[' + ','.join(f'{value:.5g}' for value in values) + ']}'


def _box_faces(size, position):
    """Emit six flat-shaded quads with the same winding as a native box."""
    x, y, z = position
    hx, hy, hz = (value / 2 for value in size)
    corners = (
        ((-hx, hy, -hz), (-hx, hy, hz), (hx, hy, hz), (hx, hy, -hz)),
        ((-hx, -hy, hz), (-hx, -hy, -hz), (hx, -hy, -hz), (hx, -hy, hz)),
        ((hx, -hy, -hz), (hx, hy, -hz), (hx, hy, hz), (hx, -hy, hz)),
        ((-hx, -hy, hz), (-hx, hy, hz), (-hx, hy, -hz), (-hx, -hy, -hz)),
        ((hx, -hy, hz), (hx, hy, hz), (-hx, hy, hz), (-hx, -hy, hz)),
        ((-hx, -hy, -hz), (-hx, hy, -hz), (hx, hy, -hz), (hx, -hy, -hz)),
    )
    return [[(x + dx, y + dy, z + dz) for dx, dy, dz in face] for face in corners]


def build_city(box, cylinder, model=None, primitive=None, batch_boxes=False):
    """Generate four buildings at the original positions and footprints.

    Return CompoundAsset XML when model+primitive callbacks are provided;
    batch_boxes also returns material-bound MeshAsset XML. Append the result
    to the generator's asset declarations and include MATERIALS_XML. All
    coordinates are local to each building, with its origin at y=-0.2m.

    All balcony decks, frames and roof hardware remain within each original
    x/z footprint. Only rooftop details extend up to 0.64m above the massing.
    """
    if (model is None) != (primitive is None):
        raise ValueError('Provide both model and primitive, or neither.')
    use_compounds = model is not None
    compound_xml = []
    merged_xml = []
    merged_models = []
    residual_models = []
    facade_materials = (
        'city_limestone', 'city_warm_plaster',
        'city_stonegray', 'city_graphite',
    )
    window_materials = (
        'city_window_blue', 'city_window_green', 'city_window_dim',
    )

    for index, (world_x, world_z, width, depth, height) in enumerate(BUILDINGS):
        prefix = f'city_detail_{index}'
        facade_material = facade_materials[index]
        parts = []
        boxes_by_material = {}

        def add_box(suffix, size, position, material, bevel=0, rotation=None):
            name = f'{prefix}_{suffix}'
            if use_compounds:
                params = dict(size=list(size))
                if bevel:
                    params.update(bevelRadius=min(bevel, min(size)*.35), bevelSegments=2)
                asset = primitive('box', material, **params)
                if batch_boxes and not bevel and not rotation:
                    boxes_by_material.setdefault(material, []).append((size, position))
                else:
                    attrs = f'asset="{escape(asset, quote=True)}" position={_vec(position)}'
                    if rotation:
                        attrs += f' rotation={_vec(rotation)}'
                    parts.append(f'      <Instance {attrs} />')
            else:
                position = [world_x+position[0], GROUND_Y+position[1], world_z+position[2]]
                box(name, list(size), position, material, bevel=bevel, rotation=rotation)

        def add_cylinder(suffix, radius, length, position, material, rotation=None):
            name = f'{prefix}_{suffix}'
            if use_compounds:
                asset = primitive('cylinder', material, radius=radius, height=length, segments=16)
                attrs = f'asset="{escape(asset, quote=True)}" position={_vec(position)}'
                if rotation:
                    attrs += f' rotation={_vec(rotation)}'
                parts.append(f'      <Instance {attrs} />')
            else:
                position = [world_x+position[0], GROUND_Y+position[1], world_z+position[2]]
                cylinder(name, radius, length, position, material, rotation=rotation)

        # The central mass stops behind the pane plane, leaving genuine depth
        # between the visible glazing and the exterior wall/frame surfaces.
        add_box('core', [width-1.8, height-.18, depth-1.8],
                [0, height/2-.03, 0], 'city_recess')
        # Recess the plinth by 20 mm: its vertical faces must not share the
        # facade piers' planes. Its bottom meets the site's y=-0.23 surface.
        add_box('foundation', [width-.04, .16, depth-.04], [0, .05, 0], 'city_sill')
        floors = (3, 3, 2, 3)[index]
        floor_height = height/floors

        # Facades use piers plus lower/upper spandrels; window apertures remain
        # empty until the recessed, opaque pane and its separate frame are added.
        for face_index, (axis, sign) in enumerate((('x', 1), ('z', -1), ('z', 1), ('x', -1))):
            span = width if axis == 'x' else depth
            across = depth if axis == 'x' else width
            bays = max(3, round(span/1.65))
            pitch = span/bays
            outer = sign*across/2
            front = outer-sign*.1
            face_name = f'f{face_index}'

            def face_box(suffix, along_size, up_size, thick, along, up, fixed, material, bevel=0):
                if axis == 'x':
                    size, position = [along_size, up_size, thick], [along, up, fixed]
                else:
                    size, position = [thick, up_size, along_size], [fixed, up, along]
                add_box(f'{face_name}_{suffix}', size, position, material, bevel)

            for level in range(floors):
                base = level*floor_height
                top = base+floor_height
                balcony_bay = bays//2
                for bay in range(bays):
                    along = -.5*span+(bay+.5)*pitch
                    label = f'l{level}_b{bay}'
                    is_balcony = face_index == 0 and level == 1 and bay == balcony_bay
                    is_entry = face_index == 0 and level == 0 and bay == balcony_bay
                    pane_width = pitch-.23
                    sill = base+(.12 if is_balcony or is_entry else .66)
                    head = top-.36
                    pane_height = head-sill
                    surface = front-sign*.53 if is_balcony else front
                    # Slightly inset upper balcony door keeps its guard/deck
                    # entirely within the original building's south boundary.
                    lower_height = sill-base
                    face_box(label+'_lower', pitch-.16, lower_height, .18,
                             along, base+lower_height/2, surface, facade_material)
                    face_box(label+'_lintel', pitch-.16, top-head, .18,
                             along, (head+top)/2, surface, facade_material)
                    pane_fixed = surface-sign*.17
                    pane_material = window_materials[(index+face_index+bay+level)%3]
                    face_box(label+'_pane', pane_width, pane_height, .027,
                             along, (sill+head)/2, pane_fixed, pane_material)
                    # A muted upper reflection changes tint without making
                    # windows transparent or using a transmission material.
                    face_box(label+'_sky', pane_width-.075, .095, .008,
                             along, head-.13, pane_fixed+sign*.019, 'city_sky_reflection')
                    frame_fixed = surface-sign*.04
                    for side in (-1, 1):
                        face_box(label+f'_jamb{side}', .045, pane_height+.06, .15,
                                 along+side*(pane_width/2+.012), (sill+head)/2,
                                 frame_fixed, 'city_frame')
                    for end_name, up in (('sill', sill-.023), ('head', head+.023)):
                        face_box(label+'_'+end_name, pane_width+.07, .047, .15,
                                 along, up, frame_fixed, 'city_frame')
                    face_box(label+'_mullion', .025, pane_height-.025, .07,
                             along, (sill+head)/2, frame_fixed, 'city_frame')
                    if not is_balcony and not is_entry:
                        # Sills project from the recessed frame, within the
                        # massing edge, casting a narrow visible ledge shadow.
                        face_box(label+'_ledge', pane_width+.16, .06, .27,
                                 along, sill-.055, outer-sign*.14, 'city_sill', .008)
                    if is_entry:
                        face_box(label+'_door_rail', pane_width-.05, .035, .055,
                                 along, sill+.94, frame_fixed, 'city_frame')
                        face_box(label+'_handle', .018, .25, .025,
                                 along+.1, sill+1.04, frame_fixed+sign*.049, 'city_equipment')
                    if is_balcony:
                        # Recess side returns, deck, metal guard and repeated
                        # balusters provide readable three-dimensional detail.
                        for side in (-1, 1):
                            face_box(label+f'_return{side}', .07, floor_height-.1, .53,
                                     along+side*(pitch/2-.09), base+(floor_height-.1)/2,
                                     outer-sign*.34, facade_material)
                        face_box(label+'_deck', pitch-.15, .095, .57,
                                 along, base+.04, outer-sign*.325, 'city_trim')
                        rail_fixed = outer-sign*.055
                        for rail_name, rail_y in (('top', base+.98), ('bottom', base+.23)):
                            face_box(label+'_rail_'+rail_name, pitch-.19, .032, .03,
                                     along, rail_y, rail_fixed, 'city_frame')
                        for bar in range(7):
                            face_box(label+f'_baluster{bar}', .024, .75, .024,
                                     along-(pitch-.23)/2+bar*(pitch-.23)/6,
                                     base+.605, rail_fixed, 'city_frame')

                # Continuous structural piers and restrained slab edges make
                # the apertures read as part of a facade rather than decals.
                for pier in range(bays+1):
                    along = -.5*span+.08 if pier == 0 else (.5*span-.08 if pier == bays else -.5*span+pier*pitch)
                    face_box(f'l{level}_pier{pier}', .16, floor_height, .2,
                             along, base+floor_height/2, front, facade_material)
                # Lift the band top 8 mm above the adjoining lintel/pier tops.
                # Coplanar trim and masonry otherwise alternate during motion.
                face_box(f'l{level}_band', span-.02, .065, .24,
                         0, top-.0245, outer-sign*.125,
                         'city_trim' if index != 3 else 'city_sill')

        # Roof slab/parapet, access hatch, paired HVAC and solar racks.
        # A 25 mm raised, inset roof surface clears all facade and band tops.
        # Keep the underside embedded in the core and roof hardware seated.
        add_box('roof_deck', [width-.24, .16, depth-.24],
                [0, height-.055, 0], 'city_roof')
        for sign in (-1, 1):
            add_box(f'roof_parapet_x{sign}', [width, .24, .12],
                    [0, height+.06, sign*(depth/2-.06)], facade_material)
            add_box(f'roof_parapet_z{sign}', [.12, .24, depth-.24],
                    [sign*(width/2-.06), height+.06, 0], facade_material)
        add_box('roof_access', [.84, .6, .97],
                [width*.22, height+.3, -depth*.2], facade_material, .015)
        add_box('roof_access_cap', [.91, .04, 1.04],
                [width*.22, height+.62, -depth*.2], 'city_sill', .008)
        for unit in range(2):
            unit_x = -width*.19+unit*.96
            unit_z = -depth*.22
            add_box(f'hvac{unit}', [.74, .38, .69],
                    [unit_x, height+.19, unit_z], 'city_equipment', .025)
            add_box(f'hvac{unit}_grille', [.58, .28, .012],
                    [unit_x, height+.2, unit_z+.351], 'city_recess')
            for fin in range(6):
                add_box(f'hvac{unit}_fin{fin}', [.009, .25, .018],
                        [unit_x-.245+fin*.098, height+.2, unit_z+.361], 'city_equipment')
            add_cylinder(f'vent{unit}', .082, .43,
                         [unit_x, height+.215, depth*.27], 'city_equipment')
            add_cylinder(f'vent{unit}_cap', .112, .044,
                         [unit_x, height+.452, depth*.27], 'city_frame')
        for panel in range(2):
            panel_x = -width*.24+panel*1.32
            panel_z = depth*.16
            add_box(f'solar{panel}_rack', [1.2, .095, .7],
                    [panel_x, height+.095, panel_z], 'city_frame')
            add_box(f'solar{panel}', [1.16, .027, .74],
                    [panel_x, height+.21, panel_z], 'city_solar', rotation=[-12, 0, 0])
            for divider in range(4):
                add_box(f'solar{panel}_grid{divider}', [.012, .008, .74],
                        [panel_x-.43+divider*.285, height+.228, panel_z],
                        'city_sky_reflection', rotation=[-12, 0, 0])

        if use_compounds:
            asset_name = f's99_{prefix}_asset'
            compound_xml.append(f'    <CompoundAsset id="{asset_name}">\n' + '\n'.join(parts) + '\n    </CompoundAsset>')
            if batch_boxes:
                residual_models.append((prefix, asset_name, [world_x, GROUND_Y, world_z]))
                for material, boxes in boxes_by_material.items():
                    mesh_id = f's99_city_merged_{index}_{material}'
                    geometry_id = f'{mesh_id}_geometry'
                    vertices = []
                    faces = []
                    for size, position in boxes:
                        for quad in _box_faces(size, position):
                            first = len(vertices)
                            vertices.extend(quad)
                            faces.append((first, first + 1, first + 2, first + 3))
                    tags = [f'        <Vertex position={{[{x:.5f},{y:.5f},{z:.5f}]}} />'
                            for x, y, z in vertices]
                    tags.extend(f'        <Face indices={{[{a},{b},{c},{d}]}} />'
                                for a, b, c, d in faces)
                    merged_xml.append(f'    <GeometryAsset id="{geometry_id}">\n'
                                      f'      <Mesh>\n' + '\n'.join(tags) +
                                      f'\n      </Mesh>\n    </GeometryAsset>\n'
                                      f'    <MeshAsset id="{mesh_id}" material="{material}" geometry="{geometry_id}" />')
                    merged_models.append((f'city_merged_{index}_{material}_model', mesh_id,
                                          [world_x, GROUND_Y, world_z]))
            else:
                model(prefix, asset_name, [world_x, GROUND_Y, world_z])

    for name, asset, position in merged_models + residual_models:
        model(name, asset, position)
    return '\n'.join(compound_xml + merged_xml)
