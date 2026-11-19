#!/usr/bin/env python3
import asyncio, json, os, subprocess, shutil, time
from pathlib import Path
import edge_tts

ROOT=Path(__file__).resolve().parents[2]
OUT=ROOT/"output"/"f35"; FRAMES=OUT/"frames"; WORK=OUT/"work"
for p in (OUT,FRAMES,WORK): p.mkdir(parents=True,exist_ok=True)
VOICE="my-MM-ThihaNeural"
SECTIONS=[
("မင်္ဂလာပါ။ ဒီနေ့မှာတော့ ခေတ်မီ တိုက်လေယာဉ် F-35 Lightning II ကို သုံးဖက်မြင် ရုပ်ပုံလှုပ်ရှားမှုနဲ့ လေ့လာကြပါမယ်။ ဒီလေယာဉ်ဟာ ပဉ္စမမျိုးဆက် ဘက်စုံသုံး တိုက်လေယာဉ်တစ်မျိုးဖြစ်ပြီး အမေရိကန် လေတပ်၊ ရေတပ်နဲ့ မရိန်းတပ်တို့ရဲ့ လိုအပ်ချက်အမျိုးမျိုးကို ဖြည့်ဆည်းဖို့ မိသားစုတစ်ခုအဖြစ် ဖွံ့ဖြိုးတိုးတက်လာခဲ့တာ ဖြစ်ပါတယ်။"),
("F-35 ရဲ့ ဒီဇိုင်းသမိုင်းကို ကြည့်မယ်ဆိုရင် လေတပ်တစ်ခုတည်းအတွက် မဟုတ်ဘဲ ဝန်ဆောင်မှုအမျိုးမျိုးအတွက် အခြေခံပလက်ဖောင်းတစ်ခုတည်းကို မျှဝေသုံးစွဲနိုင်ဖို့ ရည်ရွယ်ခဲ့တာကို တွေ့ရပါတယ်။ ဒါကြောင့် ပုံစံကွဲ သုံးမျိုးရှိလာပါတယ်။ F-35A က ပုံမှန်ပြေးလမ်းကနေ ပျံတက်ဆင်းသက်နိုင်တဲ့ မော်ဒယ်ဖြစ်ပါတယ်။"),
("F-35B ဟာ အကွာအဝေးတို ပျံတက်ခြင်းနဲ့ ဒေါင်လိုက်ဆင်းသက်ခြင်းကို အထူးပြုထားတဲ့ မော်ဒယ်ဖြစ်ပါတယ်။ F-35C ကတော့ လေယာဉ်တင်သင်္ဘောပေါ်ကနေ လုပ်ဆောင်ဖို့ ဒီဇိုင်းပြုလုပ်ထားတာပါ။ မော်ဒယ်တစ်ခုချင်းစီမှာ အရွယ်အစားနဲ့ လုပ်ဆောင်ပုံ ကွာခြားချက်တွေ ရှိပေမဲ့ မိသားစုတစ်ခုတည်းရဲ့ အခြေခံဒီဇိုင်းကို မျှဝေထားပါတယ်။"),
("အခု 3D မော်ဒယ်ကို အပြင်ဘက်ကနေ လှည့်ပတ်ကြည့်ကြရအောင်။ ရှေ့ပိုင်းမှာ ချွန်ထက်တဲ့ နှာခေါင်းပိုင်း၊ အလယ်မှာ လေယာဉ်ကိုယ်ထည်နဲ့ ဘေးနှစ်ဖက်မှာ တောင်ပံတွေကို တွေ့နိုင်ပါတယ်။ ဒီမော်ဒယ်ဟာ ပုံစံနဲ့ အစိတ်အပိုင်းတွေရဲ့ အခန်းကဏ္ဍကို နားလည်စေဖို့ ဖန်တီးထားတဲ့ ပညာပေးပုံစံဖြစ်ပြီး စက်ရုံသုံး အင်ဂျင်နီယာပုံစံအတိအကျ မဟုတ်ပါဘူး။"),
("လေယာဉ်ကိုယ်ထည်ဟာ အဓိက အစိတ်အပိုင်းတွေကို ချိတ်ဆက်ပေးတဲ့ ဗဟိုဖွဲ့စည်းပုံ ဖြစ်ပါတယ်။ လေယာဉ်မှူးခန်း၊ အင်ဂျင်တပ်ဆင်ရာ နေရာ၊ လောင်စာသိုလှောင်ရာ နေရာနဲ့ အခြားစနစ်တွေကို ဒီကိုယ်ထည်အတွင်းမှာ ပေါင်းစည်းထားပါတယ်။ ကိုယ်ထည်ရဲ့ အလေးချိန်၊ ခိုင်ခံ့မှုနဲ့ ပုံသဏ္ဌာန်တို့ဟာ လေယာဉ်တစ်စင်းလုံးရဲ့ စွမ်းဆောင်ရည်အပေါ် သက်ရောက်မှုရှိပါတယ်။"),
("တောင်ပံတွေဟာ ပျံသန်းစဉ် လိုအပ်တဲ့ Lift လို့ခေါ်တဲ့ မြှောက်အားကို ဖြစ်ပေါ်စေဖို့ အရေးကြီးပါတယ်။ F-35 ရဲ့ တောင်ပံပုံစံဟာ ကိုယ်ထည်နဲ့ ချောမွေ့စွာ ပေါင်းစပ်ထားပါတယ်။ တောင်ပံနောက်ဘက်မှာ ရှိတဲ့ ထိန်းချုပ်မျက်နှာပြင်တွေက လေယာဉ်ရဲ့ လှည့်ခြင်းနဲ့ ဦးတည်ချက်ပြောင်းလဲခြင်းတွေကို ကူညီပေးပါတယ်။"),
("နောက်ပိုင်းမှာ အပြင်ဘက်ကို စောင်းထားတဲ့ ဒေါင်လိုက်အမြီးတောင်ပံ နှစ်ခုကို တွေ့ရပါတယ်။ ဒီအစိတ်အပိုင်းတွေဟာ လေယာဉ်ရဲ့ ဦးတည်တည်ငြိမ်မှုကို ကူညီပေးပြီး အလျားလိုက် ထိန်းချုပ်မျက်နှာပြင်တွေနဲ့ ပေါင်းစပ်လုပ်ဆောင်ပါတယ်။ အမြီးပိုင်းရဲ့ တည်ဆောက်ပုံကို ဒီ 3D Exploded View မှာ ခွဲထုတ်ပြထားပါတယ်။"),
("လေယာဉ်မှူးခန်းမှာ အကာအကွယ်ပေးတဲ့ Canopy အမိုးခုံး၊ ထိုင်ခုံနဲ့ ထိန်းချုပ်ကိရိယာတွေ ပါဝင်ပါတယ်။ F-35 ရဲ့ ခေတ်မီ Helmet-Mounted Display ဟာ လေယာဉ်မှူးအတွက် အချက်အလက်တွေကို မြင်ကွင်းထဲမှာ ပြသပေးတဲ့ စနစ်တစ်ခုဖြစ်ပါတယ်။ ဒီနေရာမှာတော့ အတွင်းပိုင်းကို ပညာပေးအဆင့်သာ ဖော်ပြထားပါတယ်။"),
("ခေတ်မီ လေယာဉ်တွေမှာ Sensor နဲ့ Avionics စနစ်တွေဟာ အရေးကြီးတဲ့ အခန်းကဏ္ဍက ပါဝင်ပါတယ်။ F-35 မှာ ပတ်ဝန်းကျင်အခြေအနေကို သိရှိနားလည်စေဖို့ အာရုံခံစနစ်အမျိုးမျိုးနဲ့ အချက်အလက်ပေါင်းစည်းမှုကို အသုံးပြုထားပါတယ်။ ဒီဗီဒီယိုမှာတော့ စနစ်တွေရဲ့ ရည်ရွယ်ချက်ကိုသာ ရှင်းပြပြီး လုပ်ဆောင်ချက်အသေးစိတ်တွေကို မဖော်ပြပါဘူး။"),
("F-35A မှာ Pratt and Whitney F135 အင်ဂျင် တစ်လုံးတပ်ဆင်ထားပါတယ်။ အင်ဂျင်ဟာ လေကို စုပ်ယူပြီး စွမ်းအင်အဖြစ် ပြောင်းလဲကာ တွန်းအားကို ထုတ်ပေးပါတယ်။ ဒီ 3D ပုံစံမှာ အင်ဂျင်အပြင်ပိုင်းနဲ့ Fan အယူအဆကိုသာ ရိုးရှင်းစွာ ပြသထားပါတယ်။ အတွင်းပိုင်း အင်ဂျင်ဒီဇိုင်းအသေးစိတ်ကိုတော့ မော်ဒယ်ထဲမှာ မထည့်သွင်းထားပါဘူး။"),
("ဆင်းသက်ဘီးစနစ်ဟာ မြေပြင်ပေါ်မှာ ရွေ့လျားခြင်း၊ ပြေးလမ်းပေါ်မှာ အရှိန်တင်ခြင်းနဲ့ ဆင်းသက်ချိန်မှာ အလေးချိန်ကို ထောက်ပံ့ပေးခြင်းတို့အတွက် ဖြစ်ပါတယ်။ ရှေ့ဘီးတစ်စုံနဲ့ အဓိကဘီးတွေဟာ လေယာဉ်ရဲ့ အလေးချိန်ကို ခွဲဝေထောက်ပံ့ပေးပါတယ်။ ပြုပြင်ထိန်းသိမ်းရာမှာ ဘီးနဲ့ Strut အစိတ်အပိုင်းတွေကို စစ်ဆေးခြင်းလည်း အရေးကြီးပါတယ်။"),
("လေယာဉ်တစ်စင်းကို ထုတ်လုပ်ရာမှာ ဒီဇိုင်းရေးဆွဲခြင်း၊ အစိတ်အပိုင်းတွေ ထုတ်လုပ်ခြင်း၊ တပ်ဆင်ခြင်းနဲ့ အရည်အသွေးစစ်ဆေးခြင်း အဆင့်တွေ ပါဝင်ပါတယ်။ F-35 ပရိုဂရမ်မှာ နိုင်ငံတကာ မိတ်ဖက်ကုမ္ပဏီများစွာ ပူးပေါင်းပါဝင်ခဲ့ကြပါတယ်။ ဒါဟာ ခေတ်မီ လေကြောင်းစက်မှုလုပ်ငန်းမှာ ပူးပေါင်းဆောင်ရွက်မှုရဲ့ ဥပမာတစ်ခု ဖြစ်ပါတယ်။"),
("ခေတ်မီ လေယာဉ်တွေမှာ သတ္တုနဲ့ ပေါင်းစပ်ပစ္စည်းတွေကို လိုအပ်ချက်အလိုက် အသုံးပြုကြပါတယ်။ အလေးချိန်လျှော့ချခြင်း၊ ခိုင်ခံ့မှုရရှိခြင်းနဲ့ ပတ်ဝန်းကျင်အခြေအနေကို ခံနိုင်ရည်ရှိခြင်းတို့ကို ထည့်သွင်းစဉ်းစားရပါတယ်။ ပစ္စည်းရွေးချယ်မှုနဲ့ ပြုပြင်ထိန်းသိမ်းမှုဟာ လေယာဉ်ရဲ့ သက်တမ်းတစ်လျှောက် လုံခြုံစိတ်ချရမှုအတွက် အရေးပါပါတယ်။"),
("နောက်ဆုံးစစ်ဆေးမှုတွေမှာ ကိုယ်ထည်၊ တောင်ပံ၊ လျှပ်စစ်စနစ်၊ အင်ဂျင်နဲ့ မြေပြင်စမ်းသပ်မှုတွေ ပါဝင်ပါတယ်။ စမ်းသပ်မှုတွေကို အဆင့်လိုက် လုပ်ဆောင်ပြီး လိုအပ်တဲ့ စံနှုန်းတွေ ပြည့်မီမှသာ နောက်တစ်ဆင့်ကို ဆက်လက်လုပ်ဆောင်ပါတယ်။ လေယာဉ်တစ်စင်းရဲ့ ယုံကြည်စိတ်ချရမှုဟာ ဒီလို စနစ်တကျ စစ်ဆေးမှုတွေအပေါ် မူတည်ပါတယ်။"),
("အနှစ်ချုပ်ရရင် F-35 Lightning II ဟာ ကိုယ်ထည်၊ တောင်ပံ၊ အမြီးပိုင်း၊ လေယာဉ်မှူးခန်း၊ အင်ဂျင်နဲ့ အာရုံခံစနစ်တွေကို ပေါင်းစည်းထားတဲ့ ခေတ်မီ လေယာဉ်မိသားစုတစ်ခု ဖြစ်ပါတယ်။ ဒီဗီဒီယိုဟာ အများပြည်သူသိရှိနိုင်တဲ့ အချက်အလက်တွေကို အခြေခံထားတဲ့ ပညာပေး 3D ရှင်းလင်းချက်ဖြစ်ပါတယ်။ ကြည့်ရှုပေးတဲ့အတွက် ကျေးဇူးတင်ပါတယ်။")
]

def run(cmd):
    subprocess.run(cmd,check=True)
def probe(path):
    return float(subprocess.check_output(["ffprobe","-v","error","-show_entries","format=duration","-of","default=noprint_wrappers=1:nokey=1",str(path)],text=True).strip())
async def make_voice(i,text):
    p=WORK/f"voice_{i:02d}.mp3"
    await edge_tts.Communicate(text,VOICE,rate="-3%").save(str(p))
    return p

async def main():
    voice_files=[]
    for i,text in enumerate(SECTIONS,1):
        p=await make_voice(i,text); voice_files.append(p)
        print(f"VOICE {i}/{len(SECTIONS)} complete",flush=True)
    concat=WORK/"voice-list.txt"
    with concat.open("w",encoding="utf-8") as f:
        for p in voice_files:f.write("file '"+str(p.resolve())+"'\n")
    # Fit every narration chapter into the exact five-minute runtime.
    segment=300.0/len(SECTIONS); voice_window=segment-1.0
    wavs=[]; srt=[]
    for i,(txt,src) in enumerate(zip(SECTIONS,voice_files)):
        d=probe(src); speed=max(1.0,d/voice_window)
        speed=min(speed,2.0)
        dst=WORK/f"beat_{i+1:02d}.wav"
        run(["ffmpeg","-y","-i",str(src),"-af",f"atempo={speed:.4f},apad=pad_dur={segment:.4f},atrim=duration={segment:.4f}","-ar","48000","-ac","2","-c:a","pcm_s16le",str(dst)])
        wavs.append(dst)
        start=i*segment; end=(i+1)*segment-0.15
        def stamp(t):
            h=int(t//3600); m=int((t%3600)//60); sec=t%60
            return f"{h:02d}:{m:02d}:{sec:06.3f}".replace(".",",")
        srt.append(f"{i+1}\n{stamp(start)} --> {stamp(end)}\n{txt}\n")
    (OUT/"subtitles-my.srt").write_text("\n".join(srt),encoding="utf-8")
    (OUT/"narration-my.txt").write_text("\n\n".join(SECTIONS),encoding="utf-8")
    lst=WORK/"beats.txt"
    lst.write_text("".join("file '"+str(p.resolve())+"'\n" for p in wavs),encoding="utf-8")
    narration=WORK/"narration.wav"
    run(["ffmpeg","-y","-f","concat","-safe","0","-i",str(lst),"-c:a","pcm_s16le",str(narration)])
    music=WORK/"music.wav"
    src="aevalsrc=0.032*sin(2*PI*110*t)+0.023*sin(2*PI*164.81*t)+0.018*sin(2*PI*220*t)+0.009*sin(2*PI*329.63*t)+0.008*sin(2*PI*55*t):s=48000:d=300"
    run(["ffmpeg","-y","-f","lavfi","-i",src,"-af","afade=t=in:st=0:d=4,afade=t=out:st=294:d=6,volume=0.8","-t","300","-c:a","pcm_s16le",str(music)])
    blender_script=Path(__file__).with_name("scene.py")
    run(["blender","-b","--python",str(blender_script),"--",str(FRAMES)])
    profile=os.environ.get("RENDER_PROFILE","standard")
    crf="21" if profile=="standard" else "25"
    mp4=OUT/"GI-KO-KO-F35-Lightning-II-3D-Explainer.mp4"
    run(["ffmpeg","-y","-framerate","12","-i",str(FRAMES/"frame_%04d.png"),"-i",str(narration),"-i",str(music),
         "-filter_complex","[1:a][2:a]amix=inputs=2:weights='1 0.20':duration=longest,alimiter=limit=0.95[a]",
         "-map","0:v:0","-map","[a]","-t","300","-c:v","libx264","-preset","veryfast","-crf",crf,"-pix_fmt","yuv420p","-r","12","-c:a","aac","-b:a","128k","-movflags","+faststart",str(mp4)])
    duration=probe(mp4); size=mp4.stat().st_size
    report={"title":"G.I KO KO — F-35 Lightning II 3D Explainer","duration_seconds":duration,"file_size_bytes":size,"resolution":"1280x720","fps":12,"narration_voice":VOICE,"subtitles":"separate Burmese SRT","visual_method":"procedural Blender 3D educational model and animated exploded view","music":"original synthesized ambient score","profile":profile,"note":"Conceptual educational model, not engineering CAD."}
    (OUT/"production-report.json").write_text(json.dumps(report,ensure_ascii=False,indent=2),encoding="utf-8")
    print(json.dumps(report,ensure_ascii=False),flush=True)
    if abs(duration-300)>1.5: raise SystemExit(f"Unexpected runtime: {duration:.2f}s")

if __name__=="__main__": asyncio.run(main())
