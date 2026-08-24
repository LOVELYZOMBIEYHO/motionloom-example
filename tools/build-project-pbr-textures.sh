#!/usr/bin/env bash
set -euo pipefail

ROOT="$(cd "$(dirname "$0")/.." && pwd)"
PBR="$ROOT/showcase/s-000074/assets/textures/pbr"
WORK="$(mktemp -d /tmp/motionloom-project-pbr.XXXXXX)"
trap 'rm -rf "$WORK"' EXIT

command -v magick >/dev/null || {
  echo "ImageMagick (magick) is required" >&2
  exit 1
}

normal_map() {
  local source="$1"
  local target="$2"
  local strength="$3"
  local name="$4"
  local height="$WORK/${name}-height.png"
  local nx="$WORK/${name}-nx.png"
  local ny="$WORK/${name}-ny.png"

  magick "$source" -alpha off -colorspace gray -resize 512x512! -blur 0x0.8 "$height"
  magick "$height" -fx "0.5 + ${strength}*(u.p{i-1,j}.r-u.p{i+1,j}.r)" "$nx"
  magick "$height" -fx "0.5 + ${strength}*(u.p{i,j-1}.r-u.p{i,j+1}.r)" "$ny"
  magick "$nx" "$ny" -size 512x512 xc:white -combine \
    -strip -define png:exclude-chunks=all PNG24:"$target"
}

roughness_map() {
  local source="$1"
  local target="$2"
  local spread="$3"
  local floor="$4"
  magick "$source" -alpha off -colorspace gray -resize 512x512! -auto-level \
    -evaluate Multiply "$spread" -evaluate Add "$floor" \
    -strip -define png:exclude-chunks=all PNG24:"$target"
}

metallic_roughness_map() {
  local roughness="$1"
  local target="$2"
  local metallic="$3"
  magick \( -size 512x512 xc:white \) "$roughness" \
    \( -size 512x512 "xc:gray($metallic)" \) -combine \
    -strip -define png:exclude-chunks=all PNG24:"$target"
}

ao_map() {
  local source="$1"
  local target="$2"
  magick "$source" -alpha off -colorspace gray -resize 512x512! -blur 0x1.4 -auto-level \
    -evaluate Multiply 0.18 -evaluate Add 80% \
    -strip -define png:exclude-chunks=all PNG24:"$target"
}

build_nonmetal() {
  local name="$1"
  local source="$PBR/${name}_base.jpg"
  local strength="$2"
  normal_map "$source" "$PBR/${name}_normal.png" "$strength" "$name"
  roughness_map "$source" "$WORK/${name}-roughness.png" 0.20 70%
  metallic_roughness_map "$WORK/${name}-roughness.png" \
    "$PBR/${name}_metallic_roughness.png" 0%
  ao_map "$source" "$PBR/${name}_ao.png"
}

build_nonmetal courtyard 0.9
build_nonmetal plaster 0.55
build_nonmetal weathered_concrete 1.0

normal_map "$PBR/brushed_metal_base.jpg" "$PBR/brushed_metal_normal.png" 0.45 metal
roughness_map "$PBR/brushed_metal_base.jpg" "$WORK/metal-roughness.png" 0.22 32%
metallic_roughness_map "$WORK/metal-roughness.png" \
  "$PBR/brushed_metal_metallic_roughness.png" 92%

roughness_map "$PBR/glass_roughness_source.png" "$WORK/glass-roughness.png" 0.22 10%
metallic_roughness_map "$WORK/glass-roughness.png" \
  "$PBR/glass_metallic_roughness.png" 0%

normal_map "$PBR/foliage_cluster.png" "$PBR/foliage_normal.png" 0.6 foliage
roughness_map "$PBR/foliage_cluster.png" "$WORK/foliage-roughness.png" 0.16 68%
metallic_roughness_map "$WORK/foliage-roughness.png" \
  "$PBR/foliage_metallic_roughness.png" 0%

# Re-encode every retained source/output without ancillary metadata.
for image in \
  "$ROOT/showcase/s-000074/assets/textures/Texture_Stone.jpg" \
  "$ROOT/showcase/s-000074/assets/textures/Texture_Wood.jpg" \
  "$PBR/courtyard_base.jpg" \
  "$PBR/plaster_base.jpg" \
  "$PBR/brushed_metal_base.jpg" \
  "$PBR/weathered_concrete_base.jpg"; do
  clean="$WORK/$(basename "$image")"
  magick "$image" -strip -quality 88 "$clean"
  mv "$clean" "$image"
done

for image in "$PBR"/*.png; do
  clean="$WORK/$(basename "$image")"
  if [[ "$(magick identify -format '%[channels]' "$image")" == *a* ]]; then
    magick "$image" -strip -define png:exclude-chunks=all PNG32:"$clean"
  else
    magick "$image" -strip -define png:exclude-chunks=all PNG24:"$clean"
  fi
  mv "$clean" "$image"
done

echo "Rebuilt project-owned PBR maps under $PBR"
