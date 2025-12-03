function computeAll() {
  const getNum = id => parseFloat(document.getElementById(id).value);
  const H_frame = getNum('H_frame');
  const W_frame = getNum('W_frame');
  const D_frame = getNum('D_frame');
  const t_tabletop = getNum('t_tabletop');
  const H_casters = getNum('H_casters');
  const S_drawer = getNum('S_drawer');
  const H_low = getNum('H_low');
  const H_mid = getNum('H_mid');
  const H_high = getNum('H_high');
  const n_low = getNum('n_low');
  const n_mid = getNum('n_mid');
  const n_high = getNum('n_high');
  const C_204080 = getNum('C_204080');
  const C_2020 = getNum('C_2020');
  const C_4040 = getNum('C_4040');
  const C_404080 = getNum('C_404080');
  const C_2040 = getNum('C_2040');
  const C_slides = getNum('C_slides');
  const t_slide = getNum('t_slide');
  const t_bracket = getNum('t_bracket');

  const H_usable = H_frame - 80;
  const N = Math.floor(H_usable / H_low);
  const n_tot = n_low + n_mid + n_high;
  const H_spacing = S_drawer * (n_tot + 1);
  const H_drawersmax = H_usable - H_spacing;
  const X_drawers = H_low * n_low + H_mid * n_mid + H_high * n_high;

  const D_drawer = Math.floor((D_frame - 40) / 50) * 50;
  const D_side = D_drawer - 40;
  const W_drawer = W_frame - 2 * (t_slide + t_bracket + 40);

  const C_base =
    4 * C_204080 * H_frame +
    4 * C_4040 * (W_frame + D_drawer - 240) +
    40;

  const C_drawer =
    n_tot * (2 * C_2040 * (W_drawer + D_side) + C_slides);

  const C_tot = C_base + C_drawer;

  let warnings = [];
  if (n_tot > N)
    warnings.push(`Warning: Total drawers (${n_tot}) exceed maximum slots (${N})`);
  if (X_drawers > H_drawersmax)
    warnings.push(
      `Warning: Drawer heights (H=${X_drawers} mm) + spacing (S=${H_spacing} mm) exceed usable height (${H_usable} mm)`
    );
  if (X_drawers < H_drawersmax)
    warnings.push(`Info: Remaining vertical space: ${H_drawersmax - X_drawers} mm`);

  const outputText = `
H_usable:      ${H_usable} mm
H_drawersmax:  ${H_drawersmax} mm
N (max slots): ${N}
n_tot:         ${n_tot}
X_drawers:     ${X_drawers} mm
Remaining space: ${H_drawersmax - X_drawers} mm

Geometry:
D_drawer:  ${D_drawer} mm
D_side:    ${D_side} mm
W_drawer:  ${W_drawer} mm

Cost:
C_base:    ${C_base.toFixed(2)} CHF
C_drawer:  ${C_drawer.toFixed(2)} CHF
C_total:   ${C_tot.toFixed(2)} CHF

${warnings.join('\n')}
`;

  document.getElementById('output').textContent = outputText;
}

// Attach event listeners
document.querySelectorAll('input').forEach(input => {
  input.addEventListener('input', computeAll);
});

// Initial compute on load
window.onload = computeAll;
