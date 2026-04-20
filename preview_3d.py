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
    w4040, sFront, sRear,
):
    """
    Build a list of 3D box/cylinder parts for the Three.js renderer.
    Coordinate system (Inventor-style, looking at XY front plane):
      X = width  (left -> right)
      Y = height (bottom -> top)
      Z = depth  (back -> front)
    Origin (0,0,0) = left, bottom-of-frame, back corner.
    Castors extend into -Y below origin.
    """
    parts = []
    tV_x = 40          # vertical profile width in X (always 40)
    tV_z = tUprights   # vertical profile depth in Z (40 for 4040, 80 for 4080)
    tH   = 40          # horizontal profile cross-section (always 40x40)

    # VERTICALS (4x)
    for xi in [0, frmWo - tV_x]:
        for zi in [0, frmDo - tV_z]:
            parts.append({
                "name": "Vertical",
                "group": "frame",
                "color": "#9E9E9E",
                "x": xi, "y": 0, "z": zi,
                "w": tV_x, "h": frmHo, "d": tV_z,
            })

    # HORIZONTALS W — left/right spanning (4x: top+bottom x front+back)
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

    # HORIZONTALS D — front/back spanning (4x: top+bottom x left+right)
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

    # DRAWERS — stacked bottom->top
    drawer_types = (
        [("bottom", drwHb)] * nDrwB +
        [("mid",    drwHm)] * nDrwM +
        [("top",    drwHt)] * nDrwT
    )

    # outer drawer dimensions
    drw_box_w = frmWi - 2 * sDrw
    drw_box_d = drwD + 2 * tBox

    # drawer position — anchored from rear clearance
    drw_x = tV_x + sDrw
    drw_z = sRear

    # safety clamp for preview only
    if drw_z < 0:
        drw_z = 0
    if drw_z + drw_box_d > frmDo:
        drw_box_d = max(0, frmDo - drw_z)

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

    # TABLETOP — only when thickness > 0
    if tTbl > 0:
        parts.append({
            "name": "Tabletop",
            "group": "tabletop",
            "color": "#5D4037",
            "x": 0, "y": frmHo, "z": 0,
            "w": frmWo, "h": tTbl, "d": frmDo,
        })

    # CASTORS — only when height > 0
    # Wheel circle sits in XY plane (axis = Z), 40 mm thick in Z.
    # 80% of hCastors = wheel diameter, 20% = gap between wheel top and frame bottom.
    if hCastors > 0:
        gap      = hCastors * 0.2          # distance from frame bottom to wheel top
        wheel_r  = (hCastors * 0.8) / 2   # wheel radius
        wheel_t  = 40                      # wheel thickness in Z direction
        # wheel centre Y: frame is at Y=0, wheel top is at Y = -gap,
        # so wheel centre is at Y = -gap - wheel_r
        wheel_cy = -gap - wheel_r

        for xi, zi in [
            (tV_x / 2,        tV_z / 2 + wheel_t / 2),
            (frmWo - tV_x/2,  tV_z / 2 + wheel_t / 2),
            (tV_x / 2,        frmDo - tV_z/2 - wheel_t / 2),
            (frmWo - tV_x/2,  frmDo - tV_z/2 - wheel_t / 2),
        ]:
            parts.append({
                "name": "Castor",
                "group": "castors",
                "type": "wheel",        # Z-axis cylinder (circle in XY plane)
                "color": "#212121",
                "x": xi,
                "y": wheel_cy,
                "z": zi,
                "r": wheel_r,
                "t": wheel_t,
            })

    return parts


HTML_TEMPLATE = """
<!DOCTYPE html>
<html>
<head>
<meta charset="utf-8">
<style>
  * { margin: 0; padding: 0; box-sizing: border-box; }
  body { background: transparent; overflow: hidden; }
  canvas { display: block; }
  #controls {
    position: absolute; top: 10px; left: 10px;
    display: flex; flex-direction: column; gap: 6px;
    background: rgba(255,255,255,0.08);
    padding: 10px 14px; border-radius: 8px;
    font-family: sans-serif; font-size: 13px; color: #eee;
  }
  #controls label { display: flex; align-items: center; cursor: pointer; gap: 8px; }
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
<div id="info">Scroll to zoom &middot; Drag to rotate &middot; Right-drag to pan</div>

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

const W = window.innerWidth, H = window.innerHeight;
const renderer = new THREE.WebGLRenderer({ antialias: true, alpha: true });
renderer.setSize(W, H);
renderer.setPixelRatio(devicePixelRatio);
renderer.shadowMap.enabled = true;
document.body.appendChild(renderer.domElement);

const scene = new THREE.Scene();
scene.background = null;
renderer.setClearColor(0x000000, 0);
scene.fog = null;

const camera = new THREE.PerspectiveCamera(45, W / H, 1, 20000);

// ── Lighting ──────────────────────────────────────────────────────────────
scene.add(new THREE.AmbientLight(0xffffff, 1));
const dir1 = new THREE.DirectionalLight(0xffffff, 0.8);
dir1.position.set(1000, 2000, 1000);
dir1.castShadow = true;
scene.add(dir1);
const dir2 = new THREE.DirectionalLight(0xffffff, 0.3);
dir2.position.set(-800, 500, -600);
scene.add(dir2);

const grid = new THREE.GridHelper(4000, 40, 0x444466, 0x333355);
scene.add(grid);

const groups = { frame: [], drawers: [], tabletop: [], castors: [] };
const meshMat = (hex) => new THREE.MeshLambertMaterial({ color: new THREE.Color(hex) });

for (const p of PARTS) {
  let mesh;
  if (p.type === 'wheel') {
    // Cylinder with circle in XY plane — axis along Z
    // THREE.CylinderGeometry axis is Y by default, so rotate 90deg around X
    const geo = new THREE.CylinderGeometry(p.r, p.r, p.t, 32);
    mesh = new THREE.Mesh(geo, meshMat(p.color));
    mesh.rotation.x = Math.PI / 2;
    mesh.position.set(p.x, p.y, p.z);
  } else {
    const geo = new THREE.BoxGeometry(p.w, p.h, p.d);
    mesh = new THREE.Mesh(geo, meshMat(p.color));
    mesh.position.set(p.x + p.w/2, p.y + p.h/2, p.z + p.d/2);
  }
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

const box = new THREE.Box3().setFromObject(scene);
const center = box.getCenter(new THREE.Vector3());
const size   = box.getSize(new THREE.Vector3());
const maxDim = Math.max(size.x, size.y, size.z);

camera.position.set(center.x + maxDim, center.y + maxDim * 0.6, center.z + maxDim * 1.2);
camera.lookAt(center);
grid.position.y = box.min.y;

const controls = new OrbitControls(camera, renderer.domElement);
controls.target.copy(center);
controls.enableDamping = true;
controls.dampingFactor = 0.08;
controls.update();

for (const [id, key] of [
  ['tog-frame','frame'], ['tog-drawers','drawers'],
  ['tog-tabletop','tabletop'], ['tog-castors','castors']
]) {
  document.getElementById(id).addEventListener('change', e => {
    groups[key].forEach(m => m.visible = e.target.checked);
  });
}

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


def render_3d(parts: list, height: int = 600) -> None:
    """Inject Three.js HTML into Streamlit with parts data."""
    import streamlit.components.v1 as components
    html = HTML_TEMPLATE.replace("__PARTS_JSON__", json.dumps(parts))
    components.html(html, height=height, scrolling=False)
