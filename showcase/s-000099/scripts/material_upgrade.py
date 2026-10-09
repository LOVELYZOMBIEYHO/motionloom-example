"""S99 finish-specific PBR assets and metre-scaled geometry UV policies.

Maps are unmodified CC0 datasets. Roughness is a texture value multiplied by
the material factor, so calibrated sets use a neutral factor of one.
"""
from __future__ import annotations

TEXTURE_SETS = {
    'oak': ('white_oak_veneer', '2k', .5),
    'walnut': ('walnut_veneer_02', '1k', 1.0),
    'stone': ('marble_01', '1k', 1.5),
    'plaster': ('white_plaster_02', '1k', 1.0),
    'weave': ('terlenka', '1k', .266),
}


def image_assets() -> str:
    lines = []
    for label, (source, resolution, _) in TEXTURE_SETS.items():
        for slot, suffix, extension in [('color', 'diff', 'jpg'),
                                         ('normal', 'nor_gl', 'png'),
                                         ('arm', 'arm', 'png')]:
            color_space = 'srgb' if slot == 'color' else 'linear-srgb'
            lines.append(f'    <ImageAsset id="s99_{label}_{slot}" '
                         f'src="assets/pbr-v2/{source}/{source}_{suffix}_{resolution}.{extension}" '
                         f'colorSpace="{color_space}" />')
    for slot, suffix in [('color', 'Color'), ('normal', 'NormalGL'), ('rough', 'Roughness')]:
        color_space = 'srgb' if slot == 'color' else 'linear-srgb'
        lines.append(f'    <ImageAsset id="s99_worktop_{slot}" '
                     f'src="assets/pbr-v2/marble012/Marble012_2K-PNG_{suffix}.png" '
                     f'colorSpace="{color_space}" />')
    lines.append('    <ImageAsset id="s99_environment" '
                 'src="assets/environment-v2/kloofendal_overcast_puresky_2k.hdr" '
                 'colorSpace="linear-srgb" />')
    return '\n'.join(lines)


def pbr(identifier, source, *, tint='#FFFFFF', normal=.3, specular=.7,
        roughness=1, scale=None, ao=.2, albedo=True) -> str:
    tile = TEXTURE_SETS[source][2]
    repeats = scale if scale is not None else 1 / tile
    color = f' baseColorTexture="s99_{source}_color"' if albedo else ''
    return (f'    <MaterialAsset id="{identifier}" shading="pbr" baseColor="{tint}"{color}'
            f' normalTexture="s99_{source}_normal" normalScale="{normal}"'
            f' metallicRoughnessTexture="s99_{source}_arm" roughnessChannel="g" metallicChannel="b"'
            f' occlusionTexture="s99_{source}_arm" occlusionChannel="r" occlusionStrength="{ao}"'
            f' metallic="0" roughness="{roughness}" specular="{specular}"'
            f' textureScale={{[{repeats:.5g},{repeats:.5g}]}} />')


def material_assets() -> str:
    lines = [
        pbr('oak', 'oak', normal=.28),
        pbr('oak_floor', 'oak', normal=.32),
        pbr('walnut', 'walnut', normal=.22),
        # Default box UV puts V along Y on vertical faces. Use the oak source's
        # V-aligned grain for tall entry joinery; horizontal walnut grain is U.
        # This avoids rotating normal samples without rotating their tangent frame.
        pbr('vertical_oak_joinery', 'oak', tint='#D8BCA3', normal=.22),
        pbr('stone', 'stone', normal=.25, specular=.7),
        pbr('stone_interior', 'stone', normal=.18, specular=.85),
        # A neutral authored plaster tint avoids baked dirt in the source albedo.
        pbr('plaster', 'plaster', tint='#E8E3D8', normal=.12, specular=.55,
            albedo=False, ao=.1),
        pbr('ceiling', 'plaster', tint='#F3EEE4', normal=.08, specular=.45,
            albedo=False, ao=.08),
        pbr('linen_upholstery', 'weave', tint='#FFF9EF', normal=.45, specular=.6, ao=.18),
        pbr('sage_fabric', 'weave', tint='#A1B298', normal=.45, specular=.6, ao=.18),
        pbr('clay_fabric', 'weave', tint='#D9A381', normal=.45, specular=.6, ao=.18),
        pbr('woven_rug', 'weave', tint='#F1E7D4', normal=.6, specular=.35,
            scale=5.5, ao=.22),
        pbr('bedding_fabric', 'weave', tint='#FFFAF1', normal=.32, specular=.45, ao=.15),
        pbr('towel_fabric', 'weave', tint='#F1ECE1', normal=.6, specular=.35,
            scale=6, ao=.2),
        pbr('shade_fabric', 'weave', tint='#FFF5DF', normal=.2, specular=.4, ao=.12),
        '    <MaterialAsset id="worktop" shading="pbr" baseColor="#FFFFFF" '
        'baseColorTexture="s99_worktop_color" normalTexture="s99_worktop_normal" normalScale=".18" '
        'metallicRoughnessTexture="s99_worktop_rough" roughnessChannel="r" '
        'metallic="0" roughness="1" specular="1" textureScale={[.55,.55]} />',
        '    <MaterialAsset id="sage_joinery" shading="pbr" baseColor="#91A08A" roughness=".52" specular="1" />',
        '    <MaterialAsset id="book_cream" shading="pbr" baseColor="#EAE2D3" roughness=".9" specular=".2" />',
        '    <MaterialAsset id="book_sage" shading="pbr" baseColor="#7C8974" roughness=".85" specular=".2" />',
        '    <MaterialAsset id="art_canvas" shading="pbr" baseColor="#EAE2D3" roughness=".94" specular=".12" />',
        '    <MaterialAsset id="linen" shading="pbr" baseColor="#EAE2D3" roughness=".94" specular=".12" />',
        '    <MaterialAsset id="sage" shading="pbr" baseColor="#7C8974" roughness=".91" specular=".15" />',
        '    <MaterialAsset id="clay" shading="pbr" baseColor="#B56745" roughness=".87" />',
        '    <MaterialAsset id="terracotta" shading="pbr" baseColor="#A47256" roughness=".91" />',
        '    <MaterialAsset id="metal" shading="pbr" baseColor="#292E2B" metallic=".72" roughness=".36" />',
        '    <MaterialAsset id="brass" shading="pbr" baseColor="#B59758" metallic=".82" roughness=".3" />',
        '    <MaterialAsset id="glass" shading="pbr" baseColor="#F6FAF8" roughness=".04" transmission=".98" ior="1.52" thickness=".012" attenuationColor="#C9DFD4" attenuationDistance="8" depthWrite="auto" doubleSided="true" />',
        '    <MaterialAsset id="shower_glass" shading="pbr" baseColor="#F6FAF8" roughness=".065" transmission=".97" ior="1.52" thickness=".012" attenuationColor="#C3DECE" attenuationDistance="5" depthWrite="auto" doubleSided="true" />',
        '    <MaterialAsset id="mirror" shading="pbr" baseColor="#E5E5E5" metallic="1" roughness=".04" specular="1" transmission="0" doubleSided="false" />',
        '    <MaterialAsset id="ceramic" shading="pbr" baseColor="#E9E5DC" roughness=".24" specular=".65" />',
        '    <MaterialAsset id="light" shading="pbr" baseColor="#FFF2CF" roughness=".5" emissive="#FFD09A" emissiveStrength="3" />',
        '    <MaterialAsset id="soil" shading="pbr" baseColor="#393729" roughness="1" />',
        '    <MaterialAsset id="leaf" shading="pbr" baseColor="#59684A" roughness=".83" doubleSided="true" />',
        '    <MaterialAsset id="bark" shading="pbr" baseColor="#655744" roughness=".97" />',
        '    <MaterialAsset id="grass" shading="pbr" baseColor="#8A9475" roughness=".95" />',
        '    <MaterialAsset id="road" shading="pbr" baseColor="#686D67" roughness=".98" />',
        '    <MaterialAsset id="context" shading="pbr" baseColor="#B7BCAF" roughness=".96" />',
        '    <MaterialAsset id="bookblue" shading="pbr" baseColor="#667E82" roughness=".85" />',
    ]
    return image_assets() + '\n' + '\n'.join(lines) + '\n'


def surface_material(name: str, material: str) -> str:
    if material == 'walnut' and (name == 'entry' or name.startswith(('entry_slat', 'island_flute'))):
        return 'vertical_oak_joinery'
    if material == 'oak' and ('floor' in name or name.startswith('floor_plank')):
        return 'oak_floor'
    if material == 'stone' and name in {'hall_floor', 'bath_floor'}:
        return 'stone_interior'
    if material == 'sage':
        if name.startswith(('cabinet', 'wardrobe')):
            return 'sage_joinery'
        return 'book_sage' if name.startswith('book') else 'sage_fabric'
    if material == 'clay' and name.startswith('pillow'):
        return 'clay_fabric'
    if material == 'linen':
        if name.startswith('book'):
            return 'book_cream'
        if 'rug' in name:
            return 'woven_rug'
        if name == 'primary_art':
            return 'art_canvas'
        if name == 'towel':
            return 'towel_fabric'
        if any(part in name for part in ['mattress', 'duvet', 'bed_pillow', 'guest_pillow']):
            return 'bedding_fabric'
        return 'linen_upholstery'
    return material


TEXTURED = {'oak', 'oak_floor', 'walnut', 'vertical_oak_joinery', 'stone', 'stone_interior', 'plaster',
            'ceiling', 'worktop', 'linen_upholstery', 'sage_fabric', 'clay_fabric',
            'woven_rug', 'bedding_fabric', 'towel_fabric', 'shade_fabric'}


def uv_xml(shape, material, params) -> str:
    if material not in TEXTURED:
        return ''
    if shape in {'cylinder', 'cone'}:
        # Cylindrical U is a turn; scale it to metres of circumference before
        # applying the material's repeats-per-metre sampling multiplier.
        if 'radius' in params:
            radius = params['radius']
        else:
            radius = sum(params.get('bottomSize', [.3, .3])) / 4
        circumference = 2 * 3.141592653589793 * radius
        return f'\n      <UV mode="cylindrical" axis="y" scale={{[{circumference:.5g},1]}} />'
    # MotionLoom's frustum is rectangular, so face projection is metre-scaled;
    # cylindrical projection would stretch the lampshade weave around corners.
    return '\n      <UV mode="box" />'
