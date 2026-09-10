#!/bin/sh
set -eu

root=$(CDPATH= cd -- "$(dirname -- "$0")" && pwd)
tmp_dir="${TMPDIR:-/tmp}/motionloom-s86-review"
mkdir -p "$tmp_dir"

# The clean turnaround measures 455 px from crown to chin. Register it to the
# rendered 600 px crown-to-chin span, preserving one scale for all three views.
magick -size 900x1000 canvas:'#ebe8e5' \
  \( "$root/face-reference.png" -crop 482x1086+0+0 +repage -resize 636x1432\! \) \
  -geometry +109-205 -composite "$tmp_dir/face-ref-front.png"
magick -size 900x1000 canvas:'#ebe8e5' \
  \( "$root/face-reference.png" -crop 483x1086+482+0 +repage -resize 637x1432\! \) \
  -geometry +145-205 -composite "$tmp_dir/face-ref-left.png"
magick -size 900x1000 canvas:'#ebe8e5' \
  \( "$root/face-reference.png" -crop 483x1086+965+0 +repage -resize 637x1432\! \) \
  -geometry +154-205 -composite "$tmp_dir/face-ref-back.png"

for view in front left back; do
  magick "$tmp_dir/face-ref-$view.png" "$root/face-$view.png" -compose blend \
    -define compose:args=50 -composite "$root/face-overlay-$view.png"
done

magick "$tmp_dir/face-ref-front.png" "$tmp_dir/face-ref-left.png" "$tmp_dir/face-ref-back.png" +append "$tmp_dir/face-reference-row.png"
magick "$root/face-front.png" "$root/face-left.png" "$root/face-back.png" +append "$tmp_dir/face-render-row.png"
magick "$root/face-overlay-front.png" "$root/face-overlay-left.png" "$root/face-overlay-back.png" +append "$tmp_dir/face-overlay-row.png"
magick "$tmp_dir/face-reference-row.png" "$tmp_dir/face-render-row.png" "$tmp_dir/face-overlay-row.png" -append "$root/face-review-contact-sheet.png"

# Retain the hair-turnaround comparison as a separate review artifact.
magick -size 900x1000 canvas:white \
  \( "$root/hair-reference.png" -crop 482x1086+0+0 +repage -resize 752x1695\! \) \
  -geometry +48-272 -composite "$tmp_dir/hair-ref-front.png"
magick "$root/hair-reference.png" -crop 482x620+483+155 +repage -resize 900x1000\! "$tmp_dir/hair-ref-three-quarter.png"
magick "$root/hair-reference.png" -crop 482x620+966+155 +repage -resize 900x1000\! "$tmp_dir/hair-ref-back.png"
for view in front three-quarter back; do
  magick "$tmp_dir/hair-ref-$view.png" "$root/$view.png" -compose blend \
    -define compose:args=50 -composite "$root/overlay-$view.png"
done
magick "$tmp_dir/hair-ref-front.png" "$tmp_dir/hair-ref-three-quarter.png" "$tmp_dir/hair-ref-back.png" +append "$tmp_dir/hair-reference-row.png"
magick "$root/front.png" "$root/three-quarter.png" "$root/back.png" +append "$tmp_dir/hair-render-row.png"
magick "$root/overlay-front.png" "$root/overlay-three-quarter.png" "$root/overlay-back.png" +append "$tmp_dir/hair-overlay-row.png"
magick "$tmp_dir/hair-reference-row.png" "$tmp_dir/hair-render-row.png" "$tmp_dir/hair-overlay-row.png" -append "$root/review-contact-sheet.png"
