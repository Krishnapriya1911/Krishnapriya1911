"""Render a self-hosted profile animation. Requires Pillow; no remote services."""
from pathlib import Path
import math
from PIL import Image, ImageDraw, ImageFont

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / 'assets'
OUT.mkdir(exist_ok=True)
W, H = 1000, 320
FONT = '/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf'
BOLD = '/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf'
MONO = '/usr/share/fonts/truetype/dejavu/DejaVuSansMono.ttf'
def font(size, path=FONT): return ImageFont.truetype(path, size)

def butterfly(image, phase):
    """A little guide with shaded wings, perspective flapping and a looping flight."""
    x = 604 + 20 * math.sin(phase)
    y = 155 + 69 * math.sin(phase * 2)
    flap = .28 + .72 * (1 + math.sin(phase * 9)) / 2
    layer = Image.new('RGBA', (180, 150))
    pen = ImageDraw.Draw(layer)
    # Draw large, then downsample for smooth wing edges.
    def wing(side, points, fill, inset, shine):
        scale = flap * (1 if side == -1 else .82 + .14 * math.cos(phase))
        def project(ps):
            return [(90 + side * px * scale, 76 + py) for px, py in ps]
        pen.polygon(project(points), fill=fill)
        pen.line(project(points + [points[0]]), fill='#e6dfff', width=2)
        pen.polygon(project(inset), fill=shine)
        pen.line(project([(0, 0), (24, -20), (39, -32)]), fill='#e2d7ff', width=2)
        pen.line(project([(0, 1), (20, 22), (29, 26)]), fill='#aef9ee', width=2)
        for dx, dy in [(38,-32),(45,-22),(28,26)]:
            cx, cy = project([(dx,dy)])[0]
            pen.ellipse((cx-2,cy-2,cx+2,cy+2), fill='#fff3ff')
    upper = [(0,0),(12,-31),(31,-48),(47,-45),(54,-29),(46,-10),(26,4),(0,7)]
    lower = [(0,4),(25,1),(37,15),(31,35),(18,42),(7,32),(0,10)]
    for side in [-1,1]:
        wing(side, lower, '#537dc3', [(3,8),(20,8),(28,20),(20,31),(9,26)], '#8be1dc')
        wing(side, upper, '#7c67ce', [(5,-2),(16,-26),(33,-39),(42,-34),(34,-17)], '#c6acff')
    pen.ellipse((85,56,95,98), fill='#d7f9ff', outline='#3b566f', width=2)
    pen.line((89,64,89,90), fill='#ffffff', width=2)
    pen.ellipse((85,52,95,62), fill='#f0edff')
    pen.line((87,54,80,44,76,43), fill='#dacbff', width=2)
    pen.line((93,54,100,44,104,43), fill='#dacbff', width=2)
    layer = layer.resize((90,75), Image.Resampling.LANCZOS)
    image.paste(layer, (round(x-45),round(y-38)), layer)

base = Image.new('RGB', (W, H))
pixels = base.load()
for y in range(H):
    for x in range(W):
        glow = max(0, 1 - math.hypot((x-820)/520, (y-120)/300))
        pixels[x, y] = (int(10+13*glow), int(17+13*glow), int(31+34*glow))
d = ImageDraw.Draw(base)
d.rounded_rectangle((1, 1, W-2, H-2), radius=20, outline='#33435c', width=2)
for x in range(600, W, 35): d.line((x, 28, x, H-30), fill='#202d43')
for y in range(40, H-20, 35): d.line((595, y, W-28, y), fill='#202d43')
d.rounded_rectangle((36, 30, 305, 58), radius=14, fill='#173838')
d.ellipse((49, 40, 57, 48), fill='#7ce6cd')
d.text((66, 35), 'DATA / SOFTWARE / CLOUD', font=font(14, MONO), fill='#9cebd8')
d.text((37, 81), "Hi, I'm", font=font(23), fill='#a7b9d0')
# Shallow extruded lettering gives the name depth without losing legibility.
for offset in range(5, 0, -1):
    d.text((36+offset, 111+offset), 'Krishna Priya', font=font(48, BOLD), fill='#274252')
d.text((36, 111), 'Krishna Priya', font=font(48, BOLD), fill='#eff8ff')
d.text((38, 174), 'Building ideas into working systems.', font=font(21), fill='#c4d0e0')
d.line((38, 262, 555, 262), fill='#33435c', width=1)
d.text((38, 279), 'PYTHON  /  SQL  /  TYPESCRIPT', font=font(14, MONO), fill='#a7b9d0')

vertices = [(x, y, z) for x in (-1, 1) for y in (-1, 1) for z in (-1, 1)]
edges = [(i,j) for i in range(8) for j in range(i+1,8)
         if sum(a != b for a,b in zip(vertices[i],vertices[j])) == 1]
frames=[]
roles=['Data engineering', 'Backend development', 'Cloud automation']
for n in range(90):
    im=base.copy(); d=ImageDraw.Draw(im)
    phase=2*math.pi*n/90
    angle=phase+0.4
    points=[]
    for x,y,z in vertices:
        xr=x*math.cos(angle)+z*math.sin(angle)
        zr=-x*math.sin(angle)+z*math.cos(angle)
        yr=y*math.cos(.45)-zr*math.sin(.45)
        zr2=y*math.sin(.45)+zr*math.cos(.45)
        scale=63*(3.8/(3.8+zr2))
        points.append((int(793+xr*scale), int(144+yr*scale+7*math.sin(phase))))
    d.ellipse((697, 245, 890, 273), fill='#142a37', outline='#2d6c72', width=2)
    for i,j in edges: d.line((points[i],points[j]), fill='#81e2d1', width=3)
    for x,y in points: d.ellipse((x-4,y-4,x+4,y+4), fill='#ddfff8')
    # A packet orbits the wireframe, while one role types in per segment.
    ox=int(793+133*math.cos(phase)); oy=int(151+49*math.sin(phase))
    d.ellipse((ox-5,oy-5,ox+5,oy+5), fill='#bfafff')
    role=roles[n//30]
    count=min(len(role), (n%30)*2+1)
    d.text((38, 220), '> '+role[:count]+('|' if n%10<6 else ''), font=font(20, MONO), fill='#89e5cf')
    d.text((725, 283), 'BUILD. TEST. REFINE.', font=font(12, MONO), fill='#b8c7db')
    butterfly(im, phase)
    frames.append(im)
palette = frames[0].quantize(colors=96)
frames[20].save(OUT/'profile-banner-static.png')
frames = [frame.quantize(palette=palette, dither=Image.Dither.NONE) for frame in frames]
frames[0].save(OUT/'profile-banner.gif', save_all=True, append_images=frames[1:], duration=90, loop=0, optimize=True, disposal=1)
print(f'Created {len(frames)} frames; GIF { (OUT / "profile-banner.gif").stat().st_size:,} bytes')
