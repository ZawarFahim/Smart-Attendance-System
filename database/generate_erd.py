#!/usr/bin/env python3
"""
Attendify – ERD PDF Generator
Run:   python database/generate_erd.py
Output: database/erd_diagram.pdf
"""

import os
from reportlab.pdfgen import canvas
from reportlab.lib import colors
from reportlab.lib.pagesizes import A4

# ─── Output path ──────────────────────────────────────────────────────────────
OUTPUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "erd_diagram.pdf")

# ─── Custom page (large landscape for the diagram) ───────────────────────────
PW, PH = 2400, 1660          # Points  (~84 cm × 58 cm)

# ─── Box geometry ─────────────────────────────────────────────────────────────
BOX_W    = 258
HEADER_H = 26
ATTR_H   = 19
PAD      = 8

# ─── Colour palette ──────────────────────────────────────────────────────────
C_CORE   = colors.HexColor("#1565C0")   # Users, Departments
C_PEOPLE = colors.HexColor("#2E7D32")   # Students, Faculty
C_ACAD   = colors.HexColor("#6A1B9A")   # Courses, Rooms
C_SECT   = colors.HexColor("#4527A0")   # Sections, Enrollments
C_ATTN   = colors.HexColor("#B71C1C")   # All attendance tables
C_SCHED  = colors.HexColor("#E65100")   # Timetable
C_SYS    = colors.HexColor("#37474F")   # Leave / Notifications / Audit

WHITE    = colors.white
ODD_BG   = colors.HexColor("#F5F5F5")
EVEN_BG  = colors.HexColor("#FFFFFF")
BORDER   = colors.HexColor("#BDBDBD")
BG_PAGE  = colors.HexColor("#F8F9FA")

PK_CLR   = colors.HexColor("#C62828")
FK_CLR   = colors.HexColor("#1565C0")
PKFK_CLR = colors.HexColor("#6A1B9A")
TYPE_CLR = colors.HexColor("#757575")
NAME_CLR = colors.HexColor("#212121")
REL_CLR  = colors.HexColor("#90A4AE")
LBL_CLR  = colors.HexColor("#37474F")

# ─── Entity definitions ───────────────────────────────────────────────────────
# attr tuple: (column_name, data_type, key)   key ∈ {"PK","FK","PK,FK",""}
ENTITIES = {
    "Users": {
        "color": C_CORE,
        "attrs": [
            ("user_id",       "SERIAL",       "PK"),
            ("username",      "VARCHAR(50)",   ""),
            ("email",         "VARCHAR(100)",  ""),
            ("password_hash", "VARCHAR(255)",  ""),
            ("role",          "VARCHAR(20)",   ""),
            ("created_at",    "TIMESTAMP",     ""),
        ],
    },
    "Departments": {
        "color": C_CORE,
        "attrs": [
            ("dept_id",   "SERIAL",       "PK"),
            ("dept_name", "VARCHAR(100)", ""),
        ],
    },
    "Students": {
        "color": C_PEOPLE,
        "attrs": [
            ("student_id",      "INTEGER",     "PK,FK"),
            ("first_name",      "VARCHAR(50)", ""),
            ("last_name",       "VARCHAR(50)", ""),
            ("enrollment_date", "DATE",        ""),
            ("dept_id",         "INTEGER",     "FK"),
        ],
    },
    "Faculty": {
        "color": C_PEOPLE,
        "attrs": [
            ("faculty_id",  "INTEGER",     "PK,FK"),
            ("first_name",  "VARCHAR(50)", ""),
            ("last_name",   "VARCHAR(50)", ""),
            ("hire_date",   "DATE",        ""),
            ("dept_id",     "INTEGER",     "FK"),
        ],
    },
    "Courses": {
        "color": C_ACAD,
        "attrs": [
            ("course_id",   "SERIAL",       "PK"),
            ("course_code", "VARCHAR(20)",   ""),
            ("course_name", "VARCHAR(100)",  ""),
            ("credits",     "INTEGER",       ""),
            ("dept_id",     "INTEGER",       "FK"),
        ],
    },
    "Rooms": {
        "color": C_ACAD,
        "attrs": [
            ("room_id",   "SERIAL",      "PK"),
            ("room_name", "VARCHAR(50)", ""),
            ("capacity",  "INTEGER",     ""),
        ],
    },
    "Sections": {
        "color": C_SECT,
        "attrs": [
            ("section_id",    "SERIAL",      "PK"),
            ("course_id",     "INTEGER",     "FK"),
            ("faculty_id",    "INTEGER",     "FK"),
            ("room_id",       "INTEGER",     "FK"),
            ("semester",      "VARCHAR(20)", ""),
            ("academic_year", "VARCHAR(10)", ""),
        ],
    },
    "Enrollments": {
        "color": C_SECT,
        "attrs": [
            ("enrollment_id", "SERIAL",  "PK"),
            ("student_id",    "INTEGER", "FK"),
            ("section_id",    "INTEGER", "FK"),
            ("enrolled_date", "DATE",    ""),
        ],
    },
    "AttendanceStatus": {
        "color": C_ATTN,
        "attrs": [
            ("status_id",   "SERIAL",      "PK"),
            ("status_name", "VARCHAR(20)", ""),
        ],
    },
    "AttendanceSessions": {
        "color": C_ATTN,
        "attrs": [
            ("session_id",   "SERIAL",  "PK"),
            ("section_id",   "INTEGER", "FK"),
            ("session_date", "DATE",    ""),
            ("start_time",   "TIME",    ""),
            ("end_time",     "TIME",    ""),
            ("created_by",   "INTEGER", "FK"),
        ],
    },
    "StudentAttendance": {
        "color": C_ATTN,
        "attrs": [
            ("attendance_id", "SERIAL",       "PK"),
            ("session_id",    "INTEGER",      "FK"),
            ("student_id",    "INTEGER",      "FK"),
            ("status_id",     "INTEGER",      "FK"),
            ("remarks",       "VARCHAR(255)", ""),
        ],
    },
    "FacultyAttendance": {
        "color": C_ATTN,
        "attrs": [
            ("faculty_attendance_id", "SERIAL",  "PK"),
            ("faculty_id",            "INTEGER", "FK"),
            ("date",                  "DATE",    ""),
            ("status_id",             "INTEGER", "FK"),
        ],
    },
    "Timetable": {
        "color": C_SCHED,
        "attrs": [
            ("timetable_id", "SERIAL",      "PK"),
            ("section_id",   "INTEGER",     "FK"),
            ("day_of_week",  "VARCHAR(15)", ""),
            ("start_time",   "TIME",        ""),
            ("end_time",     "TIME",        ""),
            ("room_id",      "INTEGER",     "FK"),
        ],
    },
    "LeaveRequests": {
        "color": C_SYS,
        "attrs": [
            ("leave_id",    "SERIAL",      "PK"),
            ("user_id",     "INTEGER",     "FK"),
            ("start_date",  "DATE",        ""),
            ("end_date",    "DATE",        ""),
            ("reason",      "TEXT",        ""),
            ("status",      "VARCHAR(20)", ""),
            ("reviewed_by", "INTEGER",     "FK"),
            ("created_at",  "TIMESTAMP",   ""),
        ],
    },
    "Notifications": {
        "color": C_SYS,
        "attrs": [
            ("notification_id", "SERIAL",    "PK"),
            ("user_id",         "INTEGER",   "FK"),
            ("message",         "TEXT",      ""),
            ("is_read",         "BOOLEAN",   ""),
            ("created_at",      "TIMESTAMP", ""),
        ],
    },
    "AuditLogs": {
        "color": C_SYS,
        "attrs": [
            ("log_id",     "SERIAL",      "PK"),
            ("user_id",    "INTEGER",     "FK"),
            ("action",     "VARCHAR(50)", ""),
            ("table_name", "VARCHAR(50)", ""),
            ("record_id",  "INTEGER",     ""),
            ("timestamp",  "TIMESTAMP",   ""),
        ],
    },
}

# ─── Layout: (x_left, y_top)  in top-down coords (y=0 at page top) ───────────
#  Row 1 y=80   Row 2 y=310   Row 3 y=520   Row 4 y=740
POSITIONS = {
    # Row 1 ─ core / academic / rooms
    "LeaveRequests":      ( 30,  80),
    "Users":              (325,  80),
    "Departments":        (620,  80),
    "Courses":            (915,  80),
    "Rooms":              (1210, 80),

    # Row 2 ─ people / sections / scheduling / faculty attendance
    "Notifications":      ( 30,  318),
    "Students":           (325,  318),
    "Faculty":            (620,  318),
    "Sections":           (915,  318),
    "Timetable":          (1210, 318),
    "FacultyAttendance":  (1505, 318),

    # Row 3 ─ audit / enrollments / sessions / status
    "AuditLogs":          ( 30,  534),
    "Enrollments":        (325,  534),
    "AttendanceSessions": (915,  534),
    "AttendanceStatus":   (1505, 534),

    # Row 4 ─ student attendance (central)
    "StudentAttendance":  (620,  753),
}

# ─── Relationships: (from, to, from_card, to_card, label) ────────────────────
RELATIONSHIPS = [
    ("Users",              "Students",           "1", "N", "is a"),
    ("Users",              "Faculty",            "1", "N", "is a"),
    ("Departments",        "Students",           "1", "N", "has"),
    ("Departments",        "Faculty",            "1", "N", "has"),
    ("Departments",        "Courses",            "1", "N", "offers"),
    ("Courses",            "Sections",           "1", "N", "has"),
    ("Faculty",            "Sections",           "1", "N", "teaches"),
    ("Rooms",              "Sections",           "1", "N", "hosts"),
    ("Students",           "Enrollments",        "1", "N", "enrolled"),
    ("Sections",           "Enrollments",        "1", "N", "has"),
    ("Sections",           "AttendanceSessions", "1", "N", "holds"),
    ("Faculty",            "AttendanceSessions", "1", "N", "creates"),
    ("AttendanceSessions", "StudentAttendance",  "1", "N", "records"),
    ("Students",           "StudentAttendance",  "1", "N", "tracked"),
    ("AttendanceStatus",   "StudentAttendance",  "1", "N", "status"),
    ("Faculty",            "FacultyAttendance",  "1", "N", "tracked"),
    ("AttendanceStatus",   "FacultyAttendance",  "1", "N", "status"),
    ("Sections",           "Timetable",          "1", "N", "scheduled"),
    ("Rooms",              "Timetable",          "1", "N", "used in"),
    ("Users",              "LeaveRequests",      "1", "N", "submits"),
    ("Users",              "Notifications",      "1", "N", "receives"),
    ("Users",              "AuditLogs",          "1", "N", "generates"),
]

# ─── Helpers ──────────────────────────────────────────────────────────────────
def box_h(name):
    """Total height of an entity box (points)."""
    return HEADER_H + len(ENTITIES[name]["attrs"]) * ATTR_H + PAD


def get_cp(name):
    """Return connection-point dict in ReportLab coordinates (y from bottom)."""
    x, yt = POSITIONS[name]
    h = box_h(name)
    rl_top = PH - yt
    rl_bot = rl_top - h
    cx = x + BOX_W / 2
    cy = (rl_top + rl_bot) / 2
    return {
        "left":   (x,           cy),
        "right":  (x + BOX_W,   cy),
        "top":    (cx,           rl_top),
        "bottom": (cx,           rl_bot),
    }


def pick_sides(fn, tn):
    """Choose which sides to connect based on relative entity positions."""
    fx, fy = POSITIONS[fn]
    tx, ty = POSITIONS[tn]
    fx_c = fx + BOX_W / 2
    tx_c = tx + BOX_W / 2
    fy_c = fy + box_h(fn) / 2
    ty_c = ty + box_h(tn) / 2
    dx = tx_c - fx_c
    dy = ty_c - fy_c       # positive → tn is lower on the page
    if abs(dx) >= abs(dy):
        return ("right", "left") if dx > 0 else ("left", "right")
    else:
        return ("bottom", "top") if dy > 0 else ("top", "bottom")


# ─── Drawing functions ────────────────────────────────────────────────────────
def draw_entity(cv, name):
    ent = ENTITIES[name]
    x, yt = POSITIONS[name]
    h = box_h(name)
    rl_top = PH - yt
    col = ent["color"]
    attrs = ent["attrs"]

    # Drop shadow
    cv.setFillColor(colors.HexColor("#D0D0D0"))
    cv.rect(x + 3, rl_top - h - 3, BOX_W, h, fill=1, stroke=0)

    # ── Header ──
    cv.setFillColor(col)
    cv.rect(x, rl_top - HEADER_H, BOX_W, HEADER_H, fill=1, stroke=0)
    cv.setFillColor(WHITE)
    cv.setFont("Helvetica-Bold", 10)
    cv.drawCentredString(x + BOX_W / 2, rl_top - HEADER_H + 8, name)

    # ── Attributes ──
    for i, (aname, atype, key) in enumerate(attrs):
        ay = rl_top - HEADER_H - (i + 1) * ATTR_H
        bg = ODD_BG if i % 2 == 0 else EVEN_BG
        cv.setFillColor(bg)
        cv.setStrokeColor(BORDER)
        cv.setLineWidth(0.4)
        cv.rect(x, ay, BOX_W, ATTR_H, fill=1, stroke=1)

        # Key badge
        bx = x + 3
        if "PK" in key and "FK" in key:
            cv.setFillColor(PKFK_CLR)
            cv.setFont("Helvetica-Bold", 5.5)
            cv.drawString(bx, ay + 8.5, "PK")
            cv.drawString(bx, ay + 2.5, "FK")
        elif "PK" in key:
            cv.setFillColor(PK_CLR)
            cv.setFont("Helvetica-Bold", 6)
            cv.drawString(bx, ay + 5.5, "PK")
        elif "FK" in key:
            cv.setFillColor(FK_CLR)
            cv.setFont("Helvetica-Bold", 6)
            cv.drawString(bx, ay + 5.5, "FK")

        # Attribute name
        cv.setFillColor(NAME_CLR)
        cv.setFont("Helvetica-Bold" if "PK" in key else "Helvetica", 8)
        cv.drawString(x + 27, ay + 5.5, aname)

        # Underline for PK
        if "PK" in key:
            tw = cv.stringWidth(aname, "Helvetica-Bold", 8)
            cv.setStrokeColor(PK_CLR)
            cv.setLineWidth(0.5)
            cv.line(x + 27, ay + 4, x + 27 + tw, ay + 4)

        # Data type  (right-aligned, italic grey)
        cv.setFillColor(TYPE_CLR)
        cv.setFont("Helvetica-Oblique", 6.5)
        cv.drawRightString(x + BOX_W - 4, ay + 5.5, atype)

    # ── Outer border ──
    cv.setStrokeColor(col)
    cv.setLineWidth(1.6)
    cv.setFillColor(colors.transparent)
    cv.rect(x, rl_top - h, BOX_W, h, fill=0, stroke=1)


def draw_relationship(cv, fn, tn, fc, tc, label):
    cp_f = get_cp(fn)
    cp_t = get_cp(tn)
    fs, ts = pick_sides(fn, tn)
    p1 = cp_f[fs]
    p2 = cp_t[ts]

    # Line
    cv.setStrokeColor(REL_CLR)
    cv.setLineWidth(1.0)
    cv.line(p1[0], p1[1], p2[0], p2[1])

    # Midpoint label
    mx = (p1[0] + p2[0]) / 2
    my = (p1[1] + p2[1]) / 2
    lw = cv.stringWidth(label, "Helvetica", 6.5) + 4
    cv.setFillColor(BG_PAGE)
    cv.rect(mx - lw / 2, my - 1, lw, 9, fill=1, stroke=0)
    cv.setFillColor(LBL_CLR)
    cv.setFont("Helvetica", 6.5)
    cv.drawCentredString(mx, my + 1.5, label)

    # Cardinality near p1 (1 side)
    cv.setFont("Helvetica-Bold", 8)
    off = {"right": (6, 3), "left": (-14, 3), "bottom": (3, -10), "top": (3, 4)}
    ox, oy = off[fs]
    cv.setFillColor(PK_CLR)
    cv.drawString(p1[0] + ox, p1[1] + oy, fc)

    # Cardinality near p2 (N side)
    ox2, oy2 = off[ts]
    cv.setFillColor(FK_CLR)
    cv.drawString(p2[0] + ox2, p2[1] + oy2, tc)


def draw_legend(cv):
    lx = 1820
    ly_top = PH - 80          # ReportLab y for legend top

    # Box
    cv.setFillColor(colors.HexColor("#ECEFF1"))
    cv.setStrokeColor(colors.HexColor("#B0BEC5"))
    cv.setLineWidth(0.8)
    cv.rect(lx - 8, ly_top - 300, 260, 298, fill=1, stroke=1)

    y = ly_top - 14
    cv.setFont("Helvetica-Bold", 9)
    cv.setFillColor(NAME_CLR)
    cv.drawString(lx, y, "LEGEND")
    y -= 14

    # Entity groups
    groups = [
        ("Core / Identity",            C_CORE),
        ("People (Student, Faculty)",   C_PEOPLE),
        ("Academic (Courses, Rooms)",   C_ACAD),
        ("Sections / Enrollments",      C_SECT),
        ("Attendance",                  C_ATTN),
        ("Scheduling (Timetable)",      C_SCHED),
        ("System (Leave/Notif/Audit)",  C_SYS),
    ]
    cv.setFont("Helvetica-Bold", 7.5)
    cv.setFillColor(NAME_CLR)
    cv.drawString(lx, y, "Entity Groups")
    y -= 11
    for grp_lbl, grp_col in groups:
        cv.setFillColor(grp_col)
        cv.rect(lx, y - 7, 11, 10, fill=1, stroke=0)
        cv.setFillColor(NAME_CLR)
        cv.setFont("Helvetica", 7)
        cv.drawString(lx + 14, y - 4, grp_lbl)
        y -= 13

    y -= 4
    cv.setFont("Helvetica-Bold", 7.5)
    cv.setFillColor(NAME_CLR)
    cv.drawString(lx, y, "Key Types")
    y -= 11
    for badge, clr, desc in [
        ("PK",    PK_CLR,   "Primary Key  (underlined)"),
        ("FK",    FK_CLR,   "Foreign Key"),
        ("PK/FK", PKFK_CLR, "Primary + Foreign Key"),
    ]:
        cv.setFillColor(clr)
        cv.setFont("Helvetica-Bold", 7)
        cv.drawString(lx, y - 2, badge)
        cv.setFillColor(NAME_CLR)
        cv.setFont("Helvetica", 7)
        cv.drawString(lx + 28, y - 2, desc)
        y -= 12

    y -= 4
    cv.setFont("Helvetica-Bold", 7.5)
    cv.setFillColor(NAME_CLR)
    cv.drawString(lx, y, "Cardinality")
    y -= 11
    cv.setFillColor(PK_CLR)
    cv.setFont("Helvetica-Bold", 8)
    cv.drawString(lx, y - 2, "1")
    cv.setFillColor(NAME_CLR)
    cv.setFont("Helvetica", 7)
    cv.drawString(lx + 12, y - 2, "One (origin side)")
    y -= 12
    cv.setFillColor(FK_CLR)
    cv.setFont("Helvetica-Bold", 8)
    cv.drawString(lx, y - 2, "N")
    cv.setFillColor(NAME_CLR)
    cv.setFont("Helvetica", 7)
    cv.drawString(lx + 12, y - 2, "Many (target side)")


# ─── Main ─────────────────────────────────────────────────────────────────────
def main():
    cv = canvas.Canvas(OUTPUT, pagesize=(PW, PH))
    cv.setTitle("Attendify – Entity Relationship Diagram")
    cv.setAuthor("Attendify Smart Attendance System")
    cv.setSubject("ERD – PostgreSQL Database Schema")

    # Page background
    cv.setFillColor(BG_PAGE)
    cv.rect(0, 0, PW, PH, fill=1, stroke=0)

    # ── Title bar ──────────────────────────────────────────────────────────────
    cv.setFillColor(C_CORE)
    cv.rect(0, PH - 58, PW, 58, fill=1, stroke=0)
    # Accent strip
    cv.setFillColor(colors.HexColor("#0D47A1"))
    cv.rect(0, PH - 58, 8, 58, fill=1, stroke=0)

    cv.setFillColor(WHITE)
    cv.setFont("Helvetica-Bold", 22)
    cv.drawString(26, PH - 37, "ATTENDIFY  –  Smart Attendance System")
    cv.setFont("Helvetica", 10)
    cv.drawString(26, PH - 52, "Entity Relationship Diagram  |  PostgreSQL  |  16 Tables  |  22 Relationships")

    cv.setFont("Helvetica", 9)
    cv.setFillColor(colors.HexColor("#BBDEFB"))
    cv.drawRightString(PW - 20, PH - 37, "database/schema.sql")

    # ── Draw relationships (behind entities) ──────────────────────────────────
    for fn, tn, fc, tc, lbl in RELATIONSHIPS:
        draw_relationship(cv, fn, tn, fc, tc, lbl)

    # ── Draw entities ─────────────────────────────────────────────────────────
    for name in ENTITIES:
        draw_entity(cv, name)

    # ── Legend ────────────────────────────────────────────────────────────────
    draw_legend(cv)

    # ── Footer ────────────────────────────────────────────────────────────────
    cv.setFillColor(colors.HexColor("#E8EAF6"))
    cv.rect(0, 0, PW, 22, fill=1, stroke=0)
    cv.setFillColor(colors.HexColor("#3949AB"))
    cv.setFont("Helvetica", 7.5)
    cv.drawString(20, 7, "Attendify Smart Attendance Management System  ·  Generated from schema.sql")
    cv.drawRightString(PW - 20, 7,
        "16 Tables  |  22 Relationships  |  70+ Attributes  |  3 User Roles")

    cv.save()
    print(f"[OK] ERD PDF saved: {OUTPUT}")


if __name__ == "__main__":
    main()
