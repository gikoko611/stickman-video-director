#!/usr/bin/env python3
"""GI KO KO cinematic Myanmar village story renderer.
Uses Deepgram Aura-2 for role-specific English dialogue, Pillow for original
illustrated 2.5D scene plates, and FFmpeg for camera motion, subtitles and export.
"""
import os, sys, json, time, math, subprocess, urllib.request, urllib.error
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont, ImageFilter

ROOT = Path(__file__).resolve().parents[2]
OUT = ROOT / "output"
WORK = OUT / "work"
W, H, FPS = 1280, 720, 12
MAX_BYTES = 10_000_000
API_KEY = os.environ.get("DEEPGRAM_API_KEY", "").strip()
if not API_KEY:
    raise SystemExit("DEEPGRAM_API_KEY secret is missing.")
OUT.mkdir(parents=True, exist_ok=True)
WORK.mkdir(parents=True, exist_ok=True)

# Role-specific voices. All are English Aura-2 voices; Burmese is subtitle-only.
VOICES = {
    "narrator": "aura-2-thalia-en",
    "boy": "aura-2-orion-en",
    "mother": "aura-2-luna-en",
    "friend": "aura-2-zeus-en",
    "farmer": "aura-2-asteria-en",
}
# 24 authored dialogue beats: each English line has a meaning-matched Burmese subtitle.
BEATS = [
("narrator","In a quiet village beside the green hills of Myanmar, the morning began with birdsong.","မြန်မာနိုင်ငံရဲ့ စိမ်းလန်းတဲ့ တောင်ကုန်းတွေအနီးက ရွာလေးမှာ မနက်ခင်းဟာ ငှက်ကလေးတွေရဲ့ တေးသံနဲ့ စတင်ခဲ့တယ်။","village"),
("narrator","Twelve-year-old Min Thu loved his little calf, Shwe Wah, more than anything.","အသက် ဆယ့်နှစ်နှစ်အရွယ် မင်းသူဟာ သူ့ရဲ့ နွားကလေး ရွှေဝါကို အရာအားလုံးထက် ပိုချစ်တယ်။","yard"),
("mother","Min Thu, please bring Shwe Wah home before the rain arrives.","မင်းသူရေ၊ မိုးမရွာခင် ရွှေဝါကို အိမ်ပြန်ခေါ်လာခဲ့နော်။","yard"),
("boy","I will, Mother. We will be back before the first thunder.","ဟုတ်ကဲ့ အမေ။ မိုးခြိမ်းသံ ပထမဆုံးမကြားခင် ပြန်လာခဲ့မယ်။","yard"),
("narrator","But when Min Thu reached the bamboo pasture, the little calf was gone.","ဒါပေမဲ့ မင်းသူ ဝါးခြံဝင်းကို ရောက်တဲ့အခါ နွားကလေးဟာ ပျောက်နေခဲ့ပြီ။","pasture"),
("boy","Shwe Wah! Where are you? This is not a game. Please answer me!","ရွှေဝါရေ။ မင်း ဘယ်မှာလဲ။ ဒါ ကစားတာမဟုတ်ဘူးနော်။ ပြန်ထူးပါဦး။","pasture"),
("narrator","He found tiny hoofprints leading away from the field and into the forest path.","လယ်ကွင်းကနေ တောလမ်းလေးဘက်ကို ဦးတည်နေတဲ့ ခွာရာသေးသေးလေးတွေကို သူတွေ့ခဲ့တယ်။","path"),
("friend","Min Thu! I heard you calling. What happened to your calf?","မင်းသူရေ။ မင်းခေါ်နေတာ ကြားလို့ လာခဲ့တာ။ နွားကလေး ဘာဖြစ်လို့လဲ။","path"),
("boy","Shwe Wah is missing. I found these tracks, but the clouds are getting dark.","ရွှေဝါ ပျောက်နေတယ်။ ဒီခြေရာတွေ တွေ့ထားပေမဲ့ တိမ်တွေက မည်းလာပြီ။","path"),
("friend","Then we search together. Two pairs of eyes are better than one.","ဒါဆို အတူရှာကြမယ်။ လူနှစ်ယောက်ဆို ပိုပြီး သေချာရှာနိုင်တယ်။","path"),
("narrator","They crossed a wooden bridge, listening carefully beneath the rustling bamboo.","သူတို့ဟာ ဝါးရွက်တွေ လှုပ်ခတ်သံကို နားစွင့်ရင်း သစ်သားတံတားလေးကို ဖြတ်ကျော်ခဲ့ကြတယ်။","bridge"),
("boy","Wait. Did you hear that soft bell near the old teak trees?","ခဏနေဦး။ ကျွန်းပင်အိုကြီးတွေနားက ခေါင်းလောင်းသံလေး ကြားလိုက်သလား။","forest"),
("friend","Yes! It came from beyond those rocks. Let us move slowly.","ကြားတယ်။ ဟိုကျောက်တုံးတွေရဲ့ ဟိုဘက်က လာတာ။ ဖြည်းဖြည်းသွားကြရအောင်။","forest"),
("narrator","Behind a fallen branch, Shwe Wah stood frightened beside a shallow muddy stream.","လဲကျနေတဲ့ သစ်ကိုင်းတစ်ခုရဲ့ နောက်မှာ ရွှေဝါဟာ ရွှံ့ရေချောင်းလေးဘေးမှာ ကြောက်လန့်စွာ ရပ်နေခဲ့တယ်။","stream"),
("boy","Shwe Wah! You are safe. I have been looking everywhere for you.","ရွှေဝါရေ။ မင်း ဘေးကင်းနေပြီ။ ငါ နေရာတိုင်း လိုက်ရှာနေတာ။","stream"),
("narrator","The calf had slipped into soft mud and could not climb the slippery bank.","နွားကလေးဟာ ပျော့နေတဲ့ ရွှံ့ထဲ ချော်ကျပြီး ချောနေတဲ့ ကမ်းပါးပေါ် ပြန်မတက်နိုင်ဖြစ်နေခဲ့တယ်။","stream"),
("friend","I will hold the branch. You guide her gently toward the flat stones.","ငါ သစ်ကိုင်းကို ကိုင်ထားမယ်။ မင်းက သူ့ကို ကျောက်ပြားတွေဆီ ဖြည်းဖြည်း ခေါ်ပေး။","stream"),
("boy","Easy, little one. One step... now another. You can do it!","ဖြည်းဖြည်းနော် ကလေးလေး။ တစ်လှမ်း... နောက်တစ်လှမ်း။ မင်း လုပ်နိုင်တယ်။","stream"),
("narrator","Together they freed the calf just as the first warm drops of rain began to fall.","သူတို့နှစ်ယောက် အတူကြိုးစားပြီး နွားကလေးကို ကယ်နိုင်ခဲ့ချိန်မှာပဲ မိုးစက်နွေးနွေးလေးတွေ စကျလာခဲ့တယ်။","rain"),
("farmer","There you are! I brought a lantern and a rope. Your mother is waiting.","ဒီမှာပဲ ရှိနေကြတာကိုး။ မီးအိမ်နဲ့ ကြိုး ယူလာတယ်။ မင်းအမေ စောင့်နေတယ်။","rain"),
("boy","Thank you, Uncle. We found her because we did not give up.","ကျေးဇူးတင်ပါတယ် ဦးလေး။ ကျွန်တော်တို့ လက်မလျှော့ခဲ့လို့ သူ့ကို ရှာတွေ့ခဲ့တာပါ။","rain"),
("narrator","Under the lantern glow, the three friends guided Shwe Wah back through the rain.","မီးအိမ်ရောင်အောက်မှာ သူငယ်ချင်းသုံးယောက်ဟာ မိုးရေထဲကနေ ရွှေဝါကို အိမ်ပြန်ခေါ်လာခဲ့ကြတယ်။","home"),
("mother","My brave boy! And my precious Shwe Wah. I am so glad you are home.","ငါ့သားလေးက တကယ်သတ္တိရှိတာပဲ။ ချစ်ရတဲ့ ရွှေဝါလေးလည်း ပြန်ရောက်လာပြီ။ ဝမ်းသာလိုက်တာ။","home"),
("narrator","That night Min Thu learned that courage grows stronger when friends stand together.","အဲဒီညမှာ မင်းသူ သိလိုက်ရတာက သူငယ်ချင်းတွေ အတူရပ်တည်တဲ့အခါ သတ္တိဟာ ပိုမိုကြီးထွားလာတယ် ဆိုတာပါပဲ။","home"),
]

def run(cmd):
    p = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
    if p.returncode:
        raise RuntimeError(f"Command failed: {' '.join(map(str,cmd))}\n{p.stderr[-3000:]}")
    return p.stdout.strip()

def log(msg):
    print(f"::notice::{msg}", flush=True)
    print(msg, flush=True)

def tts(text, model, dest):
    url = f"https://api.deepgram.com/v1/speak?model={model}&encoding=mp3"
    body = json.dumps({"text": text}).encode()
    req = urllib.request.Request(url, data=body, headers={
        "Authorization": f"Token {API_KEY}",
        "Content-Type": "application/json",
        "Accept": "audio/mpeg",
    }, method="POST")
    for attempt in range(3):
        try:
            with urllib.request.urlopen(req, timeout=120) as res:
                data = res.read()
                if len(data) < 1000:
                    raise RuntimeError("Deepgram returned an unexpectedly small audio response.")
                dest.write_bytes(data)
                return
        except urllib.error.HTTPError as e:
            detail = e.read().decode("utf-8", "replace")[:1000]
            if e.code in (401, 402, 403):
                raise RuntimeError(f"Deepgram rejected the key/model (HTTP {e.code}): {detail}")
            if attempt == 2:
                raise RuntimeError(f"Deepgram TTS failed (HTTP {e.code}): {detail}")
            time.sleep(2 ** attempt)
        except Exception:
            if attempt == 2: raise
            time.sleep(2 ** attempt)

def duration(file):
    return float(run(["ffprobe","-v","error","-show_entries","format=duration","-of","default=nw=1:nk=1",str(file)]))

def font_path():
    candidates = [
        "/usr/share/fonts/truetype/noto/NotoSansMyanmar-Regular.ttf",
        "/usr/share/fonts/truetype/noto/NotoSansMyanmar[wght].ttf",
    ]
    for p in candidates:
        if Path(p).exists(): return p
    # Subtitle burn-in uses libass fontconfig fallback if the exact file is elsewhere.
    return ""

def lerp(a,b,t): return int(a+(b-a)*t)

def draw_gradient(draw, top, bottom):
    for y in range(H):
        t=y/(H-1)
        c=tuple(lerp(top[i],bottom[i],t) for i in range(3))
        draw.line((0,y,W,y),fill=c)

def person(d, x, y, scale=1.0, role="boy", pose=0):
    # Layered, softly shaded stylized characters; coordinates are ground-centred.
    palette={"boy":("#e9b879","#203d4a","#d7a14c"),"friend":("#d99e72","#31513c","#c88d4c"),
             "mother":("#e9bd91","#7e3548","#d4a75e"),"farmer":("#bd8b63","#4c5140","#8d633d")}
    skin,shirt,lower=palette.get(role,palette["boy"])
    s=scale
    # soft ground shadow
    d.ellipse((x-42*s,y-8*s,x+42*s,y+10*s),fill=(28,35,28,90))
    # legs
    hip=(x,y-70*s)
    if pose%2:
        d.line((hip[0],hip[1],x-17*s,y-7*s),fill=lower,width=max(5,int(12*s)))
        d.line((hip[0],hip[1],x+23*s,y-8*s),fill=lower,width=max(5,int(12*s)))
    else:
        d.line((hip[0],hip[1],x-23*s,y-8*s),fill=lower,width=max(5,int(12*s)))
        d.line((hip[0],hip[1],x+17*s,y-8*s),fill=lower,width=max(5,int(12*s)))
    # torso
    d.rounded_rectangle((x-23*s,y-150*s,x+23*s,y-65*s),radius=int(17*s),fill=shirt)
    # arms
    d.line((x-18*s,y-137*s,x-48*s,y-95*s),fill=skin,width=max(5,int(11*s)))
    d.line((x+18*s,y-137*s,x+48*s,y-103*s),fill=skin,width=max(5,int(11*s)))
    # head and hair
    d.ellipse((x-29*s,y-213*s,x+29*s,y-153*s),fill=skin,outline=(65,49,39),width=max(1,int(2*s)))
    d.pieslice((x-31*s,y-220*s,x+31*s,y-160*s),180,355,fill=(42,35,29))
    d.ellipse((x+7*s,y-190*s,x+12*s,y-185*s),fill=(30,25,20))
    if role=="mother":
        d.arc((x-33*s,y-220*s,x+33*s,y-155*s),180,355,fill=(48,32,28),width=max(3,int(8*s)))

def calf(d,x,y,s=1.0):
    # Small white calf with brown patches, bell and expressive face.
    d.ellipse((x-63*s,y-70*s,x+61*s,y-12*s),fill="#f0e7d2",outline="#8b7860",width=2)
    d.ellipse((x+28*s,y-98*s,x+83*s,y-48*s),fill="#f0e7d2",outline="#8b7860",width=2)
    d.ellipse((x+60*s,y-82*s,x+68*s,y-74*s),fill="#27211d")
    d.ellipse((x-45*s,y-65*s,x-12*s,y-25*s),fill="#9b6848")
    for lx in [-38,25]:
        d.line((x+lx*s,y-24*s,x+(lx-2)*s,y+4*s),fill="#57483b",width=max(3,int(7*s)))
    d.line((x+48*s,y-96*s,x+43*s,y-111*s),fill="#8b7860",width=max(2,int(4*s)))
    d.ellipse((x+41*s,y-115*s,x+48*s,y-108*s),fill="#d5ad55")

def scene_plate(index, beat):
    who, text, my, place = beat
    img=Image.new("RGB",(W,H))
    d=ImageDraw.Draw(img)
    moods={
      "village":((80,143,177),(238,194,129),"#426b48"),
      "yard":((93,155,184),(242,197,131),"#58784a"),
      "pasture":((92,153,174),(224,190,129),"#4c7547"),
      "path":((76,130,151),(211,173,121),"#345c42"),
      "bridge":((68,116,145),(196,163,119),"#315b45"),
      "forest":((52,91,105),(160,137,96),"#244d38"),
      "stream":((59,117,139),(185,162,119),"#315a45"),
      "rain":((49,71,91),(119,111,98),"#304b42"),
      "home":((42,55,74),(181,122,83),"#294638"),
    }
    top,bottom,green=moods[place]
    draw_gradient(d,top,bottom)
    # distant mountain silhouettes
    for j,(yy,col) in enumerate([(300,"#6d8875"),(355,"#526f58"),(405,green)]):
        pts=[(0,H),(0,yy+70)]
        for xx in range(0,W+100,100):
            pts.append((xx,yy+int(30*math.sin((xx+index*31+j*19)/145))+int(18*math.cos(xx/87))))
        pts.append((W,H))
        d.polygon(pts,fill=col)
    # sun / moon glow
    sun=(1040-(index%4)*45,145+(index%3)*22)
    d.ellipse((sun[0]-68,sun[1]-68,sun[0]+68,sun[1]+68),fill="#f5d79a")
    # fields, path and water
    d.polygon([(0,510),(W,465),(W,H),(0,H)],fill="#66804a" if place not in ("rain","home") else "#455c48")
    if place in ("stream","bridge","rain"):
        d.polygon([(0,570),(W,520),(W,650),(0,700)],fill="#587f87")
        for yy in range(575,680,22):
            d.line((40,yy,W-30,yy-35),fill="#91b5ae",width=2)
    else:
        d.polygon([(500,720),(690,720),(830,450),(690,450)],fill="#b89a6d")
    # trees at varied depth
    for tx,ty,sc in [(95,460,1.0),(240,430,.8),(1090,455,1.15),(1200,430,.75)]:
        d.rectangle((tx-9*sc,ty-115*sc,tx+9*sc,ty+5),fill="#594a35")
        for ox,oy,r in [(-28,-120,48),(15,-145,54),(0,-190,46)]:
            d.ellipse((tx+(ox-r)*sc,ty+(oy-r)*sc,tx+(ox+r)*sc,ty+(oy+r)*sc),fill="#315c42")
    # bamboo hut in village/home
    if place in ("village","yard","home"):
        d.rectangle((850,355,1120,520),fill="#76543b")
        d.polygon([(810,360),(980,245),(1160,360)],fill="#473a32")
        for x in range(870,1110,26): d.line((x,360,x,515),fill="#9b704a",width=4)
        d.rectangle((950,420,1015,520),fill="#342f2b")
    # bamboo grove in forest
    if place in ("forest","path","pasture"):
        for x in range(30,1260,70):
            d.line((x,100,x+int(20*math.sin(x)),510),fill="#52764b",width=8)
            for yy in range(170,440,80):
                d.line((x,yy,x+55,yy-24),fill="#7b9b5e",width=4)
    # rain streaks
    if place=="rain":
        for n in range(180):
            x=(n*73+index*29)%W; y=(n*47+index*61)%H
            d.line((x,y,x-8,y+22),fill="#a9bdc4",width=2)
    # Characters positioned by dramatic beat
    if place in ("village","yard","home"):
        person(d,330,615,1.0,"boy",index)
        person(d,500,615,.95,"mother",index+1)
        calf(d,690,610,.85)
        if place=="home" and index>20: person(d,870,615,.9,"friend",index)
    elif place in ("pasture","path","bridge","forest"):
        person(d,420,620,1.0,"boy",index)
        if index>=7: person(d,610,620,.9,"friend",index+1)
        if place=="pasture" and index<6: calf(d,900,610,.75)
    elif place in ("stream","rain"):
        person(d,350,620,1.0,"boy",index)
        person(d,520,620,.9,"friend",index+1)
        calf(d,790,615,.95)
        if place=="rain": person(d,1010,620,.88,"farmer",index)
    # subtle foreground grass
    for x in range(0,W,31):
        y=660+(x*13%55)
        d.line((x,y,x-8,y-20),fill="#a0a66a",width=3)
    # cinematic vignette and letterbox
    shade=Image.new("L",(W,H),0); sd=ImageDraw.Draw(shade)
    sd.ellipse((-180,-170,W+180,H+170),fill=215)
    shade=shade.filter(ImageFilter.GaussianBlur(85))
    overlay=Image.new("RGB",(W,H),(8,13,17))
    img=Image.composite(img,overlay,shade)
    d=ImageDraw.Draw(img)
    d.rectangle((0,0,W,28),fill="#10151b")
    d.rectangle((0,H-28,W,H),fill="#10151b")
    # scene marker / chapter feel
    d.text((48,48),f"MYANMAR  •  A VILLAGE STORY  /  {index+1:02d}",fill="#e7d4ae")
    return img

def srt_time(sec):
    ms=int(round(sec*1000)); h=ms//3600000; ms%=3600000
    m=ms//60000; ms%=60000; s=ms//1000; ms%=1000
    return f"{h:02d}:{m:02d}:{s:02d},{ms:03d}"

def main():
    log("Stage 1/5: generating Deepgram character dialogue")
    audio_slots=[]; subtitle=[]; cursor=0.0; shot_files=[]
    for i,beat in enumerate(BEATS):
        role,english,burmese,place=beat
        model=VOICES[role]
        mp3=WORK/f"voice_{i:02d}.mp3"
        log(f"Deepgram voice {i+1}/{len(BEATS)} — {role} / {model}")
        tts(english,model,mp3)
        speech=duration(mp3)
        slot=max(5.6,speech+0.65)
        if cursor+slot>177:
            raise RuntimeError("Dialogue exceeds the 3-minute film timing budget. Shorten dialogue or use a faster voice pace.")
        # Pad each spoken line to its shot duration for exact picture/audio synchronization.
        padded=WORK/f"slot_{i:02d}.mp3"
        silence=max(0.0,slot-speech)
        run(["ffmpeg","-y","-loglevel","error","-i",str(mp3),"-af",f"apad=pad_dur={silence:.3f}","-t",f"{slot:.3f}","-ac","1","-ar","22050","-c:a","libmp3lame","-b:a","32k",str(padded)])
        audio_slots.append(padded)
        subtitle.append((cursor+0.18,cursor+min(speech+0.2,slot-0.05),burmese))
        plate=WORK/f"plate_{i:02d}.png"
        scene_plate(i,beat).save(plate,optimize=True)
        clip=WORK/f"shot_{i:02d}.mp4"
        frames=max(1,int(round(slot*FPS)))
        # A gentle moving camera on each illustrated plate gives a cinematic 2.5D feel.
        zoom_expr="min(zoom+0.00055,1.055)"
        x_expr="iw/2-(iw/zoom/2)"
        y_expr="ih/2-(ih/zoom/2)"
        run(["ffmpeg","-y","-loglevel","error","-loop","1","-i",str(plate),"-vf",
             f"scale=1360:765,zoompan=z='{zoom_expr}':x='{x_expr}':y='{y_expr}':d={frames}:s=854x480:fps={FPS},format=yuv420p",
             "-frames:v",str(frames),"-an","-c:v","libx264","-preset","ultrafast","-crf","24",str(clip)])
        shot_files.append(clip)
        cursor+=slot
        log(f"Beat {i+1}/{len(BEATS)} ready — {speech:.1f}s speech, {slot:.1f}s scene")
    if cursor>=180:
        raise RuntimeError("Shot timeline leaves no room for final cinematic end card.")
    # Hold on the homecoming scene for the remaining runtime.
    final_plate=WORK/f"plate_final.png"
    scene_plate(len(BEATS)-1,BEATS[-1]).save(final_plate,optimize=True)
    end_seconds=180.0-cursor
    end_frames=int(round(end_seconds*FPS))
    end_clip=WORK/"shot_end.mp4"
    run(["ffmpeg","-y","-loglevel","error","-loop","1","-i",str(final_plate),"-vf",
         f"scale=1360:765,zoompan=z='min(zoom+0.00025,1.035)':x='iw/2-(iw/zoom/2)':y='ih/2-(ih/zoom/2)':d={end_frames}:s=854x480:fps={FPS},format=yuv420p",
         "-frames:v",str(end_frames),"-an","-c:v","libx264","-preset","ultrafast","-crf","24",str(end_clip)])
    shot_files.append(end_clip)
    # Audio bed matches all shot durations; final hold remains silent.
    concat_list=WORK/"audio_concat.txt"
    concat_list.write_text("".join(f"file '{p.as_posix()}'\n" for p in audio_slots),encoding="utf-8")
    voice_track=WORK/"voice_track.mp3"
    run(["ffmpeg","-y","-loglevel","error","-f","concat","-safe","0","-i",str(concat_list),"-c:a","libmp3lame","-b:a","32k","-ac","1","-ar","22050",str(voice_track)])
    # Soft cinematic pad generated locally (no unlicensed music source).
    bed=WORK/"score.wav"
    run(["ffmpeg","-y","-loglevel","error","-f","lavfi","-i",
         "aevalsrc=0.012*sin(2*PI*110*t)+0.008*sin(2*PI*164.81*t)+0.006*sin(2*PI*220*t):s=22050:d=180",
         "-af","lowpass=f=700,afade=t=in:st=0:d=4,afade=t=out:st=172:d=8","-ac","1",str(bed)])
    # SRT uses measured speech durations and is kept editable as a separate artifact.
    srt=[]
    for i,(a,b,txt) in enumerate(subtitle,1):
        srt += [str(i),f"{srt_time(a)} --> {srt_time(b)}",txt,""]
    srt_path=OUT/"subtitles-my.srt"
    srt_path.write_text("\n".join(srt),encoding="utf-8")
    shot_list=WORK/"video_concat.txt"
    shot_list.write_text("".join(f"file '{p.as_posix()}'\n" for p in shot_files),encoding="utf-8")
    silent_video=WORK/"picture.mp4"
    run(["ffmpeg","-y","-loglevel","error","-f","concat","-safe","0","-i",str(shot_list),"-an","-c:v","copy",str(silent_video)])
    log("Stage 2/5: assembling cinematic picture, English dialogue and Burmese subtitles")
    subfont=font_path()
    vf=f"subtitles={srt_path.as_posix()}:force_style='FontName=Noto Sans Myanmar,FontSize=19,Outline=2,Shadow=1,Alignment=2,MarginV=32'"
    if subfont:
        vf=f"subtitles={srt_path.as_posix()}:fontsdir=/usr/share/fonts/truetype/noto:force_style='FontName=Noto Sans Myanmar,FontSize=19,Outline=2,Shadow=1,Alignment=2,MarginV=32'"
    mixed=WORK/"mixed_audio.m4a"
    run(["ffmpeg","-y","-loglevel","error","-i",str(voice_track),"-i",str(bed),"-filter_complex",
         "[0:a]volume=1.0[voice];[1:a]volume=0.20[score];[voice][score]amix=inputs=2:duration=longest:normalize=0,apad=pad_dur=180,atrim=0:180[a]",
         "-map","[a]","-c:a","aac","-b:a","24k","-ac","1","-ar","22050",str(mixed)])
    output=OUT/"GI-KO-KO-Myanmar-Village-Cinematic-480p.mp4"
    log("Stage 3/5: encoding 854x480 H.264 under strict 10 MB ceiling")
    quality=os.environ.get("RENDER_QUALITY","balanced")
    profiles=[(330,24),(285,20)] if quality=="balanced" else [(285,20),(250,18)]
    success=False
    for attempt,(vb,ab) in enumerate(profiles,1):
        run(["ffmpeg","-y","-loglevel","error","-i",str(silent_video),"-i",str(mixed),
             "-vf",vf,"-map","0:v:0","-map","1:a:0","-t","180",
             "-c:v","libx264","-preset","slow","-profile:v","main","-level","3.0",
             "-pix_fmt","yuv420p","-r",str(FPS),"-b:v",f"{vb}k","-maxrate",f"{vb}k","-bufsize",f"{vb*2}k",
             "-pass","1","-passlogfile",str(WORK/"passlog"),"-an","-f","mp4",os.devnull])
        run(["ffmpeg","-y","-loglevel","error","-i",str(silent_video),"-i",str(mixed),
             "-vf",vf,"-map","0:v:0","-map","1:a:0","-t","180",
             "-c:v","libx264","-preset","slow","-profile:v","main","-level","3.0",
             "-pix_fmt","yuv420p","-r",str(FPS),"-b:v",f"{vb}k","-maxrate",f"{vb}k","-bufsize",f"{vb*2}k",
             "-pass","2","-passlogfile",str(WORK/"passlog"),"-c:a","aac","-b:a",f"{ab}k","-ac","1","-ar","22050",
             "-movflags","+faststart",str(output)])
        size=output.stat().st_size
        log(f"Encoding attempt {attempt}: {size/1_000_000:.2f} MB (limit 10.00 MB)")
        if size<MAX_BYTES:
            success=True; break
    if not success:
        raise RuntimeError(f"Final MP4 is {output.stat().st_size} bytes; strict 10 MB cap not met.")
    info=json.loads(run(["ffprobe","-v","error","-show_entries","format=duration,size:stream=codec_name,width,height,avg_frame_rate","-of","json",str(output)]))
    report={
      "project":"G.I KO KO — The Missing Calf",
      "duration_seconds":180,
      "resolution":"854x480",
      "fps":FPS,
      "format":"MP4 / H.264 + AAC",
      "voice_provider":"Deepgram Aura-2",
      "character_voices":VOICES,
      "subtitle_language":"Myanmar",
      "subtitle_file":"subtitles-my.srt",
      "size_bytes":output.stat().st_size,
      "size_mb":round(output.stat().st_size/1_000_000,3),
      "size_limit_bytes":MAX_BYTES,
      "size_check":"PASS",
      "visual_style":"cinematic illustrated 2.5D with slow camera motion (not full 3D rigged animation)",
      "shots":len(BEATS)+1,
      "deepgram_voice_lines":len(BEATS),
      "streams":info.get("streams",[])
    }
    (OUT/"production-report.json").write_text(json.dumps(report,ensure_ascii=False,indent=2),encoding="utf-8")
    log("Stage 4/5: verifying output duration, resolution and file size")
    if output.stat().st_size>=MAX_BYTES or abs(float(info["format"]["duration"])-180)>1.2:
        raise RuntimeError("Final verification failed.")
    log("Stage 5/5: SUCCESS — MP4 is ready as a GitHub Actions artifact.")
    print(json.dumps(report,ensure_ascii=False,indent=2))

if __name__=="__main__":
    main()
