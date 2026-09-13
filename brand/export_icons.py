"""Mechanical web exports of the supplied mark; no drawing or shape reconstruction.
Preserve source alpha, trim transparent padding, and apply the specified flat inks.
Requires Pillow only when exporting brand assets, never during site deployment.
"""
from pathlib import Path
from PIL import Image
import base64
ROOT=Path(__file__).resolve().parents[1]
out=ROOT/'public/brand'
source=Image.open(ROOT/'brand/originals/antique-gold.png').convert('RGBA')
# Frame the visible source mark, excluding only distant nearly-transparent padding.
box=source.getchannel('A').point(lambda a:255 if a>=64 else 0).getbbox()
x0,y0,x1,y1=box
box=(max(0,x0-8),max(0,y0-8),min(source.width,x1+8),min(source.height,y1+8))
alpha=source.getchannel('A').crop(box)
for name,color in [('gold','#9A8357'),('ivory','#E8E1D3')]:
    mark=Image.new('RGBA',alpha.size,color);mark.putalpha(alpha)
    mark.save(out/f'logo-{name}.png',optimize=True)
    small=mark.copy();small.thumbnail((160,240),Image.Resampling.LANCZOS)
    small.save(out/f'logo-{name}-small.png',optimize=True)
# Square icons use the same mark, with warm ivory for legibility at tiny sizes.
mark=Image.open(out/'logo-ivory.png')
def icon(size):
    canvas=Image.new('RGBA',(size,size),'#1C1B19')
    emblem=mark.copy();emblem.thumbnail((round(size*.88),round(size*.92)),Image.Resampling.LANCZOS)
    canvas.alpha_composite(emblem,((size-emblem.width)//2,(size-emblem.height)//2))
    return canvas
for size in (16,32,180,192,512):icon(size).convert('RGB').save(out/f'icon-{size}.png',optimize=True)
icon(256).save(ROOT/'public/favicon.ico',sizes=[(16,16),(32,32),(48,48)])
encoded=base64.b64encode((out/'logo-ivory.png').read_bytes()).decode()
w,h=mark.size;ih=92;iw=ih*w/h
(ROOT/'public/favicon.svg').write_text(f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 100 100"><rect width="100" height="100" rx="14" fill="#1C1B19"/><image x="{(100-iw)/2:.3f}" y="4" width="{iw:.3f}" height="92" href="data:image/png;base64,{encoded}"/></svg>\n')
print('Exported the original silhouette in flat gold/ivory and square icon sizes.')
