# SortFusion

A hybrid sorting algorithm that combines an **adaptive merge sort** with **insertion sort**,
plus a [Manim](https://www.manim.community/) walkthrough of how it works.

## The algorithm

[`sortfusion.py`](sortfusion.py)

| Function | What it does |
| --- | --- |
| `merge(a, b)` | Classic two-pointer merge of two sorted lists, with a tail `extend` when one side runs out. |
| `split(arr)` | Merge sort that checks each half before recursing. A half that is already sorted becomes a merge run directly instead of being split further. |
| `split_v2(arr)` | Same recursion, but returns the *number* of sorted runs it bottoms out on instead of the sorted list. |
| `insertsort(arr)` | Insertion sort. |
| `hybrid_sort(arr, S)` | Runs `insertsort` when `split_v2(arr) > S`, otherwise `mergesort`. |

Because `split` stops recursing on an already-sorted half, the recursion tree adapts to
how ordered the input is. On `[1, 4, 6, 9, 7, 2, 8, 3]` the left half `[1, 4, 6, 9]` is
already sorted and is never split, while the right half recurses all the way down:

```
                [1 4 6 9 7 2 8 3]
                /               \
       [1 4 6 9] (sorted)     [7 2 8 3]
                              /       \
                          [7 2]      [8 3]
```

`split_v2` on that array returns `5` — one run for `[1, 4, 6, 9]` and four singletons.

## The animation

[`sortfusion_anim.py`](sortfusion_anim.py) contains four Manim Community scenes:

| Scene | Covers |
| --- | --- |
| `S1Intro` | Title card and the three-step pipeline. |
| `S2SmartSplit` | `split()` — the adjacent-pair scan, the pruned left half, the inversion found at `7 > 2`, and merging on the way back up. |
| `S3Merge` | `merge()` — the `i` / `j` pointers step by step, including the tail `new.extend(a[3:])`. |
| `S4Hybrid` | `split_v2()` counting the five runs, and `hybrid_sort()` picking a branch for `S = 8` versus `S = 3`. |

Every value shown on screen is the real output of the code in `sortfusion.py`.

### Rendering

```bash
pip install -r requirements.txt

# one scene, preview quality
manim -pql sortfusion_anim.py S2SmartSplit

# all four at 1080p60
for S in S1Intro S2SmartSplit S3Merge S4Hybrid; do
  manim -qh sortfusion_anim.py $S
done
```

Rendered files land in `media/` and are gitignored.

Manim needs [Cairo, Pango and FFmpeg](https://docs.manim.community/en/stable/installation.html)
on the system. The scenes use `Helvetica Neue` and `Menlo`; on Linux or Windows, change
`SANS` and `MONO` at the top of `sortfusion_anim.py` to fonts you have installed.

## Note on the threshold

`hybrid_sort` currently switches to insertion sort when the run count is *above* `S`. A high
run count means the input is more disordered, which is where the O(n²) insertion sort is
weakest — so the comparison may be the wrong way round. It is left as written here; the
animation shows the rule as implemented.
