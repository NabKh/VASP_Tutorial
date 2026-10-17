# VASP tutorial: band structure of 2H-MoS<sub>2</sub>, PBE vs HSE06

A hands-on VASP tutorial. You relax bulk 2H-MoS<sub>2</sub> with PBE+D3, then compute its band structure with PBE and with the HSE06 hybrid functional, and compare the two band gaps.

Only input files and scripts are given, with no outputs: you run every step yourself and check the result against the points listed below. The same system is treated with Quantum ESPRESSO in [Quantum_Espresso_Tutorials](https://github.com/NabKh/Quantum_Espresso_Tutorials), so you can compare the two codes.

## Requirements

- VASP 6.3.0 or newer, which is needed for `KPOINTS_OPT` (see the [VASP wiki](https://www.vasp.at/wiki/index.php/KPOINTS_OPT)). For older versions, see [Older VASP versions](#older-vasp-versions).
- The PBE PAW potentials (`potpaw_PBE`). They are licensed with VASP and are **not** included here.
- Python with `pymatgen` and `matplotlib` for `plot_bands.py`.

## Layout

```
VASP_Tutorial/
├── 1-relax/     PBE+D3(BJ) relaxation of cell and atoms
├── 2-pbe/       PBE SCF + band structure along KPOINTS_OPT
├── 3-hse06/     HSE06 SCF + band structure along KPOINTS_OPT
└── plot_bands.py   prints both gaps, plots PBE and HSE06 together
```

Each folder has a `run.sbatch` for a Slurm cluster. Edit the module line and the resources for your machine.

## Step 0: build the POTCAR

The order of the potentials must follow the order of the species in the POSCAR (Mo, then S):

```bash
cd 1-relax
cat /path/to/potpaw_PBE/Mo_sv/POTCAR /path/to/potpaw_PBE/S/POTCAR > POTCAR
grep -E "TITEL|ZVAL|ENMAX" POTCAR
```

`Mo_sv` treats the Mo 4s and 4p semicore states as valence (14 electrons per Mo), and `S` has 6. The cell holds 2 Mo and 4 S, so it has 2×14 + 4×6 = 52 electrons, i.e. 26 occupied bands. Check the `ZVAL` lines against these numbers. If you pick other potentials, recount and adjust `NBANDS`.

## Step 1: relaxation (`1-relax`)

The starting POSCAR is the PBE+D3 cell from the QE tutorial. 2H-MoS<sub>2</sub> is a layered crystal held together along *c* by van der Waals forces, which PBE alone misses: without a dispersion correction the layers drift apart and *c* comes out far too long.

| Tag | Why |
|---|---|
| `IVDW = 12` | Grimme D3 with Becke–Johnson damping ([IVDW](https://www.vasp.at/wiki/index.php/IVDW)) |
| `ISIF = 3`, `IBRION = 2` | relax ions, cell shape and volume with conjugate gradients |
| `ENCUT = 450` | a cell relaxation needs a cutoff well above `ENMAX`, otherwise Pulay stress shrinks the cell |
| `EDIFFG = -0.005` | stop when every force is below 5 meV/Å |
| `ISMEAR = 0`, `SIGMA = 0.05` | Gaussian smearing, safe for a semiconductor |

```bash
sbatch run.sbatch
```

Check:

- `grep "reached required accuracy" OUTCAR`. If it is missing, the run hit `NSW`.
- When the cell changes, the plane-wave basis is set up for the starting cell. Copy `CONTCAR` to `POSCAR` and run again until the volume stops changing.
- Compare the final *a* and *c* (`head -5 CONTCAR`) with experiment and with the QE result.

## Step 2: PBE bands (`2-pbe`)

`run.sbatch` copies the relaxed `CONTCAR` and the `POTCAR` from `1-relax`. This is a single SCF run on the 9×9×2 grid in `KPOINTS`. Because `KPOINTS_OPT` is present, VASP then also computes the eigenvalues along the path Γ–M–K–Γ–A–L–H–A|L–M|K–H from the converged density.

| Tag | Why |
|---|---|
| `NBANDS = 32` | 26 occupied + 6 empty bands, so the conduction band is there. Use the same value in `3-hse06` |
| `LORBIT = 11` | orbital projections, also on the path (`PROCAR_OPT`) |
| `LWAVE = .TRUE.` | the HSE06 run starts from this WAVECAR |

There is no `IVDW` here. D3 adds an energy and forces that depend only on the atomic positions, so at fixed geometry it does not change the Kohn–Sham eigenvalues.

## Step 3: HSE06 bands (`3-hse06`)

Same geometry and k-points, now with the hybrid functional:

| Tag | Why |
|---|---|
| `LHFCALC = .TRUE.`, `GGA = PE` | hybrid functional built on PBE |
| `HFSCREEN = 0.2` | screening parameter of HSE06; the exact-exchange fraction keeps its default, 0.25 |
| `HFRCUT = -1` | truncated Coulomb kernel, which converges faster for systems with a gap and is the setting the wiki gives for `KPOINTS_OPT` with hybrids ([HFRCUT](https://www.vasp.at/wiki/index.php/HFRCUT)) |
| `ALGO = All` | direct minimisation, robust for hybrids |
| `ISTART = 1` | start from the PBE WAVECAR of step 2 |

A non-self-consistent band run (`ICHARG = 11`) is **not** possible with a hybrid functional, since the exact exchange needs the orbitals and not only the density. That is why `KPOINTS_OPT` is used here. Expect this step to cost much more than step 2; compare the `Elapsed time` at the end of the two `OUTCAR` files.

## Step 4: compare

```bash
python plot_bands.py
```

The script reads `2-pbe/vasprun.xml` and `3-hse06/vasprun.xml` with pymatgen. `Vasprun.get_band_structure()` takes the eigenvalues on the `KPOINTS_OPT` path. The script prints the gap of each functional, whether it is direct or indirect, and between which k-points, and it writes `MoS2_PBE_HSE06_bands.png/.pdf` with both band structures aligned at the valence band maximum.

Check:

- Where are the valence band maximum and the conduction band minimum? Do they sit at the same k-points in PBE and HSE06?
- How large is the gap shift from PBE to HSE06? Is it a near-rigid shift of the conduction bands, or does the band shape change?
- Compare with the QE gaps from `Electronic_properties/` and `Hybrid_HSE06/` in the QE tutorial. Note that the QE HSE gap is taken only on the SCF grid, while here it is taken along the full path.

## Older VASP versions

Without `KPOINTS_OPT` (before 6.3.0):

- **PBE:** run the SCF, then a second run with `ICHARG = 11` and a line-mode `KPOINTS`.
- **HSE06:** take the `IBZKPT` of an SCF run, append the path k-points with weight 0, and use that as `KPOINTS` in a single SCF run. Only the weighted k-points enter the density; the zero-weight ones give the bands.

## Things to try

1. Converge `ENCUT` (400–600 eV) and the k-grid (6×6×2 to 12×12×3) for the PBE gap before trusting any number.
2. Cheaper exact exchange: add `NKREDX = 3`, `NKREDY = 3`, `NKREDZ = 1` to `3-hse06`, so the Fock operator uses a 3×3×2 sub-grid of the 9×9×2 k-grid ([NKRED](https://www.vasp.at/wiki/index.php/NKRED)). Choose factors that divide the k-grid. How much does the gap change, and how much time do you save?
3. Set `AEXX = 0.35` (the PBE exchange part, `AGGAX`, follows automatically as 1 − `AEXX`) and follow the gap as a function of the exact-exchange fraction.
4. Relax with `IVDW = 11` (D3 zero damping) and compare *a*, *c* and the PBE gap with `IVDW = 12`.
5. Relax without `IVDW` and watch what happens to *c*, then rerun step 2 on that cell.
6. Plot the orbital character from `PROCAR_OPT` (pymatgen: `Vasprun(..., parse_projected_eigen=True)`). Which Mo d and S p orbitals form the band edges at Γ and K?
