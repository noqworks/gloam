"""Gloam controller enclosure: box and lid (CadQuery).

Holds a Mean Well LRS-75-12 power supply and a 50 × 70 mm perfboard with the Wemos D1 mini, the 12 V → 5 V
step-down, the ULN2003A and two 3-way terminal blocks. Mains and the LED line come in through two M16 cable glands
on the same end wall; a divider keeps the mains terminals apart from the 12 V side. The lid is held by four M3
countersunk screws in heat-set inserts.

Coordinates: X along the box (the cable wall is at X = 0), Y across it (the USB wall is at Y = 0), Z up from the
print bed. X and Y are measured on the inside of the walls. Units: mm.

    python3 gloam_controller.py       # writes ../step and ../stl (box, lid, assembly)

The box is parametric: the power supply, the perfboard and one extra component on the floor can be changed, and the walls,
glands, divider, screw columns and lid follow. The same parameters drive the online box designer on open.noq.works.

    python3 gloam_controller.py --set psu_x=129 --set board_x=80 --out /tmp/box    # a box for an LRS-100-12 and an 80 mm board
    python3 gloam_controller.py --params                                              # the parameters, their ranges and defaults (JSON)
"""
from __future__ import annotations

import argparse
import json
import math
import pathlib
import sys

import cadquery as cq

# ── shell ───────────────────────────────────────────────────────────────────────────────────────────────
WALL = 2.4                # side walls (6 lines with a 0.4 mm nozzle)
FLOOR = 2.4
LID_T = 3.0
CORNER_R = 4.0            # outer vertical edge radius
FIT = 0.3                 # general clearance between printed parts

# ── power supply: Mean Well LRS-75-12 (12 V 6 A, case 240A) ────────────────────────────────────────────
# The terminal side (5 screw terminals, wires enter from the side) faces the cable wall.
PSU_X = 99.0              # depth, away from the terminal side
PSU_Y = 97.0              # width, along the terminal row
PSU_H = 30.0
# Terminal centres measured from the PSU edge nearest the perfboard: 1 AC/L, 2 AC/N, 3 FG, 4 -V, 5 +V.
PSU_TERMINALS = (81.3, 71.8, 62.3, 52.8, 43.3)
PSU_TERMINAL_DEPTH = 17.0  # terminal block depth inside the case outline
PSU_BEHIND = 9.0          # air gap behind the PSU (vents in that wall)
PSU_SIDE = 1.5            # gap to the side wall
PSU_DIVIDER = (PSU_TERMINALS[2] + PSU_TERMINALS[3]) / 2   # mains divider, from the PSU edge nearest the board: between FG and -V

# ── wiring channel between the cable wall and the PSU terminals ────────────────────────────────────────
WIRING = 22.0

# ── perfboard (50 × 70 mm, Ø2 mm holes 2 mm in from the corners) ───────────────────────────────────────
BOARD_X, BOARD_Y, BOARD_T = 70.0, 50.0, 1.6
BOARD_HOLE_INSET = 2.0
BOARD_STANDOFF = 5.0      # height of the standoffs above the floor
BOARD_PILOT = 1.8         # pilot hole for M2 self-tapping screws (M2 × 6)
BOARD_AT = (WIRING + 2.0, 3.0)   # board corner nearest the origin
BOARD_TO_PSU = 5.0        # gap between the board and the PSU

# ── lid screws ──────────────────────────────────────────────────────────────────────────────────────────
BOSS_D = 8.4              # corner column
INSERT_D = 4.0            # hole for M3 heat-set inserts (M3 × 5.7, outer Ø4.6)
INSERT_DEPTH = 6.4
SCREW_D = 3.4             # M3 clearance in the lid
SCREW_CSK = 6.6           # countersink for DIN 7991 / ISO 10642 M3 screws

# ── cable glands (polyamide PG glands, both on the cable wall) ────────────────────────────────────────
# mains: PG11, clamps Ø5–10 mm (3 × 0.75 mm² H05VV-F); LED line: PG7, clamps Ø3–7 mm (3 × 0.5 mm² round).
# Positions follow the layout (see _derive): mains near the far wall by the L/N terminals, LED in the middle of the board zone.
GLANDS = {
    "mains": {"y": 0.0, "hole": 19.0, "thread": 18.6, "nut": 22.0, "body": 24.0},
    "led":   {"y": 0.0, "hole": 12.9, "thread": 12.5, "nut": 15.0, "body": 16.0},
}
MAINS_FROM_FAR_WALL = 22.5

# ── mains divider ───────────────────────────────────────────────────────────────────────────────────────
DIVIDER_T = 2.0

# ── PSU retention ───────────────────────────────────────────────────────────────────────────────────────
STOP_T, STOP_H, STOP_LEG = 1.2, 4.0, 8.0     # L-shaped corner stops on the floor
PAD_D = 7.0                                  # pads under the lid that hold the PSU down
PAD_PRESS = 0.2                              # interference on the PSU top
PAD_IN = (28.0, 12.0)                        # pad centres from the terminal-side corner (clear of the terminal block)
PAD_BACK = (9.0, 12.0)                       # and from the far corner

# ── USB access to the D1 mini ───────────────────────────────────────────────────────────────────────────
USB_SLOT = (13.0, 8.0)    # width, height: micro-USB and USB-C plug bodies (USB-C overmoulds up to ~12.4 × 6.5)

# ── vents ───────────────────────────────────────────────────────────────────────────────────────────────
VENT_W = 2.0              # slot width: keeps fingers and tools out
VENT_PITCH = 6.0

# ── wall mounting ears ──────────────────────────────────────────────────────────────────────────────────
EAR_W, EAR_OUT, EAR_T = 20.0, 12.0, 4.0
EAR_HOLE, EAR_CSK = 4.5, 9.0                  # 4 mm countersunk wood or wall screws

# ── components on the perfboard (board coordinates: x along 70, y along 50, from the board corner) ─────
# name: (x, y, size x, size y, height above the board)
PARTS = {
    "d1-mini":        (41.0, 0.0, 25.6, 34.2, 8.5 + 1.0 + 3.3),   # on female headers, USB at the board edge
    "uln2003a":       (16.0, 6.0, 21.0, 8.0, 9.0),                # DIP-16 in a socket
    "step-down":      (14.0, 34.0, 17.2, 11.2, 6.5),              # Mini-360 on pin headers
    "terminal-led":   (0.0, 12.0, 7.5, 15.2, 10.0),               # 3-way 5.08 mm: +12 V, amber -, warm white -
    "terminal-power": (0.0, 31.0, 7.5, 15.2, 10.0),               # 3-way 5.08 mm: +12 V, GND
}
USB_CENTRE_ABOVE_BOARD = 8.5 + 1.0 + 1.5
D1_FROM_BOARD_END = 29.0  # the D1 mini sits at the far end of the board, its USB at the front edge

# ── extra component (optional): a module standing on the floor next to the board, held by corner stops ──
EXTRA_X, EXTRA_Y, EXTRA_H = 0.0, 0.0, 0.0     # 0 = none
EXTRA_GAP = 4.0           # gap to the board

# ── user parameters (the online box designer and --set change these; the defaults are the Gloam build) ──
GRUPLAR = {
    "psu": {"tr": "Güç kaynağı", "en": "Power supply"},
    "board": {"tr": "Delikli kart (pertinaks)", "en": "Perfboard"},
    "extra": {"tr": "Ek bileşen", "en": "Extra component"},
}
PARAMETRELER = {
    "psu_x": dict(hedef="PSU_X", grup="psu", min=60.0, max=200.0,
                  ad={"tr": "Derinlik", "en": "Depth"},
                  aciklama={"tr": "Vidalı klemens tarafından arka kenara.", "en": "From the terminal side to the back."}),
    "psu_y": dict(hedef="PSU_Y", grup="psu", min=50.0, max=150.0,
                  ad={"tr": "Genişlik", "en": "Width"},
                  aciklama={"tr": "Klemens sırası boyunca.", "en": "Along the row of terminals."}),
    "psu_h": dict(hedef="PSU_H", grup="psu", min=22.0, max=60.0,
                  ad={"tr": "Yükseklik", "en": "Height"}, aciklama={"tr": "", "en": ""}),
    "psu_divider": dict(hedef="PSU_DIVIDER", grup="psu", min=10.0, max=140.0,
                        ad={"tr": "Ayraç konumu", "en": "Divider position"},
                        aciklama={"tr": "Kart tarafındaki kenardan, FG ile −V vidalarının arası. Şebeke ile 12 V kablolarını ayırır.",
                                  "en": "From the edge nearest the board, between the FG and −V screws. Keeps mains and 12 V wires apart."}),
    "board_x": dict(hedef="BOARD_X", grup="board", min=67.0, max=160.0,
                    ad={"tr": "Uzun kenar", "en": "Long side"},
                    aciklama={"tr": "Gloam devresi en az 67 × 47 mm ister.", "en": "The Gloam circuit needs at least 67 × 47 mm."}),
    "board_y": dict(hedef="BOARD_Y", grup="board", min=47.0, max=120.0,
                    ad={"tr": "Kısa kenar", "en": "Short side"}, aciklama={"tr": "", "en": ""}),
    "extra_x": dict(hedef="EXTRA_X", grup="extra", min=0.0, max=120.0,
                    ad={"tr": "En", "en": "Length"},
                    aciklama={"tr": "Kartın yanında tabana oturur, köşe tutucularla yerinde kalır. Yoksa 0.",
                              "en": "Stands on the floor next to the board, held by corner stops. 0 if none."}),
    "extra_y": dict(hedef="EXTRA_Y", grup="extra", min=0.0, max=120.0,
                    ad={"tr": "Boy", "en": "Width"}, aciklama={"tr": "", "en": ""}),
    "extra_h": dict(hedef="EXTRA_H", grup="extra", min=0.0, max=50.0,
                    ad={"tr": "Yükseklik", "en": "Height"}, aciklama={"tr": "", "en": ""}),
}
VARSAYILAN = {k: float(globals()[v["hedef"]]) for k, v in PARAMETRELER.items()}


class ParametreHatasi(ValueError):
    def __init__(self, kod: str, tr: str, en: str):
        super().__init__(en)
        self.kod, self.tr, self.en = kod, tr, en


def _extra() -> bool:
    return EXTRA_X > 0 and EXTRA_Y > 0 and EXTRA_H > 0


def _derive() -> None:
    """Layout from the parameters: zone widths, inside size, glands, divider, screw columns."""
    global ZONE_Y, EXTRA_AT, PSU_AT, XI, YI, ZI, BOX_H, DIVIDER_Y, GLAND_MAINS_Y, GLAND_LED_Y, GLAND_Z, BOSS_OFF, BOSSES, BOARD_TOP
    global PAD_XY, VENT_CX, VENT_LEN
    PARTS["d1-mini"] = (BOARD_X - D1_FROM_BOARD_END, *PARTS["d1-mini"][1:])
    ZONE_Y = max(BOARD_Y, EXTRA_Y if _extra() else 0.0)
    EXTRA_AT = (BOARD_AT[0] + BOARD_X + EXTRA_GAP, BOARD_AT[1])
    PSU_AT = (WIRING, BOARD_AT[1] + ZONE_Y + BOARD_TO_PSU)
    XI = max(WIRING + PSU_X + PSU_BEHIND, BOARD_AT[0] + BOARD_X + BOSS_D + 1.0,
             EXTRA_AT[0] + EXTRA_X + BOSS_D + 1.0 if _extra() else 0.0)
    YI = PSU_AT[1] + PSU_Y + PSU_SIDE
    tallest = max(PSU_H, BOARD_STANDOFF + BOARD_T + max(p[4] for p in PARTS.values()), EXTRA_H if _extra() else 0.0)
    ZI = tallest + 2.0
    BOX_H = FLOOR + ZI
    DIVIDER_Y = PSU_AT[1] + PSU_DIVIDER
    GLAND_MAINS_Y = YI - MAINS_FROM_FAR_WALL
    GLAND_LED_Y = BOARD_AT[1] + ZONE_Y / 2
    GLANDS["mains"]["y"], GLANDS["led"]["y"] = GLAND_MAINS_Y, GLAND_LED_Y
    GLAND_Z = FLOOR + ZI / 2 - 0.5
    BOSS_OFF = BOSS_D / 2
    BOSSES = [(BOSS_OFF, BOSS_OFF), (XI - BOSS_OFF, BOSS_OFF), (BOSS_OFF, YI - BOSS_OFF), (XI - BOSS_OFF, YI - BOSS_OFF)]
    BOARD_TOP = FLOOR + BOARD_STANDOFF + BOARD_T
    PAD_XY = [(PAD_IN[0], PAD_IN[1]), (PSU_X - PAD_BACK[0], PAD_IN[1]), (PAD_IN[0], PSU_Y - PAD_BACK[1]), (PSU_X - PAD_BACK[0], PSU_Y - PAD_BACK[1])]
    VENT_CX = (PAD_IN[0] + PSU_X - PAD_BACK[0]) / 2
    VENT_LEN = (PSU_X - PAD_BACK[0] - PAD_IN[0]) - 18.0


def _check() -> list[dict]:
    """Blocking problems raise ParametreHatasi; the rest come back as warnings (print bed size)."""
    m, led = GLANDS["mains"], GLANDS["led"]
    if not 10.0 <= PSU_DIVIDER <= PSU_Y - 10.0:
        raise ParametreHatasi("ayrac", "Ayraç güç kaynağının içinde olmalı (kenarlardan en az 10 mm).",
                              "The divider must be within the power supply (at least 10 mm from its edges).")
    if GLAND_MAINS_Y - m["nut"] / 2 < DIVIDER_Y + DIVIDER_T / 2 + 1.0:
        raise ParametreHatasi("ayrac_rakor", "Şebeke rakoru ayracın şebeke tarafına sığmıyor: ayracı kart tarafına yaklaştırın.",
                              "The mains gland does not fit on the mains side of the divider: move the divider towards the board.")
    if GLAND_LED_Y + led["nut"] / 2 > DIVIDER_Y - DIVIDER_T / 2 - 1.0:
        raise ParametreHatasi("led_rakor", "LED rakoru ayracın 12 V tarafına sığmıyor: ayracı kart tarafından uzaklaştırın.",
                              "The LED gland does not fit on the 12 V side of the divider: move the divider away from the board.")
    if GLAND_Z + m["body"] / 2 > BOX_H - 0.5:
        raise ParametreHatasi("alcak", "Kutu şebeke rakoru için çok alçak; güç kaynağı yüksekliği en az 22 mm olmalı.",
                              "The box is too low for the mains gland; the power supply must be at least 22 mm tall.")
    uyari = []
    dis = (XI + 2 * WALL, YI + 2 * WALL + 2 * EAR_OUT, BOX_H)
    for ad, tabla in (("A1 mini", 180.0), ("A1 · P1 · X1", 256.0)):
        if max(dis[0], dis[1]) > tabla:
            uyari.append({"kod": "tabla", "tr": f"{ad} tablasına ({tabla:.0f} mm) sığmaz.", "en": f"Does not fit the {ad} bed ({tabla:.0f} mm)."})
    return uyari


def configure(degerler: dict | None = None) -> list[dict]:
    """Set the parameters (missing ones keep their defaults) and lay the box out again. Returns warnings."""
    d = dict(VARSAYILAN)
    for k, v in (degerler or {}).items():
        if k not in PARAMETRELER:
            raise ParametreHatasi("bilinmeyen", f"Bilinmeyen parametre: {k}", f"Unknown parameter: {k}")
        try:
            x = float(v)
        except (TypeError, ValueError):
            raise ParametreHatasi("sayi", f"{k}: sayı olmalı.", f"{k}: must be a number.") from None
        p = PARAMETRELER[k]
        if not (p["min"] <= x <= p["max"]) and not (p["grup"] == "extra" and x == 0):
            raise ParametreHatasi("aralik", f"{p['ad']['tr']}: {p['min']:g}–{p['max']:g} mm olmalı.",
                                  f"{p['ad']['en']}: must be {p['min']:g}–{p['max']:g} mm.")
        d[k] = round(x, 2)
    for k, v in d.items():
        globals()[PARAMETRELER[k]["hedef"]] = v
    _derive()
    return _check()


_derive()


def board_xy(x: float, y: float) -> tuple[float, float]:
    return BOARD_AT[0] + x, BOARD_AT[1] + y


def block(x0, y0, z0, dx, dy, dz) -> cq.Workplane:
    return cq.Workplane("XY").box(dx, dy, dz, centered=False).translate((x0, y0, z0))


def teardrop_x(y: float, z: float, d: float, depth: float, x0: float) -> cq.Workplane:
    """Horizontal hole through a wall normal to X, with a 45° roof so it prints without support."""
    r = d / 2
    k = r * math.sqrt(0.5)
    prof = (cq.Workplane("YZ").workplane(offset=x0).center(y, z).circle(r).extrude(depth)
            .union(cq.Workplane("YZ").workplane(offset=x0)
                   .polyline([(y - k, z + k), (y, z + r * math.sqrt(2)), (y + k, z + k)]).close().extrude(depth)))
    return prof


def corner_stops(b: cq.Workplane, px: float, py: float, dx: float, dy: float) -> cq.Workplane:
    g = 0.4
    for cx, cy, sx, sy in ((px, py, 1, 1), (px + dx, py, -1, 1), (px, py + dy, 1, -1), (px + dx, py + dy, -1, -1)):
        x_out = cx - sx * (g + STOP_T)            # outer edge of the stop in X
        y_out = cy - sy * (g + STOP_T)
        x_end = cx + sx * STOP_LEG
        y_end = cy + sy * STOP_LEG
        b = b.union(block(min(x_out, x_end), min(y_out, y_out + sy * STOP_T), FLOOR, abs(x_end - x_out), STOP_T, STOP_H))
        b = b.union(block(min(x_out, x_out + sx * STOP_T), min(y_out, y_end), FLOOR, STOP_T, abs(y_end - y_out), STOP_H))
    return b


def box() -> cq.Workplane:
    outer = (cq.Workplane("XY").box(XI + 2 * WALL, YI + 2 * WALL, BOX_H, centered=False)
             .translate((-WALL, -WALL, 0)).edges("|Z").fillet(CORNER_R))
    cavity = block(0, 0, FLOOR, XI, YI, ZI + 1)
    b = outer.cut(cavity)

    # corner columns with heat-set insert holes
    for x, y in BOSSES:
        r = BOSS_D / 2
        xw = 0.0 if x < XI / 2 else XI
        yw = 0.0 if y < YI / 2 else YI
        col = cq.Workplane("XY").circle(r).extrude(ZI).translate((x, y, FLOOR))
        col = col.union(block(min(xw, x), y - r, FLOOR, abs(x - xw), 2 * r, ZI))     # tie into the X wall
        col = col.union(block(x - r, min(yw, y), FLOOR, 2 * r, abs(y - yw), ZI))     # tie into the Y wall
        b = b.union(col)
        b = b.cut(cq.Workplane("XY").circle(INSERT_D / 2).extrude(INSERT_DEPTH).translate((x, y, BOX_H - INSERT_DEPTH)))
        b = b.cut(cq.Workplane("XY").circle(1.4).extrude(3.0).translate((x, y, BOX_H - INSERT_DEPTH - 3.0)))

    # mains divider in the wiring channel, between terminal 3 (FG) and terminal 4 (-V)
    b = b.union(block(0, DIVIDER_Y - DIVIDER_T / 2, FLOOR, WIRING - FIT, DIVIDER_T, ZI - 0.2))

    # PSU corner stops: an L outside each corner, 0.4 mm clear of the case (the extra component gets the same)
    b = corner_stops(b, *PSU_AT, PSU_X, PSU_Y)
    if _extra():
        b = corner_stops(b, *EXTRA_AT, EXTRA_X, EXTRA_Y)

    # perfboard standoffs
    for hx in (BOARD_HOLE_INSET, BOARD_X - BOARD_HOLE_INSET):
        for hy in (BOARD_HOLE_INSET, BOARD_Y - BOARD_HOLE_INSET):
            x, y = board_xy(hx, hy)
            b = b.union(cq.Workplane("XY").circle(3.0).extrude(BOARD_STANDOFF).translate((x, y, FLOOR)))
            b = b.cut(cq.Workplane("XY").circle(BOARD_PILOT / 2).extrude(BOARD_STANDOFF + 1.0).translate((x, y, FLOOR - 1.0)))

    # cable glands in the cable wall (X = 0)
    for gl in GLANDS.values():
        b = b.cut(teardrop_x(gl["y"], GLAND_Z, gl["hole"], WALL + 2, -WALL - 1))

    # USB slot in the front wall (Y = 0) at the D1 mini
    dx, dy, dsx, dsy, dh = PARTS["d1-mini"]
    ux, _ = board_xy(dx + dsx / 2, 0)
    uz = BOARD_TOP + USB_CENTRE_ABOVE_BOARD
    w, h = USB_SLOT
    b = b.cut(cq.Workplane("XZ").workplane(offset=-1).center(ux, uz).rect(w, h).extrude(WALL + 2)
              .edges("|Y").fillet(2.0))

    # vents in the wall behind the PSU (X = XI)
    y = PSU_AT[1] + 8
    while y < PSU_AT[1] + PSU_Y - 8:
        b = b.cut(cq.Workplane("YZ").workplane(offset=XI - 1).center(y, FLOOR + ZI / 2 + 1.0).slot2D(min(20.0, ZI - 12.0), VENT_W, angle=90)
                  .extrude(WALL + 2))
        y += VENT_PITCH

    # wall mounting ears on both long sides
    for side in (-1, 1):
        ey = -WALL - EAR_OUT if side < 0 else YI + WALL
        ear = (cq.Workplane("XY").box(EAR_W, EAR_OUT + 2, EAR_T, centered=False)
               .translate((XI / 2 - EAR_W / 2, ey - (0 if side < 0 else 2), 0)))
        ear = ear.edges("|Z").fillet(3.0)
        b = b.union(ear)
        hy = -WALL - EAR_OUT / 2 if side < 0 else YI + WALL + EAR_OUT / 2
        b = b.cut(cq.Workplane("XY").circle(EAR_HOLE / 2).extrude(EAR_T + 1).translate((XI / 2, hy, -0.5)))
        b = b.cut(cq.Workplane("XY").add(cq.Solid.makeCone(EAR_HOLE / 2, EAR_CSK / 2, (EAR_CSK - EAR_HOLE) / 2,
                                                            cq.Vector(XI / 2, hy, EAR_T - (EAR_CSK - EAR_HOLE) / 2 + 0.01))))

    return b


def lid() -> cq.Workplane:
    """Printed top face down. In this model the lid sits in place (its underside at the box top)."""
    z0 = BOX_H
    plate = (cq.Workplane("XY").box(XI + 2 * WALL, YI + 2 * WALL, LID_T, centered=False)
             .translate((-WALL, -WALL, z0)).edges("|Z").fillet(CORNER_R))
    lid_ = plate.edges(">Z").chamfer(0.6)

    # countersunk screw holes over the corner columns
    for x, y in BOSSES:
        lid_ = lid_.cut(cq.Workplane("XY").circle(SCREW_D / 2).extrude(LID_T + 2).translate((x, y, z0 - 1)))
        h = (SCREW_CSK - SCREW_D) / 2
        lid_ = lid_.cut(cq.Workplane("XY").add(cq.Solid.makeCone(SCREW_D / 2, SCREW_CSK / 2, h,
                                                                  cq.Vector(x, y, z0 + LID_T - h + 0.01))))

    # locating lip just inside the walls (leaves the corners, the divider and the gland nuts free)
    lip_t, lip_h = 1.2, 2.5
    span_x = (BOSS_D + 2, XI - BOSS_D - 2)
    span_y = (BOSS_D + 2, YI - BOSS_D - 2)
    lip = block(span_x[0], FIT, z0 - lip_h, span_x[1] - span_x[0], lip_t, lip_h)                    # Y = 0 wall
    lip = lip.union(block(span_x[0], YI - FIT - lip_t, z0 - lip_h, span_x[1] - span_x[0], lip_t, lip_h))  # Y = YI
    lip = lip.union(block(XI - FIT - lip_t, span_y[0], z0 - lip_h, lip_t, span_y[1] - span_y[0], lip_h))  # X = XI
    lip = lip.union(block(FIT, span_y[0], z0 - lip_h, lip_t, DIVIDER_Y - 3 - span_y[0], lip_h))            # X = 0, below
    lip = lip.union(block(FIT, DIVIDER_Y + 3, z0 - lip_h, lip_t, span_y[1] - DIVIDER_Y - 3, lip_h))         # X = 0, above
    lid_ = lid_.union(lip)

    # divider continued over the PSU terminal block
    lid_ = lid_.union(block(WIRING - FIT, DIVIDER_Y - DIVIDER_T / 2, z0 - (BOX_H - FLOOR - PSU_H) + 0.5,
                            PSU_TERMINAL_DEPTH + 3, DIVIDER_T, BOX_H - FLOOR - PSU_H - 0.5))

    # pads holding the PSU down
    px, py = PSU_AT
    pad_len = BOX_H - (FLOOR + PSU_H) + PAD_PRESS
    for ox, oy in PAD_XY:
        lid_ = lid_.union(cq.Workplane("XY").circle(PAD_D / 2).extrude(pad_len).translate((px + ox, py + oy, z0 - pad_len)))

    # vents over the PSU (clear of the pads and the terminals)
    y = py + 22
    while y < py + PSU_Y - 20:
        lid_ = lid_.cut(cq.Workplane("XY").workplane(offset=z0 - 1).center(px + VENT_CX, y).slot2D(VENT_LEN, VENT_W)
                        .extrude(LID_T + 2))
        y += VENT_PITCH

    # name and cable markings on the top face (read with the cable wall on the left)
    top = cq.Workplane("XY").workplane(offset=z0 + LID_T)
    for label, gy in (("230 V~", GLAND_MAINS_Y), ("12 V LED", GLAND_LED_Y)):
        lid_ = lid_.cut(top.center(WIRING / 2 + 2, gy).text(label, 4.0, -0.5, combine=False, font="FreeSans",
                                                            kind="bold", halign="center", valign="center"))
    lid_ = lid_.cut(top.center(px + VENT_CX, py - 22).text("GLOAM", 9.0, -0.6, combine=False, font="FreeSans",
                                                      kind="bold", halign="center", valign="center"))
    return lid_


# ── simple component bodies for the assembly and the fit check ─────────────────────────────────────────
def components() -> dict[str, cq.Workplane]:
    c: dict[str, cq.Workplane] = {}
    px, py = PSU_AT
    c["psu"] = block(px, py, FLOOR, PSU_X, PSU_Y, PSU_H)
    c["perfboard"] = block(*board_xy(0, 0), FLOOR + BOARD_STANDOFF, BOARD_X, BOARD_Y, BOARD_T)
    for name, (x, y, sx, sy, h) in PARTS.items():
        c[name] = block(*board_xy(x, y), BOARD_TOP, sx, sy, h)
    if _extra():
        c["extra"] = block(*EXTRA_AT, FLOOR, EXTRA_X, EXTRA_Y, EXTRA_H)
    # USB plug protruding from the D1 mini towards the slot
    dx, dy, dsx, dsy, dh = PARTS["d1-mini"]
    ux, uy = board_xy(dx + dsx / 2, 0)
    c["usb-connector"] = block(ux - 4, uy - 1.0, BOARD_TOP + USB_CENTRE_ABOVE_BOARD - 1.5, 8, 1.0, 3)   # 1 mm proud of the board edge
    for key, gl in GLANDS.items():
        gy = gl["y"]
        thread = cq.Workplane("YZ").workplane(offset=-WALL - 2).center(gy, GLAND_Z).circle(gl["thread"] / 2).extrude(WALL + 8)
        dome = cq.Workplane("YZ").workplane(offset=-WALL - 18).center(gy, GLAND_Z).circle(gl["body"] / 2).extrude(16)
        nut = (cq.Workplane("YZ").workplane(offset=0.2).center(gy, GLAND_Z).polygon(6, gl["nut"] / math.cos(math.pi / 6))
               .extrude(5.0))
        c[f"gland-{key}"] = thread.union(dome).union(nut)
    return c


def fit_report(parts: dict[str, cq.Workplane]) -> list[str]:
    """Volume of every overlap between the box, the lid and the components (should all be zero)."""
    names = list(parts)
    out = []
    for i, a in enumerate(names):
        for b_ in names[i + 1:]:
            v = parts[a].val().intersect(parts[b_].val()).Volume()
            if {a, b_} == {"lid", "psu"}:
                expected = 4 * math.pi * (PAD_D / 2) ** 2 * PAD_PRESS
                if abs(v - expected) < 1.0:
                    continue                                   # the hold-down pads press the PSU on purpose
            if v > 0.01:
                out.append(f"{a} × {b_}: {v:.2f} mm³")
    return out


def export(out: pathlib.Path, assembly: bool = True) -> dict[str, cq.Workplane]:
    (out / "step").mkdir(parents=True, exist_ok=True)
    (out / "stl").mkdir(parents=True, exist_ok=True)
    b, l = box(), lid()
    cq.exporters.export(b, str(out / "step" / "controller-box.step"))
    cq.exporters.export(b, str(out / "stl" / "controller-box.stl"), tolerance=0.01, angularTolerance=0.1)
    # the lid is exported flipped, top face down, as it is printed
    l_print = l.rotate((0, 0, 0), (1, 0, 0), 180).translate((0, 0, BOX_H + LID_T))
    cq.exporters.export(l_print, str(out / "step" / "controller-lid.step"))
    cq.exporters.export(l_print, str(out / "stl" / "controller-lid.stl"), tolerance=0.01, angularTolerance=0.1)

    if not assembly:
        return {"box": b, "lid": l, **components()}
    asm = cq.Assembly(name="gloam-controller")
    asm.add(b, name="box", color=cq.Color(0.93, 0.93, 0.91))
    asm.add(l, name="lid", color=cq.Color(0.93, 0.93, 0.91, 0.5))
    colours = {"psu": (0.62, 0.64, 0.66), "perfboard": (0.25, 0.45, 0.25), "gland-mains": (0.15, 0.15, 0.15),
               "gland-led": (0.15, 0.15, 0.15)}
    for name, shape in components().items():
        asm.add(shape, name=name, color=cq.Color(*colours.get(name, (0.2, 0.3, 0.6))))
    asm.export(str(out / "step" / "controller-assembly.step"))
    return {"box": b, "lid": l, **components()}


def params_json() -> dict:
    return {"ad": "gloam-controller", "birim": "mm", "gruplar": GRUPLAR,
            "parametreler": {k: {"grup": v["grup"], "min": v["min"], "max": v["max"], "varsayilan": VARSAYILAN[k], "ad": v["ad"],
                                 "aciklama": v["aciklama"]} for k, v in PARAMETRELER.items()}}


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description="Gloam controller box (CadQuery)")
    ap.add_argument("--set", action="append", default=[], metavar="NAME=VALUE", help="change a parameter (see --params)")
    ap.add_argument("--json", help="parameters from a JSON object file (- for stdin)")
    ap.add_argument("--out", help="output folder (step/ and stl/ are created); default: the hardware folder of the repo")
    ap.add_argument("--no-assembly", action="store_true", help="box and lid only")
    ap.add_argument("--report", help="write the layout, warnings and fit check as JSON here")
    ap.add_argument("--params", action="store_true", help="print the parameters, their ranges and defaults as JSON")
    a = ap.parse_args(argv)
    if a.params:
        print(json.dumps(params_json(), ensure_ascii=False, indent=2))
        return 0
    deg: dict = {}
    if a.json:
        deg.update(json.load(sys.stdin if a.json == "-" else open(a.json)))
    for kv in a.set:
        k, _, v = kv.partition("=")
        deg[k.strip()] = v.strip()
    try:
        uyari = configure(deg)
    except ParametreHatasi as e:
        if a.report:
            pathlib.Path(a.report).write_text(json.dumps({"ok": False, "kod": e.kod, "tr": e.tr, "en": e.en}, ensure_ascii=False))
        print(f"error: {e.en}", file=sys.stderr)
        return 2
    hw = pathlib.Path(a.out) if a.out else pathlib.Path(__file__).resolve().parent.parent
    parts = export(hw, assembly=not a.no_assembly)
    bb = parts["box"].val().BoundingBox()
    problems = fit_report(parts)
    print(f"box {bb.xlen:.1f} × {bb.ylen:.1f} × {bb.zlen:.1f} mm (with ears), inside {XI:.1f} × {YI:.1f} × {ZI:.1f} mm")
    print("fit: ok" if not problems else "fit:\n  " + "\n  ".join(problems))
    if a.report:
        pathlib.Path(a.report).write_text(json.dumps({
            "ok": not problems, "parametreler": {k: globals()[v["hedef"]] for k, v in PARAMETRELER.items()},
            "ic": [round(XI, 1), round(YI, 1), round(ZI, 1)],
            "dis": [round(XI + 2 * WALL, 1), round(YI + 2 * WALL, 1), round(BOX_H + LID_T, 1)],
            "kulakli": [round(bb.xlen, 1), round(bb.ylen, 1), round(bb.zlen, 1)], "kutu_h": BOX_H, "kapak_t": LID_T,
            "uyarilar": uyari, "cakisma": problems}, ensure_ascii=False))
    return 0 if not problems else 1


if __name__ == "__main__":
    sys.exit(main())
