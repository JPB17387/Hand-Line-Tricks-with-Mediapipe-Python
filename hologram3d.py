"""
hologram3d.py
=============
A tiny, dependency-free (numpy + OpenCV only) real-time 3D wireframe engine
used to render "holographic" objects that the user can grab, spin on the
X and Y axes, and zoom in/out with their hand — Iron-Man / Tony Stark style.

This module owns three things:
  1. Model builders  -> procedural vertex/edge lists for each object
  2. Math            -> real rotation matrices (X then Y) + perspective projection
  3. Renderer        -> draws the projected wireframe onto an OpenCV canvas
                         with depth-based glow shading and a holographic
                         projector-disc base.

Everything is normalized into "model space" roughly in the range [-1, 1]
before being scaled to pixels, so every model behaves the same way under
rotation, translation and zoom.
"""

import math
import numpy as np
import cv2

# ---------------------------------------------------------------------------
# Model builders — each returns (vertices: Nx3 float32 ndarray, edges: list[(i,j)])
# ---------------------------------------------------------------------------

def make_cube():
    v = np.array([
        (-1, -1, -1), (1, -1, -1), (1, 1, -1), (-1, 1, -1),
        (-1, -1, 1), (1, -1, 1), (1, 1, 1), (-1, 1, 1),
    ], dtype=np.float32)
    e = [(0, 1), (1, 2), (2, 3), (3, 0),
         (4, 5), (5, 6), (6, 7), (7, 4),
         (0, 4), (1, 5), (2, 6), (3, 7)]
    return v, e


def make_globe(lat_n=9, lon_n=14):
    """A latitude/longitude wireframe sphere, like a spinning holographic earth."""
    verts = []
    idx = {}
    for la in range(lat_n + 1):
        theta = math.pi * la / lat_n  # 0..pi (pole to pole)
        y = math.cos(theta)
        r = math.sin(theta)
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
    return np.array(verts, dtype=np.float32), edges


def make_pyramid():
    v = np.array([
        (0, -1.2, 0),
        (-1, 0.8, -1), (1, 0.8, -1), (1, 0.8, 1), (-1, 0.8, 1),
    ], dtype=np.float32)
    e = [(0, 1), (0, 2), (0, 3), (0, 4), (1, 2), (2, 3), (3, 4), (4, 1)]
    return v, e


def make_human():
    """Simple humanoid stick figure (head down to feet), same spirit as the
    hand skeleton already drawn elsewhere in this app."""
    pts = {
        'head': (0, -1.65, 0), 'neck': (0, -1.25, 0),
        'l_shoulder': (-0.36, -1.15, 0), 'r_shoulder': (0.36, -1.15, 0),
        'l_elbow': (-0.55, -0.65, 0.12), 'r_elbow': (0.55, -0.65, 0.12),
        'l_hand': (-0.62, -0.15, 0.18), 'r_hand': (0.62, -0.15, 0.18),
        'spine': (0, -0.65, 0), 'hip': (0, -0.25, 0),
        'l_hip': (-0.22, -0.25, 0), 'r_hip': (0.22, -0.25, 0),
        'l_knee': (-0.26, 0.45, 0.05), 'r_knee': (0.26, 0.45, 0.05),
        'l_foot': (-0.28, 1.15, 0.12), 'r_foot': (0.28, 1.15, 0.12),
    }
    names = list(pts.keys())
    verts = np.array([pts[n] for n in names], dtype=np.float32)
    i = names.index
    bones = [
        ('head', 'neck'), ('neck', 'l_shoulder'), ('neck', 'r_shoulder'),
        ('l_shoulder', 'l_elbow'), ('l_elbow', 'l_hand'),
        ('r_shoulder', 'r_elbow'), ('r_elbow', 'r_hand'),
        ('neck', 'spine'), ('spine', 'hip'),
        ('hip', 'l_hip'), ('hip', 'r_hip'),
        ('l_hip', 'l_knee'), ('l_knee', 'l_foot'),
        ('r_hip', 'r_knee'), ('r_knee', 'r_foot'),
    ]
    edges = [(i(a), i(b)) for a, b in bones]
    return verts, edges, {'big_points': [i('head')]}


def make_car():
    body = [
        (-1, -0.15, -0.55), (1, -0.15, -0.55), (1, 0.2, -0.55), (-1, 0.2, -0.55),
        (-1, -0.15, 0.55), (1, -0.15, 0.55), (1, 0.2, 0.55), (-1, 0.2, 0.55),
    ]
    cabin = [
        (-0.42, -0.62, -0.48), (0.42, -0.62, -0.48), (0.42, -0.15, -0.48), (-0.42, -0.15, -0.48),
        (-0.42, -0.62, 0.48), (0.42, -0.62, 0.48), (0.42, -0.15, 0.48), (-0.42, -0.15, 0.48),
    ]
    verts = list(body) + list(cabin)

    def box_edges(o):
        return [(o, o + 1), (o + 1, o + 2), (o + 2, o + 3), (o + 3, o),
                (o + 4, o + 5), (o + 5, o + 6), (o + 6, o + 7), (o + 7, o + 4),
                (o, o + 4), (o + 1, o + 5), (o + 2, o + 6), (o + 3, o + 7)]

    edges = box_edges(0) + box_edges(8)

    wheel_centers = [(-0.68, 0.2, -0.55), (0.68, 0.2, -0.55),
                      (-0.68, 0.2, 0.55), (0.68, 0.2, 0.55)]
    n = 10
    for cx, cy, cz in wheel_centers:
        start = len(verts)
        for k in range(n):
            a = 2 * math.pi * k / n
            verts.append((cx, cy + 0.24 * math.sin(a), cz + 0.24 * math.cos(a)))
        edges += [(start + k, start + (k + 1) % n) for k in range(n)]

    return np.array(verts, dtype=np.float32), edges


def make_plane():
    v = []
    e = []
    segs = [(-1.3, 0.02), (-0.5, 0.16), (0.35, 0.16), (1.15, 0.02)]
    ring_idx = []
    for z, r in segs:
        base = len(v)
        for k in range(4):
            a = math.pi / 4 + k * math.pi / 2
            v.append((r * math.cos(a), r * math.sin(a), z))
        ring_idx.append(base)
    for ridx in range(len(ring_idx)):
        base = ring_idx[ridx]
        e += [(base, base + 1), (base + 1, base + 2), (base + 2, base + 3), (base + 3, base)]
        if ridx > 0:
            prev = ring_idx[ridx - 1]
            e += [(prev + k, base + k) for k in range(4)]

    # wings
    base = len(v)
    v += [(-0.05, 0, -0.15), (-1.5, 0, -0.45), (-0.05, 0, 0.45)]
    e += [(base, base + 1), (base + 1, base + 2), (base + 2, base)]
    base2 = len(v)
    v += [(0.05, 0, -0.15), (1.5, 0, -0.45), (0.05, 0, 0.45)]
    e += [(base2, base2 + 1), (base2 + 1, base2 + 2), (base2 + 2, base2)]

    # tail fin
    base3 = len(v)
    v += [(0, 0, 1.0), (0, -0.5, 1.25), (0, 0, 1.4)]
    e += [(base3, base3 + 1), (base3 + 1, base3 + 2), (base3 + 2, base3)]

    return np.array(v, dtype=np.float32), e


def make_building(floors=7):
    hw, hd = 0.62, 0.42
    top, bottom = -1.2, 1.2
    box = [(-hw, bottom, -hd), (hw, bottom, -hd), (hw, bottom, hd), (-hw, bottom, hd),
           (-hw, top, -hd), (hw, top, -hd), (hw, top, hd), (-hw, top, hd)]
    v = list(box)
    e = [(0, 1), (1, 2), (2, 3), (3, 0), (4, 5), (5, 6), (6, 7), (7, 4),
         (0, 4), (1, 5), (2, 6), (3, 7)]
    for f in range(1, floors):
        t = f / floors
        y = bottom + (top - bottom) * t
        base = len(v)
        v += [(-hw, y, -hd), (hw, y, -hd), (hw, y, hd), (-hw, y, hd)]
        e += [(base, base + 1), (base + 1, base + 2), (base + 2, base + 3), (base + 3, base)]
    base = len(v)
    v += [(0, top, 0), (0, top - 0.45, 0)]
    e.append((base, base + 1))
    return np.array(v, dtype=np.float32), e


def make_atom(n=40):
    v = []
    e = []
    tilts_deg = [0, 60, -60]
    for deg in tilts_deg:
        rad = math.radians(deg)
        base = len(v)
        for k in range(n):
            a = 2 * math.pi * k / n
            x, y, z = math.cos(a), math.sin(a), 0.0
            y2 = y * math.cos(rad) - z * math.sin(rad)
            z2 = y * math.sin(rad) + z * math.cos(rad)
            v.append((x, y2, z2))
        e += [(base + k, base + (k + 1) % n) for k in range(n)]
    nucleus_idx = len(v)
    v.append((0, 0, 0))
    return np.array(v, dtype=np.float32), e, {'big_points': [nucleus_idx]}


# ---------------------------------------------------------------------------
# Registry
# ---------------------------------------------------------------------------

def _wrap2(fn):
    def inner():
        verts, edges = fn()
        return verts, edges, {}
    return inner


MODEL_ORDER = ['cube', 'globe', 'human', 'car', 'plane', 'building', 'pyramid', 'atom']

_BUILDERS = {
    'cube': _wrap2(make_cube),
    'globe': _wrap2(make_globe),
    'human': make_human,
    'car': _wrap2(make_car),
    'plane': _wrap2(make_plane),
    'building': _wrap2(make_building),
    'pyramid': _wrap2(make_pyramid),
    'atom': make_atom,
}

MODEL_LABELS = {
    'cube': 'Cube', 'globe': 'Globe', 'human': 'Human', 'car': 'Car',
    'plane': 'Plane', 'building': 'Building', 'pyramid': 'Pyramid', 'atom': 'Atom',
}

# Distinct holographic tint per object (BGR)
MODEL_COLORS = {
    'cube': (255, 180, 200),
    'globe': (255, 220, 90),      # cyan-teal "earth" glow
    'human': (220, 160, 255),     # violet
    'car': (80, 140, 255),        # orange-red
    'plane': (255, 210, 150),     # pale sky blue
    'building': (210, 230, 140),  # cool cyan-grey
    'pyramid': (90, 210, 255),    # gold
    'atom': (150, 255, 140),      # electric green
}

_cache = {}


def get_model(key):
    if key not in _cache:
        result = _BUILDERS.get(key, _BUILDERS['cube'])()
        verts, edges, extra = result
        _cache[key] = (verts, edges, extra)
    return _cache[key]


# ---------------------------------------------------------------------------
# Math: real rotation matrices + perspective projection
# ---------------------------------------------------------------------------

def rotate_xy(v, rot_x_rad, rot_y_rad):
    """Rotate Nx3 vertices around the X axis, then the Y axis (world space)."""
    cx, sx = math.cos(rot_x_rad), math.sin(rot_x_rad)
    x = v[:, 0]
    y = v[:, 1] * cx - v[:, 2] * sx
    z = v[:, 1] * sx + v[:, 2] * cx

    cy, sy = math.cos(rot_y_rad), math.sin(rot_y_rad)
    x2 = x * cy + z * sy
    z2 = -x * sy + z * cy
    return np.stack([x2, y, z2], axis=1)


def project(v, center, pixel_size, focal=4.2):
    """Perspective-project rotated model-space verts to 2D screen pixels.
    Returns (Nx2 screen points, N depth values used for shading/order)."""
    zc = v[:, 2] + focal
    zc = np.clip(zc, 0.35, None)
    f = focal / zc
    sx = v[:, 0] * f * pixel_size + center[0]
    sy = v[:, 1] * f * pixel_size + center[1]
    return np.stack([sx, sy], axis=1), zc


# ---------------------------------------------------------------------------
# Renderer
# ---------------------------------------------------------------------------

def render_hologram(canvas, model_key, center, rot_x_deg, rot_y_deg, pixel_size,
                     color=None, alpha_boost=1.0):
    """Draw a glowing wireframe hologram onto `canvas` (BGR uint8 ndarray, mutated in place).

    center       : (x, y) pixel position of the object's origin
    rot_x_deg    : rotation around X axis in degrees (unbounded, can spin past 360)
    rot_y_deg    : rotation around Y axis in degrees (unbounded, can spin past 360)
    pixel_size   : radius in pixels the [-1,1] model space maps to
    """
    verts, edges, extra = get_model(model_key)
    if color is None:
        color = MODEL_COLORS.get(model_key, (200, 180, 255))

    rv = rotate_xy(verts, math.radians(rot_x_deg), math.radians(rot_y_deg))
    pts2d, depth = project(rv, center, pixel_size)

    dmin, dmax = float(depth.min()), float(depth.max())
    rng = max(1e-3, dmax - dmin)

    # --- holographic projector base (soft glowing ellipse "floor" disc) ---
    try:
        base_r = int(pixel_size * 1.05)
        base_y = int(center[1] + pixel_size * 0.98)
        disc = canvas.copy()
        cv2.ellipse(disc, (int(center[0]), base_y), (base_r, max(4, base_r // 5)), 0, 0, 360, color, -1)
        cv2.addWeighted(disc, 0.10 * alpha_boost, canvas, 1.0 - 0.10 * alpha_boost, 0, canvas)
        cv2.ellipse(canvas, (int(center[0]), base_y), (base_r, max(4, base_r // 5)), 0, 0, 360,
                    tuple(min(255, int(c * 0.9)) for c in color), 1, cv2.LINE_AA)
    except Exception:
        pass

    # painter's algorithm: draw far edges first, near edges last so the
    # front of the object reads clearly on top
    order = sorted(range(len(edges)), key=lambda i: -(depth[edges[i][0]] + depth[edges[i][1]]))

    pts2d_i = pts2d.astype(np.int32)
    for ei in order:
        a, b = edges[ei]
        davg = (depth[a] + depth[b]) / 2.0
        t = 1.0 - (davg - dmin) / rng  # 1 = closest to camera, 0 = farthest
        brightness = 0.35 + 0.65 * t
        thickness = 2 if t > 0.6 else 1
        pa = (int(pts2d_i[a][0]), int(pts2d_i[a][1]))
        pb = (int(pts2d_i[b][0]), int(pts2d_i[b][1]))
        c = tuple(min(255, int(ch * brightness * alpha_boost)) for ch in color)
        # soft white halo underneath for a glowing look, then the tinted core line
        cv2.line(canvas, pa, pb, (245, 245, 250), thickness + 1, cv2.LINE_AA)
        cv2.line(canvas, pa, pb, c, thickness, cv2.LINE_AA)

    # glowing vertex nodes (grid intersections / joints / nucleus etc.)
    big_points = set(extra.get('big_points', [])) if extra else set()
    for idx in range(len(pts2d_i)):
        t = 1.0 - (depth[idx] - dmin) / rng
        px, py = int(pts2d_i[idx][0]), int(pts2d_i[idx][1])
        r = 3 if idx in big_points else 2
        r = max(1, int(r * (0.7 + 0.6 * t)))
        c = tuple(min(255, int(ch * (0.5 + 0.5 * t))) for ch in color)
        cv2.circle(canvas, (px, py), r, (255, 255, 255), -1, cv2.LINE_AA)
        cv2.circle(canvas, (px, py), r + 2, c, 1, cv2.LINE_AA)


def next_model(key):
    i = MODEL_ORDER.index(key) if key in MODEL_ORDER else 0
    return MODEL_ORDER[(i + 1) % len(MODEL_ORDER)]


def prev_model(key):
    i = MODEL_ORDER.index(key) if key in MODEL_ORDER else 0
    return MODEL_ORDER[(i - 1) % len(MODEL_ORDER)]
