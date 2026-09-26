"""Utilidades para dibujar diagramas como HTML/SVG y renderizarlos a PNG con Chromium headless."""
import html
import os
import shutil
import subprocess

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
HTML_DIR = os.path.join(ROOT, 'diagrams', 'html')
FONT = "'Noto Sans', 'Liberation Sans', Arial, sans-serif"

# Paleta de EventStorming (convención de Alberto Brandolini).
ES = {
    'event': '#ffa94d', 'command': '#74c0fc', 'actor': '#ffec99', 'policy': '#d0bfff',
    'aggregate': '#fff3bf', 'readmodel': '#8ce99a', 'external': '#faa2c1', 'hotspot': '#f06595',
}


def esc(text):
    return html.escape(text).replace('\n', '<br>')


def box(x, y, w, h, text, bg='#fff', cls='', style=''):
    return ('<div class="abs %s" style="left:%dpx;top:%dpx;width:%dpx;height:%dpx;background:%s;%s">'
            '<div>%s</div></div>' % (cls, x, y, w, h, bg, style, text))


def label(x, y, w, text, size=15, weight=400, color='#222', align='left', style=''):
    return ('<div class="abs" style="left:%dpx;top:%dpx;width:%dpx;font-size:%dpx;font-weight:%d;color:%s;'
            'text-align:%s;%s">%s</div>' % (x, y, w, size, weight, color, align, style, text))


class Svg:
    """Capa SVG superpuesta para flechas y conectores."""

    def __init__(self, w, h):
        self.w, self.h, self.items = w, h, []

    def line(self, pts, color='#444', width=2, dashed=False, arrow=True, curve=False):
        d = 'M %d %d ' % pts[0]
        if curve and len(pts) == 2:
            (x1, y1), (x2, y2) = pts
            mx = (x1 + x2) / 2
            d += 'C %d %d %d %d %d %d' % (mx, y1, mx, y2, x2, y2)
        else:
            d += ' '.join('L %d %d' % p for p in pts[1:])
        self.items.append('<path d="%s" fill="none" stroke="%s" stroke-width="%s" %s %s/>' % (
            d, color, width, 'stroke-dasharray="7 5"' if dashed else '',
            'marker-end="url(#arr)"' if arrow else ''))

    def text(self, x, y, text, size=13, color='#333', anchor='middle', weight=400):
        self.items.append('<text x="%d" y="%d" font-size="%d" fill="%s" text-anchor="%s" font-weight="%d" '
                          'paint-order="stroke" stroke="#f7f7f4" stroke-width="5" stroke-linejoin="round">%s</text>'
                          % (x, y, size, color, anchor, weight, html.escape(text)))

    def circle(self, x, y, r, fill, text='', size=13):
        self.items.append('<circle cx="%d" cy="%d" r="%d" fill="%s"/>' % (x, y, r, fill))
        if text:
            self.items.append('<text x="%d" y="%d" font-size="%d" fill="#fff" text-anchor="middle" '
                              'font-weight="700">%s</text>' % (x, y + size / 3 + 1, size, text))

    def raw(self, s):
        self.items.append(s)

    def render(self):
        return ('<svg class="abs" style="left:0;top:0" width="%d" height="%d"><defs>'
                '<marker id="arr" markerUnits="userSpaceOnUse" markerWidth="14" markerHeight="12" refX="11" refY="5" orient="auto">'
                '<path d="M0,0 L0,10 L12,5 z" fill="#444"/></marker></defs>%s</svg>'
                % (self.w, self.h, ''.join(self.items)))


CSS = """
* { box-sizing: border-box; }
body { margin: 0; background: #f7f7f4; font-family: %s; color: #222; position: relative; overflow: hidden; }
.abs { position: absolute; }
.sticky { display: flex; align-items: center; justify-content: center; text-align: center; padding: 8px;
          box-shadow: 1px 2px 4px rgba(0,0,0,.20); font-size: 15px; line-height: 1.25; }
.card { display: flex; align-items: center; justify-content: center; text-align: center; padding: 10px;
        border-radius: 10px; border: 1.5px solid #555; font-size: 14px; line-height: 1.3; background: #fff; }
.small { font-size: 13px; }
.mono { font-family: 'JetBrainsMono Nerd Font', monospace; }
""" % FONT


def page(w, h, body, title=''):
    return ('<!doctype html><html lang="es"><head><meta charset="utf-8"><title>%s</title><style>%s</style>'
            '</head><body style="width:%dpx;height:%dpx">%s</body></html>' % (esc(title), CSS, w, h, body))


def chromium():
    for name in ('chromium', 'chromium-browser', 'google-chrome', 'google-chrome-stable'):
        path = shutil.which(name)
        if path:
            return path
    raise SystemExit('Se requiere Chromium o Google Chrome para renderizar los diagramas.')


def render(name, w, h, body, png, title='', scale=1.5):
    """Escribe diagrams/html/<name>.html y lo renderiza a imgs/<png>."""
    os.makedirs(HTML_DIR, exist_ok=True)
    src = os.path.join(HTML_DIR, name + '.html')
    with open(src, 'w', encoding='utf-8') as f:
        f.write(page(w, h, body, title))
    out = os.path.join(ROOT, png)
    os.makedirs(os.path.dirname(out), exist_ok=True)
    subprocess.run([chromium(), '--headless=new', '--no-sandbox', '--disable-gpu', '--hide-scrollbars',
                    '--force-device-scale-factor=%s' % scale, '--window-size=%d,%d' % (w, h),
                    '--screenshot=' + out, 'file://' + src],
                   check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    print('✓', png)
