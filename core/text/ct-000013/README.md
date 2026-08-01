# CT-000013 — Transparent Subtitle Shadow

A minimal overlay-ready subtitle treatment inspired by condensed documentary
titles: white `Impact` lettering on a transparent background with a soft black
shadow below it.

- `Background color="transparent"` preserves alpha.
- `fontFamily="Impact"` gives the title its condensed silhouette.
- `renderScale="auto"` keeps the edge clean without an unnecessarily heavy
  fixed supersampling cost.
- `TextAnimator` `Style` supplies the offset blurred shadow without duplicating
  the text.
