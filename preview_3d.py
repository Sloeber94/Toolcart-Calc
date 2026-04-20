import json


def build_assembly(
    frmWo, frmHo, frmDo,
    frmWi, frmHi, frmDi,
    tUprights, uprights,
    tTbl, hCastors,
    nDrwT, nDrwM, nDrwB,
    drwW, drwD,
    drwHt, drwHm, drwHb,
    tBox, sDrw,
    w4040,
):
    """
    Build a list of 3D box/cylinder parts for the Three.js renderer.
    Coordinate system (Inventor-style, looking at XY front plane):
      X = width  (left → right)
      Y = height (bottom → top)
      Z = depth  (back → front)
    Origin (0,0,0) = left, bottom-of-frame, back corner.
    Castors extend into -Y below origin.
    """
    parts = []
    tV_x = 40          # vertical profile width in X (always 40)
    tV_z = tUprights   # vertical profile depth in Z (40 for 4040, 80 for 4080)
    tH   = 40          # horizontal profile cross-section (always 40×40)

    # ── VERTICALS (4×) ───────────────────────────────────────────────────────
    for xi in [0, frmWo - tV_x]:
        for zi in [0, frmDo - tV_z]:
            parts.append({
                "name": "Vertical",
                "group": "frame",
                "color": "#9E9E9E",
                "x": xi, "y": 0, "z": zi,
                "w": tV_x, "h": frmHo, "d": tV_z,
            })

    # ── HORIZONTALS W — left/right spanning (4×: top+bottom × front+back) ───
    h_w_len = frmWo - 2 * tV_x
    for yi in [0, frmHo - tH]:
        for zi in [0, frmDo - tH]:
            parts.append({
                "name": "Horizontal W",
                "group": "frame",
                "color": "#BDBDBD",
                "x": tV_x, "y": yi, "z": zi,
                "w": h_w_len, "h": tH, "d": tH,
            })

    # ── HORIZONTALS D — front/back spanning (4×: top+bottom × left+right) ───
    h_d_len = frmDo - 2 * tV_z
    for yi in [0, frmHo - tH]:
        for xi in [0, frmWo - tH]:
            parts.append({
                "name": "Horizontal D",
                "group": "frame",
                "color": "#BDBDBD",
                "x": xi, "y": yi, "z": tV_z,
                "w": tH, "h": tH, "d": h_d_len,
            })

    # ── DRAWERS — stacked top→bottom (top drawer at highest Y) ──────────────
    # Order in Y: bottom drawers at low Y, top drawers at high Y
    # Stack: bottom (nDrwB) first, then mid (nDrwM), then top (nDrwT)
    drawer_types = (
        [("bottom", drwHb)] * nDrwB +
        [("mid",    drwHm)] * nDrwM +
        [("top",    drwHt)] * nDrwT
    )

    # outer drawer dimensions
    drwOW = drwW   # outer width  = frmWi clearance handled by sDrw
    drwOD = drwD
    drw_x = tV_x + sDrw
    drw_z = tV_z + sDrw
    drw_box_w = frmWo - 2 * tV_x - 2 * sDrw
    drw_box_d = frmDo - 2 * tV_z - 2 * sDrw

    colors = {"top": "#D7CCC8", "mid": "#BCAAA4", "bottom": "#A1887F"}
    y_cursor = tH + sDrw   # start above bottom horizontal

    for dtype, dh in drawer_types:
        parts.append({
            "name": f"Drawer ({dtype})",
            "group": "drawers",
            "color": colors[dtype],
            "x": drw_x, "y": y_cursor, "z": drw_z,
            "w": drw_box_w, "h": dh, "d": drw_box_d,
        })
        y_cursor += dh + sDrw

    # ── TABLETOP ─────────────────────────────────────────────────────────────
    parts.append({
        "name": "Tabletop",
        "group": "tabletop",
        "color": "#5D4037",
        "x": 0, "y": frmHo, "z": 0,
        "w": frmWo, "h": tTbl, "d": frmDo,
    })

    # ── CASTORS (4× cylinders) ───────────────────────────────────────────────
    castor_r = 25   # visual radius in mm
    for xi, zi in [
        (tV_x / 2,        tV_z / 2),
        (frmWo - tV_x/2,  tV_z / 2),
        (tV_x / 2,        frmDo - tV_z/2),
        (frmWo - tV_x/2,  frmDo - tV_z/2),
    ]:
        parts.append({
            "name": "Castor",
            "group": "castors",
            "type": "cylinder",
            "color": "#212121",
            "x": xi, "y": -hCastors, "z": zi,
            "r": castor_r, "h": hCastors,
        })

    return parts


HTML_TEMPLATE = """
<!DOCTYPE html>
<html>
<head>
<meta charset="utf-8">
<style>
  * { margin: 0; padding: 0; box-sizing: border-box; }
  body { background: #1a1a2e; overflow: hidden; }
  canvas { display: block; }
  #controls {
    position: absolute; top: 10px; left: 10px;
    display: flex; flex-direction: column; gap: 6px;
    background: rgba(255,255,255,0.08);
    padding: 10px 14px; border-radius: 8px;
    font-family: sans-serif; font-size: 13px; color: #eee;
  }
  #controls label { display: flex; align-items: center; gap-6px; cursor: pointer; gap: 8px; }
  #controls input[type=checkbox] { width: 14px; height: 14px; cursor: pointer; }
  #info {
    position: absolute; bottom: 10px; left: 50%;
    transform: translateX(-50%);
    color: rgba(255,255,255,0.4);
    font-family: sans-serif; font-size: 11px;
  }
</style>
</head>
<body>
<div id="controls">
  <strong style="margin-bottom:4px">Show / Hide</strong>
  <label><input type="checkbox" id="tog-frame"    checked> Frame</label>
  <label><input type="checkbox" id="tog-drawers"  checked> Drawers</label>
  <label><input type="checkbox" id="tog-tabletop" checked> Tabletop</label>
  <label><input type="checkbox" id="tog-castors"  checked> Castors</label>
</div>
<div id="info">Scroll to zoom · Drag to rotate · Right-drag to pan</div>

<script type="importmap">
{
  "imports": {
    "three": "https://unpkg.com/three@0.163.0/build/three.module.js",
    "three/addons/": "https://unpkg.com/three@0.163.0/examples/jsm/"
  }
}
</script>

<script type="module">
import * as THREE from 'three';
import { OrbitControls } from 'three/addons/controls/OrbitControls.js';

const PARTS = __PARTS_JSON__;

// ── Scene setup ────────────────────────────────────────────────────────────
const W = window.innerWidth, H = window.innerHeight;
const renderer = new THREE.WebGLRenderer({ antialias: true });
renderer.setSize(W, H);
renderer.setPixelRatio(devicePixelRatio);
renderer.shadowMap.enabled = true;
document.body.appendChild(renderer.domElement);

const scene = new THREE.Scene();
scene.background = new THREE.Color(0x1a1a2e);
scene.fog = new THREE.Fog(0x1a1a2e, 3000, 8000);

const camera = new THREE.PerspectiveCamera(45, W / H, 1, 20000);

// ── Lighting ──────────────────────────────────────────────────────────────
scene.add(new THREE.AmbientLight(0xffffff, 0.6));
const dir1 = new THREE.DirectionalLight(0xffffff, 0.8);
dir1.position.set(1000, 2000, 1000);
dir1.castShadow = true;
scene.add(dir1);
const dir2 = new THREE.DirectionalLight(0xffffff, 0.3);
dir2.position.set(-800, 500, -600);
scene.add(dir2);

// ── Grid ──────────────────────────────────────────────────────────────────
const grid = new THREE.GridHelper(4000, 40, 0x444466, 0x333355);
scene.add(grid);

// ── Build meshes ──────────────────────────────────────────────────────────
const groups = { frame: [], drawers: [], tabletop: [], castors: [] };
const meshMat = (hex, opacity=1) => new THREE.MeshLambertMaterial({
  color: new THREE.Color(hex),
  transparent: opacity < 1,
  opacity,
});

// Convert mm → scene units (1:1, mm)
for (const p of PARTS) {
  let mesh;
  if (p.type === 'cylinder') {
    const geo = new THREE.CylinderGeometry(p.r, p.r, p.h, 16);
    mesh = new THREE.Mesh(geo, meshMat(p.color));
    // CylinderGeometry is centered; shift so base sits at y=0
    mesh.position.set(p.x, p.y + p.h / 2, p.z);
  } else {
    const geo = new THREE.BoxGeometry(p.w, p.h, p.d);
    mesh = new THREE.Mesh(geo, meshMat(p.color));
    mesh.position.set(p.x + p.w/2, p.y + p.h/2, p.z + p.d/2);
  }

  // Edges
  const edges = new THREE.LineSegments(
    new THREE.EdgesGeometry(mesh.geometry),
    new THREE.LineBasicMaterial({ color: 0x000000, opacity: 0.25, transparent: true })
  );
  mesh.add(edges);
  mesh.castShadow = true;
  mesh.receiveShadow = true;
  mesh.userData.group = p.group;
  scene.add(mesh);
  groups[p.group].push(mesh);
}

// ── Fit camera to assembly ────────────────────────────────────────────────
const box = new THREE.Box3().setFromObject(scene);
const center = box.getCenter(new THREE.Vector3());
const size   = box.getSize(new THREE.Vector3());
const maxDim = Math.max(size.x, size.y, size.z);

camera.position.set(center.x + maxDim, center.y + maxDim * 0.6, center.z + maxDim * 1.2);
camera.lookAt(center);
grid.position.y = box.min.y;

// ── Orbit controls ────────────────────────────────────────────────────────
const controls = new OrbitControls(camera, renderer.domElement);
controls.target.copy(center);
controls.enableDamping = true;
controls.dampingFactor = 0.08;
controls.update();

// ── Toggle checkboxes ─────────────────────────────────────────────────────
for (const [id, key] of [
  ['tog-frame','frame'], ['tog-drawers','drawers'],
  ['tog-tabletop','tabletop'], ['tog-castors','castors']
]) {
  document.getElementById(id).addEventListener('change', e => {
    groups[key].forEach(m => m.visible = e.target.checked);
  });
}

// ── Render loop ───────────────────────────────────────────────────────────
window.addEventListener('resize', () => {
  camera.aspect = innerWidth / innerHeight;
  camera.updateProjectionMatrix();
  renderer.setSize(innerWidth, innerHeight);
});

(function animate() {
  requestAnimationFrame(animate);
  controls.update();
  renderer.render(scene, camera);
})();
</script>
</body>
</html>
"""


def render_3d(parts: list, height: int = 600) -> str:
    """Return the HTML string with parts data injected."""
    import streamlit.components.v1 as components
    html = HTML_TEMPLATE.replace("__PARTS_JSON__", json.dumps(parts))
    components.html(html, height=height, scrolling=False)