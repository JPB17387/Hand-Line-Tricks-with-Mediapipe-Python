"""
hologram3d.py
=============
A real-time, dependency-free (NumPy + OpenCV only) 3D holographic wireframe
engine used to render interactive 3D holograms that the user can pick up,
move anywhere on screen, rotate & tilt 360 degrees freely on all axes, and
zoom in/out with their hands — 100% keyboard-free Iron-Man / Tony Stark style.

Features:
  1. 16 procedural 3D model builders (Rocket, House, Hypercube, Globe, Human,
     Car, Plane, Building, Pyramid, Atom, Spaceship, Diamond, DNA, Heart,
     Drone, Satellite).
  2. Full 3-axis 3D rotation math (Pitch Rx, Yaw Ry, Roll Rz) + perspective projection.
  3. Depth-based glow rendering with painter's algorithm, projector disc base,
     ascending holographic emitter beams, and glowing vertex hubs.
"""

import math
import numpy as np
import cv2


# ---------------------------------------------------------------------------
# Procedural 3D Model Builders
# Each returns (vertices: Nx3 float32 ndarray, edges: list[(i,j)], extra: dict)
# ---------------------------------------------------------------------------

def make_cube():
    """Sci-Fi 4D Tesseract / Hypercube: concentric outer and inner cubes
    connected with holographic hyper-struts and a central singularity core."""
    outer = [
        (-1.0, -1.0, -1.0), (1.0, -1.0, -1.0), (1.0, 1.0, -1.0), (-1.0, 1.0, -1.0),
        (-1.0, -1.0, 1.0), (1.0, -1.0, 1.0), (1.0, 1.0, 1.0), (-1.0, 1.0, 1.0),
    ]
    s = 0.52
    inner = [(x * s, y * s, z * s) for x, y, z in outer]
    verts = list(outer) + list(inner)
    
    def box_edges(o):
        return [
            (o, o + 1), (o + 1, o + 2), (o + 2, o + 3), (o + 3, o),
            (o + 4, o + 5), (o + 5, o + 6), (o + 6, o + 7), (o + 7, o + 4),
            (o, o + 4), (o + 1, o + 5), (o + 2, o + 6), (o + 3, o + 7)
        ]
    
    edges = box_edges(0) + box_edges(8)
    # Struts connecting outer to inner corners
    for i in range(8):
        edges.append((i, i + 8))
        
    core_idx = len(verts)
    verts.append((0.0, 0.0, 0.0))
    # Internal energy axes
    edges += [(core_idx, 8 + i) for i in range(8)]
    
    return np.array(verts, dtype=np.float32), edges, {'big_points': [core_idx] + list(range(8, 16))}


def make_globe(lat_n=8, lon_n=14):
    """Holographic Earth globe with latitude/longitude grid, equator ring,
    and a tilted orbital satellite ring with an orbiting satellite beacon."""
    verts = []
    idx = {}
    for la in range(lat_n + 1):
        theta = math.pi * la / lat_n  # 0..pi
        y = math.cos(theta) * 0.95
        r = math.sin(theta) * 0.95
        for lo in range(lon_n):
            phi = 2 * math.pi * lo / lon_n
            x = r * math.cos(phi)
            z = r * math.sin(phi)
            idx[(la, lo)] = len(verts)
            verts.append((x, y, z))
            
    edges = []
    for la in range(lat_n + 1):
        for lo in range(lon_n):
            a = idx[(la, lo)]
            b = idx[(la, (lo + 1) % lon_n)]
            edges.append((a, b))  # latitude ring
            if la < lat_n:
                edges.append((a, idx[(la + 1, lo)]))  # longitude line
                
    # Tilted orbital ring
    orb_tilt = math.radians(28)
    orb_r = 1.35
    orb_start = len(verts)
    orb_n = 20
    for k in range(orb_n):
        a = 2 * math.pi * k / orb_n
        ox = orb_r * math.cos(a)
        oz = orb_r * math.sin(a)
        oy = oz * math.sin(orb_tilt)
        oz = oz * math.cos(orb_tilt)
        verts.append((ox, oy, oz))
        edges.append((orb_start + k, orb_start + (k + 1) % orb_n))
        
    sat_idx = len(verts)
    verts.append((orb_r * 0.98, orb_r * 0.98 * math.sin(orb_tilt), orb_r * 0.98 * math.cos(orb_tilt)))
    
    return np.array(verts, dtype=np.float32), edges, {'big_points': [0, idx[(lat_n, 0)], sat_idx]}


def make_human():
    """Cybernetic Android Humanoid with visor helmet, chest frame, spine,
    pelvis, articulated limbs and glowing joint hubs."""
    pts = {
        'visor_top': (0.0, -1.65, 0.15),
        'visor_bot': (0.0, -1.35, 0.18),
        'head_top': (0.0, -1.75, 0.0),
        'head_back': (0.0, -1.45, -0.22),
        'head_l': (-0.22, -1.50, 0.0),
        'head_r': (0.22, -1.50, 0.0),
        'neck': (0.0, -1.25, 0.0),
        'l_shoulder': (-0.45, -1.18, 0.0), 'r_shoulder': (0.45, -1.18, 0.0),
        'chest_l': (-0.32, -0.85, 0.12), 'chest_r': (0.32, -0.85, 0.12),
        'chest_back': (0.0, -0.85, -0.12),
        'heart_core': (0.0, -0.92, 0.08),
        'spine': (0.0, -0.60, 0.0),
        'l_elbow': (-0.62, -0.65, 0.10), 'r_elbow': (0.62, -0.65, 0.10),
        'l_wrist': (-0.72, -0.18, 0.18), 'r_wrist': (0.72, -0.18, 0.18),
        'l_hand': (-0.78, 0.05, 0.22), 'r_hand': (0.78, 0.05, 0.22),
        'pelvis': (0.0, -0.25, 0.0),
        'l_hip': (-0.28, -0.25, 0.0), 'r_hip': (0.28, -0.25, 0.0),
        'l_knee': (-0.32, 0.45, 0.08), 'r_knee': (0.32, 0.45, 0.08),
        'l_ankle': (-0.34, 1.15, 0.05), 'r_ankle': (0.34, 1.15, 0.05),
        'l_foot': (-0.34, 1.25, 0.32), 'r_foot': (0.34, 1.25, 0.32),
    }
    names = list(pts.keys())
    verts = np.array([pts[n] for n in names], dtype=np.float32)
    i = names.index
    bones = [
        ('head_top', 'visor_top'), ('visor_top', 'visor_bot'), ('visor_bot', 'neck'),
        ('head_top', 'head_l'), ('head_top', 'head_r'), ('head_top', 'head_back'),
        ('head_back', 'neck'), ('head_l', 'neck'), ('head_r', 'neck'),
        ('head_l', 'visor_top'), ('head_r', 'visor_top'),
        ('neck', 'l_shoulder'), ('neck', 'r_shoulder'),
        ('neck', 'chest_l'), ('neck', 'chest_r'), ('neck', 'chest_back'),
        ('chest_l', 'chest_r'), ('chest_l', 'chest_back'), ('chest_r', 'chest_back'),
        ('chest_l', 'spine'), ('chest_r', 'spine'), ('chest_back', 'spine'),
        ('heart_core', 'chest_l'), ('heart_core', 'chest_r'), ('heart_core', 'neck'),
        ('l_shoulder', 'l_elbow'), ('l_elbow', 'l_wrist'), ('l_wrist', 'l_hand'),
        ('r_shoulder', 'r_elbow'), ('r_elbow', 'r_wrist'), ('r_wrist', 'r_hand'),
        ('spine', 'pelvis'), ('pelvis', 'l_hip'), ('pelvis', 'r_hip'),
        ('l_hip', 'l_knee'), ('l_knee', 'l_ankle'), ('l_ankle', 'l_foot'),
        ('r_hip', 'r_knee'), ('r_knee', 'r_ankle'), ('r_ankle', 'r_foot'),
    ]
    edges = [(i(a), i(b)) for a, b in bones]
    big_pts = [i('heart_core'), i('visor_top'), i('l_hand'), i('r_hand'), i('l_knee'), i('r_knee')]
    return verts, edges, {'big_points': big_pts}


def make_car():
    """Futuristic Cyberpunk Sports Car with aerodynamic cabin, fastback roof,
    rear wing spoiler, front headlights, and 3D spoked wheel cylinders."""
    verts = []
    edges = []
    
    # Chassis bottom frame
    chassis = [
        (-1.25, 0.15, -0.55), (1.25, 0.15, -0.55), (1.25, 0.15, 0.55), (-1.25, 0.15, 0.55),
        (-1.20, -0.10, -0.55), (1.15, -0.10, -0.55), (1.15, -0.10, 0.55), (-1.20, -0.10, 0.55)
    ]
    verts += chassis
    c_base = 0
    # Lower body lines
    edges += [
        (0, 1), (1, 2), (2, 3), (3, 0),
        (4, 5), (5, 6), (6, 7), (7, 4),
        (0, 4), (1, 5), (2, 6), (3, 7)
    ]
    
    # Cabin / Windshield / Fastback roof
    cabin = [
        (-0.55, -0.62, -0.42), (0.35, -0.62, -0.42), (0.35, -0.62, 0.42), (-0.55, -0.62, 0.42),  # roof
        (-0.95, -0.10, -0.50), (-0.95, -0.10, 0.50),  # hood/windshield base
        (0.85, -0.10, -0.50), (0.85, -0.10, 0.50)     # rear deck
    ]
    cb = len(verts)
    verts += cabin
    # Roof perimeter
    edges += [(cb, cb + 1), (cb + 1, cb + 2), (cb + 2, cb + 3), (cb + 3, cb)]
    # Windshield pillars
    edges += [(cb, cb + 4), (cb + 3, cb + 5), (cb + 4, cb + 5)]
    # Fastback C-pillars
    edges += [(cb + 1, cb + 6), (cb + 2, cb + 7), (cb + 6, cb + 7)]
    # Hood & trunk links
    edges += [(cb + 4, 4), (cb + 5, 7), (cb + 6, 5), (cb + 7, 6)]
    
    # Rear spoiler
    sp_base = len(verts)
    verts += [
        (1.05, -0.42, -0.52), (1.05, -0.42, 0.52),
        (0.95, -0.10, -0.38), (0.95, -0.10, 0.38)
    ]
    edges += [
        (sp_base, sp_base + 1),
        (sp_base, sp_base + 2), (sp_base + 1, sp_base + 3)
    ]
    
    # 4 3D spoked wheels
    wheel_locs = [(-0.80, 0.18, -0.58), (0.75, 0.18, -0.58),
                  (-0.80, 0.18, 0.58), (0.75, 0.18, 0.58)]
    big_pts = []
    for cx, cy, cz in wheel_locs:
        w_start = len(verts)
        big_pts.append(w_start)  # hub center
        verts.append((cx, cy, cz))
        wn = 8
        wr = 0.26
        for k in range(wn):
            a = 2 * math.pi * k / wn
            verts.append((cx + wr * math.sin(a), cy + wr * math.cos(a), cz))
            edges.append((w_start + 1 + k, w_start + 1 + (k + 1) % wn))
            if k % 2 == 0:
                edges.append((w_start, w_start + 1 + k))  # spokes
                
    return np.array(verts, dtype=np.float32), edges, {'big_points': big_pts + [cb + 4, cb + 5]}


def make_plane():
    """Supersonic Stealth Fighter Jet with radome nose, cockpit canopy bubble,
    delta wings with wingtip missile rails, canted twin tail fins, and twin afterburners."""
    verts = [
        (0.0, 0.0, -1.65),            # 0: Radome needle nose
        (0.0, -0.24, -0.75),          # 1: Cockpit canopy apex
        (0.0, -0.05, -0.45),          # 2: Canopy rear
        (-0.25, 0.05, -0.65), (0.25, 0.05, -0.65),   # 3,4: Forward fuselage
        (-0.35, 0.08, 0.50), (0.35, 0.08, 0.50),     # 5,6: Mid fuselage
        (-0.25, 0.08, 1.25), (0.25, 0.08, 1.25),     # 7,8: Aft fuselage
        # Wings
        (-1.65, 0.05, 0.55), (1.65, 0.05, 0.55),     # 9,10: Wingtips leading edge
        (-1.45, 0.05, 0.85), (1.45, 0.05, 0.85),     # 11,12: Wingtips trailing edge
        # Wingtip missiles
        (-1.65, 0.05, 0.35), (1.65, 0.05, 0.35),     # 13,14: Missile tips
        # Twin canted vertical fins
        (-0.45, -0.65, 1.15), (0.45, -0.65, 1.15),   # 15,16: Fin tips
        (-0.28, 0.05, 1.30), (0.28, 0.05, 1.30),     # 17,18: Fin aft bases
        # Twin engine exhausts
        (-0.15, 0.05, 1.35), (0.15, 0.05, 1.35),     # 19,20: Exhaust nozzles
    ]
    edges = [
        # Nose cone & canopy
        (0, 1), (1, 2), (0, 3), (0, 4), (1, 3), (1, 4), (2, 3), (2, 4),
        # Fuselage spine & chine
        (3, 5), (4, 6), (5, 7), (6, 8), (7, 19), (8, 20), (19, 20),
        # Delta Wings
        (3, 9), (9, 11), (11, 7), (4, 10), (10, 12), (12, 8),
        (5, 11), (6, 12),
        # Missiles
        (13, 9), (13, 11), (14, 10), (14, 12),
        # Twin tail fins
        (7, 15), (15, 17), (17, 7),
        (8, 16), (16, 18), (18, 8),
        (15, 16),
    ]
    big_pts = [0, 1, 13, 14, 15, 16, 19, 20]
    return np.array(verts, dtype=np.float32), edges, {'big_points': big_pts}


def make_building():
    """Cyber Metropolis Skyscraper with tiered architectural floors, diagonal
    structural lattice bracing, external glass elevator shaft, crown spire,
    and broadcast antenna beacon."""
    verts = []
    edges = []
    
    # Tier 1 (Base - floors 0..3)
    w1, d1 = 0.75, 0.55
    y_bot = 1.35
    y_mid1 = 0.45
    b1 = [
        (-w1, y_bot, -d1), (w1, y_bot, -d1), (w1, y_bot, d1), (-w1, y_bot, d1),
        (-w1, y_mid1, -d1), (w1, y_mid1, -d1), (w1, y_mid1, d1), (-w1, y_mid1, d1)
    ]
    verts += b1
    edges += [
        (0, 1), (1, 2), (2, 3), (3, 0),
        (4, 5), (5, 6), (6, 7), (7, 4),
        (0, 4), (1, 5), (2, 6), (3, 7),
        # Diagonal lattice bracing
        (0, 5), (1, 4), (2, 7), (3, 6)
    ]
    
    # Tier 2 (Mid tower - floors 4..8)
    w2, d2 = 0.52, 0.38
    y_mid2 = -0.65
    b2_base = len(verts)
    b2 = [
        (-w2, y_mid1, -d2), (w2, y_mid1, -d2), (w2, y_mid1, d2), (-w2, y_mid1, d2),
        (-w2, y_mid2, -d2), (w2, y_mid2, -d2), (w2, y_mid2, d2), (-w2, y_mid2, d2)
    ]
    verts += b2
    edges += [
        (b2_base, b2_base + 1), (b2_base + 1, b2_base + 2), (b2_base + 2, b2_base + 3), (b2_base + 3, b2_base),
        (b2_base + 4, b2_base + 5), (b2_base + 5, b2_base + 6), (b2_base + 6, b2_base + 7), (b2_base + 7, b2_base + 4),
        (b2_base, b2_base + 4), (b2_base + 1, b2_base + 5), (b2_base + 2, b2_base + 6), (b2_base + 3, b2_base + 7),
        (b2_base, b2_base + 5), (b2_base + 1, b2_base + 4)
    ]
    
    # Tier 3 (Crown penthouse)
    w3, d3 = 0.32, 0.24
    y_top = -1.15
    b3_base = len(verts)
    b3 = [
        (-w3, y_mid2, -d3), (w3, y_mid2, -d3), (w3, y_mid2, d3), (-w3, y_mid2, d3),
        (-w3, y_top, -d3), (w3, y_top, -d3), (w3, y_top, d3), (-w3, y_top, d3)
    ]
    verts += b3
    edges += [
        (b3_base, b3_base + 1), (b3_base + 1, b3_base + 2), (b3_base + 2, b3_base + 3), (b3_base + 3, b3_base),
        (b3_base + 4, b3_base + 5), (b3_base + 5, b3_base + 6), (b3_base + 6, b3_base + 7), (b3_base + 7, b3_base + 4),
        (b3_base, b3_base + 4), (b3_base + 1, b3_base + 5), (b3_base + 2, b3_base + 6), (b3_base + 3, b3_base + 7)
    ]
    
    # Antenna Spire
    sp_base = len(verts)
    verts += [
        (0.0, y_top, 0.0),
        (0.0, y_top - 0.55, 0.0),
        (-0.08, y_top - 0.25, 0.0), (0.08, y_top - 0.25, 0.0)
    ]
    edges += [
        (sp_base, sp_base + 1),
        (sp_base + 2, sp_base + 3),
        (sp_base + 1, sp_base + 2), (sp_base + 1, sp_base + 3)
    ]
    
    return np.array(verts, dtype=np.float32), edges, {'big_points': [sp_base + 1, b3_base + 4, b3_base + 5]}


def make_pyramid():
    """Stepped Stargate Pyramid with multi-tier terraces, central glowing
    apex capstone, and internal energy conduit lines."""
    verts = []
    edges = []
    
    levels = [
        (1.20, 1.05),
        (0.92, 0.55),
        (0.64, 0.05),
        (0.36, -0.45),
    ]
    prev_base = None
    for hw, y in levels:
        cur_base = len(verts)
        verts += [(-hw, y, -hw), (hw, y, -hw), (hw, y, hw), (-hw, y, hw)]
        edges += [
            (cur_base, cur_base + 1), (cur_base + 1, cur_base + 2),
            (cur_base + 2, cur_base + 3), (cur_base + 3, cur_base)
        ]
        if prev_base is not None:
            for k in range(4):
                edges.append((prev_base + k, cur_base + k))
        prev_base = cur_base
        
    # Floating Apex Capstone
    apex_base = len(verts)
    verts += [
        (0.0, -1.25, 0.0),            # Apex tip
        (-0.22, -0.65, -0.22), (0.22, -0.65, -0.22),
        (0.22, -0.65, 0.22), (-0.22, -0.65, 0.22)
    ]
    edges += [
        (apex_base, apex_base + 1), (apex_base, apex_base + 2),
        (apex_base, apex_base + 3), (apex_base, apex_base + 4),
        (apex_base + 1, apex_base + 2), (apex_base + 2, apex_base + 3),
        (apex_base + 3, apex_base + 4), (apex_base + 4, apex_base + 1),
    ]
    # Center ground energy beam
    ground_core = len(verts)
    verts.append((0.0, 1.05, 0.0))
    edges.append((ground_core, apex_base))
    
    return np.array(verts, dtype=np.float32), edges, {'big_points': [apex_base, ground_core]}


def make_atom(n=32):
    """Quantum Orbital Atom with 4 tilted electron shells, valence electron
    nodes at multiple orbital inclinations, and an octahedron nucleus core."""
    verts = []
    edges = []
    tilts_deg = [0, 48, -48, 90]
    big_pts = []
    
    for i, deg in enumerate(tilts_deg):
        rad = math.radians(deg)
        base = len(verts)
        for k in range(n):
            a = 2 * math.pi * k / n
            x = math.cos(a) * 1.05
            y_raw = math.sin(a) * 1.05
            y = y_raw * math.cos(rad)
            z = y_raw * math.sin(rad)
            verts.append((x, y, z))
        for k in range(n):
            edges.append((base + k, base + (k + 1) % n))
        # Valence electron node on this shell
        electron_idx = base + (i * (n // 4) + 3) % n
        big_pts.append(electron_idx)
        
    # Octahedron Nucleus Core
    nuc_base = len(verts)
    ns = 0.22
    verts += [
        (0.0, -ns, 0.0), (0.0, ns, 0.0),
        (-ns, 0.0, 0.0), (ns, 0.0, 0.0),
        (0.0, 0.0, -ns), (0.0, 0.0, ns),
        (0.0, 0.0, 0.0)  # Core center
    ]
    edges += [
        (nuc_base, nuc_base + 2), (nuc_base, nuc_base + 3), (nuc_base, nuc_base + 4), (nuc_base, nuc_base + 5),
        (nuc_base + 1, nuc_base + 2), (nuc_base + 1, nuc_base + 3), (nuc_base + 1, nuc_base + 4), (nuc_base + 1, nuc_base + 5),
        (nuc_base + 2, nuc_base + 4), (nuc_base + 4, nuc_base + 3), (nuc_base + 3, nuc_base + 5), (nuc_base + 5, nuc_base + 2)
    ]
    big_pts.append(nuc_base + 6)
    
    return np.array(verts, dtype=np.float32), edges, {'big_points': big_pts}


# ---------------------------------------------------------------------------
# NEW REQUESTED & EXPANDED MODELS
# ---------------------------------------------------------------------------

def make_rocket():
    """Multi-stage Aerospace Rocket with aerodynamic nose cone, cylindrical
    fuselage rings, 4 swept delta stabilizer fins, engine bell nozzle, and
    glowing exhaust thrust plume."""
    verts = []
    edges = []
    
    # 0: Aerodynamic Nose Tip
    verts.append((0.0, -1.65, 0.0))
    
    # Ring definitions: (y, radius, num_points)
    sections = [
        (-1.25, 0.26, 10),   # Nose cone base
        (-0.70, 0.38, 10),   # Payload fairing
        (0.00, 0.38, 10),    # Interstage ring
        (0.65, 0.38, 10),    # Main booster tank
        (1.10, 0.38, 10),    # Booster aft skirt
        (1.35, 0.24, 10),    # Engine bell nozzle
    ]
    
    ring_bases = []
    for y, r, np_pts in sections:
        base = len(verts)
        ring_bases.append((base, np_pts))
        for k in range(np_pts):
            a = 2 * math.pi * k / np_pts
            verts.append((r * math.cos(a), y, r * math.sin(a)))
        for k in range(np_pts):
            edges.append((base + k, base + (k + 1) % np_pts))
            
    # Connect nose tip to first ring
    first_base, first_n = ring_bases[0]
    for k in range(first_n):
        edges.append((0, first_base + k))
        
    # Connect consecutive rings along longitudinal stringers
    for r_idx in range(len(ring_bases) - 1):
        b1, n1 = ring_bases[r_idx]
        b2, n2 = ring_bases[r_idx + 1]
        for k in range(n1):
            edges.append((b1 + k, b2 + k))
            
    # 4 Large Swept Delta Stabilizing Fins at 0, 90, 180, 270 deg
    fin_angles = [0.0, math.pi / 2, math.pi, 3 * math.pi / 2]
    fin_tips = []
    for fa in fin_angles:
        dx = math.cos(fa)
        dz = math.sin(fa)
        ft_idx = len(verts)
        fin_tips.append(ft_idx)
        # Fin root top, fin tip, fin root bottom
        verts.append((dx * 0.95, 1.15, dz * 0.95))
        # Find nearest vertices on booster rings
        b_mid, _ = ring_bases[3]
        b_aft, _ = ring_bases[4]
        verts.append((dx * 0.38, 0.50, dz * 0.38))
        verts.append((dx * 0.38, 1.10, dz * 0.38))
        edges += [
            (ft_idx + 1, ft_idx), (ft_idx, ft_idx + 2),
            (ft_idx + 1, ft_idx + 2)
        ]
        
    # Thrust Exhaust Plume (Glowing rocket flame diamond)
    flame_tip = len(verts)
    verts.append((0.0, 1.85, 0.0))
    nozzle_base, nozzle_n = ring_bases[-1]
    for k in range(nozzle_n):
        edges.append((nozzle_base + k, flame_tip))
        
    big_pts = [0, flame_tip] + fin_tips
    return np.array(verts, dtype=np.float32), edges, {'big_points': big_pts}


def make_house():
    """3D Architectural House with pitched gable roof, ridge beam, chimney,
    front door frame, cross-pane window frames, and foundation perimeter."""
    verts = []
    edges = []
    
    # House main body walls
    # Base floor rectangle (y = 0.95)
    # Eaves ceiling rectangle (y = 0.05)
    hw, hd = 0.85, 0.65
    y_bot = 0.95
    y_eave = 0.05
    body = [
        (-hw, y_bot, -hd), (hw, y_bot, -hd), (hw, y_bot, hd), (-hw, y_bot, hd),  # 0..3: floor
        (-hw, y_eave, -hd), (hw, y_eave, -hd), (hw, y_eave, hd), (-hw, y_eave, hd),  # 4..7: eaves
    ]
    verts += body
    edges += [
        (0, 1), (1, 2), (2, 3), (3, 0),
        (4, 5), (5, 6), (6, 7), (7, 4),
        (0, 4), (1, 5), (2, 6), (3, 7)
    ]
    
    # Gable Roof Ridge (y = -0.75)
    y_ridge = -0.75
    ridge = [
        (-hw * 1.05, y_ridge, 0.0),  # 8: Left gable peak
        (hw * 1.05, y_ridge, 0.0)    # 9: Right gable peak
    ]
    r_base = len(verts)
    verts += ridge
    edges += [
        (r_base, r_base + 1),  # Ridge beam
        (r_base, 4), (r_base, 7),  # Left triangular gable
        (r_base + 1, 5), (r_base + 1, 6),  # Right triangular gable
    ]
    
    # Chimney on right roof slope
    ch_base = len(verts)
    cx = 0.42
    cw = 0.14
    verts += [
        (cx - cw, -0.92, -0.22), (cx + cw, -0.92, -0.22),
        (cx + cw, -0.92, 0.02), (cx - cw, -0.92, 0.02),  # Chimney top
        (cx - cw, -0.35, -0.22), (cx + cw, -0.35, -0.22),
        (cx + cw, -0.35, 0.02), (cx - cw, -0.35, 0.02),  # Chimney roof junction
    ]
    edges += [
        (ch_base, ch_base + 1), (ch_base + 1, ch_base + 2), (ch_base + 2, ch_base + 3), (ch_base + 3, ch_base),
        (ch_base, ch_base + 4), (ch_base + 1, ch_base + 5), (ch_base + 2, ch_base + 6), (ch_base + 3, ch_base + 7)
    ]
    
    # Front Door Frame (facing front +Z, on side (2, 3, 6, 7))
    door_base = len(verts)
    dw, dh = 0.18, 0.55
    verts += [
        (-dw, y_bot, hd + 0.02), (dw, y_bot, hd + 0.02),
        (dw, y_bot - dh, hd + 0.02), (-dw, y_bot - dh, hd + 0.02),
        (dw * 0.65, y_bot - dh * 0.5, hd + 0.04)  # Doorknob
    ]
    edges += [
        (door_base, door_base + 1), (door_base + 1, door_base + 2),
        (door_base + 2, door_base + 3), (door_base + 3, door_base)
    ]
    
    # Windows (Left and right on front facade)
    for wx_center in [-0.52, 0.52]:
        w_base = len(verts)
        ww, wh = 0.16, 0.18
        wy = 0.42
        verts += [
            (wx_center - ww, wy - wh, hd + 0.02), (wx_center + ww, wy - wh, hd + 0.02),
            (wx_center + ww, wy + wh, hd + 0.02), (wx_center - ww, wy + wh, hd + 0.02),
            # Cross mullions
            (wx_center, wy - wh, hd + 0.02), (wx_center, wy + wh, hd + 0.02),
            (wx_center - ww, wy, hd + 0.02), (wx_center + ww, wy, hd + 0.02),
        ]
        edges += [
            (w_base, w_base + 1), (w_base + 1, w_base + 2), (w_base + 2, w_base + 3), (w_base + 3, w_base),
            (w_base + 4, w_base + 5), (w_base + 6, w_base + 7)
        ]
        
    return np.array(verts, dtype=np.float32), edges, {'big_points': [r_base, r_base + 1, ch_base, door_base + 4]}


def make_spaceship():
    """Interstellar Sci-Fi Starship with forward elliptical command saucer,
    secondary engineering hull, navigational deflector dish, and twin warp nacelles."""
    verts = []
    edges = []
    
    # Command Saucer (Elliptical disc at front)
    saucer_base = len(verts)
    sn = 12
    sr_x, sr_z = 0.95, 0.75
    y_saucer = -0.15
    for k in range(sn):
        a = 2 * math.pi * k / sn
        verts.append((sr_x * math.cos(a), y_saucer, -0.65 + sr_z * math.sin(a)))
    for k in range(sn):
        edges.append((saucer_base + k, saucer_base + (k + 1) % sn))
        
    # Bridge Dome & Saucer Center
    bridge_idx = len(verts)
    verts.append((0.0, y_saucer - 0.28, -0.65))
    for k in range(0, sn, 2):
        edges.append((bridge_idx, saucer_base + k))
        
    # Secondary Engineering Hull (Cylinder extending aft)
    hull_base = len(verts)
    hn = 6
    hr = 0.24
    for y_h, z_h in [(0.22, -0.15), (0.22, 0.85)]:
        h_start = len(verts)
        for k in range(hn):
            a = 2 * math.pi * k / hn
            verts.append((hr * math.cos(a), y_h + hr * math.sin(a) * 0.8, z_h))
        for k in range(hn):
            edges.append((h_start + k, h_start + (k + 1) % hn))
    # Longitudinal hull lines
    for k in range(hn):
        edges.append((hull_base + k, hull_base + hn + k))
    # Connecting neck from saucer to engineering hull
    edges += [(saucer_base + sn // 2, hull_base), (saucer_base, hull_base + hn // 2)]
    
    # Deflector Dish at front of secondary hull
    dish_idx = len(verts)
    verts.append((0.0, 0.22, -0.22))
    for k in range(hn):
        edges.append((dish_idx, hull_base + k))
        
    # Twin Warp Nacelle Pylons & Nacelles (Port & Starboard)
    for side in [-1, 1]:
        p_base = len(verts)
        nx = side * 0.82
        # Pylon root on hull to nacelle mount
        verts.append((side * hr, 0.18, 0.45))
        verts.append((nx, -0.10, 0.65))
        edges.append((p_base, p_base + 1))
        
        # Warp Nacelle Tube
        verts.append((nx, -0.10, 0.05))   # Nacelle Bussard collector (front)
        verts.append((nx, -0.10, 1.25))   # Nacelle exhaust (rear)
        edges += [
            (p_base + 2, p_base + 3),
            (p_base + 1, p_base + 2), (p_base + 1, p_base + 3)
        ]
        
    big_pts = [bridge_idx, dish_idx, len(verts) - 6, len(verts) - 2]
    return np.array(verts, dtype=np.float32), edges, {'big_points': big_pts}


def make_diamond():
    """Faceted Brilliant-Cut 3D Gemstone with flat octagonal table facet,
    upper crown facets, girdle polygon, and pavilion converging to a culet point."""
    verts = []
    edges = []
    
    n = 8
    # 1. Octagonal Table Facet (top flat, y = -0.85)
    r_table = 0.45
    table_base = len(verts)
    for k in range(n):
        a = 2 * math.pi * k / n + math.pi / n
        verts.append((r_table * math.cos(a), -0.85, r_table * math.sin(a)))
    for k in range(n):
        edges.append((table_base + k, table_base + (k + 1) % n))
        
    # 2. Girdle Ring (widest perimeter, y = -0.25)
    r_girdle = 0.98
    girdle_base = len(verts)
    for k in range(n):
        a = 2 * math.pi * k / n
        verts.append((r_girdle * math.cos(a), -0.25, r_girdle * math.sin(a)))
    for k in range(n):
        edges.append((girdle_base + k, girdle_base + (k + 1) % n))
        
    # Crown Kite & Triangular Facets (connecting table to girdle)
    for k in range(n):
        edges.append((table_base + k, girdle_base + k))
        edges.append((table_base + k, girdle_base + (k + 1) % n))
        
    # 3. Sharp Culet Point (bottom apex, y = 1.05)
    culet_idx = len(verts)
    verts.append((0.0, 1.05, 0.0))
    # Pavilion facets (connecting girdle to culet)
    for k in range(n):
        edges.append((girdle_base + k, culet_idx))
        
    return np.array(verts, dtype=np.float32), edges, {'big_points': [culet_idx] + list(range(table_base, table_base + n))}


def make_dna(steps=20):
    """Intertwined Double Helix Strand with spiraling nucleotide backbones
    connected by horizontal base-pair rungs."""
    verts = []
    edges = []
    r = 0.65
    y_min, y_max = -1.35, 1.35
    big_pts = []
    
    strand1_indices = []
    strand2_indices = []
    
    for k in range(steps):
        t = k / (steps - 1)
        y = y_min + (y_max - y_min) * t
        angle = t * 3.5 * math.pi  # ~1.75 full rotations
        
        idx1 = len(verts)
        verts.append((r * math.cos(angle), y, r * math.sin(angle)))
        strand1_indices.append(idx1)
        
        idx2 = len(verts)
        verts.append((r * math.cos(angle + math.pi), y, r * math.sin(angle + math.pi)))
        strand2_indices.append(idx2)
        
        # Base-pair rung connecting Strand 1 and Strand 2
        edges.append((idx1, idx2))
        if k % 3 == 0:
            big_pts.append(idx1)
            big_pts.append(idx2)
            
    # Connect helix strands
    for k in range(steps - 1):
        edges.append((strand1_indices[k], strand1_indices[k + 1]))
        edges.append((strand2_indices[k], strand2_indices[k + 1]))
        
    return np.array(verts, dtype=np.float32), edges, {'big_points': big_pts}


def make_heart():
    """3D Faceted Cyberpunk Anatomical Heart with left and right ventricle curves,
    atrium chambers, and curved aortic arch conduit."""
    verts = []
    edges = []
    
    # 3D parametric heart wireframe
    # Cross sections from bottom apex (y = 0.95) to atrium tops (y = -0.55)
    apex_idx = len(verts)
    verts.append((0.0, 0.95, 0.0))  # Heart bottom apex
    
    # Mid-ventricle ring
    mid_base = len(verts)
    mid_pts = [
        (0.0, 0.35, 0.45), (0.42, 0.35, 0.30), (0.58, 0.35, -0.05), (0.35, 0.35, -0.38),
        (0.0, 0.35, -0.22), (-0.35, 0.35, -0.38), (-0.58, 0.35, -0.05), (-0.42, 0.35, 0.30)
    ]
    verts += mid_pts
    for k in range(len(mid_pts)):
        edges.append((mid_base + k, mid_base + (k + 1) % len(mid_pts)))
        edges.append((apex_idx, mid_base + k))
        
    # Upper Atrium Lobes (Left & Right)
    left_lobe = len(verts)
    verts += [
        (-0.48, -0.35, 0.15), (-0.35, -0.65, 0.0), (-0.05, -0.45, 0.18),
        (-0.25, -0.35, -0.30)
    ]
    edges += [
        (left_lobe, left_lobe + 1), (left_lobe + 1, left_lobe + 2), (left_lobe + 2, left_lobe),
        (left_lobe, mid_base + 6), (left_lobe + 2, mid_base + 7)
    ]
    
    right_lobe = len(verts)
    verts += [
        (0.48, -0.35, 0.15), (0.35, -0.65, 0.0), (0.05, -0.45, 0.18),
        (0.25, -0.35, -0.30)
    ]
    edges += [
        (right_lobe, right_lobe + 1), (right_lobe + 1, right_lobe + 2), (right_lobe + 2, right_lobe),
        (right_lobe, mid_base + 1), (right_lobe + 2, mid_base)
    ]
    
    # Aortic Arch (Curving up from core to top)
    aorta_base = len(verts)
    verts += [
        (0.0, -0.45, 0.0), (0.10, -0.85, -0.05), (-0.12, -1.05, -0.15), (-0.28, -0.88, -0.22)
    ]
    edges += [
        (aorta_base, aorta_base + 1), (aorta_base + 1, aorta_base + 2), (aorta_base + 2, aorta_base + 3)
    ]
    
    return np.array(verts, dtype=np.float32), edges, {'big_points': [apex_idx, aorta_base + 2, left_lobe + 1, right_lobe + 1]}


def make_drone():
    """Tactical Quadcopter Drone with central avionics body pod, 4 carbon-fiber
    arms, 4 spinning rotor discs, landing skids, and forward camera gimbal."""
    verts = []
    edges = []
    
    # Central Fuselage Pod (octagon box)
    body_base = len(verts)
    bn = 6
    br = 0.28
    for y in [-0.10, 0.12]:
        b_sub = len(verts)
        for k in range(bn):
            a = 2 * math.pi * k / bn
            verts.append((br * math.cos(a), y, br * math.sin(a)))
        for k in range(bn):
            edges.append((b_sub + k, b_sub + (k + 1) % bn))
    for k in range(bn):
        edges.append((body_base + k, body_base + bn + k))
        
    # 4 Carbon-Fiber Motor Arms & Rotors
    arm_angles = [math.pi / 4, 3 * math.pi / 4, 5 * math.pi / 4, 7 * math.pi / 4]
    arm_len = 0.95
    rotor_r = 0.32
    big_pts = []
    for aa in arm_angles:
        mx = arm_len * math.cos(aa)
        mz = arm_len * math.sin(aa)
        my = -0.05
        # Arm from body to motor hub
        m_hub = len(verts)
        verts.append((mx, my, mz))
        big_pts.append(m_hub)
        edges.append((body_base, m_hub))
        
        # Rotor Disc Circle
        r_start = len(verts)
        rn = 8
        for k in range(rn):
            a = 2 * math.pi * k / rn
            verts.append((mx + rotor_r * math.cos(a), my - 0.04, mz + rotor_r * math.sin(a)))
        for k in range(rn):
            edges.append((r_start + k, r_start + (k + 1) % rn))
        # 2-blade propeller lines
        edges += [(m_hub, r_start), (m_hub, r_start + 4)]
        
    # Camera Gimbal
    gimbal_idx = len(verts)
    verts.append((0.0, 0.24, -0.22))
    edges.append((body_base, gimbal_idx))
    big_pts.append(gimbal_idx)
    
    # Landing Skids (2 parallel rails underneath)
    skid_base = len(verts)
    verts += [
        (-0.35, 0.38, -0.65), (-0.35, 0.38, 0.65),
        (0.35, 0.38, -0.65), (0.35, 0.38, 0.65),
        (-0.35, 0.12, -0.15), (-0.35, 0.12, 0.15),
        (0.35, 0.12, -0.15), (0.35, 0.12, 0.15)
    ]
    edges += [
        (skid_base, skid_base + 1), (skid_base + 2, skid_base + 3),
        (skid_base, skid_base + 4), (skid_base + 1, skid_base + 5),
        (skid_base + 2, skid_base + 6), (skid_base + 3, skid_base + 7)
    ]
    
    return np.array(verts, dtype=np.float32), edges, {'big_points': big_pts}


def make_satellite():
    """Space Satellite with cuboid instrument bus, dual solar panel arrays
    with individual photo-voltaic cells, and parabolic communication dish."""
    verts = []
    edges = []
    
    # Central Bus Box ([-0.25, 0.25], [-0.35, 0.35], [-0.25, 0.25])
    bw, bh, bd = 0.28, 0.38, 0.28
    bus = [
        (-bw, -bh, -bd), (bw, -bh, -bd), (bw, bh, -bd), (-bw, bh, -bd),
        (-bw, -bh, bd), (bw, -bh, bd), (bw, bh, bd), (-bw, bh, bd)
    ]
    verts += bus
    edges += [
        (0, 1), (1, 2), (2, 3), (3, 0),
        (4, 5), (5, 6), (6, 7), (7, 4),
        (0, 4), (1, 5), (2, 6), (3, 7)
    ]
    
    # Dual Solar Panel Wings (Port & Starboard along X axis)
    big_pts = []
    for side in [-1, 1]:
        wing_base = len(verts)
        x_in = side * (bw + 0.08)
        x_out = side * 1.35
        y_top, y_bot = -0.32, 0.32
        verts += [
            (x_in, y_top, 0.0), (x_out, y_top, 0.0),
            (x_out, y_bot, 0.0), (x_in, y_bot, 0.0)
        ]
        edges += [
            (wing_base, wing_base + 1), (wing_base + 1, wing_base + 2),
            (wing_base + 2, wing_base + 3), (wing_base + 3, wing_base),
            (0 if side < 0 else 1, wing_base)  # Mount boom
        ]
        # Grid cell dividers
        x_mid = (x_in + x_out) / 2
        m_base = len(verts)
        verts += [(x_mid, y_top, 0.0), (x_mid, y_bot, 0.0)]
        edges.append((m_base, m_base + 1))
        big_pts.append(wing_base + 1)
        big_pts.append(wing_base + 2)
        
    # Parabolic High-Gain Dish Antenna on top
    dish_base = len(verts)
    verts += [
        (0.0, -bh, 0.0), (0.0, -bh - 0.22, 0.0),  # Feed mast
        (-0.35, -bh - 0.42, 0.0), (0.35, -bh - 0.42, 0.0),
        (0.0, -bh - 0.42, -0.35), (0.0, -bh - 0.42, 0.35)
    ]
    edges += [
        (dish_base, dish_base + 1),
        (dish_base + 1, dish_base + 2), (dish_base + 1, dish_base + 3),
        (dish_base + 1, dish_base + 4), (dish_base + 1, dish_base + 5),
        (dish_base + 2, dish_base + 3), (dish_base + 4, dish_base + 5)
    ]
    big_pts.append(dish_base + 1)
    
    return np.array(verts, dtype=np.float32), edges, {'big_points': big_pts}


# ---------------------------------------------------------------------------
# Registry & Model Catalog (16 Holographic Objects)
# ---------------------------------------------------------------------------

def _wrap2(fn):
    def inner():
        res = fn()
        if len(res) == 2:
            verts, edges = res
            return verts, edges, {}
        return res
    return inner


MODEL_ORDER = [
    'rocket',     # 🚀 Rocket (User requested)
    'house',      # 🏠 House (User requested)
    'cube',       # 🧊 Hypercube Tesseract
    'globe',      # 🌐 Orbital Earth Globe
    'human',      # 🧍 Cyber Android Human
    'car',        # 🚗 Cyberpunk Sports Car
    'plane',      # ✈️ Stealth Fighter Jet
    'building',   # 🏢 Metropolis Skyscraper
    'pyramid',    # 🔺 Stargate Pyramid
    'atom',       # ⚛️ Quantum Atom
    'spaceship',  # 🛸 Star Cruiser
    'diamond',    # 💎 Faceted Gemstone
    'dna',        # 🧬 Double Helix
    'heart',      # 🫀 Cyber Heart
    'drone',      # 🚁 Tactical Drone
    'satellite',  # 🛰️ Orbital Satellite
]

_BUILDERS = {
    'rocket': _wrap2(make_rocket),
    'house': _wrap2(make_house),
    'cube': _wrap2(make_cube),
    'globe': _wrap2(make_globe),
    'human': _wrap2(make_human),
    'car': _wrap2(make_car),
    'plane': _wrap2(make_plane),
    'building': _wrap2(make_building),
    'pyramid': _wrap2(make_pyramid),
    'atom': _wrap2(make_atom),
    'spaceship': _wrap2(make_spaceship),
    'diamond': _wrap2(make_diamond),
    'dna': _wrap2(make_dna),
    'heart': _wrap2(make_heart),
    'drone': _wrap2(make_drone),
    'satellite': _wrap2(make_satellite),
}

MODEL_LABELS = {
    'rocket': 'Rocket',
    'house': 'House',
    'cube': 'Tesseract',
    'globe': 'Globe',
    'human': 'Human',
    'car': 'Cyber Car',
    'plane': 'Stealth Jet',
    'building': 'Skyscraper',
    'pyramid': 'Pyramid',
    'atom': 'Quantum Atom',
    'spaceship': 'Star Cruiser',
    'diamond': 'Diamond',
    'dna': 'DNA Helix',
    'heart': 'Cyber Heart',
    'drone': 'Tactical Drone',
    'satellite': 'Satellite',
}

# Vibrant sci-fi holographic neon tints per object (BGR format)
MODEL_COLORS = {
    'rocket': (50, 160, 255),      # Blaze Solar Orange / Amber
    'house': (100, 215, 255),      # Golden Amber Sand
    'cube': (255, 220, 80),        # High-Tech Electric Cyan
    'globe': (255, 200, 40),       # Earth Teal & Aqua
    'human': (255, 120, 220),      # Neon Violet / Magenta
    'car': (60, 110, 255),         # Cyberpunk Vermilion Red
    'plane': (255, 210, 120),      # Electric Sky Azure
    'building': (220, 240, 100),   # Cool Metropolis Ice Cyan
    'pyramid': (40, 215, 255),     # Radiant Pharaoh Gold
    'atom': (100, 255, 120),       # Electric Lime / Emerald
    'spaceship': (255, 170, 100),  # Quantum Cobalt Blue
    'diamond': (255, 245, 190),    # Crystal Aquamarine
    'dna': (230, 100, 255),        # Magenta-Purple Helix
    'heart': (120, 80, 255),       # Pulsing Crimson Red
    'drone': (120, 240, 140),      # High-Tech Emerald Green
    'satellite': (255, 200, 90),   # Solar Deep Cyan
}

_cache = {}


def get_model(key):
    """Retrieve or build the cached geometry for model `key`."""
    if key not in _cache:
        builder = _BUILDERS.get(key, _BUILDERS['rocket'])
        verts, edges, extra = builder()
        _cache[key] = (verts, edges, extra)
    return _cache[key]


# ---------------------------------------------------------------------------
# 3D Math: Full 3-Axis Rotation Matrices + Perspective Projection
# ---------------------------------------------------------------------------

def rotate_xyz(v, rot_x_rad, rot_y_rad, rot_z_rad=0.0):
    """Rotate Nx3 vertices in 3D around X (pitch), Y (yaw), and Z (roll) axes."""
    cx, sx = math.cos(rot_x_rad), math.sin(rot_x_rad)
    cy, sy = math.cos(rot_y_rad), math.sin(rot_y_rad)
    cz, sz = math.cos(rot_z_rad), math.sin(rot_z_rad)

    x = v[:, 0]
    y = v[:, 1]
    z = v[:, 2]

    # Rotate around Z (roll)
    if abs(rot_z_rad) > 1e-5:
        x_z = x * cz - y * sz
        y_z = x * sz + y * cz
        x, y = x_z, y_z

    # Rotate around X (pitch)
    y_x = y * cx - z * sx
    z_x = y * sx + z * cx
    y, z = y_x, z_x

    # Rotate around Y (yaw)
    x_y = x * cy + z * sy
    z_y = -x * sy + z * cy
    x, z = x_y, z_y

    return np.stack([x, y, z], axis=1)


# Legacy alias
def rotate_xy(v, rot_x_rad, rot_y_rad):
    return rotate_xyz(v, rot_x_rad, rot_y_rad, 0.0)


def project(v, center, pixel_size, focal=4.2):
    """Perspective-project rotated model-space vertices to 2D screen pixels.
    Returns (Nx2 screen points, N depth values)."""
    zc = v[:, 2] + focal
    zc = np.clip(zc, 0.35, None)
    f = focal / zc
    sx = v[:, 0] * f * pixel_size + center[0]
    sy = v[:, 1] * f * pixel_size + center[1]
    return np.stack([sx, sy], axis=1), zc


# ---------------------------------------------------------------------------
# Holographic Renderer
# ---------------------------------------------------------------------------

def render_hologram(canvas, model_key, center, rot_x_deg, rot_y_deg, pixel_size,
                    color=None, alpha_boost=1.0, rot_z_deg=0.0):
    """Draw a glowing, depth-shaded wireframe hologram with projector disc base
    and ascending laser emitter lines onto `canvas` in place.
    
    canvas      : BGR uint8 ndarray image
    model_key   : key in MODEL_ORDER (e.g. 'rocket', 'house', 'cube', etc.)
    center      : (x, y) pixel location on canvas
    rot_x_deg   : rotation around X axis (pitch) in degrees (unbounded)
    rot_y_deg   : rotation around Y axis (yaw) in degrees (unbounded)
    pixel_size  : radius in pixels that [-1, 1] maps to
    color       : optional BGR tint tuple
    alpha_boost : glow opacity multiplier
    rot_z_deg   : optional rotation around Z axis (roll) in degrees
    """
    verts, edges, extra = get_model(model_key)
    if color is None:
        color = MODEL_COLORS.get(model_key, (255, 200, 80))

    rx = math.radians(rot_x_deg)
    ry = math.radians(rot_y_deg)
    rz = math.radians(rot_z_deg)

    rv = rotate_xyz(verts, rx, ry, rz)
    pts2d, depth = project(rv, center, pixel_size)

    dmin, dmax = float(depth.min()), float(depth.max())
    rng = max(1e-3, dmax - dmin)

    # --- Holographic Projector Base Floor Disc ---
    try:
        base_r = int(pixel_size * 1.12)
        base_y = int(center[1] + pixel_size * 1.05)
        disc = canvas.copy()
        cv2.ellipse(disc, (int(center[0]), base_y), (base_r, max(4, base_r // 5)), 0, 0, 360, color, -1)
        cv2.addWeighted(disc, 0.12 * alpha_boost, canvas, 1.0 - 0.12 * alpha_boost, 0, canvas)
        # Glowing outer rings
        cv2.ellipse(canvas, (int(center[0]), base_y), (base_r, max(4, base_r // 5)), 0, 0, 360,
                    tuple(min(255, int(c * 0.9)) for c in color), 1, cv2.LINE_AA)
        cv2.ellipse(canvas, (int(center[0]), base_y), (int(base_r * 0.65), max(3, base_r // 8)), 0, 0, 360,
                    (255, 255, 255), 1, cv2.LINE_AA)
        
        # Ascending projector light beam lines from base to bottom points
        pts2d_i = pts2d.astype(np.int32)
        lowest_indices = np.argsort(pts2d[:, 1])[-4:]
        beam_color = tuple(min(255, int(c * 0.45 * alpha_boost)) for c in color)
        for li in lowest_indices:
            cv2.line(canvas, (int(center[0]), base_y), (int(pts2d_i[li][0]), int(pts2d_i[li][1])),
                     beam_color, 1, cv2.LINE_AA)
    except Exception:
        pts2d_i = pts2d.astype(np.int32)

    # --- Painter's Algorithm: Depth-Sorted Glowing Wireframe Edges ---
    order = sorted(range(len(edges)), key=lambda i: -(depth[edges[i][0]] + depth[edges[i][1]]))

    for ei in order:
        a, b = edges[ei]
        davg = (depth[a] + depth[b]) / 2.0
        t = 1.0 - (davg - dmin) / rng  # 1.0 = nearest, 0.0 = farthest
        brightness = 0.40 + 0.60 * t
        thickness = 2 if t > 0.62 else 1
        pa = (int(pts2d_i[a][0]), int(pts2d_i[a][1]))
        pb = (int(pts2d_i[b][0]), int(pts2d_i[b][1]))
        c = tuple(min(255, int(ch * brightness * alpha_boost)) for ch in color)
        # Soft outer halo + crisp inner core
        cv2.line(canvas, pa, pb, (250, 250, 255), thickness + 1, cv2.LINE_AA)
        cv2.line(canvas, pa, pb, c, thickness, cv2.LINE_AA)

    # --- Glowing Vertex Nodes ---
    big_points = set(extra.get('big_points', [])) if extra else set()
    for idx in range(len(pts2d_i)):
        t = 1.0 - (depth[idx] - dmin) / rng
        px, py = int(pts2d_i[idx][0]), int(pts2d_i[idx][1])
        r = 4 if idx in big_points else 2
        r = max(1, int(r * (0.75 + 0.5 * t)))
        c = tuple(min(255, int(ch * (0.6 + 0.4 * t))) for ch in color)
        cv2.circle(canvas, (px, py), r, (255, 255, 255), -1, cv2.LINE_AA)
        cv2.circle(canvas, (px, py), r + 2, c, 1, cv2.LINE_AA)


def next_model(key):
    """Get the next model key in cyclic order."""
    i = MODEL_ORDER.index(key) if key in MODEL_ORDER else 0
    return MODEL_ORDER[(i + 1) % len(MODEL_ORDER)]


def prev_model(key):
    """Get the previous model key in cyclic order."""
    i = MODEL_ORDER.index(key) if key in MODEL_ORDER else 0
    return MODEL_ORDER[(i - 1) % len(MODEL_ORDER)]
