use std::{env, fs, path::PathBuf, time::Instant};
use motionloom::api::{motionloom_analyze_script_json, parse_graph_script, set_scene_asset_roots, SceneRenderProfile, SceneRenderer};
use motionloom::{ImmediatePreviewProfile, ImmediatePreviewSettings};
use serde_json::json;

fn main() -> Result<(), Box<dyn std::error::Error>> {
    let args: Vec<String> = env::args().collect();
    if args.len() != 5 {
        return Err("usage: realism_review <script> <asset-root> <output-dir> <frames-comma-list>".into());
    }
    let source = fs::read_to_string(&args[1])?;
    let output = PathBuf::from(&args[3]);
    fs::create_dir_all(&output)?;
    set_scene_asset_roots(vec![PathBuf::from(&args[2])]);
    let analysis = motionloom_analyze_script_json(&source);
    fs::write(output.join("authoring-report.json"), &analysis)?;
    let graph = parse_graph_script(&source)?;
    let settings = ImmediatePreviewSettings {
        profile: ImmediatePreviewProfile::Cinematic,
        target_fps: 30.0,
        dynamic_resolution: false,
        min_resolution_scale: 1.0,
    };
    let mut captures = Vec::new();
    for requested in args[4].split(',').map(str::parse::<u32>) {
        let frame = requested?;
        if frame as f64 >= graph.duration_ms as f64 * graph.fps as f64 / 1000.0 {
            return Err("frame outside graph duration".into());
        }
        // Isolate captures across timeline islands; settle TAA at the exact sample time.
        let mut renderer = pollster::block_on(SceneRenderer::new(SceneRenderProfile::Gpu))?;
        renderer.set_immediate_preview_settings(settings);
        for _ in 0..8 {
            let _ = pollster::block_on(renderer.render_frame_to_wgpu_texture(&graph, frame))?;
        }
        let start = Instant::now();
        let image = pollster::block_on(renderer.render_frame_gpu_readback(&graph, frame))?;
        let render_ms = start.elapsed().as_secs_f64() * 1000.0;
        let filename = format!("frame-{frame:04}.png");
        image.save(output.join(&filename))?;
        captures.push(json!({"frame":frame,"timeSeconds":frame as f64 / graph.fps as f64,
            "file":filename,"dimensions":[image.width(),image.height()],"readbackRenderWallMs":render_ms,
            "scene3d":renderer.last_3d_frame_profile()}));
        println!("captured frame {frame}, {render_ms:.1} ms");
    }
    fs::write(output.join("review-report.json"), serde_json::to_vec_pretty(&json!({
        "sourcePath":args[1],"assetRoot":args[2],"settings":settings,"warmFramesPerCapture":8,
        "capturePolicy":"Fresh renderer per still; TAA settles at the exact requested frame.",
        "captures":captures,"scope":"Selected still frames only; no full video export."
    }))?)?;
    Ok(())
}
