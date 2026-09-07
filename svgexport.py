# exports the figures as theme-aware SVG.
# matplotlib bakes literal hex into the SVG, so every colour the figures use is
# swapped for a CSS custom property afterwards; the report defines those
# properties once per theme and both modes then read from the same drawing.

import re
import matplotlib

VARS={
    "#fcfcfb":"var(--viz-surface)",
    "#0b0b0b":"var(--viz-ink)",
    "#52514e":"var(--viz-ink2)",
    "#e3e2dd":"var(--viz-grid)",
    "#2a78d6":"var(--viz-series)",
    "#8a8983":"var(--viz-base)",
    "#e8f0fc":"var(--viz-band)",
    "#eb6834":"var(--viz-series2)",
    "#1baf7a":"var(--viz-series3)",
    "#4a3aa7":"var(--viz-series4)",
}

def themed(path,prefix=None):
    s=open(path).read()
    if prefix is None:
        prefix=re.sub(r"\W+","",path.rsplit("/",1)[-1].rsplit(".",1)[0])+"_"
    # three figures share one document, so every id has to be unique across them
    s=re.sub(r'\bid="([^"]+)"',lambda m:'id="%s%s"'%(prefix,m.group(1)),s)
    s=re.sub(r'url\(#([^)]+)\)',lambda m:'url(#%s%s)'%(prefix,m.group(1)),s)
    s=re.sub(r'xlink:href="#([^"]+)"',lambda m:'xlink:href="#%s%s"'%(prefix,m.group(1)),s)
    for hexv,var in VARS.items():
        s=s.replace(hexv,var).replace(hexv.upper(),var)
    # matplotlib writes the page background as a bare white rect
    s=re.sub(r'(<rect[^>]*?)style="fill: ?#ffffff','\\1style="fill: var(--viz-surface)',s)
    s=s.replace('<svg ','<svg class="viz" ',1)
    # strip the fixed pixel size so the figure scales to its container
    s=re.sub(r'(<svg class="viz"[^>]*?)width="[\d.]+pt" height="[\d.]+pt"','\\1',s,count=1)
    open(path,"w").write(s)
    return s

def setup():
    matplotlib.rcParams["svg.fonttype"]="none"
    matplotlib.rcParams["font.family"]=["Helvetica Neue","Helvetica","Arial","sans-serif"]
