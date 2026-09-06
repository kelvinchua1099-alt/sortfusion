# SortFusion

A hybrid sorting algorithm that combines an **adaptive merge sort** with **insertion sort**,
plus a [Manim](https://www.manim.community/) walkthrough of how it works.

## The adaptive variant

[`sortfusion.py`](sortfusion.py) — an exploratory run-detecting sort, kept separate
from the assignment's hybrid in [`hybrid.py`](hybrid.py). Its `S` thresholds the
*number of sorted runs*, not the subarray size.

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

## Project 1 parts

| Part | File | Status |
| --- | --- | --- |
| (a) hybrid algorithm | [`hybrid.py`](hybrid.py) | done |
| (b) input data | [`datagen.py`](datagen.py) | done |
| (c) comparison counts and plots | [`bench.py`](bench.py), [`plots.py`](plots.py) | (c)(ii) done, (c)(i) and (c)(iii) pending |
| (d) comparison against original merge sort | [`bench.py`](bench.py) | measurements done, write-up pending |

### (a) `hybrid.py`

`hybrid(arr, S)` is merge sort that hands a subarray to insertion sort as soon as
its length is `<= S`. The switch happens inside the recursion, independently on
every branch. `mergesort(arr)` is the plain textbook version kept as the baseline
for part (d), and `insertsort(arr)` is a standalone insertion sort.

All three return `(sorted_list, key_comparisons)`. A key comparison is one
comparison between two array elements; loop bounds such as `j >= 0` and the
`len(arr) <= S` size test are not counted.

Running the file executes its self-checks: all three sorts agree with `sorted()`,
`hybrid(arr, 1)` reports exactly the same comparison count as `mergesort(arr)`,
and insertion sort is confirmed adaptive (999 comparisons on a sorted array of
1000, 499500 on a reversed one).

### (b) `datagen.py`

`generate(n, seed, x)` returns `n` random integers in `[1, x]`, with `x` defaulting
to `MAXVALUE = 10_000_000`. `SIZES` is the size ladder from 1,000 to 10,000,000 in
a 1-2-5 progression, which spreads evenly on the log axes part (c) needs.

Arrays are rebuilt from the seed rather than stored, so a run is reproducible from
one integer instead of a few hundred megabytes of data files. numpy is used when
present because it is roughly 3x faster; the pure-stdlib fallback produces a
different but equally valid array.

For a fixed seed the smaller arrays are prefixes of the larger ones. That is
deliberate: it isolates the effect of `n` in part (c)(i) instead of mixing it with
sampling noise. Pass a different `seed` per repetition when averaging.

At n = 10 million a sort takes roughly 20 seconds and peaks around 0.65 GB.

### Timing — `bench.py`

`python3 bench.py` sweeps the full size ladder and then sweeps `S` at n = 1,000,000;
`python3 bench.py quick` stops at n = 200,000 and sweeps `S` at n = 100,000.

CPU time comes from `time.process_time()`, which is what part (d) asks for.
`time.perf_counter()` wall time is recorded alongside it so a run disturbed by other
activity on the machine can be spotted. Small inputs are timed several times and the
fastest run is kept; inputs above 200,000 are timed once because they are slow enough
that startup noise does not matter.

### Figures - `plots.py`

`python3 plots.py` reads `results/S_sweep_n1000000.csv` and writes the matching PNG.

Comparison counts and CPU times are on unrelated scales, so they get one panel each
rather than a twin y-axis, which would invite reading a crossover that is only an
artefact of where the two scales were pinned.

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
