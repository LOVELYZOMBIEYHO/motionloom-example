#!/usr/bin/env python3
"""Assemble source-bound still comparisons and verify material asset provenance.

Requires Pillow and NumPy. It never renders a video or changes scene pixels:
figures only resize/crop the captured stills and add explanatory labels.
Render reports must already identify the exact reviewed DSL SHA-256.
"""
from __future__ import annotations

import gzip
import hashlib
import json
from pathlib import Path
import statistics

import numpy as np
from PIL import Image, ImageDraw, ImageFont

from verify_preservation import parse, walk

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / 'evidence/material-upgrade'


def digest(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def read(path: Path) -> dict:
    return json.loads(path.read_text())


def save(path: Path, data: object) -> None:
    path.write_text(json.dumps(data, indent=2, sort_keys=True) + '\n')


def font(size: int):
    for path in ['/System/Library/Fonts/Supplemental/Arial.ttf',
                 '/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf']:
        if Path(path).exists():
            return ImageFont.truetype(path, size)
    return ImageFont.load_default()


def sheet(filename: str, rows: list[list[tuple[str, str, int]]], width: int = 720):
    height = round(width * 9 / 16)
    label = 48
    columns = len(rows[0])
    canvas = Image.new('RGB', (width * columns, (height + label) * len(rows)), '#151C22')
    draw = ImageDraw.Draw(canvas)
    for row, cells in enumerate(rows):
        assert len(cells) == columns
        for column, (title, folder, frame) in enumerate(cells):
            x, y = width * column, (height + label) * row
            with Image.open(OUT / folder / f'frame-{frame:04d}.png') as source:
                image = source.convert('RGB').resize((width, height), Image.Resampling.LANCZOS)
            canvas.paste(image, (x, y + label))
            draw.text((x + 14, y + 10), title, font=font(24), fill='#F3F4F3')
    canvas.save(OUT / filename)


def material_detail():
    canvas = Image.new('RGB', (1600, 940), '#151C22')
    draw = ImageDraw.Draw(canvas)
    draw.text((20, 13), 'OAK  /  WORKTOP  /  WOVEN FABRIC  /  PLASTER — same scene finishes',
              font=font(25), fill='white')
    with Image.open(OUT / 'swatches/frame-0024.png') as source:
        board = source.convert('RGB').crop((380, 345, 1260, 565))
    canvas.paste(board.resize((1600, 400), Image.Resampling.LANCZOS), (0, 45))
    for column, frame in enumerate([48, 72]):
        x = column * 800
        draw.text((x + 18, 462), f'FINE WEAVE — raking light {column + 1}',
                  font=font(24), fill='white')
        with Image.open(OUT / 'swatches' / f'frame-{frame:04d}.png') as source:
            image = source.convert('RGB').resize((800, 450), Image.Resampling.LANCZOS)
        canvas.paste(image, (x, 490))
    canvas.save(OUT / 'swatches/material-detail.png')


def asset_check() -> dict:
    pbr = read(ROOT / 'assets/pbr-v2/provenance.json')
    files = []
    for dataset in pbr['sets']:
        assert dataset['license'] == 'CC0-1.0'
        for record in dataset['maps']:
            path = ROOT / 'assets/pbr-v2' / record['file']
            assert digest(path) == record['sha256'], path
            with Image.open(path) as image:
                assert image.size == (record['width'], record['height']), path
                image.verify()
            files.append({'file': str(path.relative_to(ROOT)), 'sha256': digest(path),
                          'bytes': path.stat().st_size})
    hdr = read(ROOT / 'assets/environment-v2/manifest.json')
    path = ROOT / 'assets/environment-v2' / hdr['asset']['localFile']
    assert digest(path) == hdr['asset']['sha256']
    assert hdr['asset']['license'] == 'CC0-1.0'
    assert hdr['validation']['finite'] and hdr['validation']['maximum'] > 1
    files.append({'file': str(path.relative_to(ROOT)), 'sha256': digest(path),
                  'bytes': path.stat().st_size})
    nodes = list(walk(parse((ROOT / 'main.motionloom').read_text())))
    images = {n.attrs['id']: n for n in nodes if n.tag == 'ImageAsset'}
    for identifier, image in images.items():
        assert (ROOT / image.attrs['src']).is_file(), identifier
        expected = 'srgb' if identifier.endswith('_color') else 'linear-srgb'
        assert image.attrs['colorSpace'] == expected, identifier
    materials = {n.attrs['id']: n for n in nodes if n.tag == 'MaterialAsset'}
    geometry = {n.attrs['id']: n for n in nodes if n.tag == 'GeometryAsset'}
    mapped_meshes = []
    for mesh in (n for n in nodes if n.tag == 'MeshAsset'):
        material = materials.get(mesh.attrs.get('material'))
        if material and 'normalTexture' in material.attrs:
            assert any(n.tag == 'UV' for n in walk(geometry[mesh.attrs['geometry']])), mesh.attrs['id']
            assert material.attrs.get('metallic') == 0
            assert material.attrs.get('roughness') == 1
            assert images[material.attrs['normalTexture']].attrs['colorSpace'] == 'linear-srgb'
            if material.attrs.get('metallicRoughnessTexture', '').endswith('_arm'):
                assert material.attrs['roughnessChannel'] == 'g'
                assert material.attrs['metallicChannel'] == 'b'
                assert material.attrs['occlusionChannel'] == 'r'
            mapped_meshes.append(mesh.attrs['id'])
    assert len(images) == 19 and len(files) == 19
    return {'status': 'passed', 'sourceMapAndHDRCount': len(files),
            'verifiedBytes': sum(f['bytes'] for f in files), 'files': files,
            'normalMappedMeshCountWithUV': len(mapped_meshes),
            'sourceMapsModified': False, 'imageGenUsed': False,
            'channelContract': 'Colour sRGB; OpenGL normal/ARM/roughness/HDR linear. ARM R=AO/G=roughness/B=metallic. Nonmetal factor 0 and roughness factor 1.',
            'materialExceptions': 'Clean plaster tint omits source albedo; worktop uses separate R roughness with no AO; tinted vertical oak keeps V grain along Y.'}


def timings(folder: str) -> dict:
    result = {}
    for frame in [360, 660]:
        data = read(OUT / folder / f'benchmark-{frame:04d}.json')
        samples = [s['submissionWallMs'] for s in data['samples']]
        resources = data['samples'][-1]['scene3d']
        result[str(frame)] = {
            'samples': len(samples), 'submissionMeanMs': statistics.mean(samples),
            'submissionMedianMs': statistics.median(samples),
            'submissionRangeMs': [min(samples), max(samples)],
            'gpuTextureResources': resources['gpu_texture_resources'],
            'gpuGeometryResources': resources['gpu_geometry_resources'],
            'drawCalls': resources['draw_calls'], 'visibleTriangles': resources['visible_triangles'],
            'renderTargetBytes': resources['render_target_bytes'],
            'warmTextureDecodes': sum(s['scene3d']['texture_decode_count'] for s in data['samples'])}
    return result


def main():
    source_sha = digest(ROOT / 'main.motionloom')
    baseline = read(OUT / 'baseline-scene-semantics.json')
    baseline_sha = baseline['sourceSHA256']
    assert hashlib.sha256(gzip.decompress((OUT / 'baseline-scene.motionloom.gz').read_bytes())).hexdigest() == baseline_sha
    preservation = read(OUT / 'preservation-check.json')
    assert preservation['status'] == 'passed' and preservation['sourceSHA256'] == source_sha
    geometry = read(ROOT / 'evidence/geometry-check.json')
    assert geometry['status'] == 'passed' and geometry['source_sha256'] == source_sha
    authoring = read(OUT / 'after/authoring-report.json')
    assert authoring['status'] == 'clean' and authoring['renderable']
    swatch_sha = digest(ROOT / 'scripts/material-swatches.motionloom')
    regeneration = read(OUT / 'regeneration-check.json')
    assert regeneration['status'] == 'passed'
    assert regeneration['mainSha256'] == source_sha
    assert regeneration['materialSwatchesSha256'] == swatch_sha
    reports = {}
    frames = []
    for folder, expected in [('after', source_sha), ('transition', source_sha),
                             ('after-balanced-repeat', source_sha), ('before', baseline_sha),
                             ('before-balanced-repeat', baseline_sha), ('swatches', swatch_sha),
                             ('material-only', None), ('environment-only', None)]:
        report = read(OUT / folder / 'review-report.json')
        assert not report['inProgress'], folder
        if expected:
            assert report['sourceSha256'] == expected, folder
        assert read(OUT / folder / 'authoring-report.json')['status'] == 'clean', folder
        reports[folder] = {'sourceSha256': report['sourceSha256'], 'settings': report['settings'],
                           'report': f'{folder}/review-report.json'}
        for capture in report['captures']:
            path = OUT / folder / capture['file']
            with Image.open(path) as image:
                assert list(image.size) == capture['dimensions']
            frames.append({'file': str(path.relative_to(OUT)), 'sha256': digest(path),
                           'frame': capture['frame'], 'dimensions': capture['dimensions'],
                           'sourceSha256': report['sourceSha256']})
    before = np.asarray(Image.open(OUT / 'before/frame-0000.png').convert('RGBA')).astype(np.int16)
    after = np.asarray(Image.open(OUT / 'after/frame-0000.png').convert('RGBA')).astype(np.int16)
    assert before.shape == after.shape
    changed = int(np.any(before != after, axis=2).sum())
    assert changed == 0
    opening = {'status': 'passed', 'baselineSourceSHA256': baseline_sha, 'sourceSHA256': source_sha,
               'differentPixels': changed, 'maximumChannelDifference': int(np.abs(before - after).max()),
               'beforePNG': digest(OUT / 'before/frame-0000.png'), 'afterPNG': digest(OUT / 'after/frame-0000.png')}
    save(OUT / 'opening-plan-comparison.json', opening)
    pairs = [(360, 'EXTERIOR'), (528, 'LIVING'), (660, 'KITCHEN'), (840, 'BEDROOM'), (984, 'DUSK')]
    sheet('before-after.png', [[(f'{name} | BEFORE', 'before', f),
                                 (f'{name} | AFTER', 'after', f)] for f, name in pairs])
    sheet('before-after-interiors.png', [[(f'{name} | BEFORE', 'before', f),
                                          (f'{name} | AFTER', 'after', f)] for f, name in pairs[1:3]])
    sheet('ablation.png', [[(f'{name} | {title}', folder, f) for title, folder in
                            [('BASELINE', 'before'), ('MATERIALS', 'material-only'),
                             ('LIGHT / HDR', 'environment-only'), ('COMBINED', 'after')]]
                          for f, name in [(528, 'LIVING'), (660, 'KITCHEN')]], width=640)
    sheet('transition.png', [[(f'{f/24:g}s | '+('BATH' if f == 912 else 'DUSK'), 'transition', f)
                              for f in [912, 936, 960]]], width=640)
    sheet('opening-ending.png', [[('OPENING | FRAME 0', 'after', 0), ('ENDING | FRAME 1055', 'after', 1055)]])
    material_detail()
    luminance = {}
    for frame in [360, 528, 660, 840, 880, 984, 1055]:
        image = np.asarray(Image.open(OUT / 'after' / f'frame-{frame:04d}.png').convert('RGB'))[:980]
        luminance[str(frame)] = {'sceneNearWhiteFraction': float(np.all(image >= 250, axis=2).mean()),
                                'sceneMeanEncodedRGB': image.mean(axis=(0, 1)).tolist()}
    save(OUT / 'after/still-luminance-summary.json', {'sourceSha256': source_sha,
         'method': 'Top 980 rows of 1080p encoded stills, excluding the bottom overlay. Near white requires all RGB channels >=250; this is a clipping diagnostic, not HDR radiometry.',
         'frames': luminance})
    save(OUT / 'validation-report.json', {
        'schemaVersion': 1, 'reviewDate': '2026-10-06', 'status': 'passed',
        'source': 'main.motionloom', 'sourceSha256': source_sha, 'baselineSourceSha256': baseline_sha,
        'deterministicRegeneration': regeneration,
        'authoring': {'status': authoring['status'], 'summary': authoring['summary']},
        'preservation': preservation, 'geometryStatus': geometry['status'],
        'assets': asset_check(), 'openingPlan': opening, 'renderReports': reports, 'frames': frames,
        'performance': {'before': timings('before-balanced-repeat'), 'after': timings('after-balanced-repeat'),
                        'method': 'Same strict GPU API, fixed 1920x1080 Balanced, eight warm frames, 12 texture-only submission samples per shot. Readback/save excluded from samples. Compositor timestamps are not full 3D GPU timings.',
                        'interpretation': 'Submission times vary with CPU work, queue backpressure and scheduling. No speedup, sustained playback FPS or 24 FPS guarantee is claimed. Retained textures increase; geometry, triangles and draws remain unchanged.'},
        'visualReview': {'houseFrames': [0,360,528,660,840,880,984,1055],
                         'transitionFrames': [912,936,960], 'swatchFrames': [0,24,48,72],
                         'observations': ['Wood pores/grain and stone pattern are more legible.',
                                          'Fine woven surface detail is visible at close range, while distant fabric stays matte.',
                                          'No obvious clipping or HDR brightness artifact in sampled stills; frame936 is the authored camera cut.']},
        'limits': ['WGPU screen-space indirect light/reflection approximations are profile-dependent; no new local reflection probes or multi-bounce indoor GI.',
                   'Fine polyester weave is reused artistically for fabric variants; no true fibres, folds, displacement or shear/fuzz model added.',
                   'Only sampled static frames were reviewed; full-motion temporal stability is not certified.'],
        'fullVideoExported': False, 'engineChangesRequired': False,
        'figures': ['before-after.png','before-after-interiors.png','ablation.png','transition.png',
                    'opening-ending.png','swatches/material-detail.png']})
    print(f'PASS: {len(frames)} source-bound captured stills, CC0 maps/HDR, opening pixels and protected scene; figures assembled.')


if __name__ == '__main__':
    main()
