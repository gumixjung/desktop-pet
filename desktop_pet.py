#!/usr/bin/env python3
"""Desktop Pet - pywebview transparent, Python controls every frame"""

import os, base64, io, json, random, threading, time
from PIL import Image
import webview

import sys
BASE_DIR   = getattr(sys, "_MEIPASS", os.path.dirname(os.path.abspath(__file__)))
SPRITE_DIR = os.path.join(BASE_DIR, "sprites")
CAT_H      = 120
SPEED      = 2
MOVE_FPS   = 30
ANIM_FPS   = 10
WIN_W      = 250
Y_OFFSET   = 80   # px from bottom of screen


def encode(height):
    out = {}
    for name in [f"walk_r_{i}" for i in range(1, 5)] + \
                [f"walk_l_{i}" for i in range(1, 5)] + \
                ["sit_1", "sit_2"]:
        p = os.path.join(SPRITE_DIR, f"{name}.png")
        if not os.path.exists(p):
            continue
        img = Image.open(p).convert("RGBA")
        w   = int(img.width * height / img.height)
        img = img.resize((w, height), Image.LANCZOS)
        buf = io.BytesIO()
        img.save(buf, "PNG")
        out[name] = "data:image/png;base64," + base64.b64encode(buf.getvalue()).decode()
    return out


def build_html(sprites):
    img_tags = "\n".join(
        f'<img id="{k}" src="{v}" class="frame">'
        for k, v in sprites.items()
    )
    return f"""<!DOCTYPE html><html><head><meta charset="utf-8"><style>
*{{margin:0;padding:0}}
html,body{{background:transparent!important;width:100%;height:100%;overflow:hidden}}
.frame{{position:absolute;bottom:0;left:0;height:{CAT_H}px;
        display:none;image-rendering:pixelated}}
.frame.active{{display:block}}
#menu{{display:none;position:fixed;background:#fff;border:1px solid #ccc;
       border-radius:6px;padding:4px 0;box-shadow:2px 2px 6px rgba(0,0,0,.3);z-index:99}}
#menu div{{padding:6px 16px;cursor:pointer;font:13px sans-serif}}
#menu div:hover{{background:#eee}}
</style></head><body>
{img_tags}
<div id="menu">
  <div onclick="pywebview.api.quit()">Quit</div>
</div>
<script>
let cur = '';
window.showFrame = function(key) {{
  if (key === cur) return;
  if (cur) document.getElementById(cur)?.classList.remove('active');
  const el = document.getElementById(key);
  if (el) {{ el.classList.add('active'); cur = key; }}
}};
const menu = document.getElementById('menu');
document.addEventListener('contextmenu', e => {{
  e.preventDefault();
  menu.style.display = 'block';
  menu.style.left = e.clientX + 'px';
  menu.style.top  = e.clientY + 'px';
}});
document.addEventListener('click', () => menu.style.display = 'none');
document.addEventListener('keydown', e => {{
  if (e.key === 'q' || e.key === 'Q') pywebview.api.quit();
}});
// Custom drag — move window via Python API
let dragging = false, startX = 0, startY = 0;
document.addEventListener('mousedown', e => {{
  dragging = true;
  startX = e.screenX;
  startY = e.screenY;
  pywebview.api.drag_start(e.screenX, e.screenY);
  e.preventDefault();
}});
document.addEventListener('mousemove', e => {{
  if (!dragging) return;
  const dx = e.screenX - startX;
  const dy = e.screenY - startY;
  startX = e.screenX;
  startY = e.screenY;
  pywebview.api.drag_move(dx, dy);
}});
document.addEventListener('mouseup', e => {{
  if (!dragging) return;
  dragging = false;
  pywebview.api.drag_end(e.screenY - (e.clientY));
}});
</script></body></html>"""


class Api:
    def quit(self):
        os._exit(0)

    def drag_start(self, sx, sy):
        global _dragging, _drag_x, _drag_y
        _drag_x   = int(sx)
        _drag_y   = int(sy)
        _dragging = True  # set immediately — no async calls

    def drag_move(self, dx, dy):
        global _drag_x, _drag_y
        _drag_x += int(dx)
        _drag_y += int(dy)
        try:
            win.move(_drag_x, _drag_y)
        except Exception:
            pass

    def drag_end(self, win_y):
        global Y_OFFSET, _sh, _dragging, _drag_y
        Y_OFFSET  = max(0, int(_sh - _drag_y - CAT_H))
        _dragging = False


_stop     = threading.Event()
_dragging = False
_drag_x   = 0
_drag_y   = 0
_sh       = 900


def show(key):
    try:
        win.evaluate_js(f"window.showFrame('{key}')")
    except Exception:
        pass


def walk_loop():
    time.sleep(0.8)
    try:
        info = json.loads(win.evaluate_js(
            "JSON.stringify({w:screen.width,h:screen.height})"))
        sw, sh = info["w"], info["h"]
    except Exception:
        sw, sh = 1440, 900

    global _sh
    _sh = sh

    keys    = list(encode(CAT_H).keys())
    walk_r  = [k for k in keys if k.startswith("walk_r_")]
    walk_l  = [k for k in keys if k.startswith("walk_l_")]
    sit     = [k for k in keys if k.startswith("sit_")]
    nw      = len(walk_r)

    x = float(random.randint(0, sw - WIN_W))
    y = float(sh - CAT_H - Y_OFFSET)
    dir_   = random.choice([-1, 1])
    state  = "walk"
    steps  = random.randint(40, 160)
    sit_t  = 0
    idle_t = 0
    fi     = 0
    bt     = 0

    win.move(int(x), int(y))

    move_interval = 1.0 / MOVE_FPS   # 33ms  — window moves this fast
    anim_interval = 1.0 / ANIM_FPS   # 100ms — sprite changes this fast
    last_anim = time.time()

    while not _stop.is_set():
        time.sleep(move_interval)
        now = time.time()
        do_anim = (now - last_anim) >= anim_interval

        if state == "walk":
            x = max(0.0, min(float(sw - WIN_W), x + dir_ * SPEED))
            if x <= 0:   dir_ = 1
            elif x >= sw - WIN_W: dir_ = -1

            if do_anim:
                fi = (fi + 1) % max(nw, 1)
                frames = walk_r if dir_ == 1 else walk_l
                show(frames[fi % len(frames)])
                steps -= 1
                if steps <= 0:
                    r = random.random()
                    if r < 0.7:
                        dir_  = random.choice([-1, 1])
                        steps = random.randint(40, 160)
                    elif r < 0.88:
                        state = "sit"; sit_t = random.randint(25, 70); bt = 0
                    else:
                        state = "idle"; idle_t = random.randint(15, 40)

        elif state == "sit":
            if do_anim:
                bt += 1
                idx = 1 if (bt % 24) < 2 else 0
                show(sit[idx % len(sit)])
                sit_t -= 1
                if sit_t <= 0:
                    state = "walk"; steps = random.randint(40, 160); fi = 0

        else:  # idle
            if do_anim:
                show(sit[0])
                idle_t -= 1
                if idle_t <= 0:
                    state = "walk"; steps = random.randint(40, 160); fi = 0

        if do_anim:
            last_anim = now

        y = float(sh - CAT_H - Y_OFFSET)
        if not _dragging:
            try:
                win.move(int(x), int(y))
            except Exception:
                break


print("Loading sprites…")
sprites = encode(CAT_H)
api = Api()
win = webview.create_window(
    title       = "Desktop Pet",
    html        = build_html(sprites),
    js_api      = api,
    width       = WIN_W,
    height      = CAT_H + 10,
    frameless   = True,
    transparent = True,
    on_top      = True,
    easy_drag   = False,
    shadow      = False,
    background_color='#00000000',
    resizable   = False,
)
win.events.loaded += lambda: threading.Thread(
    target=walk_loop, daemon=True).start()
webview.start()
