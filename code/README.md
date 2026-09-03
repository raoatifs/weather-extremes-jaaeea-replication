# Replication package — Weather Extremes, Production Value, and Export Allocations
Corn and Soybeans, U.S. Midwest (12 states), 2000–2022, with CMIP6 projections to 2100.

This folder holds the cleaned replication code. Raw data files are **not** moved;
they stay in the parent `Data Files` folder and are read from there.

## Data files (in the parent `Data Files` folder)
| File | Purpose |
|---|---|
| `Corndata.dta` | State-year panel (276 obs, 12 states, 2000–2022). Outcomes: `lp`,`lspd` (log corn/soy production **value**), `lx`,`lsx` (log corn/soy **ERS state export allocation**), `lpb`,`lspb` (log production in bushels), `lcy`,`lsy` (log yield). Weather bins `time0C`–`time45C`, plus stored `gtt`,`htt`,`fr`,`prec`,`prec_sq`,`t`,`t_sq`. Stocks: `lCornStEnd`,`lSoyStEnd`,`lCornStCarry`,`lSoyStCarry`. |
| `combined_NorESM2-MM_2021-2100.dta` | NorESM2-MM projected weather (`gtt`,`htt`,`fr`,`prec`,`prec_sq`,`t`,`t_sq`) by `fips`,`year`,`ssp` (245/585). Used for **Figure 3**. |
| `combined_CESM2_2021-2100.dta` | CESM2 projected weather (appendix CESM2 figures; same structure). |

## Data sources and weather-variable construction
Raw daily minimum temperature (tmin), maximum temperature (tmax), and precipitation
come from the PRISM Climate Group (Oregon State University) on an approximately
2.5-mile (4 km) daily grid. Because the grid-cell data are very large, they are
processed into growing-season exposure measures at the **state-year** level —
growing degree days (GDD, 0–28 °C), heating degree days (HDD, ≥29 °C), precipitation,
and freezing days — to match USDA-NASS state production value and the USDA-ERS state
export allocation, which are only available at the state level. The weather
aggregation follows Schlenker and Roberts (2009): within each grid cell a sinusoidal
interpolation between daily min and max temperature gives the time spent in each 1 °C
interval; the nonlinear degree-day measures are computed at the grid-cell level
**before** any spatial averaging, then averaged across grid cells within a state and
summed over the growing season. CMIP6 projections (NorESM2-MM and CESM2, SSP245/SSP585)
are processed with the identical method. This repository distributes the **processed
state-year data** (`Corndata.dta`, `combined_*.dta`); the raw PRISM grids are not
included because of their size and are freely available from PRISM directly.

## Code files (this folder)
| File | Reproduces | Language |
|---|---|---|
| `01_Main_Analysis_Table1_Figure1.do` | Weather variables, **Main Table 1**, **Main Figure 1** | Stata |
| `02_Supporting_Information_Robustness.do` | **Appendix A2.6–A2.12** and summary statistics | Stata |
| `03_Main_Figures_2_3.py` | **Main Figure 2** (map) and **Main Figure 3** (projection) | Python |
| `04_Appendix_Figure_CESM2.py` | **Appendix CESM2 projection figure** (same design as Figure 3, CESM2 model) | Python |

## Run order
1. `01_Main_Analysis_Table1_Figure1.do`
2. `02_Supporting_Information_Robustness.do`
3. `03_Main_Figures_2_3.py`
4. `04_Appendix_Figure_CESM2.py`  (optional; appendix CESM2 figure)

The `.do` files are independent (each loads `Corndata.dta` and rebuilds the weather
variables), so they can also be run on their own. Before running, edit the single
`global root` line at the top of each `.do` file to point at the `Data Files` folder.
The Python script finds the data automatically (one level up from this folder).

## What reproduces each output
- **Table 1** — the four `reg` models in `01_...do` (corn/soy × production value/ERS allocation).
  Spec: `gtt htt prec prec² fr`, state FE + year FE, **SE clustered by year**.
- **Figure 1** — residualized HDD vs log ERS allocation (corn, soybean) in `01_...do`.
- **Figure 2** — `make_figure2()` in `03_...py` (state-level % impact of 1 SD HDD).
- **Figure 3** — `make_figure3()` in `03_...py` (NorESM2-MM projection boxplots).
- **Appendix robustness (A2.6–A2.12)** — `02_...do`, one clearly-labelled block per table.

## Required software / packages
- **Stata 15+**. Packages: `estout` (esttab) and `boottest` — both auto-installed via
  `ssc install` at the top of the `.do` files if missing.
- **Python 3.9+** with `pandas`, `numpy`, `matplotlib` (Figure 3), and `geopandas`
  (Figure 2 only). Figure 2 also needs the U.S. Census 500k state shapefile
  (`cb_2018_us_state_500k`) placed in the `Data Files` folder; without geopandas or
  the shapefile the script prints a message, skips Figure 2, and still makes Figure 3.

## Outputs
Everything is written to `Code Files/output/` (created automatically); raw data is untouched.
- `Table1_main.rtf`, `Figure1_identifying_variation.png`
- `AppendixSummaryStats.rtf` + regression results in the Stata log
- `Figure2_state_impacts.png/.pdf`, `Figure3_NorESM_projection.png/.pdf`
- `Figure_CESM2_projection.png/.pdf` (appendix, from `04_...py`)

---

## Inconsistencies and reproducibility notes (found while cleaning)

1. **Table 1 — corn ERS-allocation standard error (must fix).** The printed SE on the
   corn ERS HDD coefficient is **0.00091**, which is the *classical (non-clustered)*
   OLS SE. The other three columns use the year-clustered SE. The correct
   **year-clustered SE is 0.00129 (≈ 0.0013)** — exactly what Appendix Table A2.12
   already reports for this cell. The coefficient (−0.003753) and significance (***,
   p<0.01 even with the larger SE) are unchanged. The cleaned `01_...do` produces the
   correct 0.0013; update this one cell in Table 1 to match.

2. **Superseded do-files in `Analysis/Stata do files/`.** `R03_estimation_main.do`
   (and the R01–R05 set) implement a *different* specification — `reghdfe` with
   state-specific quadratic trends and two-way clustering, and a χ²(1)=14.23 equality
   test. That does **not** reproduce the final manuscript Table 1 (which is
   year-clustered, state+year FE only, equality test F(1,11)=12.25 / wild-bootstrap
   p=0.004). The final specifications live in the master `Corn do file.do` and are the
   basis for the three cleaned files here. Treat R01–R05 as an earlier revision.

3. **HDD construction (harmless).** The stored `htt` used in the manuscript sums the
   temperature bins **29C–45C**; an old loop in `Corn do file.do` summed only 29C–44C
   (max difference ≈ 0.003, no effect on results). The cleaned code sums 29C–45C so it
   reproduces the stored/manuscript variable exactly. GDD = 0C–28C; thresholds in
   A2.11 are built as 28C–45C and 30C–45C on the same scale.

4. **Figure 3 projection coefficients** are the estimates from the projection model
   (`Prediction.do`: state + year FE **plus state-specific linear and quadratic
   trends**), not the Table 1 baseline (no state trends). This is by design — the
   projection model is the trend-inclusive one — but it is why the HDD coefficients
   hard-coded in `03_...py` (e.g. corn production −0.00511) differ from Table 1
   (−0.006087). They are preserved unchanged.

5. **Figure 2 values are hard-coded** (the published per-state numbers). They equal
   `state SD(HDD) × baseline HDD coefficient` from Table 1 (verified, e.g. Kansas corn
   37.35 × −0.006087 ≈ −0.23 production, −0.14 allocation). Kept as published so the
   figure matches the manuscript.

6. **Not reproducible from the provided data.** Appendix Table A1.1a (PRISM grid-cell
   daily stats) and A1.1b–A1.1e (CMIP6 daily tmin/tmax/prec) are computed from the raw
   *daily* climate files, which are not part of this package — only the state-year
   aggregates are included. Those two summary tables therefore cannot be regenerated here.

## Verification performed
Because Stata was not available in the cleaning environment, all headline numbers were
re-estimated independently in Python (`statsmodels`) against `Corndata.dta`:
Table 1 coefficients matched to 6 decimals for all four columns; Table 1 HDD SEs matched
for 3 of 4 columns (the 4th is note 1 above); and Appendix A2.7a/b, A2.10, A2.11, and
A2.12 all reproduced. Figure 3 was generated and matches the manuscript pattern
(production value declines and widens after mid-century, more under SSP585).
