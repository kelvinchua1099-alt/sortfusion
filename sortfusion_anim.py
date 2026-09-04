"""SortFusion walkthrough (Manim Community Edition).

Mirrors the four parts of sortfusion.py:
  S1Intro        overview
  S2SmartSplit   split()      - check "already sorted?" before recursing
  S3Merge        merge()      - two-pointer linear merge
  S4Hybrid       split_v2() / hybrid_sort() - run count vs threshold S

Render:  manim -pqh sortfusion_anim.py S2SmartSplit
"""

from manim import *
import numpy as np

SANS = "Helvetica Neue"
MONO = "Menlo"
BG = "#0E1117"

C_BG_IDLE, C_ST_IDLE = "#2B3A55", "#7C8DB5"
C_BG_OK, C_ST_OK = "#14532D", "#4ADE80"
C_BG_HOT, C_ST_HOT = "#4A3410", "#FBBF24"
C_BG_OUT, C_ST_OUT = "#3B1D52", "#C084FC"
C_BG_BAD, C_ST_BAD = "#4C1D24", "#F87171"

FG = "#E5E7EB"
DIM = "#9CA3AF"

DEMO = [1, 4, 6, 9, 7, 2, 8, 3]


# ---------------------------------------------------------------- primitives
def cell(value, size=0.62, bg=C_BG_IDLE, st=C_ST_IDLE):
    box = RoundedRectangle(
        corner_radius=0.09, width=size, height=size,
        fill_color=bg, fill_opacity=1.0, stroke_color=st, stroke_width=2.5,
    )
    lbl = Text(str(value), font=SANS, font_size=int(size * 38),
                color=WHITE, weight=BOLD)
    lbl.move_to(box.get_center())
    return VGroup(box, lbl)


def row(values, size=0.62, bg=C_BG_IDLE, st=C_ST_IDLE, buff=0.08):
    return VGroup(*[cell(v, size, bg, st) for v in values]).arrange(RIGHT, buff=buff)


def slot(size=0.62):
    return RoundedRectangle(
        corner_radius=0.09, width=size, height=size,
        fill_opacity=0.0, stroke_color="#374151", stroke_width=2,
    )


def paint(group, bg, st):
    """List of animations recoloring every cell of a row.

    Deliberately a plain list: wrapping these in an AnimationGroup makes Manim
    add a fresh Group of the boxes on top of the scene, which would cover the
    digits sitting inside each cell.
    """
    return [c[0].animate.set_fill(bg, opacity=1.0).set_stroke(st) for c in group]


def edge(top_mob, bottom_mob, color="#4B5563"):
    return Line(
        top_mob.get_bottom() + DOWN * 0.04,
        bottom_mob.get_top() + UP * 0.04,
        stroke_width=2, color=color,
    )


def txt(s, size=26, color=FG, **kw):
    return Text(s, font=SANS, font_size=size, color=color, **kw)


def mono(s, size=22, color=DIM, **kw):
    return Text(s, font=MONO, font_size=size, color=color, **kw)


def code_block(lines, size=22):
    """lines = [(indent_level, source, color)].

    Pango drops leading spaces, so indentation is applied by shifting each
    line right by a measured character width instead.
    """
    g = VGroup(*[mono(src, size, col) for _, src, col in lines])
    g.arrange(DOWN, buff=0.14, aligned_edge=LEFT)
    unit = mono("0000", size).width / 4
    for (indent, _, _), line in zip(lines, g):
        line.shift(RIGHT * indent * 4 * unit)
    return g


class Base(Scene):
    def setup(self):
        self.camera.background_color = BG

    def header(self, s):
        h = txt(s, 30).to_edge(UP, buff=0.38)
        self.play(FadeIn(h, shift=DOWN * 0.2), run_time=0.6)
        return h


# ------------------------------------------------------------------ S1 intro
class S1Intro(Base):
    def construct(self):
        title = Text("SortFusion", font=SANS, font_size=68, weight=BOLD, color=FG)
        sub = txt("Adaptive Merge Sort  x  Insertion Sort", 28, DIM)
        VGroup(title, sub).arrange(DOWN, buff=0.32).move_to(UP * 1.55)

        self.play(Write(title), run_time=1.1)
        self.play(FadeIn(sub, shift=UP * 0.15), run_time=0.7)
        self.wait(0.3)

        specs = [
            ("1.  Smart Split", "split()",
             "stop recursing on a half\nthat is already sorted", C_ST_OK),
            ("2.  Two-Pointer Merge", "merge()",
             "fuse two sorted runs\nin one linear pass", C_ST_OUT),
            ("3.  Threshold Switch", "hybrid_sort()",
             "run count vs S decides\nwhich sort to use", C_ST_HOT),
        ]
        cards = VGroup()
        for name, fn, desc, col in specs:
            box = RoundedRectangle(
                corner_radius=0.16, width=3.9, height=2.5,
                fill_color="#161B26", fill_opacity=1.0,
                stroke_color=col, stroke_width=2.5,
            )
            t1 = txt(name, 24, FG)
            t2 = mono(fn, 20, col)
            t3 = txt(desc, 20, DIM, line_spacing=0.75)
            body = VGroup(t1, t2, t3).arrange(DOWN, buff=0.24).move_to(box)
            cards.add(VGroup(box, body))
        cards.arrange(RIGHT, buff=0.45).move_to(DOWN * 1.25)

        arrows = VGroup(*[
            Arrow(cards[i].get_right(), cards[i + 1].get_left(),
                  buff=0.08, stroke_width=3, color="#4B5563",
                  max_tip_length_to_length_ratio=0.3)
            for i in range(2)
        ])

        self.play(LaggedStart(*[FadeIn(c, shift=UP * 0.3) for c in cards],
                              lag_ratio=0.25), run_time=1.6)
        self.play(LaggedStart(*[GrowArrow(a) for a in arrows], lag_ratio=0.3),
                  run_time=0.8)
        self.wait(1.5)
        self.play(FadeOut(VGroup(title, sub, cards, arrows)), run_time=0.7)


# ------------------------------------------------------------- S2 smart split
class S2SmartSplit(Base):
    def construct(self):
        head = self.header("1.  split(arr) - before splitting, ask: is this half already sorted?")

        r0 = row(DEMO).move_to(UP * 2.35)
        self.play(LaggedStart(*[FadeIn(c, scale=0.5) for c in r0],
                              lag_ratio=0.07), run_time=1.1)
        self.wait(0.3)

        # ---- first cut
        L = row(DEMO[:4]).move_to(np.array([-3.35, 1.02, 0]))
        R = row(DEMO[4:]).move_to(np.array([3.35, 1.02, 0]))
        cut = DashedLine(r0.get_top() + UP * 0.18, r0.get_bottom() + DOWN * 0.18,
                         color=C_ST_HOT, stroke_width=3, dash_length=0.12)
        cut.move_to([r0[3].get_right()[0] + 0.04, r0.get_center()[1], 0])
        midlbl = mono("mid = len(arr) // 2", 20).next_to(cut, RIGHT, buff=0.25).shift(UP * 0.8)

        self.play(Create(cut), FadeIn(midlbl), run_time=0.6)
        self.play(
            TransformFromCopy(r0[:4], L), TransformFromCopy(r0[4:], R),
            Create(edge(r0[:4], L)), Create(edge(r0[4:], R)),
            run_time=1.2,
        )
        self.play(FadeOut(cut), FadeOut(midlbl), run_time=0.4)

        # ---- left half: already sorted -> pruned
        self.scan(L, DEMO[:4])
        badge = VGroup(
            txt("sorted  ->  left_arranged = 1", 21, C_ST_OK),
            txt("no recursion, use it as a merge run", 20, DIM),
        ).arrange(DOWN, buff=0.12).next_to(L, DOWN, buff=0.3)
        self.play(*paint(L, C_BG_OK, C_ST_OK),
                  FadeIn(badge, shift=UP * 0.1), run_time=0.9)
        self.wait(0.6)

        # ---- right half: not sorted -> keep recursing
        bad = self.scan(R, DEMO[4:])
        self.wait(0.5)

        RL = row(DEMO[4:6]).move_to(np.array([2.05, -0.5, 0]))
        RR = row(DEMO[6:]).move_to(np.array([4.65, -0.5, 0]))
        self.play(
            TransformFromCopy(R[:2], RL), TransformFromCopy(R[2:], RR),
            Create(edge(R[:2], RL)), Create(edge(R[2:], RR)),
            FadeOut(bad),
            run_time=1.1,
        )

        note = txt("halves of length 1 are trivially sorted  ->  recursion stops", 20, C_ST_OK)
        note.next_to(VGroup(RL, RR), DOWN, buff=0.28).shift(LEFT * 1.2)
        self.play(*paint(RL, C_BG_OK, C_ST_OK), *paint(RR, C_BG_OK, C_ST_OK),
                  FadeIn(note), run_time=0.8)
        self.wait(0.7)

        # ---- merge on the way back up
        m1 = row([2, 7], bg=C_BG_OUT, st=C_ST_OUT).move_to(np.array([2.05, -1.75, 0]))
        m2 = row([3, 8], bg=C_BG_OUT, st=C_ST_OUT).move_to(np.array([4.65, -1.75, 0]))
        mlab = mono("merge()", 22, C_ST_OUT).next_to(VGroup(m1, m2), LEFT, buff=0.45)
        self.play(FadeOut(note), run_time=0.3)
        self.play(TransformFromCopy(RL, m1), TransformFromCopy(RR, m2),
                  FadeIn(mlab), run_time=1.0)

        m3 = row([2, 3, 7, 8], bg=C_BG_OUT, st=C_ST_OUT).move_to(np.array([3.35, -2.95, 0]))
        self.play(TransformFromCopy(VGroup(m1, m2), m3), run_time=1.0)
        self.wait(0.6)

        # ---- wrap up: one merge left
        self.play(FadeOut(*[m for m in self.mobjects if m is not head]), run_time=0.8)
        segA = row(DEMO[:4], bg=C_BG_OK, st=C_ST_OK)
        segB = row([2, 3, 7, 8], bg=C_BG_OK, st=C_ST_OK)
        pair = VGroup(segA, segB).arrange(RIGHT, buff=1.1).move_to(ORIGIN)
        tail = txt("two sorted runs left  ->  hand them to merge()", 26, FG)
        tail.next_to(pair, DOWN, buff=0.7)
        self.play(FadeIn(pair, shift=UP * 0.2), run_time=0.8)
        self.play(FadeIn(tail), run_time=0.5)
        self.wait(1.4)
        self.play(FadeOut(pair), FadeOut(tail), FadeOut(head), run_time=0.7)

    def scan(self, r, vals):
        """Sweep adjacent pairs. Returns the leftover caption on failure."""
        box = cap = None
        for i in range(len(vals) - 1):
            nb = SurroundingRectangle(VGroup(r[i], r[i + 1]),
                                      color=C_ST_HOT, buff=0.06, stroke_width=3)
            ok = vals[i] <= vals[i + 1]
            sym = "<" if ok else ">"
            mark = "ok" if ok else "X"
            col = C_ST_OK if ok else C_ST_BAD
            new_cap = mono(f"{vals[i]} {sym} {vals[i+1]}   {mark}", 22, col)
            new_cap.next_to(r, DOWN, buff=0.28)
            if box is None:
                self.play(Create(nb), FadeIn(new_cap), run_time=0.45)
                box, cap = nb, new_cap
            else:
                self.play(Transform(box, nb), Transform(cap, new_cap), run_time=0.4)
            if not ok:
                self.play(
                    r[i][0].animate.set_fill(C_BG_BAD).set_stroke(C_ST_BAD),
                    r[i + 1][0].animate.set_fill(C_BG_BAD).set_stroke(C_ST_BAD),
                    run_time=0.35,
                )
                stop = txt("inversion found  ->  right_arranged = 0, keep splitting",
                           20, C_ST_BAD)
                stop.next_to(cap, DOWN, buff=0.2)
                self.play(FadeIn(stop), run_time=0.5)
                self.wait(0.6)
                self.play(FadeOut(box), FadeOut(cap), run_time=0.3)
                return stop
        self.wait(0.35)
        self.play(FadeOut(box), FadeOut(cap), run_time=0.3)
        return VGroup()


# ------------------------------------------------------------------ S3 merge
class S3Merge(Base):
    def construct(self):
        self.header("2.  merge(a, b) - two pointers, always take the smaller head")

        a = [1, 4, 6, 9]
        b = [2, 3, 7, 8]
        ra = row(a, bg=C_BG_OK, st=C_ST_OK).move_to(np.array([-2.7, 1.75, 0]))
        rb = row(b, bg=C_BG_OK, st=C_ST_OK).move_to(np.array([2.7, 1.75, 0]))
        la = mono("a", 24, C_ST_OK).next_to(ra, LEFT, buff=0.3)
        lb = mono("b", 24, C_ST_OK).next_to(rb, LEFT, buff=0.3)

        out_slots = VGroup(*[slot() for _ in range(8)]).arrange(RIGHT, buff=0.08)
        out_slots.move_to(np.array([0, -2.1, 0]))
        lo = mono("new", 22, DIM).next_to(out_slots, LEFT, buff=0.3)

        self.play(FadeIn(ra), FadeIn(rb), FadeIn(la), FadeIn(lb), run_time=0.7)
        self.play(LaggedStart(*[FadeIn(s) for s in out_slots], lag_ratio=0.05),
                  FadeIn(lo), run_time=0.8)

        pi = self.pointer("i", C_ST_HOT, ra[0])
        pj = self.pointer("j", C_ST_HOT, rb[0])
        self.play(FadeIn(pi, shift=UP * 0.2), FadeIn(pj, shift=UP * 0.2), run_time=0.5)

        cap = mono("", 26).move_to(np.array([0, -0.35, 0]))
        self.add(cap)
        i = j = k = 0
        while i < len(a) and j < len(b):
            take_a = a[i] < b[j]
            src = ra[i] if take_a else rb[j]
            other = rb[j] if take_a else ra[i]
            sym = "<" if take_a else ">"
            line = mono(f"a[{i}] = {a[i]}   {sym}   b[{j}] = {b[j]}", 26, FG)
            line.move_to(np.array([0, -0.35, 0]))

            self.play(
                Transform(cap, line),
                src[0].animate.set_fill(C_BG_HOT).set_stroke(C_ST_HOT),
                other[0].animate.set_stroke(C_ST_IDLE),
                run_time=0.45,
            )

            moving = src.copy()
            self.play(
                moving.animate.move_to(out_slots[k].get_center()),
                run_time=0.55, rate_func=rate_functions.ease_in_out_sine,
            )
            self.play(
                moving[0].animate.set_fill(C_BG_OUT).set_stroke(C_ST_OUT),
                src.animate.set_opacity(0.25),
                run_time=0.3,
            )

            if take_a:
                i += 1
                nxt = (pi.animate.next_to(ra[i], DOWN, buff=0.14) if i < len(a)
                       else pi.animate.next_to(ra, RIGHT, buff=0.2).set_color(C_ST_BAD))
            else:
                j += 1
                nxt = (pj.animate.next_to(rb[j], DOWN, buff=0.14) if j < len(b)
                       else pj.animate.next_to(rb, RIGHT, buff=0.2).set_color(C_ST_BAD))
            self.play(nxt, run_time=0.3)
            k += 1

        # ---- tail append
        who, rest_row, rest_lo = (("a", ra, i) if i < len(a) else ("b", rb, j))
        tail = mono(f"other side exhausted  ->  new.extend({who}[{rest_lo}:])", 26, C_ST_OUT)
        tail.move_to(np.array([0, -0.35, 0]))
        self.play(Transform(cap, tail), run_time=0.5)

        movers = VGroup()
        anims = []
        for t, idx in enumerate(range(rest_lo, len(rest_row))):
            mv = rest_row[idx].copy()
            movers.add(mv)
            anims.append(mv.animate.move_to(out_slots[k + t].get_center()))
        self.play(*anims, run_time=0.7)
        self.play(*[m[0].animate.set_fill(C_BG_OUT).set_stroke(C_ST_OUT) for m in movers],
                  run_time=0.3)
        self.wait(0.5)

        done = txt("one linear pass  -  O(n + m)", 26, C_ST_OK)
        done.next_to(out_slots, DOWN, buff=0.5)
        self.play(FadeOut(cap), FadeIn(done, shift=UP * 0.15), run_time=0.6)
        self.wait(1.6)
        self.play(FadeOut(*self.mobjects), run_time=0.7)

    def pointer(self, name, color, target):
        tri = Triangle(fill_opacity=1, fill_color=color, stroke_width=0).scale(0.13)
        lbl = mono(name, 20, color)
        g = VGroup(tri, lbl).arrange(DOWN, buff=0.06)
        g.next_to(target, DOWN, buff=0.14)
        return g


# ----------------------------------------------------------------- S4 hybrid
class S4Hybrid(Base):
    def construct(self):
        self.header("3.  split_v2() counts the runs, hybrid_sort() picks the branch")

        r0 = row(DEMO).move_to(UP * 1.9)
        self.play(FadeIn(r0, shift=DOWN * 0.15), run_time=0.6)

        # the 5 sorted runs split_v2 bottoms out on
        groups = [(0, 4), (4, 5), (5, 6), (6, 7), (7, 8)]
        run_cols = [C_ST_OK, "#38BDF8"]
        brackets = VGroup()
        for gi, (s, e) in enumerate(groups):
            col = run_cols[gi % 2]
            br = SurroundingRectangle(r0[s:e], color=col, buff=0.05,
                                      stroke_width=3.5, corner_radius=0.1)
            num = mono(str(gi + 1), 20, col).next_to(br, DOWN, buff=0.14)
            brackets.add(VGroup(br, num))

        self.play(LaggedStart(*[Create(b[0]) for b in brackets], lag_ratio=0.25),
                  run_time=1.4)
        self.play(LaggedStart(*[FadeIn(b[1], shift=UP * 0.1) for b in brackets],
                              lag_ratio=0.15), run_time=0.7)

        count = mono("split_v2(arr)  =  5", 30, C_ST_OK)
        count.next_to(brackets, DOWN, buff=0.45)
        self.play(Write(count), run_time=0.8)
        self.wait(0.8)

        code = code_block([
            (0, "def hybrid_sort(arr, S):", FG),
            (1, "if split_v2(arr) > S:", FG),
            (2, "return insertsort(arr)", C_ST_HOT),
            (1, "else:", FG),
            (2, "return mergesort(arr)", C_ST_OUT),
        ])
        panel = RoundedRectangle(
            corner_radius=0.14,
            width=code.width + 0.7, height=code.height + 0.6,
            fill_color="#161B26", fill_opacity=1.0,
            stroke_color="#374151", stroke_width=2,
        )
        code.move_to(panel)
        block = VGroup(panel, code).move_to(np.array([-3.4, -1.6, 0]))

        self.play(FadeIn(block, shift=UP * 0.2), run_time=0.8)
        self.wait(0.4)

        verdict = None
        cur_glow = None
        for S in (8, 3):
            hit = 5 > S
            col = C_ST_HOT if hit else C_ST_OUT
            card = VGroup(
                mono(f"S = {S}", 30, FG),
                mono(f"5 > {S}   is   {hit}", 24, col),
                mono("insertsort(arr)" if hit else "mergesort(arr)", 24, col),
            ).arrange(DOWN, buff=0.24)
            ring = RoundedRectangle(
                corner_radius=0.14, width=card.width + 1.0, height=card.height + 0.7,
                fill_color="#161B26", fill_opacity=1.0,
                stroke_color=col, stroke_width=2.5,
            )
            card.move_to(ring)
            new = VGroup(ring, card).move_to(np.array([3.3, -1.6, 0]))
            glow = SurroundingRectangle(code[2 if hit else 4], buff=0.05,
                                        color=col, stroke_width=3)
            if verdict is None:
                self.play(FadeIn(new, shift=UP * 0.2), Create(glow), run_time=0.9)
                verdict, cur_glow = new, glow
            else:
                self.play(Transform(verdict, new), Transform(cur_glow, glow), run_time=0.9)
            self.wait(1.7)

        self.play(FadeOut(*self.mobjects), run_time=0.8)
        end = txt("SortFusion  =  run-aware merging  +  a threshold that swaps the algorithm",
                  26, FG)
        self.play(Write(end), run_time=1.6)
        self.wait(1.6)
        self.play(FadeOut(end), run_time=0.8)
