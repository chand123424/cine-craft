import shutil
import subprocess
from pathlib import Path

import imageio_ffmpeg

ASPECTS = {"9:16": (1080, 1920), "16:9": (1920, 1080), "1:1": (1080, 1080)}


def create_video(image_paths: list[str], audio_paths: list[str], durations: list[float], output: str, aspect_ratio: str, transition_seconds: float = 0, music_path: str | None = None) -> float:
    executable = shutil.which("ffmpeg") or imageio_ffmpeg.get_ffmpeg_exe()
    if not executable:
        raise RuntimeError("FFmpeg is required to create videos. Install it and ensure it is on PATH.")
    width, height = ASPECTS[aspect_ratio]
    output_path = Path(output)
    concat_file = output_path.with_suffix(".txt")
    with concat_file.open("w", encoding="utf-8") as file:
        for image, duration in zip(image_paths, durations):
            file.write(f"file '{Path(image).resolve().as_posix()}'\nduration {duration}\n")
        file.write(f"file '{Path(image_paths[-1]).resolve().as_posix()}'\n")
    command = [executable, "-y", "-f", "concat", "-safe", "0", "-i", str(concat_file)]
    for audio_path in audio_paths:
        command.extend(["-i", audio_path])
    if music_path:
        command.extend(["-i", music_path])
    video_filter = f"scale={width}:{height}:force_original_aspect_ratio=decrease,pad={width}:{height}:(ow-iw)/2:(oh-ih)/2"
    if transition_seconds:
        video_filter += f",fade=t=in:st=0:d={transition_seconds},fade=t=out:st={max(sum(durations) - transition_seconds, 0)}:d={transition_seconds}"
    audio_inputs = "".join(f"[{index + 1}:a]" for index in range(len(audio_paths)))
    filter_complex = f"{audio_inputs}concat=n={len(audio_paths)}:v=0:a=1[scene_audio]"
    audio_map = "[scene_audio]"
    if music_path:
        music_index = len(audio_paths) + 1
        filter_complex += f";[scene_audio][{music_index}:a]amix=inputs=2:duration=first:dropout_transition=2[mixed_audio]"
        audio_map = "[mixed_audio]"
    command.extend(["-filter_complex", filter_complex, "-vf", video_filter, "-map", "0:v", "-map", audio_map, "-t", str(sum(durations)), "-shortest", "-pix_fmt", "yuv420p", str(output_path)])
    subprocess.run(command, check=True, capture_output=True)
    return sum(durations)