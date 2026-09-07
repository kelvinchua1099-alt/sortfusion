# assembles report.html from report_body.html and the themed SVG figures

FIGS={
    "{{FIG_OVER_N}}":"results/fig_over_n.svg",
    "{{FIG_S_SWEEP}}":"results/fig_S_sweep.svg",
    "{{FIG_OPTIMAL}}":"results/fig_optimal_S.svg",
}

def build(src="report_body.html",out="report.html"):
    s=open(src).read()
    for token,path in FIGS.items():
        svg=open(path).read()
        i=svg.index("<svg")
        s=s.replace(token,svg[i:])
    open(out,"w").write(s)
    return s

if __name__=="__main__":
    s=build()
    print("report.html: %.0f KB"%(len(s)/1024))
    for t in FIGS:
        assert t not in s, "unsubstituted "+t
    print("all figures substituted, %d <svg> blocks"%s.count("<svg"))
