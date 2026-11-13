#!/usr/bin/env python3
"""Render a non-AI Mint Leaf studio tour from the original repository media."""
import pathlib, subprocess, os
ROOT=pathlib.Path(__file__).resolve().parents[1]
OUT=ROOT/"studio-tour-output"
OUT.mkdir(exist_ok=True)
VIDEOS=[
"VID_20261111_004228_091.mp4","VID_20261111_004233_681.mp4",
"VID_20261111_004237_288.mp4","VID_20261111_004242_376.mp4",
"VID_20261111_004249_556.mp4","VID_20261111_004257_667.mp4",
"VID_20261111_004300_284.mp4","VID_20261111_004304_262.mp4",
"VID_20261111_004310_278.mp4","VID_20261111_004313_013.mp4",
"VID_20261111_004329_022.mp4","VID_20261111_004330_879.mp4",
"VID_20261111_004332_617.mp4"]
# Photo capture timestamps aren't available. Photo order follows a studio walkthrough,
# not an invented chronological capture sequence.
PHOTOS=[
"storefront.webp","welcome.webp","reception.webp","waiting-area.jpg",
"hallway.webp","studio.webp","massage-room (2).jpg","room.webp",
"treatment.webp","therapist.webp","sculpture.webp","tea.webp","products.webp"]
W,H=1920,1080
# Preserve the whole portrait frame. Fill side areas with softly blurred copies
# rather than crop subjects or add black pillarboxing.
FILTER=("[0:v]split=2[fg][bg];"
        "[bg]scale=1920:1080:force_original_aspect_ratio=increase,"
        "crop=1920:1080,boxblur=18:5[blur];"
        "[fg]scale=1920:1080:force_original_aspect_ratio=decrease[front];"
        "[blur][front]overlay=(W-w)/2:(H-h)/2,setsar=1,"
        "fps=30,format=yuv420p[v]")
def run(cmd):
    print("RUN", " ".join(map(str,cmd)),flush=True)
    subprocess.run(cmd,check=True)
def duration(path):
    p=subprocess.run(["ffprobe","-v","error","-show_entries","format=duration",
        "-of","default=noprint_wrappers=1:nokey=1",str(path)],capture_output=True,text=True,check=True)
    return float(p.stdout.strip())
segments=[]
for idx,video in enumerate(VIDEOS):
    v=ROOT/video
    if not v.exists(): raise FileNotFoundError(v)
    length=max(0.5,duration(v)-1.0) # trim the social-media outro
    dest=OUT/f"segment_{len(segments):03d}.mp4"
    run(["ffmpeg","-y","-hide_banner","-loglevel","error","-i",str(v),
         "-filter_complex",FILTER,"-map","[v]","-an","-t",str(length),
         "-c:v","libx264","-preset","veryfast","-crf","22","-pix_fmt","yuv420p",str(dest)])
    segments.append(dest)
    pic=ROOT/PHOTOS[idx]
    if not pic.exists(): raise FileNotFoundError(pic)
    dest=OUT/f"segment_{len(segments):03d}.mp4"
    run(["ffmpeg","-y","-hide_banner","-loglevel","error","-loop","1","-framerate","30","-i",str(pic),
         "-filter_complex",FILTER,"-map","[v]","-an","-t","3.5",
         "-c:v","libx264","-preset","veryfast","-crf","22","-pix_fmt","yuv420p",str(dest)])
    segments.append(dest)
playlist=OUT/"concat.txt"
playlist.write_text("".join("file '"+str(x.resolve()).replace("'","'\\''")+"'\n" for x in segments))
run(["ffmpeg","-y","-hide_banner","-loglevel","error","-f","concat","-safe","0","-i",str(playlist),
     "-c","copy","-movflags","+faststart",str(OUT/"mint-leaf-studio-tour.mp4")])
print("FINISHED:",OUT/"mint-leaf-studio-tour.mp4")
