# Replication package — Weather Extremes, Production Value, and Export Allocations
Corn and Soybeans, U.S. Midwest (12 states), 2000–2022, with CMIP6 projections to 2100.

This folder holds the cleaned replication code. Raw data files are **not** moved;
they stay in the parent `Data Files` folder and are read from there.

## Data files (in the parent `Data Files` folder)
| File | Purpose |
|---|---|
| `Historical_Corn_Soybean_Analysis_Data_2000_2022.dta` | State-year panel (276 obs, 12 states, 2000–2022). Outcomes: `lp`,`lspd` (log corn/soy production **value**), `lx`,`lsx` (log corn/soy **ERS state export allocation**), `lpb`,`lspb` (log production in bushels), `lcy`,`lsy` (log yield). Weather bins `time0C`–`time45C`, plus stored `gtt`,`htt`,`fr`,`prec`,`prec_sq`,`t`,`t_sq`. Stocks: `lCornStEnd`,`lSoyStEnd`,`lCornStCarry`,`lSoyStCarry`. |
| `NorESM2-MM_Weather_Production_ERS_Projections_2021_2100.dta` | NorESM2-MM projected weather (`gtt`,`htt`,`fr`,`prec`,`prec_sq`,`t`,`t_sq`) by `fips`,`year`,`ssp` (245/585). Used for **Figure 3**. |
| `CESM2_Weather_Production_ERS_Projections_2021_2100.dta` | CESM2 projected weather (appendix CESM2 figures; same structure). |

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
state-year data** (`Historical_Corn_Soybean_Analysis_Data_2000_2022.dta` and the two projection `.dta` files); the raw PRISM grids are not
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

The `.do` files are independent (each loads `Historical_Corn_Soybean_Analysis_Data_2000_2022.dta` and rebuilds the weather
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

