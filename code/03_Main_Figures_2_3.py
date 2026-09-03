"""
03_Main_Figures_2_3.py
Paper: Weather Extremes, Production Value, and Export Allocations
       (Corn and Soybeans, U.S. Midwest)

Reproduces:
  Figure 2 - State-level % impact of a 1 SD increase in HDD on production value
             and the ERS allocation (corn = Panel A, soybean = Panel B), drawn
             as a Midwest map. Requires geopandas and the Census state shapefile.
  Figure 3 - Projected distributions of production value and the ERS allocation,
             2000-2100, NorESM2-MM under SSP245/SSP585 (corn = A, soybean = B).

Inputs (read from the Data Files folder, one level up from this script):
  Historical_Corn_Soybean_Analysis_Data_2000_2022.dta
  NorESM2-MM_Weather_Production_ERS_Projections_2021_2100.dta
  cb_2018_us_state_500k/            (Census 500k state shapefile; Figure 2 only)

Outputs (written to ./output, raw data untouched):
  Figure2_state_impacts.(png/pdf)
  Figure3_NorESM_projection.(png/pdf)

Run:  python 03_Main_Figures_2_3.py
"""

from pathlib import Path
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.patches import Patch

DATA_DIR = Path(__file__).resolve().parent.parent          # "Data Files"
OUT_DIR  = Path(__file__).resolve().parent / "output"
OUT_DIR.mkdir(exist_ok=True)
SHAPEFILE = DATA_DIR / "cb_2018_us_state_500k"             # place Census shapefile here

STATE_FIPS = {'IA':'19','IL':'17','IN':'18','KS':'20','MI':'26','MN':'27',
              'MO':'29','ND':'38','NE':'31','OH':'39','SD':'46','WI':'55'}


# ===========================================================================
# FIGURE 2 - State-level impacts of extreme heat (map)
# Values = state SD(HDD) x baseline HDD coefficient, from Table 1:
#   corn  production -0.006087, ERS -0.003753
#   soybean production -0.005728, ERS -0.004273
# The per-state numbers below are those published in the manuscript.
# ===========================================================================
def make_figure2():
    try:
        import geopandas as gpd
    except ImportError:
        print("Figure 2 skipped: geopandas is not installed "
              "(pip install geopandas).")
        return
    if not (SHAPEFILE.exists() or SHAPEFILE.with_suffix(".shp").exists()):
        print(f"Figure 2 skipped: Census shapefile not found at {SHAPEFILE}.")
        return

    corn = pd.DataFrame({
        'State_Code': ['KS','MO','NE','SD','IL','IN','IA','OH','ND','WI','MI','MN'],
        'Production_Change': [-0.23,-0.17,-0.15,-0.14,-0.13,-0.11,-0.09,-0.08,-0.06,-0.04,-0.03,-0.02],
        'Export_Change':     [-0.14,-0.11,-0.09,-0.09,-0.08,-0.07,-0.06,-0.05,-0.04,-0.03,-0.03,-0.02]})
    soy = pd.DataFrame({
        'State_Code': ['KS','MO','NE','SD','IL','IN','IA','OH','ND','WI','MI','MN'],
        'Production_Change': [-0.21,-0.16,-0.13,-0.12,-0.11,-0.10,-0.08,-0.07,-0.05,-0.04,-0.03,-0.02],
        'Export_Change':     [-0.16,-0.13,-0.10,-0.09,-0.08,-0.07,-0.06,-0.05,-0.04,-0.03,-0.02,-0.02]})
    for df in (corn, soy):
        df['FIPS'] = df['State_Code'].map(STATE_FIPS)

    states = gpd.read_file(str(SHAPEFILE))
    midwest = list(STATE_FIPS.values())

    def panel(ax, df, title):
        g = states[states['STATEFP'].isin(midwest)].merge(df, left_on='STATEFP', right_on='FIPS')
        g.plot(ax=ax, edgecolor='black', color='#e0e0e0', linewidth=0.85)
        _, y0, _, y1 = g.total_bounds
        dy = (y1 - y0) * 0.032
        for _, r in g.iterrows():
            if r['State_Code'] == 'MI':
                x, y = -85.0, 44.0
            else:
                c = r.geometry.centroid; x, y = c.x, c.y
            ax.text(x, y+dy, r['State_Code'], ha='center', va='center', fontsize=12, fontweight='bold')
            ax.text(x, y,    f"Prod. Val. {r['Production_Change']:.0%}", ha='center', va='center', fontsize=10, color='darkgreen')
            ax.text(x, y-dy, f"ERS Alloc. {r['Export_Change']:.0%}",     ha='center', va='center', fontsize=10, color='maroon')
        ax.set_title(title, fontsize=15, fontweight='bold', loc='left', pad=14)
        ax.axis('off'); ax.set_aspect('equal')

    fig, axes = plt.subplots(2, 1, figsize=(12, 15))
    panel(axes[0], corn, "Panel A. Corn")
    panel(axes[1], soy,  "Panel B. Soybeans")
    fig.suptitle("State-Level Impacts of Extreme Heat on Production Value and ERS Allocation",
                 fontsize=18, fontweight='bold', y=0.985)
    plt.subplots_adjust(top=0.94, bottom=0.02, left=0.02, right=0.98, hspace=0.12)
    fig.savefig(OUT_DIR/"Figure2_state_impacts.png", dpi=600, bbox_inches='tight', facecolor='white')
    fig.savefig(OUT_DIR/"Figure2_state_impacts.pdf", bbox_inches='tight', facecolor='white')
    plt.close(fig)
    print("Figure 2 saved to", OUT_DIR)


# ===========================================================================
# FIGURE 3 - Projected distributions, NorESM2-MM (corn + soybean)
# Predictions use the projection model coefficients (state + year FE and
# state-specific linear/quadratic trends). Coefficients below are the stored
# estimates used for the manuscript figure; do not edit.
# ===========================================================================

# --- Corn production value ---
corn_prod_coef = {'gtt':0.0001294,'htt':-0.0051105,'fr':-0.0050221,'prec':-0.0003596,
                  'prec_sq':1.12e-07,'t':0.0485294,'t_sq':-0.0016549,'_cons':20.04663}
corn_prod_ft   = {18:-0.0131439,19:0.0039499,20:-0.0184817,26:0.0214329,27:0.0022075,
                  29:-0.0213904,31:-0.0048334,38:0.1376752,39:-0.0039355,46:0.0303425,55:-0.0029476}
corn_prod_ft2  = {18:0.0004259,19:-2.79e-06,20:0.0015549,26:-0.0008162,27:0.0002434,
                  29:0.001287,31:0.0005897,38:-0.0034463,39:0.0003278,46:-0.0005,55:0.0004576}
corn_prod_yfe  = {2001:-0.0717446,2002:-0.1019899,2003:-0.1204839,2004:-0.1474265,2005:-0.0601071,
                  2006:-0.1642923,2007:0.0091514,2008:-0.1454246,2009:-0.1422745,2010:-0.1166573,
                  2011:-0.0433384,2012:-0.2009793,2013:0.0032748,2014:-0.0681432,2015:-0.1522398,
                  2016:-0.0060192,2017:-0.0685235,2018:0.0311835,2019:-0.151231,2020:-0.0842647,2021:0,2022:0}

# --- Corn ERS allocation ---
corn_ers_coef = {'gtt':0.0001024,'htt':-0.00228,'fr':0.0082767,'prec':-0.0007456,
                 'prec_sq':4.07e-07,'t':0.1394821,'t_sq':-0.0036076,'_cons':5.254178}
corn_ers_ft   = {18:-0.0113235,19:0.0112372,20:-0.0475171,26:0.0429798,27:0.0425769,
                 29:-0.0254988,31:0.008932,38:0.1342111,39:-0.0135933,46:0.0470517,55:-0.022266}
corn_ers_ft2  = {18:0.0004199,19:-0.0002624,20:0.0026928,26:-0.001458,27:-0.0011881,
                 29:0.0015893,31:0.0001763,38:-0.0032962,39:0.0006639,46:-0.0010149,55:0.0009543}
corn_ers_yfe  = {2001:-0.1850879,2002:-0.2608952,2003:-0.3964971,2004:-0.3041556,2005:-0.6252393,
                 2006:-0.2722246,2007:-0.08804,2008:0.1228735,2009:-0.4177748,2010:-0.25797,
                 2011:0.0152573,2012:-0.3970496,2013:-0.990824,2014:-0.5274567,2015:-0.7390368,
                 2016:-0.5607003,2017:-0.6762846,2018:-0.4325679,2019:-0.9263345,2020:-0.7592866,2021:0,2022:0}

# --- Soybean production value ---
soy_prod_coef = {'gtt':0.0003099,'htt':-0.0042087,'fr':-0.0038771,'prec':-0.0001195,
                 'prec_sq':3.97e-08,'t':0.0192094,'t_sq':0.00001,'_cons':19.48024}
soy_prod_ft   = {18:0.0155799,19:0.008058,20:0.0964704,26:0.0294346,27:0.014866,
                 29:0.0214356,31:0.0370895,38:0.1221991,39:0.038306,46:0.029216,55:0.0241457}
soy_prod_ft2  = {18:-0.0008174,19:-0.0007087,20:-0.0028434,26:-0.0011145,27:-0.0007596,
                 29:-0.0007397,31:-0.0014039,38:-0.0036442,39:-0.0015055,46:-0.0009429,55:-0.0004167}
soy_prod_yfe  = {2001:0.0353351,2002:0.2414595,2003:0.2304862,2004:0.0679266,2005:0.1166758,
                 2006:0.2299504,2007:0.4092119,2008:0.387572,2009:0.3959653,2010:0.5130249,
                 2011:0.5803591,2012:0.5339058,2013:0.4878304,2014:0.221329,2015:-0.0232489,
                 2016:0.089072,2017:0.0014747,2018:-0.0829934,2019:-0.4571557,2020:-0.1084623,2021:0,2022:0}

# --- Soybean ERS allocation ---
soy_ers_coef = {'gtt':0.0003597,'htt':-0.0038919,'fr':-0.0028064,'prec':-0.0002571,
                'prec_sq':1.06e-07,'t':-0.1792334,'t_sq':0.00001,'_cons':4.849282}
soy_ers_ft   = {18:0.020762,19:0.0161399,20:-0.0465307,26:0.0333821,27:0.0208521,
                29:0.0296105,31:0.0373987,38:0.1255354,39:0.0402631,46:0.0295574,55:0.0664116}
soy_ers_ft2  = {18:-0.000974,19:-0.0009913,20:0.0033764,26:-0.0012798,27:-0.0009379,
                29:-0.0009988,31:-0.0013401,38:-0.0036377,39:-0.0015459,46:-0.0008305,55:-0.0014068}
soy_ers_yfe  = {2001:0.1905542,2002:0.424283,2003:0.7554314,2004:0.5093413,2005:0.6209217,
                2006:0.767606,2007:1.107446,2008:1.49491,2009:1.473535,2010:1.549224,
                2011:1.562816,2012:1.701242,2013:1.512665,2014:1.397903,2015:0.9574496,
                2016:1.019486,2017:0.7668618,2018:0.3899819,2019:0.1930758,2020:0.2557386,2021:0,2022:0}

PERIODS = ['2000-2022','2023-2044','2045-2066','2067-2088','2089-2100']
BINS    = [2000, 2023, 2045, 2067, 2089, 2101]
COLORS  = {('Production','Historical'):'#7AA6C2', ('Production','SSP245'):'#A5C8E1', ('Production','SSP585'):'#004C6D',
           ('ERS Allocation','Historical'):'#D98B48', ('ERS Allocation','SSP245'):'#F5B66C', ('ERS Allocation','SSP585'):'#8B4513'}


def predict(data, coef, ft, ft2, yfe):
    """Linear prediction: weather terms + state-specific trends + year FE."""
    p = (coef['_cons'] + data['gtt']*coef['gtt'] + data['htt']*coef['htt'] + data['fr']*coef['fr']
         + data['prec']*coef['prec'] + data['prec_sq']*coef['prec_sq'])
    p += data['t']    * (coef['t']    + data['fips'].map(ft).fillna(0))
    p += data['t_sq'] * (coef['t_sq'] + data['fips'].map(ft2).fillna(0))
    p += data['year'].map(yfe).fillna(0)
    return p


def build_plot_df(hist, fut, prod_hist_col, ers_hist_col,
                  prod_coef, prod_ft, prod_ft2, prod_yfe,
                  ers_coef, ers_ft, ers_ft2, ers_yfe):
    frames = []
    # historical
    for col, var in [(prod_hist_col,'Production'), (ers_hist_col,'ERS Allocation')]:
        h = hist[['year', col]].rename(columns={col:'value'})
        h['variable'] = var; h['scenario'] = 'Historical'
        frames.append(h)
    # future, by scenario
    for ssp, g in fut.groupby('ssp'):
        g = g.copy()
        label = 'SSP' + str(int(float(ssp)))
        prod = g[['year']].copy(); prod['value'] = predict(g, prod_coef, prod_ft, prod_ft2, prod_yfe)
        prod['variable'] = 'Production'; prod['scenario'] = label
        ers = g[['year']].copy(); ers['value'] = predict(g, ers_coef, ers_ft, ers_ft2, ers_yfe)
        ers['variable'] = 'ERS Allocation'; ers['scenario'] = label
        frames += [prod, ers]
    df = pd.concat(frames, ignore_index=True)
    df['period'] = pd.cut(df['year'], bins=BINS, right=False, labels=PERIODS)
    return df


def draw_projection_panel(ax, df, title):
    data, positions, box_colors, ticks = [], [], [], []
    base = 0.0
    for period in PERIODS:
        pdf = df[df['period'] == period]
        scenarios = ['Historical'] if period == '2000-2022' else ['SSP245', 'SSP585']
        pos = [base + i*0.82 for i in range(len(scenarios)*2)]
        positions += pos; ticks.append(np.mean(pos))
        for variable in ['Production', 'ERS Allocation']:
            for scenario in scenarios:
                vals = pdf[(pdf['variable']==variable) & (pdf['scenario']==scenario)]['value'].dropna()
                data.append(vals); box_colors.append(COLORS[(variable, scenario)])
        base += len(scenarios)*2*0.82 + 1.35
    bp = ax.boxplot(data, positions=positions, patch_artist=True, widths=0.68,
                    medianprops={'color':'black','linewidth':1.5},
                    flierprops={'marker':'o','markersize':3.5,'markerfacecolor':'none',
                                'markeredgecolor':'black','markeredgewidth':0.6})
    for patch, c in zip(bp['boxes'], box_colors):
        patch.set_facecolor(c)
    ax.set_ylabel("Log Value", fontsize=13, fontweight='bold')
    ax.set_xlabel("Time Period", fontsize=13, fontweight='bold', labelpad=8)
    ax.set_xticks(ticks); ax.set_xticklabels(PERIODS, fontsize=11, fontweight='bold')
    ax.grid(axis='y', linestyle='--', linewidth=0.45, color='0.82')
    ax.spines['top'].set_visible(False); ax.spines['right'].set_visible(False)
    ax.set_title(title, fontsize=14, fontweight='bold', loc='left', pad=12)


def make_figure3():
    hist = pd.read_stata(DATA_DIR/"Historical_Corn_Soybean_Analysis_Data_2000_2022.dta", convert_categoricals=False)
    fut  = pd.read_stata(DATA_DIR/"NorESM2-MM_Weather_Production_ERS_Projections_2021_2100.dta", convert_categoricals=False)
    for c in ['fips', 'year']:
        hist[c] = hist[c].astype(int); fut[c] = fut[c].astype(int)
    if 'prec_sq' not in fut:
        fut['prec_sq'] = fut['prec']**2

    corn = build_plot_df(hist, fut, 'lp', 'lx',
                         corn_prod_coef, corn_prod_ft, corn_prod_ft2, corn_prod_yfe,
                         corn_ers_coef, corn_ers_ft, corn_ers_ft2, corn_ers_yfe)
    soy  = build_plot_df(hist, fut, 'lspd', 'lsx',
                         soy_prod_coef, soy_prod_ft, soy_prod_ft2, soy_prod_yfe,
                         soy_ers_coef, soy_ers_ft, soy_ers_ft2, soy_ers_yfe)

    fig, axes = plt.subplots(2, 1, figsize=(14, 14))
    draw_projection_panel(axes[0], corn, "Panel A. Corn")
    draw_projection_panel(axes[1], soy,  "Panel B. Soybeans")
    fig.suptitle("Projected Distributions of U.S. Midwest Corn and Soybean "
                 "Production Value and ERS State Export Allocation, 2000-2100",
                 fontsize=17, fontweight='bold', y=0.982)
    legend = [Patch(facecolor=COLORS[k], edgecolor='black', label=f"{k[0]}: {k[1]}")
              for k in [('Production','Historical'),('ERS Allocation','Historical'),
                        ('Production','SSP245'),('ERS Allocation','SSP245'),
                        ('Production','SSP585'),('ERS Allocation','SSP585')]]
    fig.legend(handles=legend, loc='lower center', bbox_to_anchor=(0.5, 0.015),
               ncol=2, fontsize=11, frameon=False, columnspacing=6.0)
    plt.subplots_adjust(top=0.925, bottom=0.16, left=0.09, right=0.98, hspace=0.32)
    fig.savefig(OUT_DIR/"Figure3_NorESM_projection.png", dpi=600, bbox_inches='tight', facecolor='white')
    fig.savefig(OUT_DIR/"Figure3_NorESM_projection.pdf", bbox_inches='tight', facecolor='white')
    plt.close(fig)
    print("Figure 3 saved to", OUT_DIR)


if __name__ == "__main__":
    make_figure2()
    make_figure3()
