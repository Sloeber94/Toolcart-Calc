function getClampedNumber(id, min, max, def) {
  const el = document.getElementById(id);
  let v = parseFloat(el.value);
  if (isNaN(v)) v = def;
  if (min !== null && v < min) v = min;
  if (max !== null && v > max) v = max;
  el.value = v;            // write back clamped value
  return v;
}


function computeAll() {
  // ---- INPUTS ----
  const H_frame    = getClampedNumber('H_frame',    200, 2000, 1000);
  const W_frame    = getClampedNumber('W_frame',    300, 2000, 1000);
  const D_frame    = getClampedNumber('D_frame',    300, 2000, 600);
  const t_tabletop = getClampedNumber('t_tabletop', 0,   100, 18);
  const H_casters  = getClampedNumber('H_casters',  0,   300, 125);
  const S_drawer   = getClampedNumber('S_drawer',   0,   10,  2);

  const H_low   = getClampedNumber('H_low',   20, 300, 50);
  const H_mid   = getClampedNumber('H_mid',   20, 400, 100);
  const H_high  = getClampedNumber('H_high',  20, 500, 150);
  const n_low   = getClampedNumber('n_low',   0, 100, 6);
  const n_mid   = getClampedNumber('n_mid',   0, 100, 2);
  const n_high  = getClampedNumber('n_high',  0, 100, 1);

  const C_204080 = getClampedNumber('C_204080', 0, 1, 0.01);   // 10/1000
  const C_2020   = getClampedNumber('C_2020',   0, 1, 0.005);  // 5/1000 (not used yet)
  const C_4040   = getClampedNumber('C_4040',   0, 1, 0.008);  // 8/1000
  const C_404080 = getClampedNumber('C_404080', 0, 1, 0.016);  // 16/1000 (not used yet)
  const C_2040   = getClampedNumber('C_2040',   0, 1, 0.0075); // 7.5/1000
  const C_slides = getClampedNumber('C_slides', 0, 500, 25);

  const t_slide   = getClampedNumber('t_slide',   0, 50, 12.5);
  const t_bracket = getClampedNumber('t_bracket', 0, 10, 2);

  // ---- GEOMETRY ----
  const H_usable = H_frame - 80;               // space between top/bottom frames
  const N       = Math.floor(H_usable / H_low); // max number of 50mm slots

  const n_tot = n_low + n_mid + n_high;

  const H_spacing    = S_drawer * (n_tot + 1); // gaps between drawers + frame
  const H_drawersmax = H_usable - H_spacing;   // remaining height for drawer boxes
  const X_drawers    = H_low * n_low + H_mid * n_mid + H_high * n_high;

  // drawer depth rounded down to multiple of 50
  const D_drawer = Math.floor((D_frame - 40) / 50) * 50;
  const D_side   = D_drawer - 40;                              // profile cut length
  const W_drawer = W_frame - 2 * (t_slide + t_bracket + 40);   // front/back length

  const H_tot = H_frame + t_tabletop + H_casters;

  // ---- COSTS ----
  // Base frame:
  // 4 uprights (4080-like) + 4 horizontals width + 4 horizontals depth
  const C_base =
    4 * C_204080 * H_frame +
    4 * C_4040 * (W_frame + D_drawer - 240) +
    40; // wheels ~ 4*10CHF

  // Drawers: each has front+back (W_drawer) and 2 sides (D_side)
  const C_drawer =
    n_tot * (2 * C_2040 * (W_drawer + D_side) + C_slides);

  const C_tot = C_base + C_drawer;

  // ---- WARNINGS / INFO ----
  const warnings = [];
  if (n_tot > N) {
    warnings.push(
      `Warning: Total drawers (n_tot=${n_tot}) exceed max slots N=${N}.`
    );
  }
  if (X_drawers > H_drawersmax) {
    warnings.push(
      `Warning: Drawer stack height X_drawers=${X_drawers}mm + spacing H_spacing=${H_spacing}mm exceeds usable height H_usable=${H_usable}mm.`
    );
  }
  if (X_drawers <= H_drawersmax) {
    const rem = H_drawersmax - X_drawers;
    warnings.push(`Info: Remaining vertical space for drawers: ${rem.toFixed(1)} mm.`);
  }

  // ---- OUTPUT ----
  const out = `
Frame / geometry
----------------
H_frame:    ${H_frame} mm
W_frame:    ${W_frame} mm
D_frame:    ${D_frame} mm
H_usable:   ${H_usable} mm
H_tot:      ${H_tot} mm   (frame + tabletop + casters)

Drawer layout
-------------
H_low:   ${H_low} mm   H_mid: ${H_mid} mm   H_high: ${H_high} mm
n_low:   ${n_low}      n_mid: ${n_mid}      n_high: ${n_high}
n_tot:   ${n_tot}
N (max slots of H_low): ${N}

H_spacing:    ${H_spacing} mm
H_drawersmax: ${H_drawersmax} mm
X_drawers:    ${X_drawers} mm (total drawer height)
Remaining drawer space: ${(H_drawersmax - X_drawers).toFixed(1)} mm

Drawer geometry
---------------
D_drawer (outer depth): ${D_drawer} mm
D_side (profile length): ${D_side} mm
W_drawer (front/back):  ${W_drawer} mm

Costs
-----
C_base:    ${C_base.toFixed(2)} CHF
C_drawer:  ${C_drawer.toFixed(2)} CHF
C_total:   ${C_tot.toFixed(2)} CHF

Messages
--------
${warnings.join('\n')}
`;

  document.getElementById('output').textContent = out;
}

// attach listeners
document.querySelectorAll('input').forEach(input => {
  input.addEventListener('input', computeAll);
});

window.addEventListener('load', () => {
  // link sliders with boxes
  linkSliderAndBox('H_frame_range', 'H_frame', 200, 2000, 1000);
  linkSliderAndBox('W_frame_range', 'W_frame', 300, 2000, 1000);
  linkSliderAndBox('D_frame_range', 'D_frame', 300, 2000, 600);

  // add more if you create sliders for n_low, n_mid, n_high, etc.
  // linkSliderAndBox('n_low_range', 'n_low', 0, 20, 6);
function linkSliderAndBox(rangeId, boxId, min, max, def) {
  const range = document.getElementById(rangeId);
  const box   = document.getElementById(boxId);

  // initial sync
  range.value = box.value = def;

  range.addEventListener('input', () => {
    box.value = range.value;
    computeAll();
  });

  box.addEventListener('input', () => {
    // clamp in box, then sync to range
    let v = parseFloat(box.value);
    if (isNaN(v)) v = def;
    if (v < min) v = min;
    if (v > max) v = max;
    box.value = v;
    range.value = v;
    computeAll();
  });
}
  computeAll();
});
