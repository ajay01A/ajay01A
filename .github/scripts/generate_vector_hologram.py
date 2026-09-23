#!/usr/bin/env python3
"""
Convert user photo into animated Cyberpunk Vector Particle Hologram for dark.svg and light.svg.
"""
from PIL import Image, ImageEnhance
import os, random

def generate_hologram():
    base_dir = r"c:\Users\LENOVO\OneDrive\Documents\ajaygprofile\ajaygprofile"
    src_path = os.path.join(base_dir, "my_image.jpg")
    
    im = Image.open(src_path)
    w_orig, h_orig = im.size
    
    # Target grid: 300 width x 340 height (matches SVG transform scale 1.24, 1.4471 for 400x492 card)
    target_w, target_h = 300, 340
    target_ratio = target_w / target_h
    
    if (w_orig / h_orig) > target_ratio:
        new_w = int(h_orig * target_ratio)
        crop_box = ((w_orig - new_w) // 2, 0, (w_orig - new_w) // 2 + new_w, h_orig)
    else:
        new_h = int(w_orig / target_ratio)
        crop_box = (0, int((h_orig - new_h) * 0.25), w_orig, int((h_orig - new_h) * 0.25) + new_h)
        
    cropped = im.crop(crop_box).resize((target_w, target_h), Image.Resampling.LANCZOS)
    rgb = cropped.convert("RGB")
    w, h = target_w, target_h
    
    # Accurate connected sky segmentation
    visited = set()
    queue = [(x, 0) for x in range(w)]
    sky_set = set()

    def is_shoulder_or_below(x, y):
        # Left shoulder boundary: y > 265 at x=0, y > 235 at x=90
        if x <= 95 and y >= (265 - 0.3 * x):
            return True
        # Right shoulder boundary: y > 255 at x=299, y > 230 at x=205
        if x >= 205 and y >= (230 + 0.26 * (x - 205)):
            return True
        if y >= 275:
            return True
        return False

    def is_sky(r, g, b, x, y):
        if is_shoulder_or_below(x, y):
            return False
        lum = (r + g + b) / 3
        if lum < 125:
            return False
        if r > b + 25:
            return False
        if b < r - 12:
            return False
        return True

    for pt in queue:
        if pt not in visited:
            q = [pt]
            visited.add(pt)
            while q:
                cx, cy = q.pop()
                r, g, b = rgb.getpixel((cx, cy))
                if is_sky(r, g, b, cx, cy):
                    sky_set.add((cx, cy))
                    for dx, dy in [(-1, 0), (1, 0), (0, -1), (0, 1)]:
                        nx, ny = cx + dx, cy + dy
                        if 0 <= nx < w and 0 <= ny < h and (nx, ny) not in visited:
                            visited.add((nx, ny))
                            q.append((nx, ny))

    # Foreground enhancement and dithering
    gray = cropped.convert("L")
    enh = ImageEnhance.Contrast(gray)
    gray = enh.enhance(1.85)
    enh = ImageEnhance.Sharpness(gray)
    gray = enh.enhance(2.0)
    dithered = gray.convert("1")
    
    # Extract active points (points that are in foreground AND dithered as lit)
    active_pixels = set()
    for y in range(h):
        for x in range(w):
            if (x, y) not in sky_set:
                if dithered.getpixel((x, y)) == 255:
                    active_pixels.add((x, y))
                    
    print(f"Total active hologram pixels: {len(active_pixels)}")
    
    # Generate run-length horizontal segments for optimal SVG size
    segments = []
    for y in range(h):
        x = 0
        while x < w:
            if (x, y) in active_pixels:
                start_x = x
                while x < w and (x, y) in active_pixels:
                    x += 1
                length = x - start_x
                segments.append((start_x, y, length))
            else:
                x += 1
                
    print(f"Compressed into {len(segments)} horizontal vector paths.")
    
    # Shuffle into 60 animation batches
    random.seed(42)
    batches = [[] for _ in range(60)]
    for seg in segments:
        b_idx = random.randint(0, 59)
        batches[b_idx].append(seg)
        
    def segs_to_path(segs):
        d_parts = []
        for x, y, length in segs:
            if length == 1:
                d_parts.append(f"M{x} {y}h1v1h-1z")
            else:
                d_parts.append(f"M{x} {y}h{length}v1h-{length}z")
        return "".join(d_parts)
        
    # Build entrance animation groups
    anim_groups = []
    for i, b in enumerate(batches):
        if not b:
            continue
        begin_time = 0.20 + (i * 0.03)
        path_data = segs_to_path(b)
        group_svg = (
            f'<g opacity="0">'
            f'<animate attributeName="opacity" values="0;1" dur="0.9s" begin="{begin_time:.2f}s" '
            f'fill="freeze" calcMode="spline" keyTimes="0;1" keySplines=".4 0 .2 1"/>'
            f'<path d="{path_data}"/>'
            f'</g>'
        )
        anim_groups.append(group_svg)
        
    entrance_svg = "\n".join(anim_groups)
    
    # Build steady-state vector paths
    all_path_data = segs_to_path(segments)
    
    # Floating particles (select 400 points from active pixels)
    sample_points = random.sample(list(active_pixels), min(450, len(active_pixels)))
    particle_uses_dark = []
    particle_uses_light = []
    
    for px, py in sample_points:
        dx1 = random.randint(-18, 18)
        dy1 = random.randint(-24, 24)
        dx2 = random.randint(-18, 18)
        dy2 = random.randint(-24, 24)
        p1 = f"{px} {py}"
        p2 = f"{px+dx1} {py+dy1}"
        p3 = f"{px+dx2} {py+dy2}"
        dur = round(random.uniform(9.0, 15.0), 1)
        begin = round(random.uniform(3.2, 4.5), 1)
        
        u_dark = (
            f'<use href="#tvdark" opacity="0">'
            f'<animate attributeName="opacity" values="0;0;0.9;0.9;0.9;0" keyTimes="0;0.2;0.3;0.7;0.85;1" dur="{dur}s" begin="{begin}s" repeatCount="indefinite"/>'
            f'<animateTransform attributeName="transform" type="translate" values="{p1};{p1};{p2};{p3};{p1}" dur="{dur}s" begin="{begin}s" repeatCount="indefinite"/>'
            f'</use>'
        )
        u_light = (
            f'<use href="#tvlight" opacity="0">'
            f'<animate attributeName="opacity" values="0;0;0.9;0.9;0.9;0" keyTimes="0;0.2;0.3;0.7;0.85;1" dur="{dur}s" begin="{begin}s" repeatCount="indefinite"/>'
            f'<animateTransform attributeName="transform" type="translate" values="{p1};{p1};{p2};{p3};{p1}" dur="{dur}s" begin="{begin}s" repeatCount="indefinite"/>'
            f'</use>'
        )
        particle_uses_dark.append(u_dark)
        particle_uses_light.append(u_light)
        
    particles_dark_svg = "\n".join(particle_uses_dark)
    particles_light_svg = "\n".join(particle_uses_light)
    
    # ------------------ DARK.SVG ------------------
    dark_output = f'''<svg xmlns="http://www.w3.org/2000/svg" width="1180" height="610" viewBox="0 0 1180 610" font-family="ui-monospace,SFMono-Regular,Menlo,Consolas,'Liberation Mono',monospace" role="img" aria-label="Ajay — profile.sh --live">
<defs>
<linearGradient id="accent" x1="0" y1="0" x2="1" y2="0">
      <stop offset="0" stop-color="#7C3AED"><animate attributeName="stop-color" values="#7C3AED;#22D3EE;#10B981;#7C3AED" dur="10s" repeatCount="indefinite"/></stop>
      <stop offset="0.5" stop-color="#22D3EE"><animate attributeName="stop-color" values="#22D3EE;#10B981;#7C3AED;#22D3EE" dur="10s" repeatCount="indefinite"/></stop>
      <stop offset="1" stop-color="#10B981"><animate attributeName="stop-color" values="#10B981;#7C3AED;#22D3EE;#10B981" dur="10s" repeatCount="indefinite"/></stop>
    </linearGradient>
<linearGradient id="panelGrad" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#0A101F"/><stop offset="1" stop-color="#0C1426"/></linearGradient>
<filter id="glow8" x="-60%" y="-60%" width="220%" height="220%"><feGaussianBlur stdDeviation="8"/></filter>
<filter id="glow3" x="-60%" y="-60%" width="220%" height="220%"><feGaussianBlur stdDeviation="3"/></filter>
<filter id="txtGlow" x="-30%" y="-30%" width="160%" height="160%"><feGaussianBlur stdDeviation="0.9" result="b"/><feMerge><feMergeNode in="b"/><feMergeNode in="SourceGraphic"/></feMerge></filter>
<clipPath id="winClip"><rect x="2" y="2" width="1176" height="606" rx="18"/></clipPath>
<clipPath id="mapClip"><rect x="36" y="84" width="400" height="492" rx="10"/></clipPath>
<rect id="tvdark" width="2.4" height="1.7" fill="#A78BFA"/>
</defs>
<rect x="2" y="2" width="1176" height="606" rx="18" fill="#070B16"/>
<g clip-path="url(#winClip)">
<rect x="2" y="2" width="1176" height="606" fill="url(#panelGrad)"/>
<rect x="2" y="2" width="1176" height="46" fill="#0B1222"/>
<line x1="2" y1="48" x2="1178" y2="48" stroke="rgba(255,255,255,0.10)"/>
<circle cx="30" cy="25.0" r="5.5" fill="#ff5f56"/>
<circle cx="50" cy="25.0" r="5.5" fill="#ffbd2e"/>
<circle cx="70" cy="25.0" r="5.5" fill="#27c93f"/>
<text x="590.0" y="29.0" text-anchor="middle" font-size="12" fill="#94A3B8">er.ajay0718@gmail.com - % ./profile.sh --live</text>
<text x="38" y="74" font-size="10" letter-spacing="3" fill="#475569">VISUAL.MAP</text>

<!-- VISUAL.MAP Card Frame -->
<rect x="36" y="84" width="400" height="492" rx="10" fill="none" stroke="#22D3EE" stroke-width="2" opacity="0.45" filter="url(#glow3)"/>
<rect x="36" y="84" width="400" height="492" rx="10" fill="#0A101F" stroke="rgba(34,211,238,0.35)"/>

<!-- Avatar Hologram Content (Clipped to Card) -->
<g clip-path="url(#mapClip)">
  <!-- Phase 1: Hologram entrance scanning materialization (0.2s - 3.2s) -->
  <g transform="translate(50,86) scale(1.2400,1.4471)" fill="#A78BFA" shape-rendering="crispEdges">
    <set attributeName="opacity" to="0" begin="3.2s"/>
{entrance_svg}
  </g>

  <!-- Phase 2: Steady-state hologram with continuous pulse -->
  <g transform="translate(50,86) scale(1.2400,1.4471)" fill="#A78BFA" shape-rendering="crispEdges" opacity="0">
    <set attributeName="opacity" to="1" begin="3.2s"/>
    <g opacity="1">
      <animate attributeName="opacity" values="0.88;1;0.92;1;0.88" dur="6s" repeatCount="indefinite"/>
      <path d="{all_path_data}"/>
    </g>
  </g>

  <!-- Phase 3: Dynamic Floating Cyber Particles -->
  <g transform="translate(50,86) scale(1.2400,1.4471)">
{particles_dark_svg}
  </g>

  <!-- Holographic Scanline Overlay -->
  <line x1="36" y1="84" x2="436" y2="84" stroke="#22D3EE" stroke-width="1.8" opacity="0.4" filter="url(#glow3)">
    <animateTransform attributeName="transform" type="translate" values="0 0; 0 492; 0 0" dur="4.2s" repeatCount="indefinite"/>
  </line>

  <!-- Target Reticle Overlay -->
  <g opacity="0.35">
    <circle cx="236" cy="330" r="30" fill="none" stroke="#22D3EE" stroke-width="1" stroke-dasharray="4 4">
      <animateTransform attributeName="transform" type="rotate" from="0 236 330" to="360 236 330" dur="14s" repeatCount="indefinite"/>
    </circle>
    <circle cx="236" cy="330" r="3" fill="#22D3EE"/>
    <line x1="196" y1="330" x2="218" y2="330" stroke="#22D3EE" stroke-width="1"/>
    <line x1="254" y1="330" x2="276" y2="330" stroke="#22D3EE" stroke-width="1"/>
    <line x1="236" y1="290" x2="236" y2="312" stroke="#22D3EE" stroke-width="1"/>
    <line x1="236" y1="348" x2="236" y2="370" stroke="#22D3EE" stroke-width="1"/>
  </g>
</g>

<!-- Corner HUD Brackets -->
<path d="M 54 84 L 36 84 L 36 102" fill="none" stroke="#22D3EE" stroke-width="2.5" opacity="0.85"/>
<path d="M 418 84 L 436 84 L 436 102" fill="none" stroke="#22D3EE" stroke-width="2.5" opacity="0.85"/>
<path d="M 54 576 L 36 576 L 36 558" fill="none" stroke="#22D3EE" stroke-width="2.5" opacity="0.85"/>
<path d="M 418 576 L 436 576 L 436 558" fill="none" stroke="#22D3EE" stroke-width="2.5" opacity="0.85"/>

<!-- HUD Badges -->
<g opacity="0"><animate attributeName="opacity" values="0;1" dur="0.5s" begin="0.4s" fill="freeze"/>
  <rect x="48" y="96" width="76" height="20" rx="4" fill="rgba(10,16,31,0.85)" stroke="rgba(34,211,238,0.5)" stroke-width="1"/>
  <circle cx="59" cy="106" r="3.5" fill="#10B981"><animate attributeName="opacity" values="1;0.3;1" dur="1.5s" repeatCount="indefinite"/></circle>
  <text x="68" y="110" font-size="9.5" fill="#22D3EE" font-weight="700" letter-spacing="1">LIVE.MAP</text>

  <rect x="350" y="96" width="74" height="20" rx="4" fill="rgba(10,16,31,0.85)" stroke="rgba(167,139,250,0.5)" stroke-width="1"/>
  <text x="387" y="110" text-anchor="middle" font-size="9.5" fill="#E9D5FF" font-weight="700" letter-spacing="1">ID: #AJAY</text>

  <rect x="48" y="542" width="104" height="20" rx="4" fill="rgba(10,16,31,0.85)" stroke="rgba(34,211,238,0.3)" stroke-width="1"/>
  <text x="100" y="556" text-anchor="middle" font-size="9" fill="#94A3B8" font-weight="600" letter-spacing="0.8">DEV // FULL-STACK</text>

  <rect x="330" y="542" width="94" height="20" rx="4" fill="rgba(10,16,31,0.85)" stroke="rgba(16,185,129,0.3)" stroke-width="1"/>
  <text x="377" y="556" text-anchor="middle" font-size="9" fill="#10B981" font-weight="600" letter-spacing="0.8">ONLINE &#9679; 2026</text>
</g>

<!-- SYSTEM INFO SECTION -->
<text x="470" y="106" font-size="13" letter-spacing="2" fill="#22D3EE" filter="url(#txtGlow)">SYSTEM.INFO</text>
<line x1="566" y1="102" x2="1061" y2="102" stroke="rgba(255,255,255,0.10)"/>
<text x="1125" y="106" text-anchor="end" font-size="12" fill="#F87171" font-weight="700"><tspan>&#9679;</tspan> LIVE<animate attributeName="opacity" values="1;0.25;1" dur="1.6s" repeatCount="indefinite"/></text>

<g opacity="0"><animate attributeName="opacity" from="0" to="1" dur="0.5s" begin="0.6s" fill="freeze"/>
<rect x="470" y="122" width="215" height="20" rx="4" fill="#4C1D95"/>
<text x="479" y="136" font-size="14" font-weight="700" fill="#E9D5FF">er.ajay0718@gmail.com</text>
<line x1="695" y1="130" x2="1125" y2="130" stroke="rgba(255,255,255,0.10)"/>
</g>

<g opacity="0"><animate attributeName="opacity" from="0" to="1" dur="0.4s" begin="0.90s" fill="freeze"/><animateTransform attributeName="transform" type="translate" values="-8 0;0 0" dur="0.4s" begin="0.90s" fill="freeze"/><text x="470" y="162" font-size="14" textLength="655" lengthAdjust="spacingAndGlyphs" xml:space="preserve"><tspan fill="#22D3EE">Subject </tspan><tspan fill="rgba(148,163,184,0.35)">............................................................</tspan><tspan fill="#F8FAFC" font-weight="600"> Ajay Pal</tspan></text></g>
<g opacity="0"><animate attributeName="opacity" from="0" to="1" dur="0.4s" begin="1.02s" fill="freeze"/><animateTransform attributeName="transform" type="translate" values="-8 0;0 0" dur="0.4s" begin="1.02s" fill="freeze"/><text x="470" y="185" font-size="14" textLength="655" lengthAdjust="spacingAndGlyphs" xml:space="preserve"><tspan fill="#22D3EE">Role </tspan><tspan fill="rgba(148,163,184,0.35)">.....................................................</tspan><tspan fill="#F8FAFC" font-weight="600"> Full-Stack Developer</tspan></text></g>
<g opacity="0"><animate attributeName="opacity" from="0" to="1" dur="0.4s" begin="1.14s" fill="freeze"/><animateTransform attributeName="transform" type="translate" values="-8 0;0 0" dur="0.4s" begin="1.14s" fill="freeze"/><text x="470" y="208" font-size="14" textLength="655" lengthAdjust="spacingAndGlyphs" xml:space="preserve"><tspan fill="#22D3EE">Origin </tspan><tspan fill="rgba(148,163,184,0.35)">.....................................................</tspan><tspan fill="#F8FAFC" font-weight="600"> India</tspan></text></g>
<g opacity="0"><animate attributeName="opacity" from="0" to="1" dur="0.4s" begin="1.26s" fill="freeze"/><animateTransform attributeName="transform" type="translate" values="-8 0;0 0" dur="0.4s" begin="1.26s" fill="freeze"/><text x="470" y="231" font-size="14" textLength="655" lengthAdjust="spacingAndGlyphs" xml:space="preserve"><tspan fill="#22D3EE">Education </tspan><tspan fill="rgba(148,163,184,0.35)">..........................................................</tspan><tspan fill="#F8FAFC" font-weight="600"> B.Tech / CSE</tspan></text></g>
<g opacity="0"><animate attributeName="opacity" from="0" to="1" dur="0.4s" begin="1.38s" fill="freeze"/><animateTransform attributeName="transform" type="translate" values="-8 0;0 0" dur="0.4s" begin="1.38s" fill="freeze"/><text x="470" y="254" font-size="14" textLength="655" lengthAdjust="spacingAndGlyphs" xml:space="preserve"><tspan fill="#22D3EE">Status </tspan><tspan fill="rgba(148,163,184,0.35)">.........................................</tspan><tspan fill="#F8FAFC" font-weight="600"> Building + Learning + Shipping</tspan></text></g>
<g opacity="0"><animate attributeName="opacity" from="0" to="1" dur="0.4s" begin="1.50s" fill="freeze"/><animateTransform attributeName="transform" type="translate" values="-8 0;0 0" dur="0.4s" begin="1.50s" fill="freeze"/><text x="470" y="277" font-size="14" textLength="655" lengthAdjust="spacingAndGlyphs" xml:space="preserve"><tspan fill="#22D3EE">ToolChain </tspan><tspan fill="rgba(148,163,184,0.35)">.................................</tspan><tspan fill="#F8FAFC" font-weight="600"> VS Code, Git, Docker, Figma</tspan></text></g>
<g opacity="0"><animate attributeName="opacity" from="0" to="1" dur="0.4s" begin="1.72s" fill="freeze"/><animateTransform attributeName="transform" type="translate" values="-8 0;0 0" dur="0.4s" begin="1.72s" fill="freeze"/><text x="470" y="308" font-size="14" textLength="655" lengthAdjust="spacingAndGlyphs" xml:space="preserve"><tspan fill="#22D3EE">Core.Lang </tspan><tspan fill="rgba(148,163,184,0.35)">...................................................</tspan><tspan fill="#F8FAFC" font-weight="600"> TypeScript, Python, C++</tspan></text></g>
<g opacity="0"><animate attributeName="opacity" from="0" to="1" dur="0.4s" begin="1.84s" fill="freeze"/><animateTransform attributeName="transform" type="translate" values="-8 0;0 0" dur="0.4s" begin="1.84s" fill="freeze"/><text x="470" y="331" font-size="14" textLength="655" lengthAdjust="spacingAndGlyphs" xml:space="preserve"><tspan fill="#22D3EE">Core.Frontend </tspan><tspan fill="rgba(148,163,184,0.35)">.........................................................</tspan><tspan fill="#F8FAFC" font-weight="600"> React, Next.js, TailwindCSS</tspan></text></g>
<g opacity="0"><animate attributeName="opacity" from="0" to="1" dur="0.4s" begin="1.96s" fill="freeze"/><animateTransform attributeName="transform" type="translate" values="-8 0;0 0" dur="0.4s" begin="1.96s" fill="freeze"/><text x="470" y="354" font-size="14" textLength="655" lengthAdjust="spacingAndGlyphs" xml:space="preserve"><tspan fill="#22D3EE">Core.Backend </tspan><tspan fill="rgba(148,163,184,0.35)">..........................................................</tspan><tspan fill="#F8FAFC" font-weight="600"> Node.js, Express</tspan></text></g>
<g opacity="0"><animate attributeName="opacity" from="0" to="1" dur="0.4s" begin="2.08s" fill="freeze"/><animateTransform attributeName="transform" type="translate" values="-8 0;0 0" dur="0.4s" begin="2.08s" fill="freeze"/><text x="470" y="377" font-size="14" textLength="655" lengthAdjust="spacingAndGlyphs" xml:space="preserve"><tspan fill="#22D3EE">Core.Database </tspan><tspan fill="rgba(148,163,184,0.35)">...............................................</tspan><tspan fill="#F8FAFC" font-weight="600"> MongoDB, PostgreSQL</tspan></text></g>
<g opacity="0"><animate attributeName="opacity" from="0" to="1" dur="0.4s" begin="2.20s" fill="freeze"/><animateTransform attributeName="transform" type="translate" values="-8 0;0 0" dur="0.4s" begin="2.20s" fill="freeze"/><text x="470" y="400" font-size="14" textLength="655" lengthAdjust="spacingAndGlyphs" xml:space="preserve"><tspan fill="#22D3EE">Core.Infra </tspan><tspan fill="rgba(148,163,184,0.35)">................................................</tspan><tspan fill="#F8FAFC" font-weight="600"> Vercel, Docker, Git</tspan></text></g>
<g opacity="0"><animate attributeName="opacity" from="0" to="1" dur="0.4s" begin="2.42s" fill="freeze"/><text x="470" y="431" font-size="14" textLength="655" lengthAdjust="spacingAndGlyphs" xml:space="preserve"><tspan fill="#94A3B8">- Contact </tspan><tspan fill="rgba(148,163,184,0.35)">---------------------------------------------------------------------</tspan></text></g>
<g opacity="0"><animate attributeName="opacity" from="0" to="1" dur="0.4s" begin="2.54s" fill="freeze"/><animateTransform attributeName="transform" type="translate" values="-8 0;0 0" dur="0.4s" begin="2.54s" fill="freeze"/><text x="470" y="454" font-size="14" textLength="655" lengthAdjust="spacingAndGlyphs" xml:space="preserve"><tspan fill="#22D3EE">Grid.Mail </tspan><tspan fill="rgba(148,163,184,0.35)">.........................................</tspan><tspan fill="#F8FAFC" font-weight="600"> er.ajay0718@gmail.com</tspan></text></g>
<g opacity="0"><animate attributeName="opacity" from="0" to="1" dur="0.4s" begin="2.66s" fill="freeze"/><animateTransform attributeName="transform" type="translate" values="-8 0;0 0" dur="0.4s" begin="2.66s" fill="freeze"/><text x="470" y="477" font-size="14" textLength="655" lengthAdjust="spacingAndGlyphs" xml:space="preserve"><tspan fill="#22D3EE">Grid.Portfolio </tspan><tspan fill="rgba(148,163,184,0.35)">..........................................</tspan><tspan fill="#F8FAFC" font-weight="600"> ajay.dev</tspan></text></g>
<g opacity="0"><animate attributeName="opacity" from="0" to="1" dur="0.4s" begin="2.78s" fill="freeze"/><animateTransform attributeName="transform" type="translate" values="-8 0;0 0" dur="0.4s" begin="2.78s" fill="freeze"/><text x="470" y="500" font-size="14" textLength="655" lengthAdjust="spacingAndGlyphs" xml:space="preserve"><tspan fill="#22D3EE">Grid.LinkedIn </tspan><tspan fill="rgba(148,163,184,0.35)">............................................</tspan><tspan fill="#F8FAFC" font-weight="600"> Ajay Pal</tspan></text></g>
<g opacity="0"><animate attributeName="opacity" from="0" to="1" dur="0.4s" begin="2.90s" fill="freeze"/><animateTransform attributeName="transform" type="translate" values="-8 0;0 0" dur="0.4s" begin="2.90s" fill="freeze"/><text x="470" y="523" font-size="14" textLength="655" lengthAdjust="spacingAndGlyphs" xml:space="preserve"><tspan fill="#22D3EE">Grid.GitHub </tspan><tspan fill="rgba(148,163,184,0.35)">.........................................................</tspan><tspan fill="#F8FAFC" font-weight="600"> @ajay01A</tspan></text></g>
<g opacity="0"><animate attributeName="opacity" from="0" to="1" dur="0.4s" begin="3.02s" fill="freeze"/><animateTransform attributeName="transform" type="translate" values="-8 0;0 0" dur="0.4s" begin="3.02s" fill="freeze"/><text x="470" y="546" font-size="14" textLength="655" lengthAdjust="spacingAndGlyphs" xml:space="preserve"><tspan fill="#22D3EE">Grid.Connect </tspan><tspan fill="rgba(148,163,184,0.35)">......................................................</tspan><tspan fill="#F8FAFC" font-weight="600"> Open for Collaboration</tspan></text></g>
<g opacity="0"><animate attributeName="opacity" from="0" to="1" dur="0.5s" begin="3.34s" fill="freeze"/>
<text x="470" y="577" font-size="14" fill="#94A3B8">&#9656; More about me &amp; projects below in README &#8595; <tspan fill="#22D3EE">&#9608;<animate attributeName="fill-opacity" values="1;0;1" dur="1s" repeatCount="indefinite"/></tspan></text>
</g>
</g>
<rect x="3" y="3" width="1174" height="604" rx="17" fill="none" stroke="url(#accent)" stroke-width="3" opacity="0.55" filter="url(#glow8)"/>
<rect x="3" y="3" width="1174" height="604" rx="17" fill="none" stroke="url(#accent)" stroke-width="1.6"/>
</svg>
'''
    
    with open(os.path.join(base_dir, "dark.svg"), "w", encoding="utf-8") as f:
        f.write(dark_output)
    print("dark.svg successfully written. Size:", len(dark_output), "bytes")

    # ------------------ LIGHT.SVG ------------------
    light_output = f'''<svg xmlns="http://www.w3.org/2000/svg" width="1180" height="610" viewBox="0 0 1180 610" font-family="ui-monospace,SFMono-Regular,Menlo,Consolas,'Liberation Mono',monospace" role="img" aria-label="Ajay — profile.sh --live">
<defs>
<linearGradient id="accent" x1="0" y1="0" x2="1" y2="0">
      <stop offset="0" stop-color="#2563EB"><animate attributeName="stop-color" values="#2563EB;#06B6D4;#10B981;#2563EB" dur="10s" repeatCount="indefinite"/></stop>
      <stop offset="0.5" stop-color="#06B6D4"><animate attributeName="stop-color" values="#06B6D4;#10B981;#2563EB;#06B6D4" dur="10s" repeatCount="indefinite"/></stop>
      <stop offset="1" stop-color="#10B981"><animate attributeName="stop-color" values="#10B981;#2563EB;#06B6D4;#10B981" dur="10s" repeatCount="indefinite"/></stop>
    </linearGradient>
<linearGradient id="panelGrad" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#F8FAFC"/><stop offset="1" stop-color="#FFFFFF"/></linearGradient>
<filter id="glow8" x="-60%" y="-60%" width="220%" height="220%"><feGaussianBlur stdDeviation="8"/></filter>
<filter id="glow3" x="-60%" y="-60%" width="220%" height="220%"><feGaussianBlur stdDeviation="3"/></filter>
<filter id="txtGlow" x="-30%" y="-30%" width="160%" height="160%"><feGaussianBlur stdDeviation="0.9" result="b"/><feMerge><feMergeNode in="b"/><feMergeNode in="SourceGraphic"/></feMerge></filter>
<clipPath id="winClip"><rect x="2" y="2" width="1176" height="606" rx="18"/></clipPath>
<clipPath id="mapClip"><rect x="36" y="84" width="400" height="492" rx="10"/></clipPath>
<rect id="tvlight" width="2.4" height="1.7" fill="#7C3AED"/>
</defs>
<rect x="2" y="2" width="1176" height="606" rx="18" fill="#FFFFFF"/>
<g clip-path="url(#winClip)">
<rect x="2" y="2" width="1176" height="606" fill="url(#panelGrad)"/>
<rect x="2" y="2" width="1176" height="46" fill="#F1F5F9"/>
<line x1="2" y1="48" x2="1178" y2="48" stroke="rgba(15,23,42,0.10)"/>
<circle cx="30" cy="25.0" r="5.5" fill="#ff5f56"/>
<circle cx="50" cy="25.0" r="5.5" fill="#ffbd2e"/>
<circle cx="70" cy="25.0" r="5.5" fill="#27c93f"/>
<text x="590.0" y="29.0" text-anchor="middle" font-size="12" fill="#475569">er.ajay0718@gmail.com - % ./profile.sh --live</text>
<text x="38" y="74" font-size="10" letter-spacing="3" fill="#94A3B8">VISUAL.MAP</text>

<!-- VISUAL.MAP Card Frame -->
<rect x="36" y="84" width="400" height="492" rx="10" fill="none" stroke="#06B6D4" stroke-width="2" opacity="0.45" filter="url(#glow3)"/>
<rect x="36" y="84" width="400" height="492" rx="10" fill="#F8FAFC" stroke="rgba(8,145,178,0.40)"/>

<!-- Avatar Hologram Content (Clipped to Card) -->
<g clip-path="url(#mapClip)">
  <!-- Phase 1: Hologram entrance scanning materialization (0.2s - 3.2s) -->
  <g transform="translate(50,86) scale(1.2400,1.4471)" fill="#7C3AED" shape-rendering="crispEdges">
    <set attributeName="opacity" to="0" begin="3.2s"/>
{entrance_svg}
  </g>

  <!-- Phase 2: Steady-state hologram with continuous pulse -->
  <g transform="translate(50,86) scale(1.2400,1.4471)" fill="#7C3AED" shape-rendering="crispEdges" opacity="0">
    <set attributeName="opacity" to="1" begin="3.2s"/>
    <g opacity="1">
      <animate attributeName="opacity" values="0.88;1;0.92;1;0.88" dur="6s" repeatCount="indefinite"/>
      <path d="{all_path_data}"/>
    </g>
  </g>

  <!-- Phase 3: Dynamic Floating Cyber Particles -->
  <g transform="translate(50,86) scale(1.2400,1.4471)">
{particles_light_svg}
  </g>

  <!-- Holographic Scanline Overlay -->
  <line x1="36" y1="84" x2="436" y2="84" stroke="#0891B2" stroke-width="1.8" opacity="0.4" filter="url(#glow3)">
    <animateTransform attributeName="transform" type="translate" values="0 0; 0 492; 0 0" dur="4.2s" repeatCount="indefinite"/>
  </line>

  <!-- Target Reticle Overlay -->
  <g opacity="0.35">
    <circle cx="236" cy="330" r="30" fill="none" stroke="#0891B2" stroke-width="1" stroke-dasharray="4 4">
      <animateTransform attributeName="transform" type="rotate" from="0 236 330" to="360 236 330" dur="14s" repeatCount="indefinite"/>
    </circle>
    <circle cx="236" cy="330" r="3" fill="#0891B2"/>
    <line x1="196" y1="330" x2="218" y2="330" stroke="#0891B2" stroke-width="1"/>
    <line x1="254" y1="330" x2="276" y2="330" stroke="#0891B2" stroke-width="1"/>
    <line x1="236" y1="290" x2="236" y2="312" stroke="#0891B2" stroke-width="1"/>
    <line x1="236" y1="348" x2="236" y2="370" stroke="#0891B2" stroke-width="1"/>
  </g>
</g>

<!-- Corner HUD Brackets -->
<path d="M 54 84 L 36 84 L 36 102" fill="none" stroke="#0891B2" stroke-width="2.5" opacity="0.85"/>
<path d="M 418 84 L 436 84 L 436 102" fill="none" stroke="#0891B2" stroke-width="2.5" opacity="0.85"/>
<path d="M 54 576 L 36 576 L 36 558" fill="none" stroke="#0891B2" stroke-width="2.5" opacity="0.85"/>
<path d="M 418 576 L 436 576 L 436 558" fill="none" stroke="#0891B2" stroke-width="2.5" opacity="0.85"/>

<!-- HUD Badges -->
<g opacity="0"><animate attributeName="opacity" values="0;1" dur="0.5s" begin="0.4s" fill="freeze"/>
  <rect x="48" y="96" width="76" height="20" rx="4" fill="rgba(248,250,252,0.9)" stroke="rgba(8,145,178,0.5)" stroke-width="1"/>
  <circle cx="59" cy="106" r="3.5" fill="#059669"><animate attributeName="opacity" values="1;0.3;1" dur="1.5s" repeatCount="indefinite"/></circle>
  <text x="68" y="110" font-size="9.5" fill="#0891B2" font-weight="700" letter-spacing="1">LIVE.MAP</text>

  <rect x="350" y="96" width="74" height="20" rx="4" fill="rgba(248,250,252,0.9)" stroke="rgba(124,58,237,0.5)" stroke-width="1"/>
  <text x="387" y="110" text-anchor="middle" font-size="9.5" fill="#7C3AED" font-weight="700" letter-spacing="1">ID: #AJAY</text>

  <rect x="48" y="542" width="104" height="20" rx="4" fill="rgba(248,250,252,0.9)" stroke="rgba(8,145,178,0.3)" stroke-width="1"/>
  <text x="100" y="556" text-anchor="middle" font-size="9" fill="#475569" font-weight="600" letter-spacing="0.8">DEV // FULL-STACK</text>

  <rect x="330" y="542" width="94" height="20" rx="4" fill="rgba(248,250,252,0.9)" stroke="rgba(5,150,105,0.3)" stroke-width="1"/>
  <text x="377" y="556" text-anchor="middle" font-size="9" fill="#059669" font-weight="600" letter-spacing="0.8">ONLINE &#9679; 2026</text>
</g>

<!-- SYSTEM INFO SECTION -->
<text x="470" y="106" font-size="13" letter-spacing="2" fill="#0891B2" filter="url(#txtGlow)">SYSTEM.INFO</text>
<line x1="566" y1="102" x2="1061" y2="102" stroke="rgba(15,23,42,0.10)"/>
<text x="1125" y="106" text-anchor="end" font-size="12" fill="#DC2626" font-weight="700"><tspan>&#9679;</tspan> LIVE<animate attributeName="opacity" values="1;0.25;1" dur="1.6s" repeatCount="indefinite"/></text>

<g opacity="0"><animate attributeName="opacity" from="0" to="1" dur="0.5s" begin="0.6s" fill="freeze"/>
<rect x="470" y="122" width="215" height="20" rx="4" fill="#DBEAFE"/>
<text x="479" y="136" font-size="14" font-weight="700" fill="#1D4ED8">er.ajay0718@gmail.com</text>
<line x1="695" y1="130" x2="1125" y2="130" stroke="rgba(15,23,42,0.10)"/>
</g>

<g opacity="0"><animate attributeName="opacity" from="0" to="1" dur="0.4s" begin="0.90s" fill="freeze"/><animateTransform attributeName="transform" type="translate" values="-8 0;0 0" dur="0.4s" begin="0.90s" fill="freeze"/><text x="470" y="162" font-size="14" textLength="655" lengthAdjust="spacingAndGlyphs" xml:space="preserve"><tspan fill="#0891B2">Subject </tspan><tspan fill="rgba(15,23,42,0.25)">............................................................</tspan><tspan fill="#0F172A" font-weight="600"> Ajay Pal</tspan></text></g>
<g opacity="0"><animate attributeName="opacity" from="0" to="1" dur="0.4s" begin="1.02s" fill="freeze"/><animateTransform attributeName="transform" type="translate" values="-8 0;0 0" dur="0.4s" begin="1.02s" fill="freeze"/><text x="470" y="185" font-size="14" textLength="655" lengthAdjust="spacingAndGlyphs" xml:space="preserve"><tspan fill="#0891B2">Role </tspan><tspan fill="rgba(15,23,42,0.25)">.....................................................</tspan><tspan fill="#0F172A" font-weight="600"> Full-Stack Developer</tspan></text></g>
<g opacity="0"><animate attributeName="opacity" from="0" to="1" dur="0.4s" begin="1.14s" fill="freeze"/><animateTransform attributeName="transform" type="translate" values="-8 0;0 0" dur="0.4s" begin="1.14s" fill="freeze"/><text x="470" y="208" font-size="14" textLength="655" lengthAdjust="spacingAndGlyphs" xml:space="preserve"><tspan fill="#0891B2">Origin </tspan><tspan fill="rgba(15,23,42,0.25)">.....................................................</tspan><tspan fill="#0F172A" font-weight="600"> India</tspan></text></g>
<g opacity="0"><animate attributeName="opacity" from="0" to="1" dur="0.4s" begin="1.26s" fill="freeze"/><animateTransform attributeName="transform" type="translate" values="-8 0;0 0" dur="0.4s" begin="1.26s" fill="freeze"/><text x="470" y="231" font-size="14" textLength="655" lengthAdjust="spacingAndGlyphs" xml:space="preserve"><tspan fill="#0891B2">Education </tspan><tspan fill="rgba(15,23,42,0.25)">..........................................................</tspan><tspan fill="#0F172A" font-weight="600"> B.Tech / CSE</tspan></text></g>
<g opacity="0"><animate attributeName="opacity" from="0" to="1" dur="0.4s" begin="1.38s" fill="freeze"/><animateTransform attributeName="transform" type="translate" values="-8 0;0 0" dur="0.4s" begin="1.38s" fill="freeze"/><text x="470" y="254" font-size="14" textLength="655" lengthAdjust="spacingAndGlyphs" xml:space="preserve"><tspan fill="#0891B2">Status </tspan><tspan fill="rgba(15,23,42,0.25)">.........................................</tspan><tspan fill="#0F172A" font-weight="600"> Building + Learning + Shipping</tspan></text></g>
<g opacity="0"><animate attributeName="opacity" from="0" to="1" dur="0.4s" begin="1.50s" fill="freeze"/><animateTransform attributeName="transform" type="translate" values="-8 0;0 0" dur="0.4s" begin="1.50s" fill="freeze"/><text x="470" y="277" font-size="14" textLength="655" lengthAdjust="spacingAndGlyphs" xml:space="preserve"><tspan fill="#0891B2">ToolChain </tspan><tspan fill="rgba(15,23,42,0.25)">.................................</tspan><tspan fill="#0F172A" font-weight="600"> VS Code, Git, Docker, Figma</tspan></text></g>
<g opacity="0"><animate attributeName="opacity" from="0" to="1" dur="0.4s" begin="1.72s" fill="freeze"/><animateTransform attributeName="transform" type="translate" values="-8 0;0 0" dur="0.4s" begin="1.72s" fill="freeze"/><text x="470" y="308" font-size="14" textLength="655" lengthAdjust="spacingAndGlyphs" xml:space="preserve"><tspan fill="#0891B2">Core.Lang </tspan><tspan fill="rgba(15,23,42,0.25)">...................................................</tspan><tspan fill="#0F172A" font-weight="600"> TypeScript, Python, C++</tspan></text></g>
<g opacity="0"><animate attributeName="opacity" from="0" to="1" dur="0.4s" begin="1.84s" fill="freeze"/><animateTransform attributeName="transform" type="translate" values="-8 0;0 0" dur="0.4s" begin="1.84s" fill="freeze"/><text x="470" y="331" font-size="14" textLength="655" lengthAdjust="spacingAndGlyphs" xml:space="preserve"><tspan fill="#0891B2">Core.Frontend </tspan><tspan fill="rgba(15,23,42,0.25)">.........................................................</tspan><tspan fill="#0F172A" font-weight="600"> React, Next.js, TailwindCSS</tspan></text></g>
<g opacity="0"><animate attributeName="opacity" from="0" to="1" dur="0.4s" begin="1.96s" fill="freeze"/><animateTransform attributeName="transform" type="translate" values="-8 0;0 0" dur="0.4s" begin="1.96s" fill="freeze"/><text x="470" y="354" font-size="14" textLength="655" lengthAdjust="spacingAndGlyphs" xml:space="preserve"><tspan fill="#0891B2">Core.Backend </tspan><tspan fill="rgba(15,23,42,0.25)">..........................................................</tspan><tspan fill="#0F172A" font-weight="600"> Node.js, Express</tspan></text></g>
<g opacity="0"><animate attributeName="opacity" from="0" to="1" dur="0.4s" begin="2.08s" fill="freeze"/><animateTransform attributeName="transform" type="translate" values="-8 0;0 0" dur="0.4s" begin="2.08s" fill="freeze"/><text x="470" y="377" font-size="14" textLength="655" lengthAdjust="spacingAndGlyphs" xml:space="preserve"><tspan fill="#0891B2">Core.Database </tspan><tspan fill="rgba(15,23,42,0.25)">...............................................</tspan><tspan fill="#0F172A" font-weight="600"> MongoDB, PostgreSQL</tspan></text></g>
<g opacity="0"><animate attributeName="opacity" from="0" to="1" dur="0.4s" begin="2.20s" fill="freeze"/><animateTransform attributeName="transform" type="translate" values="-8 0;0 0" dur="0.4s" begin="2.20s" fill="freeze"/><text x="470" y="400" font-size="14" textLength="655" lengthAdjust="spacingAndGlyphs" xml:space="preserve"><tspan fill="#0891B2">Core.Infra </tspan><tspan fill="rgba(15,23,42,0.25)">................................................</tspan><tspan fill="#0F172A" font-weight="600"> Vercel, Docker, Git</tspan></text></g>
<g opacity="0"><animate attributeName="opacity" from="0" to="1" dur="0.4s" begin="2.42s" fill="freeze"/><text x="470" y="431" font-size="14" textLength="655" lengthAdjust="spacingAndGlyphs" xml:space="preserve"><tspan fill="#475569">- Contact </tspan><tspan fill="rgba(15,23,42,0.25)">---------------------------------------------------------------------</tspan></text></g>
<g opacity="0"><animate attributeName="opacity" from="0" to="1" dur="0.4s" begin="2.54s" fill="freeze"/><animateTransform attributeName="transform" type="translate" values="-8 0;0 0" dur="0.4s" begin="2.54s" fill="freeze"/><text x="470" y="454" font-size="14" textLength="655" lengthAdjust="spacingAndGlyphs" xml:space="preserve"><tspan fill="#0891B2">Grid.Mail </tspan><tspan fill="rgba(15,23,42,0.25)">.........................................</tspan><tspan fill="#0F172A" font-weight="600"> er.ajay0718@gmail.com</tspan></text></g>
<g opacity="0"><animate attributeName="opacity" from="0" to="1" dur="0.4s" begin="2.66s" fill="freeze"/><animateTransform attributeName="transform" type="translate" values="-8 0;0 0" dur="0.4s" begin="2.66s" fill="freeze"/><text x="470" y="477" font-size="14" textLength="655" lengthAdjust="spacingAndGlyphs" xml:space="preserve"><tspan fill="#0891B2">Grid.Portfolio </tspan><tspan fill="rgba(15,23,42,0.25)">..........................................</tspan><tspan fill="#0F172A" font-weight="600"> ajay.dev</tspan></text></g>
<g opacity="0"><animate attributeName="opacity" from="0" to="1" dur="0.4s" begin="2.78s" fill="freeze"/><animateTransform attributeName="transform" type="translate" values="-8 0;0 0" dur="0.4s" begin="2.78s" fill="freeze"/><text x="470" y="500" font-size="14" textLength="655" lengthAdjust="spacingAndGlyphs" xml:space="preserve"><tspan fill="#0891B2">Grid.LinkedIn </tspan><tspan fill="rgba(15,23,42,0.25)">............................................</tspan><tspan fill="#0F172A" font-weight="600"> Ajay Pal</tspan></text></g>
<g opacity="0"><animate attributeName="opacity" from="0" to="1" dur="0.4s" begin="2.90s" fill="freeze"/><animateTransform attributeName="transform" type="translate" values="-8 0;0 0" dur="0.4s" begin="2.90s" fill="freeze"/><text x="470" y="523" font-size="14" textLength="655" lengthAdjust="spacingAndGlyphs" xml:space="preserve"><tspan fill="#0891B2">Grid.GitHub </tspan><tspan fill="rgba(15,23,42,0.25)">.........................................................</tspan><tspan fill="#0F172A" font-weight="600"> @ajay01A</tspan></text></g>
<g opacity="0"><animate attributeName="opacity" from="0" to="1" dur="0.4s" begin="3.02s" fill="freeze"/><animateTransform attributeName="transform" type="translate" values="-8 0;0 0" dur="0.4s" begin="3.02s" fill="freeze"/><text x="470" y="546" font-size="14" textLength="655" lengthAdjust="spacingAndGlyphs" xml:space="preserve"><tspan fill="#0891B2">Grid.Connect </tspan><tspan fill="rgba(15,23,42,0.25)">......................................................</tspan><tspan fill="#0F172A" font-weight="600"> Open for Collaboration</tspan></text></g>
<g opacity="0"><animate attributeName="opacity" from="0" to="1" dur="0.5s" begin="3.34s" fill="freeze"/>
<text x="470" y="577" font-size="14" fill="#475569">&#9656; More about me &amp; projects below in README &#8595; <tspan fill="#0891B2">&#9608;<animate attributeName="fill-opacity" values="1;0;1" dur="1s" repeatCount="indefinite"/></tspan></text>
</g>
</g>
<rect x="3" y="3" width="1174" height="604" rx="17" fill="none" stroke="url(#accent)" stroke-width="3" opacity="0.55" filter="url(#glow8)"/>
<rect x="3" y="3" width="1174" height="604" rx="17" fill="none" stroke="url(#accent)" stroke-width="1.6"/>
</svg>
'''
    
    with open(os.path.join(base_dir, "light.svg"), "w", encoding="utf-8") as f:
        f.write(light_output)
    print("light.svg successfully written. Size:", len(light_output), "bytes")

if __name__ == "__main__":
    generate_hologram()
