#!/usr/bin/env python3
"""Convert a flattened SVGMaker character into an animated MotionLoom showcase."""

from __future__ import annotations

import argparse
import colorsys
import re
import xml.etree.ElementTree as ET
from pathlib import Path


NUMBER_RE = re.compile(r"-?\d+(?:\.\d+)?(?:[eE][-+]?\d+)?")
RGB_RE = re.compile(r"rgba?\(([^)]*)\)", re.IGNORECASE)
GRADIENT_REF_RE = re.compile(r"url\(\s*['\"]?#([^)\'\"\s]+)['\"]?\s*\)", re.IGNORECASE)


def local_name(tag: str) -> str:
    return tag.rsplit("}", 1)[-1]


def parse_rgb(value: str) -> tuple[int, int, int] | None:
    match = RGB_RE.fullmatch(value.strip())
    if not match:
        if value.startswith("#") and len(value) in (7, 9):
            return tuple(int(value[index : index + 2], 16) for index in (1, 3, 5))
        return None
    parts = [part.strip() for part in match.group(1).split(",")]
    if len(parts) < 3:
        return None
    return tuple(max(0, min(255, round(float(part)))) for part in parts[:3])


def hex_color(value: str) -> str:
    rgb = parse_rgb(value)
    return value if rgb is None else "#" + "".join(f"{channel:02X}" for channel in rgb)


def safe_dsl_id(value: str) -> str:
    safe = re.sub(r"[^A-Za-z0-9_-]+", "_", value).strip("_")
    if not safe:
        safe = "svg_gradient"
    if safe[0].isdigit():
        safe = f"svg_{safe}"
    return safe


def path_bounds(data: str) -> tuple[float, float, float, float]:
    numbers = [float(value) for value in NUMBER_RE.findall(data)]
    xs = numbers[0::2]
    ys = numbers[1::2]
    return min(xs), min(ys), max(xs), max(ys)


def gradient_average(stops: list[tuple[float, str, float]]) -> tuple[int, int, int] | None:
    colors = [parse_rgb(color) for _, color, _ in stops]
    colors = [color for color in colors if color is not None]
    if not colors:
        return None
    count = len(colors)
    return tuple(round(sum(color[index] for color in colors) / count) for index in range(3))


def is_hair_accent(
    fill: str,
    bounds: tuple[float, float, float, float],
    gradient_colors: dict[str, tuple[int, int, int] | None],
) -> bool:
    gradient = re.fullmatch(r"url\(#([^)]+)\)", fill)
    rgb = gradient_colors.get(gradient.group(1)) if gradient else parse_rgb(fill)
    if rgb is None:
        return False
    hue, lightness, saturation = colorsys.rgb_to_hls(*(channel / 255 for channel in rgb))
    hue *= 360
    if not (hue >= 325 or hue <= 3) or saturation < 0.22 or not (0.18 <= lightness <= 0.92):
        return False
    min_x, min_y, max_x, max_y = bounds
    center_x = (min_x + max_x) * 0.5
    center_y = (min_y + max_y) * 0.5
    crown = min_y < 510 and max_y < 900 and 150 < center_x < 880
    side_lock = min_y < 1180 and center_y < 940 and (center_x < 360 or center_x > 650)
    return crown or side_lock


def dsl_path(
    index: int,
    element: ET.Element,
    *,
    id_prefix: str = "character_path",
    opacity_scale: float = 1.0,
    gradient_ids: dict[str, str] | None = None,
) -> str:
    fill = element.attrib.get("fill", "#000000")
    gradient_match = GRADIENT_REF_RE.fullmatch(fill.strip())
    if gradient_match and gradient_ids:
        fill = f"url(#{gradient_ids.get(gradient_match.group(1), gradient_match.group(1))})"
    elif not gradient_match:
        fill = hex_color(fill)
    opacity = float(element.attrib.get("opacity", "1")) * float(
        element.attrib.get("fill-opacity", "1")
    ) * opacity_scale
    opacity_attr = "" if opacity >= 0.999 else f' opacity="{opacity:.4f}"'
    data = element.attrib.get("d", "").replace("&", "&amp;").replace('"', "&quot;")
    return f'                <Path id="{id_prefix}_{index:04d}" d="{data}" fill="{fill}"{opacity_attr} />'


def is_head_forehead_path(element: ET.Element) -> bool:
    data = element.attrib.get("d", "")
    if not data:
        return False
    min_x, min_y, max_x, max_y = path_bounds(data)
    return min_y < 650 and max_y <= 750 and max_x >= 100 and min_x <= 900


def build(
    input_path: Path,
    output_path: Path,
    *,
    head_focus: bool = False,
) -> tuple[int, int, int]:
    root = ET.parse(input_path).getroot()
    view_box = [float(value) for value in root.attrib.get("viewBox", "0 0 1024 2048").split()]
    _, _, width, height = view_box

    gradients: list[str] = []
    gradient_colors: dict[str, tuple[int, int, int] | None] = {}
    gradient_ids: dict[str, str] = {}
    for element in root.iter():
        if local_name(element.tag) == "linearGradient" and element.attrib.get("id"):
            source_id = element.attrib["id"]
            gradient_ids[source_id] = f"{safe_dsl_id(source_id)}_001"
    for element in root.iter():
        if local_name(element.tag) != "linearGradient":
            continue
        gradient_id = element.attrib["id"]
        imported_gradient_id = gradient_ids[gradient_id]
        stops: list[tuple[float, str, float]] = []
        for stop in element:
            if local_name(stop.tag) != "stop":
                continue
            offset_raw = stop.attrib.get("offset", "0").rstrip("%")
            offset = float(offset_raw) / (100 if stop.attrib.get("offset", "").endswith("%") else 1)
            color = stop.attrib.get("stop-color", "#000000")
            opacity = float(stop.attrib.get("stop-opacity", "1"))
            stops.append((offset, color, opacity))
        gradient_colors[gradient_id] = gradient_average(stops)
        stop_dsl = []
        for offset, color, opacity in stops:
            rgb = parse_rgb(color) or (0, 0, 0)
            alpha = max(0, min(255, round(opacity * 255)))
            encoded = "#" + "".join(f"{channel:02X}" for channel in (*rgb, alpha))
            stop_dsl.append(f"{offset:g}:{encoded}")
        gradients.append(
            f'      <LinearGradient id="{imported_gradient_id}" units="userSpaceOnUse" '
            f'x1="{element.attrib.get("x1", "0")}" y1="{element.attrib.get("y1", "0")}" '
            f'x2="{element.attrib.get("x2", "1")}" y2="{element.attrib.get("y2", "0")}" '
            f'stops="{", ".join(stop_dsl)}" />'
        )

    paths = [element for element in root.iter() if local_name(element.tag) == "path"]
    if head_focus:
        paths = [element for element in paths if is_head_forehead_path(element)]
    base_paths = [
        dsl_path(
            index,
            element,
            id_prefix="head_forehead_path" if head_focus else "character_path",
            gradient_ids=gradient_ids,
        )
        for index, element in enumerate(paths, 1)
    ]
    hair_paths = []
    for index, element in enumerate(paths, 1):
        data = element.attrib.get("d", "")
        if data and is_hair_accent(element.attrib.get("fill", ""), path_bounds(data), gradient_colors):
            hair_paths.append(
                dsl_path(
                    index,
                    element,
                    id_prefix="hair_accent_path",
                    opacity_scale=0.28,
                    gradient_ids=gradient_ids,
                )
            )

    if head_focus:
        content = f'''<!-- Focused head and forehead-hair study extracted from {input_path.name}. The original z-order and SVG gradients are preserved across {len(paths)} visible MotionLoom Paths. -->
<Graph fps={{30}} duration="6s" size={{[1024,750]}} renderSize={{[1024,750]}}>
  <Background color="#FFFDE2" />
  <Scene id="s55_head_forehead_400_path_study">
    <Defs>
{chr(10).join(gradients)}
      <Precompose id="head_forehead_crop_mask" size={{[1024,750]}}>
        <Path id="head_forehead_crop_shape"
              d="M 430 40 C 560 5 750 30 835 150 C 900 250 890 500 825 620 C 760 710 650 745 520 735 C 400 730 330 650 310 560 C 285 470 295 340 320 230 C 340 145 375 80 430 40 Z"
              fill="#FFFFFF" />
      </Precompose>
    </Defs>
    <Timeline>
      <Track id="head_forehead_art" space="screen" z="0">
        <Sequence from="0s" duration="6s" out="hold">
          <Layer id="head_forehead_layer">
            <Group id="head_forehead_400_path_group"
                   maskFrom="head_forehead_crop_mask"
                   maskMode="alpha"
                   maskFeather="0">
{chr(10).join(base_paths)}
            </Group>
          </Layer>
        </Sequence>
      </Track>
    </Timeline>
  </Scene>
  <Present from="s55_head_forehead_400_path_study" />
</Graph>
'''
    else:
        content = f'''<!-- Imported from {input_path.name} as MotionLoom Path DSL; SVG gradients are preserved in Scene Defs. -->
<Graph fps={{30}} duration="6s" size={{[{int(width)},{int(height)}]}} renderSize={{[{int(width)},{int(height)}]}}>
  <Background color="#FFFDE2" />
  <Scene id="animated_svg_character">
    <Defs>
{chr(10).join(gradients)}
    </Defs>
    <Timeline>
      <Track id="character_art" space="screen" z="0">
        <Sequence from="0s" duration="6s" out="hold">
          <Layer id="character_base_layer">
            <Group id="character_base_group">
{chr(10).join(base_paths)}
            </Group>

            <!-- The source is flattened, so selected pink hair highlights animate as a retained overlay. -->
            <Group id="hair_motion_group"
                   x={{curve("0:0:linear, 1.5:3:ease_in_out, 3:-2:ease_in_out, 4.5:4:ease_in_out, 6:0:ease_in_out")}}
                   y={{curve("0:0:linear, 1.5:-2:ease_in_out, 3:1:ease_in_out, 4.5:-3:ease_in_out, 6:0:ease_in_out")}}>
{chr(10).join(hair_paths)}
            </Group>

            <Group id="left_eye_blink_group"
                   opacity={{curve("0:0:linear, 1.72:0:linear, 1.80:1:ease_in, 1.92:1:linear, 2.02:0:ease_out, 4.66:0:linear, 4.74:1:ease_in, 4.86:1:linear, 4.96:0:ease_out, 6:0:linear")}}>
              <Path id="left_eye_lid_cover"
                    d="M 356 373 C 382 336 438 328 486 362 C 460 406 392 416 356 373 Z"
                    fill="#F7C6C2" />
              <Path id="left_eye_closed_line"
                    d="M 358 374 C 394 398 450 396 486 362"
                    fill="none" stroke="#6C263C" strokeWidth="8" />
            </Group>

            <Group id="right_eye_blink_group"
                   opacity={{curve("0:0:linear, 1.72:0:linear, 1.80:1:ease_in, 1.92:1:linear, 2.02:0:ease_out, 4.66:0:linear, 4.74:1:ease_in, 4.86:1:linear, 4.96:0:ease_out, 6:0:linear")}}>
              <Path id="right_eye_lid_cover"
                    d="M 526 360 C 562 330 618 336 650 374 C 612 412 550 404 526 360 Z"
                    fill="#F7C6C2" />
              <Path id="right_eye_closed_line"
                    d="M 526 360 C 562 396 620 398 650 374"
                    fill="none" stroke="#6C263C" strokeWidth="8" />
            </Group>
          </Layer>
        </Sequence>
      </Track>
    </Timeline>
  </Scene>
  <Present from="animated_svg_character" />
</Graph>
'''
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(content, encoding="utf-8")
    return len(paths), len(gradients), len(hair_paths)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("input", type=Path)
    parser.add_argument("output", type=Path)
    parser.add_argument(
        "--head-focus",
        action="store_true",
        help="Extract the S55 head and forehead-hair region as a 400+ Path study.",
    )
    args = parser.parse_args()
    path_count, gradient_count, hair_count = build(
        args.input,
        args.output,
        head_focus=args.head_focus,
    )
    print(f"generated {path_count} paths, {gradient_count} gradients, {hair_count} hair accents")


if __name__ == "__main__":
    main()
