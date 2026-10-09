use std::{env,fs,path::{Path,PathBuf},time::Instant};
use motionloom::api::{motionloom_analyze_script_json,parse_graph_script,set_scene_asset_roots,SceneRenderProfile,SceneRenderer};
use motionloom::{ImmediatePreviewProfile,ImmediatePreviewSettings};
use serde_json::{json,Value};
use sha2::{Digest,Sha256};

fn cpu_profile(renderer:&SceneRenderer)->Value {
    let p=renderer.last_cpu_frame_profile();
    json!({"expressionMs":p.expression_ms,"traversalMs":p.traversal_ms,"uploadMs":p.upload_ms,"encodeMs":p.encode_ms,"waitMs":p.wait_ms})
}
fn snapshot(renderer:&SceneRenderer,frame:u32,elapsed:f64)->Value {
    json!({"frame":frame,"submissionWallMs":elapsed,"compositorGpuFrameMs":renderer.last_gpu_frame_ms(),"sceneCpu":cpu_profile(renderer),"scene3d":renderer.last_3d_frame_profile()})
}
fn frames(arg:&str)->Result<Vec<u32>,Box<dyn std::error::Error>> {
    if arg=="-" || arg.is_empty() {return Ok(vec![]);}
    Ok(arg.split(',').map(str::parse).collect::<Result<Vec<u32>,_>>()?)
}
fn avg(values:&[f64])->f64 {values.iter().sum::<f64>()/values.len().max(1) as f64}
fn main()->Result<(),Box<dyn std::error::Error>> {
    let args=env::args().collect::<Vec<_>>();
    if args.len()<6 {return Err("usage: review_harness <script> <asset-root> <output-dir> <cinematic|balanced|ultra|portable> <frames-comma-list|-> [--benchmark=frames] [--warm=8] [--analyze-only]".into());}
    let script_path=Path::new(&args[1]);
    let asset_root=PathBuf::from(&args[2]);
    let output=PathBuf::from(&args[3]);
    fs::create_dir_all(&output)?;
    let profile=match args[4].as_str(){"cinematic"=>ImmediatePreviewProfile::Cinematic,"balanced"=>ImmediatePreviewProfile::Balanced,"ultra"=>ImmediatePreviewProfile::Ultra,"portable"=>ImmediatePreviewProfile::Portable,_=>return Err("unknown immediate profile".into())};
    let captures=frames(&args[5])?;
    let mut benchmarks=vec![];
    let mut warm_frames=8u32;
    let mut analyze_only=false;
    for arg in &args[6..] {
        if let Some(value)=arg.strip_prefix("--benchmark="){benchmarks=frames(value)?;}
        else if let Some(value)=arg.strip_prefix("--warm="){warm_frames=value.parse()?;}
        else if arg=="--analyze-only"{analyze_only=true;}
        else {return Err(format!("unknown argument {arg}").into());}
    }
    let all_start=Instant::now();
    let source=fs::read_to_string(script_path)?;
    let source_sha=format!("{:x}",Sha256::digest(source.as_bytes()));
    set_scene_asset_roots(vec![asset_root.clone()]);
    let analyze_started=Instant::now();
    let analysis=motionloom_analyze_script_json(&source);
    let authoring:Value=serde_json::from_str(&analysis)?;
    fs::write(output.join("authoring-report.json"),&analysis)?;
    println!("authoring: {} ({:.1} ms)",authoring["status"],analyze_started.elapsed().as_secs_f64()*1000.0);
    if analyze_only{return Ok(());}
    let parse_start=Instant::now();
    let graph=parse_graph_script(&source)?;
    let parse_ms=parse_start.elapsed().as_secs_f64()*1000.0;
    let total_frames=((graph.duration_ms as f64/1000.0)*graph.fps as f64).ceil().max(1.0) as u32;
    if captures.iter().chain(benchmarks.iter()).any(|&f|f>=total_frames){return Err(format!("frame out of range; frame count={total_frames}").into());}
    let settings=ImmediatePreviewSettings{profile,target_fps:30.0,dynamic_resolution:false,min_resolution_scale:1.0};
    let init_start=Instant::now();
    let mut renderer=pollster::block_on(SceneRenderer::new(SceneRenderProfile::Gpu))?;
    renderer.set_immediate_preview_settings(settings);
    let init_ms=init_start.elapsed().as_secs_f64()*1000.0;
    let mut capture_reports=vec![];
    let mut benchmark_reports=vec![];
    for requested in captures {
        let mut warm=vec![];
        for frame in requested.saturating_sub(warm_frames)..requested {
            let begin=Instant::now();
            let texture=pollster::block_on(renderer.render_frame_to_wgpu_texture(&graph,frame))?;
            let elapsed=begin.elapsed().as_secs_f64()*1000.0;
            warm.push(snapshot(&renderer,frame,elapsed));
            drop(texture);
        }
        let begin=Instant::now();
        let image=pollster::block_on(renderer.render_frame_gpu_readback(&graph,requested))?;
        let render_ms=begin.elapsed().as_secs_f64()*1000.0;
        let filename=format!("frame-{requested:04}.png");
        let save_start=Instant::now();
        image.save(output.join(&filename))?;
        let save_ms=save_start.elapsed().as_secs_f64()*1000.0;
        let report=json!({"frame":requested,"timeSeconds":requested as f64/graph.fps as f64,"file":filename,"dimensions":[image.width(),image.height()],"readbackRenderWallMs":render_ms,"saveMs":save_ms,"warmFrames":warm,"finalScene3d":renderer.last_3d_frame_profile(),"finalSceneCpu":cpu_profile(&renderer),"compositorGpuFrameMs":renderer.last_gpu_frame_ms()});
        fs::write(output.join(format!("frame-{requested:04}.json")),serde_json::to_vec_pretty(&report)?)?;
        println!("captured {} {}x{} warm={} final={:.1} ms",requested,image.width(),image.height(),warm_frames,render_ms);
        capture_reports.push(report);
        fs::write(output.join("review-report.json"),serde_json::to_vec_pretty(&json!({"captures":capture_reports,"benchmarks":benchmark_reports,"sourceSha256":source_sha,"inProgress":true}))?)?;
    }
    for requested in benchmarks {
        let mut warm=vec![];
        for frame in requested.saturating_sub(warm_frames)..requested {
            let begin=Instant::now();
            let texture=pollster::block_on(renderer.render_frame_to_wgpu_texture(&graph,frame))?;
            let elapsed=begin.elapsed().as_secs_f64()*1000.0;
            warm.push(snapshot(&renderer,frame,elapsed));
            drop(texture);
        }
        let mut samples=vec![];
        let mut wall_times=vec![];
        let mut gpu_times=vec![];
        for frame in requested..(requested+12).min(total_frames) {
            let begin=Instant::now();
            let texture=pollster::block_on(renderer.render_frame_to_wgpu_texture(&graph,frame))?;
            let elapsed=begin.elapsed().as_secs_f64()*1000.0;
            wall_times.push(elapsed);
            if let Some(ms)=renderer.last_gpu_frame_ms(){gpu_times.push(ms);}
            samples.push(snapshot(&renderer,frame,elapsed));
            drop(texture);
        }
        // Complete pending GPU work without adding its readback cost to the benchmark samples.
        let _sync=pollster::block_on(renderer.render_frame_gpu_readback(&graph,(requested+12).min(total_frames-1)))?;
        let benchmark=json!({"startFrame":requested,"sampleCount":samples.len(),"submissionWallMeanMs":avg(&wall_times),"reportedCompositorGpuMeanMs":if gpu_times.is_empty(){None}else{Some(avg(&gpu_times))},"gpuTimestampSupported":renderer.gpu_timestamp_supported(),"warmFrames":warm,"samples":samples,"interpretation":"Submission wall time includes CPU preparation, queue backpressure and submission; no PNG save or CPU readback in samples. GPU timestamps come from the Scene compositor, are asynchronously reported, and do not measure the full 3D GPU workload; they may refer to the most recently completed compositor submission. These samples are not certified playback FPS."});
        fs::write(output.join(format!("benchmark-{requested:04}.json")),serde_json::to_vec_pretty(&benchmark)?)?;
        println!("benchmark {} count={} submissionWallMean={:.1} ms",requested,samples.len(),avg(&wall_times));
        benchmark_reports.push(benchmark);
    }
    let result=json!({"schemaVersion":2,"sourceSha256":source_sha,"sourcePath":script_path,"assetRoot":asset_root,"settings":settings,"profileBudget":settings.budget(),"parseMs":parse_ms,"rendererInitMs":init_ms,"totalWallMs":all_start.elapsed().as_secs_f64()*1000.0,"warmFramesPerCapture":warm_frames,"gpuTimestampSupported":renderer.gpu_timestamp_supported(),"captures":capture_reports,"benchmarks":benchmark_reports,"inProgress":false,"renderScope":"Selected still frames, short consecutive-frame validation and warmed performance samples; no full video export."});
    fs::write(output.join("review-report.json"),serde_json::to_vec_pretty(&result)?)?;
    println!("review complete {:.1}s",all_start.elapsed().as_secs_f64());
    Ok(())
}
