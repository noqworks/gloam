"""Gloam fixture: body and diffuser (CadQuery).

Both parts are stadium shaped (a rectangle with half-round ends). The body is printed upright in white PETG; the
diffuser is printed face down in clear PETG and drops into the ledge at the top of the body.

Coordinates: X across the fixture, Y along it, Z up from the print bed. Units: mm.

    python3 gloam_fixture.py          # writes ../step and ../stl
"""
from __future__ import annotations

import pathlib

import cadquery as cq

# ── shape ───────────────────────────────────────────────────────────────────────────────────────────────
END_CENTRE = 31.25        # distance from the middle to the centre of each half-round end
BODY_R = 13.7             # outer half width of the body (27.4 mm wide)
WALL = 1.8                # side wall
FLOOR = 2.0               # floor thickness
BODY_H = 15.77            # overall height of the body
LEDGE_Z = 14.0            # height of the ledge the diffuser rests on
LEDGE_R = 12.7            # half width at the ledge (rim thickness = BODY_R - LEDGE_R)
TOP_ROUND = 1.1           # outer top edge radius

# Grooves inside both long walls; the bumps on the diffuser lip click into them.
GROOVE_R = 12.5           # half width at the groove bottom (0.6 mm deep)
GROOVE_Z = 11.64          # groove bottom height
GROOVE_H = 1.0            # groove height
GROOVE_Y = (12.75, 25.75) # groove span along Y, on both halves (the middle stays solid)

# ── LED strips ──────────────────────────────────────────────────────────────────────────────────────────
# Two 8 mm COB strips (amber, warm white) side by side, 50 mm long, between low guide ribs.
RIB_X = (-10.3, -1.1, 1.1, 10.3)
RIB_W = 0.8
RIB_H = 0.6
RIB_L = 50.5

# ── mounting ────────────────────────────────────────────────────────────────────────────────────────────
SCREW_Y = 32.5            # two countersunk screws through the floor, head inside the body
SCREW_D = 3.2             # for 3 mm wood screws
CSK_D = 7.2               # countersink diameter at the floor top (90°)

# ── cable entry (both ends) ─────────────────────────────────────────────────────────────────────────────
# An arch through the end wall and floor: fits round ~6 mm 3-core cable. The same entry on both ends lets the
# line run fixture to fixture.
CABLE_W = 7.5             # arch width
CABLE_SPRING = 3.25       # height where the half-round top starts (arch top = CABLE_SPRING + CABLE_W / 2)
CABLE_FROM_Y = 38.0       # where the entry starts, measured from the middle

# ── diffuser ────────────────────────────────────────────────────────────────────────────────────────────
DIFF_R = 12.5             # plate half width (0.2 mm clearance to the ledge)
DIFF_T = 1.8              # plate thickness: flush with the rim when seated
DIFF_EDGE = 1.2           # rounded visible edge
LIP_OUT = 11.7            # lip outer half width (0.2 mm clearance to the inner wall)
LIP_W = 1.2               # lip wall
LIP_H = 2.4               # lip height
# Four small bumps on the lip hold the diffuser by friction (0.3 mm into the inner wall).
NUB_OUT = 0.5             # how far a bump stands out from the lip
NUB_L = 10.0              # bump length along Y
NUB_Y = 14.25             # bump start, measured from the middle
NUB_Z = 1.5               # bump bottom above the plate
NUB_H = 0.7               # bump height


def stadium(r: float, height: float, z: float = 0.0) -> cq.Workplane:
    """Stadium of half width r along Y, extruded up from z."""
    length = 2 * (END_CENTRE + r)
    return cq.Workplane("XY").workplane(offset=z).slot2D(length, 2 * r, angle=90).extrude(height)


def body() -> cq.Workplane:
    b = stadium(BODY_R, BODY_H).edges(">Z").fillet(TOP_ROUND)
    b = b.cut(stadium(BODY_R - WALL, BODY_H, FLOOR))
    b = b.cut(stadium(LEDGE_R, BODY_H, LEDGE_Z))
    g0, g1 = GROOVE_Y
    for sy in (1, -1):
        b = b.cut(cq.Workplane("XY").box(2 * GROOVE_R, g1 - g0, GROOVE_H, centered=(True, True, False))
                  .translate((0, sy * (g0 + g1) / 2, GROOVE_Z)))
    for x in RIB_X:
        b = b.union(cq.Workplane("XY").box(RIB_W, RIB_L, RIB_H, centered=(True, True, False)).translate((x, 0, FLOOR)))
    for s in (1, -1):
        y = s * SCREW_Y
        b = b.cut(cq.Workplane("XY").circle(SCREW_D / 2).extrude(FLOOR + 1).translate((0, y, -0.5)))
        b = b.cut(cq.Workplane("XY").add(cq.Solid.makeCone(SCREW_D / 2, CSK_D / 2, (CSK_D - SCREW_D) / 2,
                                                            cq.Vector(0, y, FLOOR - (CSK_D - SCREW_D) / 2))))
        # cable entry: straight part through the floor + half-round top
        y0, length = (CABLE_FROM_Y, 15.0) if s > 0 else (-CABLE_FROM_Y - 15.0, 15.0)
        b = b.cut(cq.Workplane("XY").box(CABLE_W, length, CABLE_SPRING + 1, centered=(True, False, False))
                  .translate((0, y0, -1)))
        b = b.cut(cq.Workplane("XZ").circle(CABLE_W / 2).extrude(-length)
                  .translate((0, y0, CABLE_SPRING)))
    return b


def diffuser() -> cq.Workplane:
    """Printed face down: the visible face is on the bed (z = 0), the lip points up."""
    d = stadium(DIFF_R, DIFF_T).edges("<Z").fillet(DIFF_EDGE)
    lip = stadium(LIP_OUT, LIP_H, DIFF_T).cut(stadium(LIP_OUT - LIP_W, LIP_H, DIFF_T))
    d = d.union(lip)
    for sx in (1, -1):
        for sy in (1, -1):
            x = sx * (LIP_OUT + NUB_OUT / 2 - 0.05)
            y = sy * (NUB_Y + NUB_L / 2)
            d = d.union(cq.Workplane("XY").box(NUB_OUT + 0.1, NUB_L, NUB_H, centered=(True, True, False))
                        .translate((x, y, DIFF_T + NUB_Z)))
    return d


def export(out: pathlib.Path) -> dict[str, cq.Workplane]:
    parts = {"fixture-body": body(), "fixture-diffuser": diffuser()}
    for name, part in parts.items():
        cq.exporters.export(part, str(out / "step" / f"{name}.step"))
        cq.exporters.export(part, str(out / "stl" / f"{name}.stl"), tolerance=0.01, angularTolerance=0.1)
    return parts


if __name__ == "__main__":
    hw = pathlib.Path(__file__).resolve().parent.parent
    for name in export(hw):
        print(name)
