#!/usr/bin/env bash
set -euo pipefail
root="$(cd "$(dirname "$0")/.." && pwd)"
domain="${1:-scene}"
case "$domain" in
  scene) prefix="cs" ;;
  world) prefix="cw" ;;
  process) prefix="cp" ;;
  composition) prefix="cm" ;;
  text) prefix="ct" ;;
  *)
    echo "Usage: $0 [scene|world|process|composition|text]" >&2
    exit 2
    ;;
esac
base="$root/core/$domain"
last="$(find "$base" -maxdepth 1 -type d -name "$prefix-[0-9][0-9][0-9][0-9][0-9][0-9]" -print 2>/dev/null | sed "s/.*$prefix-//" | sort -n | tail -1)"
next_num="$((10#${last:-0} + 1))"
id="$(printf '%s-%06d' "$prefix" "$next_num")"
dir="$base/$id"
mkdir -p "$dir"
case "$domain" in
  scene)
    cat > "$dir/main.motionloom" <<'EOF'
<Graph fps={30} duration="3s" size={[800,450]} renderSize={[800,450]}>
  <Background color="#FFFFFF" />
  <Scene id="ExampleScene">
    <Timeline>
      <Track id="main" space="world" z="0">
        <Sequence from="0s" duration="3s" out="hold">
          <Layer>
            <Text x="80" y="120" value="New Scene Core" fontSize="48" color="#111111" />
          </Layer>
        </Sequence>
      </Track>
    </Timeline>
  </Scene>
  <Present from="ExampleScene" />
</Graph>
EOF
    title="New Scene Core Example"
    features='["text"]'
    dsl='["text"]'
    requires='["Graph", "Scene", "Timeline", "Track", "Sequence", "Layer", "Text", "Present"]'
    ;;
  world)
    cat > "$dir/main.motionloom" <<'EOF'
<Graph fps={30} duration="3s" size={[800,450]} renderSize={[800,450]}>
  <Background color="#FFFFFF" />
  <World id="ExampleWorld">
    <Background color="#FFFFFF" />
    <Camera yaw="0" pitch="0" zoom="1" />
    <Actor id="basic_actor" model="../motionloom-example/assets/sample_assets/glb/mammuthus_primigenius_blumbach.glb" x="0" y="0" z="0" scale="0.35" opacity="1" />
  </World>
  <Present from="ExampleWorld" />
</Graph>
EOF
    title="New World Core Example"
    features='["actor"]'
    dsl='["actor"]'
    requires='["Graph", "World", "Camera", "Actor", "Present"]'
    ;;
  process)
    cat > "$dir/main.motionloom" <<'EOF'
<Graph fps={30} duration="3s" size={[800,450]} renderSize={[800,450]}>
  <Background color="#FFFFFF" />
  <Process id="ExampleProcess">
    <Input id="clip0" type="video" from="input:clip0" />
    <Tex id="src" fmt="rgba16f" from="clip0" />
    <Tex id="out" fmt="rgba16f" size={[800,450]} />
    <Pass id="fx_opacity" kind="compute" effect="opacity"
          in={["src"]} out={["out"]}
          params={{ opacity: "1.0" }} />
  </Process>
  <Present from="ExampleProcess" />
</Graph>
EOF
    title="New Process Core Example"
    features='["process"]'
    dsl='["process"]'
    requires='["Graph", "Process", "Input", "Tex", "Pass", "Present"]'
    ;;
  composition)
    cat > "$dir/main.motionloom" <<'EOF'
<Graph fps={30} duration="3s" size={[800,450]} renderSize={[800,450]}>
  <Background color="#FFFFFF" />

  <Scene id="ExampleScene">
    <Timeline>
      <Track id="scene_content" space="world" z="0">
        <Sequence from="0s" duration="3s" out="hold">
          <Layer>
            <Rect x="0" y="0" width="800" height="450" color="#FFFFFF" />
            <Text x="80" y="120" value="Scene Layer" fontSize="42" color="#111111" />
          </Layer>
        </Sequence>
      </Track>
    </Timeline>
  </Scene>

  <World id="ExampleWorld">
    <Background color="#FFFFFF" />
    <Actor id="basic_actor"
           model="../motionloom-example/assets/sample_assets/glb/mammuthus_primigenius_blumbach.glb"
           x="0" y="0" z="0" scale="0.35" opacity="1" />
  </World>

  <Process id="ExampleComposite">
    <Tex id="scene_tex" fmt="rgba16f" from="scene:ExampleScene" />
    <Tex id="world_tex" fmt="rgba16f" from="world:ExampleWorld" />
    <Tex id="out" fmt="rgba16f" size={[800,450]} />
    <Pass id="world_over_scene" kind="compute" effect="over"
          in={["scene_tex", "world_tex"]} out={["out"]} />
  </Process>

  <Present from="ExampleComposite" />
</Graph>
EOF
    title="New Scene World Process Core Example"
    features='["scene", "world", "process", "text", "shape", "actor", "gpu-pipeline"]'
    dsl='["Graph", "Background", "Scene", "Timeline", "Track", "Sequence", "Layer", "Rect", "Text", "World", "Actor", "Process", "Tex", "Pass", "Present"]'
    requires='["Graph", "Scene", "World", "Process", "Present"]'
    ;;
  text)
    cat > "$dir/main.motionloom" <<'EOF'
<Graph fps={30} duration="3s" size={[800,450]} renderSize={[800,450]}>
  <Background color="transparent" />
  <Scene id="ExampleText">
    <Timeline>
      <Track id="main" space="world" z="0">
        <Sequence from="0s" duration="3s" out="hold">
          <Layer>
            <Text x="240" y="180" value="New Text Core" fontSize="40" color="#FFFFFF"
                  fontWeight="700" textGap="-2" box="pill" boxColor="#D9251D"
                  boxPadding="54 28" boxRadius="999" />
          </Layer>
        </Sequence>
      </Track>
    </Timeline>
  </Scene>
  <Present from="ExampleText" />
</Graph>
EOF
    title="New Text Core Example"
    features='["text", "text-box", "text-gap"]'
    dsl='["Graph", "Background", "Scene", "Timeline", "Track", "Sequence", "Layer", "Text", "fontWeight", "textGap", "box"]'
    requires='["Graph", "Scene", "Timeline", "Track", "Sequence", "Layer", "Text", "Present"]'
    ;;
esac
cat > "$dir/example.json" <<EOF
{
  "id": "$id",
  "type": "core",
  "title": "$title",
  "domain": "$domain",
  "features": $features,
  "dsl": $dsl,
  "teaches": ["Create a new MotionLoom $domain core example."],
  "source_path": "",
  "demo_url": "",
  "related": [],
  "requires": $requires
}
EOF
cat > "$dir/README.md" <<EOF
# $title

ID: \`$id\`  
Type: \`core\`  
Domain: \`$domain\`

Open \`main.motionloom\`, copy all content, then paste it into the Anica VFX / MotionLoom page.
EOF
printf 'Created %s\n' "$dir"
