import streamlit as st
import yt_dlp
from youtubesearchpython import VideosSearch
from faster_whisper import WhisperModel
from deep_translator import GoogleTranslator
import subprocess, os, re

st.set_page_config(page_title="GTA 6 Viral Clips AI", page_icon="🎮", layout="wide")
os.makedirs("clips", exist_ok=True)

@st.cache_resource
def load_models():
    return WhisperModel("tiny", device="cpu", compute_type="int8")

whisper_model = load_models()

st.title("🎮 استوديو صانع الشورت الفيروسي (مجاني 100%)")

col1, col2 = st.columns(2)
with col1:
    q_cat = st.selectbox("اختر فئة سريعة:", ["GTA 6 gameplay reactions", "IShowSpeed funny moments", "Kai Cenat stream clips", "CaseOh rage moments", "xQc gaming reactions"])
with col2:
    c_search = st.text_input("أو اكتب اسم أي ستريمر أو لعبة:", placeholder="مثلاً: Adin Ross, Warzone...")

if st.button("🔍 جيب الفيديوهات الحصرية (أقل من 5 شهور)", use_container_width=True):
    term = c_search.strip() if c_search.strip() else q_cat
    res = VideosSearch(term, limit=15).result().get('result', [])
    vids = []
    for v in res:
        pub = v.get('publishedTime', '')
        if any(x in pub for x in ['year', 'years', '6 months', '7 months', '8 months', '9 months', '10 months', '11 months']):
            continue
        vids.append(v)
    st.session_state['vids'] = vids

if 'vids' in st.session_state and st.session_state['vids']:
    vids = st.session_state['vids']
    cols = st.columns(3)
    for idx, v in enumerate(vids):
        with cols[idx % 3]:
            st.image(v.get('thumbnails', [{}]).get('url', ''), use_container_width=True)
            st.markdown(f"**{v.get('title', '')[:55]}...**")
            st.caption(f"🎮 {v.get('channel', {}).get('name', '')} | 👁️ {v.get('viewCount', {}).get('short', '')} | 📅 {v.get('publishedTime', '')}")
    options = [f"{v.get('title', '')[:50]} | {v.get('link', '')}" for v in vids]
    sel_vid = st.selectbox("اختر الفيديو من القائمة أعلاه:", options)
else:
    sel_vid = ""

d_link = st.text_input("أو لصق رابط يوتيوب مباشرة هنا (اختياري):")

if st.button("🧠 تحليل واستخراج أقوى اللقطات", use_container_width=True):
    url = d_link.strip() if d_link.strip() else (sel_vid.split(" | ")[-1] if sel_vid else "")
    if url:
        with st.spinner("جاري تحليل الفيديو واستخراج أقوى اللحظات..."):
            with yt_dlp.YoutubeDL({'quiet': True}) as ydl:
                info = ydl.extract_info(url, download=False)
            dur, hm, title = info.get('duration', 60), info.get('heatmap', []), info.get('title', 'Clip')
            clips, used = [], []
            if hm:
                for item in sorted(hm, key=lambda x: x.get('value', 0), reverse=True):
                    st_t = max(0, int(item['start_time']) - 10)
                    if any(abs(st_t - u) < 35 for u in used): continue
                    used.append(st_t)
                    clips.append(f"🔥 لقطة قوية ({int(item.get('value',0.8)*100)}%) | من {st_t}s إلى {min(dur, st_t+45)}s | {url}")
                    if len(clips) >= 10: break
            else:
                for t in range(15, max(20, dur - 45), max(45, dur // 8)):
                    clips.append(f"⚡ لقطة مقترحة | من {t}s إلى {min(dur, t+45)}s | {url}")
                    if len(clips) >= 8: break
            st.session_state['clips'] = clips
            st.success(f"✅ تم استخراج {len(clips)} لقطة! | العنوان المقترح: شوف ردة فعلو فـ {title[:25]} 😱 | #gaming #gta6 #viral #fyp")

if 'clips' in st.session_state and st.session_state['clips']:
    clip_c = st.selectbox("اختر اللقطة اللي بغيتي تحولها لشورت:", st.session_state['clips'])
    c1, c2, c3 = st.columns(3)
    with c1:
        lay = st.selectbox("شكل وتقسيم الفيديو:", ["تقسيم الشاشة (الستريمر الفوق + اللعبة لتحت)", "خلفية ضبابية (Blur Background)", "شاشة كاملة (Full 9:16)"])
        fnt = st.selectbox("نوع الخط:", ["Liberation Sans", "Liberation Serif", "DejaVu Sans"])
    with c2:
        col = st.selectbox("لون الكتابة:", ["أصفر نيون", "أبيض", "أخضر", "أحمر"])
        pos = st.selectbox("مكان الكتابة:", ["الوسط", "لتحت", "الفوق"])
    with c3:
        anim = st.selectbox("حركة الكتابة:", ["نبضة (Pop-up)", "ظهور ناعم (Fade)"])
        hook = st.text_input("عنوان علوي ثابت (اختياري):", placeholder="مستحيل شنو طرا فـ GTA 6 🤯")
    
    b1, b2, b3 = st.columns(3)
    anti = b1.checkbox("🛡️ حماية ضد الكوبيرايت", value=True)
    pbar = b2.checkbox("📊 شريط التقدم الأصفر", value=True)
    cboost = b3.checkbox("🎨 تحسين الألوان (Auto-HDR)", value=True)

    if st.button("🎬 توليد الفيديو النهائي بجودة 1080p", type="primary", use_container_width=True):
        with st.spinner("جاري تقطيع الفيديو وتركيب الكتابة التلقائية والترجمة الفرنسية..."):
            parts = clip_c.split(" | ")
            times = re.findall(r'(\d+)s', parts[1])
            st_s, en_s, url = int(times[0]), int(times[1]), parts[2]
            rv, fv, af_path = "clips/raw.mp4", "clips/final.mp4", "clips/subs.ass"
            for f in [rv, fv, af_path]:
                if os.path.exists(f): os.remove(f)
            with yt_dlp.YoutubeDL({'format': 'bestvideo[height<=1080][ext=mp4]+bestaudio[ext=m4a]/best[ext=mp4]', 'outtmpl': rv, 'download_ranges': lambda i, y: [{'start_time': st_s, 'end_time': en_s}], 'force_keyframes_at_cuts': True, 'quiet': True}) as ydl:
                ydl.download([url])
            segs, _ = whisper_model.transcribe(rv)
            tr = GoogleTranslator(source='auto', target='fr')
            cmap = {"أبيض": "&H00FFFFFF", "أصفر نيون": "&H0000FFFF", "أخضر": "&H0000FF00", "أحمر": "&H000000FF"}
            amap = {"الوسط": 5, "لتحت": 2, "الفوق": 8}
            hdr = f"[Script Info]\nScriptType: v4.00+\nPlayResX: 1080\nPlayResY: 1920\n[V4+ Styles]\nFormat: Name, Fontname, Fontsize, PrimaryColour, SecondaryColour, OutlineColour, BackColour, Bold, Italic, Underline, StrikeOut, ScaleX, ScaleY, Spacing, Angle, BorderStyle, Outline, Shadow, Alignment, MarginL, MarginR, MarginV, Encoding\nStyle: Default,{fnt},60,{cmap.get(col,'&H0000FFFF')},&H000000FF,&H00000000,&H80000000,-1,0,0,0,100,100,0,0,1,4,2,{amap.get(pos,5)},40,40,180,1\n[Events]\nFormat: Layer, Start, End, Style, Name, MarginL, MarginR, MarginV, Effect, Text\n"
            evs = []
            for s in segs:
                txt = s.text.strip()
                if not txt: continue
                try: fr = tr.translate(txt)
                except: fr = ""
                def ft(x): return f"{int(x//3600)}:{int((x%3600)//60):02d}:{x%60:05.2f}"
                tag = r"{\fscx115\fscy115\t(0,120,\fscx100\fscy100)}" if "نبضة" in anim else r"{\fad(80,80)}"
                evs.append(f"Dialogue: 0,{ft(s.start)},{ft(s.end)},Default,,0,0,0,,{tag}{txt}\\N{{\\fs44\\c&H00FFFFFF&}}({fr})")
            open(af_path, "w", encoding="utf-8").write(hdr + "\n".join(evs))
            if "تقسيم" in lay:
                vf = "[0:v]split=2[top][bot];[top]crop=ih*0.6:ih*0.6:iw*0.1:ih*0.1,scale=1080:720[t];[bot]scale=1080:1200:force_original_aspect_ratio=increase,crop=1080:1200[b];[t][b]vstack=inputs=2"
            elif "ضبابية" in lay:
                vf = "[0:v]split=2[bg][fg];[bg]scale=1080:1920:force_original_aspect_ratio=increase,crop=1080:1920,boxblur=25:5[b];[fg]scale=1080:-2[f];[b][f]overlay=(W-w)/2:(H-h)/2"
            else:
                vf = "[0:v]scale=1080:1920:force_original_aspect_ratio=increase,crop=1080:1920"
            ext = []
            if cboost: ext.append("eq=contrast=1.12:saturation=1.18")
            if hook.strip(): ext.append(f"drawbox=x=0:y=60:w=1080:h=130:color=black@0.75:t=fill,drawtext=text='{hook.strip().replace(chr(39),'')}':fontcolor=white:fontsize=46:x=(w-text_w)/2:y=105")
            if pbar: ext.append(f"drawbox=x=0:y=1905:w=iw*(t/{max(1,en_s-st_s)}):h=15:color=yellow:t=fill")
            ext.append(f"ass={af_path}")
            cmd = ["ffmpeg", "-y", "-i", rv, "-filter_complex", f"{vf},{','.join(ext)}{',setpts=0.97*PTS' if anti else ''}[vout]", "-map", "[vout]", "-map", "0:a?", "-af", "atempo=1.03,asetrate=44100*1.01,aresample=44100" if anti else "anull", "-c:v", "libx264", "-preset", "fast", "-crf", "18", "-c:a", "aac", "-b:a", "192k", fv]
            subprocess.run(cmd, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            if os.path.exists(fv):
                st.video(fv)
                with open(fv, "rb") as file:
                    st.download_button("⬇️ تحميل الفيديو بجودة 1080p", data=file, file_name="viral_short_1080p.mp4", mime="video/mp4", use_container_width=True)
                    
