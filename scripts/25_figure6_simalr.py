# Composite figure: SIMALR regulatory context + HLA-II binders
import os
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches

os.chdir("D:/T1D_DarkGenome")
os.makedirs("results/figures", exist_ok=True)

fig = plt.figure(figsize=(14, 10))
gs = fig.add_gridspec(3, 2, height_ratios=[1.2,1,1.2], hspace=0.55, wspace=0.3)

ax_a = fig.add_subplot(gs[0, :])
genes = [("WAKMAR2",137823673,137868233,"#888888"),
         ("TNFAIP3",137867214,137883314,"#B2182B"),
         ("SIMALR",137943079,137957657,"#D6604D"),
         ("LINC02865",137945366,137972522,"#888888"),
         ("PERP",138088505,138107419,"#4393C3")]
for name, s, e, c in genes:
    ax_a.barh(0, e-s, left=s, height=0.4, color=c, edgecolor="black", linewidth=0.5)
    ax_a.text((s+e)/2, 0.5, name, ha="center", fontsize=9, fontweight="bold")
ax_a.axvline(137885000, color="darkred", linestyle="--", linewidth=1.5)
ax_a.text(137885000, -0.55, "rs6920220\n(T1D risk)", ha="center", fontsize=8, color="darkred")
ax_a.set_xlim(137800000, 138120000); ax_a.set_ylim(-0.9, 1.2); ax_a.set_yticks([])
ax_a.set_xlabel("chr6 position (hg38)")
ax_a.set_title("A. SIMALR locus in the TNFAIP3-PERP regulatory hub", fontweight="bold")
for sp in ["top","right","left"]: ax_a.spines[sp].set_visible(False)

ax_b = fig.add_subplot(gs[1, 0])
names_b = ["SIMALR","TNFAIP3","PERP","AC093063.1","AC007991.2"]
logfc = [6.31, 1.32, 0.52, 10.99, 10.44]
colors = ["#D6604D","#B2182B","#4393C3","#888888","#888888"]
ax_b.bar(names_b, logfc, color=colors, edgecolor="black", linewidth=0.5)
ax_b.set_ylabel("log2 FC"); ax_b.set_title("B. Cytokine induction in human islets",
                                            fontweight="bold")
ax_b.axhline(0, color="black", linewidth=0.5)
plt.setp(ax_b.get_xticklabels(), rotation=30, ha="right", fontsize=8)

ax_c = fig.add_subplot(gs[1, 1])
top = [("EHKDGQVQAKGERPG","DQ8",0.146),("CEHKDGQVQAKGERP","DQ8",0.205),
       ("MRYWSDAGAGIWTIT","DQ2.5",0.414),("HGSDFATKMSYENPA","DQ8",0.463),
       ("SMRYWSDAGAGIWTI","DQ2.5",0.539),("MKRAGGATAWKDSMC","DQ8",0.553),
       ("HRNLRRDNQISICKP","DRB1*03:01",0.785),("MSFFIFQNLASGLDR","DRB1*04:01",0.849),
       ("LLYIQQEASNVEVIR","DRB1*04:01",1.24)]
color_map = {"DQ8":"#B2182B","DQ2.5":"#D6604D","DRB1*03:01":"#4393C3","DRB1*04:01":"#2166AC"}
ax_c.barh(range(len(top)), [t[2] for t in top],
          color=[color_map[t[1]] for t in top], edgecolor="black", linewidth=0.5)
ax_c.set_yticks(range(len(top)))
ax_c.set_yticklabels([t[0] for t in top], fontsize=7, family="monospace")
ax_c.set_xlabel("%Rank (lower = stronger)")
ax_c.set_title("C. SIMALR micropeptides — top HLA-II binders", fontweight="bold")
ax_c.axvline(2, color="grey", linestyle="--", linewidth=0.8)
ax_c.invert_yaxis()

ax_d = fig.add_subplot(gs[2, 0])
ax_d.pie([10,6,3,4], labels=["DQ8","DQ2.5","DRB1*03:01","DRB1*04:01"],
         autopct="%d", colors=[color_map[k] for k in ["DQ8","DQ2.5","DRB1*03:01","DRB1*04:01"]],
         wedgeprops={"edgecolor":"black","linewidth":0.5})
ax_d.set_title("D. SIMALR strong binders by allele (23 total)", fontweight="bold")

ax_e = fig.add_subplot(gs[2, 1]); ax_e.axis("off")
ax_e.text(0.5, 1.02, "E. Proposed mechanism", ha="center", fontsize=11,
          fontweight="bold", transform=ax_e.transAxes)
steps = [("Cytokine stress (T1D islet)", "#F4A582"),
         ("Macrophage activation", "#D6604D"),
         ("SIMALR upregulation at TNFAIP3 locus", "#B2182B"),
         ("Macrophage survival via HIF1alpha/NTN1", "#B2182B"),
         ("Prolonged inflammation", "#4393C3"),
         ("beta-cell destruction", "#2166AC")]
y = 0.90
for i,(txt,c) in enumerate(steps):
    ax_e.text(0.5, y, txt, ha="center", va="center",
              bbox=dict(boxstyle="round,pad=0.3", fc=c, ec="black", lw=0.5),
              fontsize=8, transform=ax_e.transAxes)
    if i < len(steps)-1:
        ax_e.annotate("", xy=(0.5, y-0.035), xytext=(0.5, y-0.115),
                      xycoords="axes fraction",
                      arrowprops=dict(arrowstyle="->", lw=1.2))
    y -= 0.145

plt.suptitle("SIMALR: a T1D-specific lncRNA at the TNFAIP3 risk locus",
             fontsize=13, fontweight="bold", y=1.00)
plt.savefig("results/figures/Figure6_SIMALR_composite.pdf", bbox_inches="tight")
plt.savefig("results/figures/Figure6_SIMALR_composite.png", dpi=200, bbox_inches="tight")
print("Saved Figure6_SIMALR_composite")
