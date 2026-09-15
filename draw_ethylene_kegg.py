import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
from matplotlib.patches import FancyBboxPatch
import numpy as np
import pandas as pd
import os, warnings
warnings.filterwarnings("ignore")

OUTDIR = "go-enrichment-assets"
up = pd.read_csv(f"{OUTDIR}/RNAseq_Oui_ethylene_upstream_genelist.csv")
gl = pd.read_csv(f"{OUTDIR}/RNAseq_Oui_ethylene_pathway_genelist.csv")

SU = "#ef4444"; UP = "#fca5a5"; NS = "#e2e8f0"
SD = "#3b82f6"; DN = "#93c5fd"; ND = "#f8fafc"; TX = "#1e293b"

def gc(l, p, s):
    if pd.isna(l) or pd.isna(p): return ND, "#94a3b8"
    if s: return (SU, "white") if l > 0 else (SD, "white")
    return (UP, "#dc2626") if l > 0 else (DN, "#2563eb")

def gr(r):
    """Return (Dh_log2FC, Dh_padj, Dh_sig, Pt_log2FC, Pt_padj, Pt_sig)"""
    # upstream CSV has no sig column; compute from padj
    dh_sig = r["Dharia_padj"] < 0.01 if pd.notna(r["Dharia_padj"]) else False
    pt_sig = r["PTT1_padj"] < 0.01 if pd.notna(r["PTT1_padj"]) else False
    return (r["Dharia_log2FC"], r["Dharia_padj"], dh_sig,
            r["PTT1_log2FC"],   r["PTT1_padj"],   pt_sig)

def gt(df, s):
    """Find row matching symbol s. Try symbol column first, then locus/gene_id."""
    r2 = df[df["symbol"] == s]
    if r2.empty:
        # upstream uses 'locus', genelist uses 'gene_id'
        if "locus" in df.columns:
            r2 = df[df["locus"] == s]
        elif "gene_id" in df.columns:
            r2 = df[df["gene_id"] == s]
    return r2.iloc[0] if not r2.empty else None

fig, ax = plt.subplots(1, 1, figsize=(14, 24))
ax.set_xlim(0, 14); ax.set_ylim(0, 30); ax.axis("off")
XC = 7.0; BW = 4.0; BH = 1.5



def dsb(ax, y, label, genes):
    n = len(genes); h = BH * n + 0.25 * (n - 1); x0 = XC - BW / 2
    bg = FancyBboxPatch((x0-0.1, y-0.1), BW+0.2, h+0.2, boxstyle='round,pad=0.05', ec='#d1d5db', fc='white', lw=1)
    ax.add_patch(bg)
    ax.text(XC, y+h+0.2, label, ha='center', va='bottom', fontsize=11, fontweight='bold', color='#475569')
    for i, (name, *vals) in enumerate(genes):
        dfc, dp, ds, pfc, pp, ps = vals; yi = y + (n-1-i) * (BH + 0.25)
        fc, tc = gc(dfc, dp, ds)
        rd = FancyBboxPatch((x0, yi), BW/2-0.03, BH, boxstyle='round,pad=0.04', ec='#cbd5e1' if tc!='white' else '#d1d5db', fc=fc, lw=0.8)
        ax.add_patch(rd)
        fc2, tc2 = gc(pfc, pp, ps)
        rp = FancyBboxPatch((x0+BW/2+0.03, yi), BW/2-0.03, BH, boxstyle='round,pad=0.04', ec='#cbd5e1' if tc2!='white' else '#d1d5db', fc=fc2, lw=0.8)
        ax.add_patch(rp)
        ax.text(x0-0.15, yi+BH/2, name, ha='right', va='center', fontsize=8, fontweight='bold', color=TX)
        ax.text(x0+BW/4, yi+BH/2+0.4, 'Dh', ha='center', va='center', fontsize=5.5, color='#94a3b8')
        ax.text(x0+BW/4, yi+BH/2-0.35, (f'{dfc:+.2f}' if pd.notna(dfc) else '\u2014'), ha='center', va='center', fontsize=9, fontweight='bold', color=tc)
        ax.text(x0+3*BW/4, yi+BH/2+0.4, 'Pt', ha='center', va='center', fontsize=5.5, color='#94a3b8')
        ax.text(x0+3*BW/4, yi+BH/2-0.35, (f'{pfc:+.2f}' if pd.notna(pfc) else '\u2014'), ha='center', va='center', fontsize=9, fontweight='bold', color=tc2)
    return y + h + 0.1

def dar(ax, y1, y2):
    ax.annotate('', xy=(XC, y2), xytext=(XC, y1), arrowprops=dict(arrowstyle='->', color='#64748b', lw=1.8, shrinkA=0, shrinkB=0))

def din(ax, y1, y2):
    ax.annotate('', xy=(XC, y2+0.1), xytext=(XC, y1-0.1), arrowprops=dict(arrowstyle='-|>', color='#64748b', lw=1.8, shrinkA=0, shrinkB=0))

# === DRAW CASCADE ===
Y = 27.0

ax.text(XC, Y, "ETHYLENE (C\u2082H\u2084)", ha="center", va="center",
        fontsize=12, fontweight="bold", color="#0ea5e9",
        bbox=dict(boxstyle="round,pad=0.4", fc="#e0f2fe", ec="#38bdf8", lw=1.5))
Y -= 1.8; dar(ax, Y+0.1, Y-0.5)

recs = []
for s in ["ERS1", "ETR2", "ETR3", "ETR4"]:
    r = gt(up, s)
    recs.append((s, *gr(r)) if r is not None else (s, np.nan, np.nan, False, np.nan, np.nan, False))
Y = dsb(ax, Y-2.0, "Ethylene Receptors (ETR/ERS)", recs); Y -= 0.3; din(ax, Y, Y-0.5)

ctrs = []
for s in ["OsCTR2", "Os08g0103000", "Os09g0566550"]:
    r = gt(up, s)
    lbl = s if s == "OsCTR2" else f"CTR1-like ({s[-4:]})"
    ctrs.append((lbl, *gr(r)) if r is not None else (lbl, np.nan, np.nan, False, np.nan, np.nan, False))
Y = dsb(ax, Y-2.0, "CTR1-like Kinases (Negative Regulators)", ctrs); Y -= 0.3; din(ax, Y, Y-0.5)

r = gt(gl, "EIN2")
if r is None:
    r = gt(gl, "Os07g0155600")
e2 = [("EIN2", *gr(r))] if r is not None else [("EIN2", np.nan, np.nan, False, np.nan, np.nan, False)]
Y = dsb(ax, Y-1.5, "EIN2 (Central Signal Transducer)", e2); Y -= 0.3; dar(ax, Y, Y-0.5)

r = gt(up, "EIL1/EIN3")
e3 = [("EIN3/EIL1 (Master TF)", *gr(r))] if r is not None else []
Y = dsb(ax, Y-1.5, "EIN3/EIL1 (Master Transcription Factor)", e3); Y -= 0.3; dar(ax, Y, Y-0.5)

fb = []
lbl_map = {"OsEBF1": "OsEBF1 (F-box)", "OsEBF2": "OsEBF2 (F-box)",
            "OsETOL1": "OsETOL1 (E3)", "Os07g0178100": "Os07g (ETO1-like)",
            "Os11g0585900": "Os11g (ETO1-like)"}
for s in ["OsEBF1", "OsEBF2", "OsETOL1", "Os07g0178100", "Os11g0585900"]:
    r = gt(up, s)
    fb.append((lbl_map[s], *gr(r)) if r is not None else (lbl_map[s], np.nan, np.nan, False, np.nan, np.nan, False))
Y = dsb(ax, Y-1.5, "Negative Feedback: EBF1/2 + ETO1-like", fb); Y -= 0.6

ax.text(XC, Y, "ERF/EREBP Family (39 Downstream TFs)", ha="center", va="center",
        fontsize=10, fontweight="bold",
        bbox=dict(boxstyle="round,pad=0.3", fc="#f1f5f9", ec="#94a3b8", lw=1))
Y -= 0.9

gs = gl.dropna(subset=["symbol"]).copy()
gs["sn"] = gs["symbol"].str.extract(r"(\d+)", expand=False).fillna("0").astype(int)
gs = gs.sort_values("sn")

ng = len(gs); cw = 0.21; ch = 0.2; sx = XC - (ng*cw)/2 - 0.5

ax.text(sx-0.3, Y-0.05, "Dharia", fontsize=8, fontweight="bold", color="#64748b", va="center")
dhy = Y - 0.15
for i, (_, row) in enumerate(gs.iterrows()):
    xc = sx + i*cw; fc, tc = gc(row["Dharia_log2FC"], row["Dharia_padj"], row["Dharia_sig"])
    rr = mpatches.FancyBboxPatch((xc, dhy-ch/2), cw, ch, boxstyle="round,pad=0.02", ec="#e2e8f0", fc=fc, lw=0.5)
    ax.add_patch(rr)
    if row["Dharia_sig"]:
        ax.text(xc+cw/2, dhy-ch/2-0.1, row["symbol"], ha="center", va="top", fontsize=4, fontweight="bold", color=SU)

pty = dhy - ch - 0.35
ax.text(sx-0.3, pty-0.05, "PTT1", fontsize=8, fontweight="bold", color="#64748b", va="center")
pty -= 0.15
for i, (_, row) in enumerate(gs.iterrows()):
    xc = sx + i*cw; fc, tc = gc(row["PTT1_log2FC"], row["PTT1_padj"], row["PTT1_sig"])
    rr = mpatches.FancyBboxPatch((xc, pty-ch/2), cw, ch, boxstyle="round,pad=0.02", ec="#e2e8f0", fc=fc, lw=0.5)
    ax.add_patch(rr)
    if row["PTT1_sig"]:
        val = row["PTT1_log2FC"]
        v = "+{:.1f}".format(val) if val > 0 else "{:.1f}".format(val)
        ax.text(xc+cw/2, pty+ch+0.02, v, ha="center", va="bottom", fontsize=3.8, color=tc)
        ax.text(xc+cw/2, pty-ch/2-0.1, row["symbol"], ha="center", va="top", fontsize=4, fontweight="bold",
                color="#db2777" if val > 0 else "#2563eb")

ly = pty - ch - 1.2
legs = [(SU, "Significant up (padj<0.01)"), (SD, "Significant down"),
        (UP, "Up, not sig"), (DN, "Down, not sig"),
        (NS, "NS (|lfc| small)"), (ND, "Filtered by DESeq2")]
for i, (c, l) in enumerate(legs):
    x = 2.5 + (i%3)*3.2; yl = ly - (i//3)*0.55
    rr = mpatches.FancyBboxPatch((x, yl-0.15), 0.3, 0.3, boxstyle="round,pad=0.02",
                                 ec="#cbd5e1", fc=c, lw=0.5)
    ax.add_patch(rr)
    ax.text(x+0.4, yl, l, ha="left", va="center", fontsize=8, color=TX)

ax.text(XC, ly-1.5,
        "Split boxes: Dharia (left) vs PTT1 (right) log\u2082FC. Red=up, Blue=down, Gray=NS, White=no data.",
        ha="center", va="center", fontsize=9, color="#64748b", style="italic")

ax.text(XC, 28.5, "Ethylene-Activated Signaling Pathway: Dharia vs PTT1",
        ha="center", va="center", fontsize=15, fontweight="bold", color=TX)
ax.text(XC, 28.0,
        "KEGG-style cascade diagram with split-box comparison | log\u2082FoldChange | padj<0.01",
        ha="center", va="center", fontsize=9, color="#64748b")

os.makedirs(OUTDIR, exist_ok=True)
fig.savefig(f"{OUTDIR}/RNAseq_Oui_ethylene_kegg_pathway.png", dpi=250,
            bbox_inches="tight", facecolor="white")
fig.savefig(f"{OUTDIR}/RNAseq_Oui_ethylene_kegg_pathway.pdf", bbox_inches="tight",
            facecolor="white")
plt.close()
print(f"Saved: {OUTDIR}/RNAseq_Oui_ethylene_kegg_pathway.png/pdf")