*===============================================================================
* 02_Supporting_Information_Robustness.do
* Paper: Weather Extremes, Production Value, and Export Allocations
*
* Reproduces the Supporting Information Appendix diagnostics and robustness:
*   Summary statistics (state-year variables)
*   A2.6   Within-state variation + production/allocation correlations
*          + cross-equation test of HDD coefficient equality
*   A2.7a  HDD effect on ending stocks (pass-through)
*   A2.7b  Allocation equation with HDD x carry-in interaction
*   A2.7c  Marginal effect of HDD across the carry-in distribution
*   A2.8   Lagged-weather specification (allocation)
*   A2.9   Robustness to time trends
*   A2.10  Price-offset check: production in value vs quantity
*   A2.11  Robustness to alternative heat thresholds (28/29/30 C)
*   A2.12  Robustness to alternative clustering
*
* Input:  Corndata.dta
* Output: results printed to the log; edit the esttab lines to export if needed.
*
* Baseline throughout = state FE + year FE, SE clustered by year (matches file 01).
*===============================================================================

version 15
clear all
set more off

global root "/Users/atifrao/OneDrive - Kansas State University/1 PhD Study/Kansas/KSU Study/Research/PhD Proposal/1st/Data Files"
global out  "${root}/Code Files/output"
cap mkdir "${out}"

cap which esttab
if _rc ssc install estout, replace
cap which boottest
if _rc ssc install boottest, replace

use "${root}/Corndata.dta", clear
keep if inlist(fips,17,18,19,20,26,27,29,31,38,39,46,55)
xtset fips year

* Weather variables (see file 01 for definitions)
cap drop gtt htt
gen gtt = 0
forval i = 0/28  { replace gtt = gtt + time`i'C }
gen htt = 0
forval i = 29/45 { replace htt = htt + time`i'C }
cap drop prec_sq
gen prec_sq = prec^2

*-------------------------------------------------------------------------------
* Summary statistics (state-year variables used in estimation)
*-------------------------------------------------------------------------------
estpost tabstat gtt htt prec fr lp lx lspd lsx, ///
    statistics(mean sd min max) columns(statistics)
esttab using "${out}/AppendixSummaryStats.rtf", replace ///
    cells("mean(fmt(3)) sd(fmt(3)) min(fmt(3)) max(fmt(3))") noobs nonumber label

*-------------------------------------------------------------------------------
* A2.6  Within-state variation and production/allocation correlations
*-------------------------------------------------------------------------------
foreach v in lp lx lspd lsx {
    di _n "xtsum `v'"
    xtsum `v'
}
* correlation before and after state & year FE
foreach pair in "lp lx" "lspd lsx" {
    tokenize "`pair'"
    di _n "raw corr `1' `2'"
    corr `1' `2'
    qui reg `1' ib17.fips ib2022.year
    predict double r1, resid
    qui reg `2' ib17.fips ib2022.year
    predict double r2, resid
    di "corr after state & year FE:"
    corr r1 r2
    drop r1 r2
}

*-------------------------------------------------------------------------------
* A2.6  Cross-equation test: is the HDD coefficient equal across outcomes?
*    Stack production and allocation; interact all regressors with an outcome
*    indicator. Coef on (alloc x HDD) = (beta_alloc - beta_prod). Cluster by state
*    (12 clusters), so also report a Webb wild cluster bootstrap p-value.
*-------------------------------------------------------------------------------
foreach pair in "corn lp lx" "soy lspd lsx" {
    gettoken crop rest : pair
    gettoken prodv expv : rest
    preserve
        keep fips year `prodv' `expv' htt gtt prec prec_sq fr t t_sq
        rename `prodv' y_prod
        rename `expv'  y_exp
        reshape long y_, i(fips year) j(eqn) string
        gen byte alloc = (eqn=="exp")
        foreach v in htt gtt prec prec_sq fr t t_sq { gen double a_`v' = alloc*`v' }
        egen fo = group(fips alloc)
        egen yo = group(year alloc)
        di _n "==== Cross-equation HDD equality test: `crop' ===="
        reg y_ htt gtt prec prec_sq fr t t_sq a_* i.fo i.yo, cluster(fips)
        test a_htt = 0
        boottest a_htt, weight(webb) reps(9999) nograph
        nlcom (ratio: (_b[htt]+_b[a_htt])/_b[htt])
    restore
}

*-------------------------------------------------------------------------------
* A2.7a  HDD pass-through to ending stocks (Dec 1 level, log bushels)
*-------------------------------------------------------------------------------
eststo clear
eststo: reg lSoyStEnd  c.t c.t#c.t c.gtt c.htt c.prec c.prec#c.prec fr ib17.fips ib2022.year, cluster(year)
eststo: reg lCornStEnd c.t c.t#c.t c.gtt c.htt c.prec c.prec#c.prec fr ib17.fips ib2022.year, cluster(year)
esttab, keep(gtt htt fr) se b(%9.4f) mtitles("Soy end stk" "Corn end stk")

*-------------------------------------------------------------------------------
* A2.7b/c  Allocation with HDD x carry-in interaction, and marginal effects
*    Carry-in = March 1 stock (predetermined), centered at its mean.
*-------------------------------------------------------------------------------
foreach v in lCornStCarry lSoyStCarry {
    qui summ `v'
    cap drop `v'_c
    gen double `v'_c = `v' - r(mean)
}
* Corn allocation
reg lx  c.htt##c.lCornStCarry_c c.t c.t#c.t c.gtt c.prec c.prec#c.prec fr ib17.fips ib2022.year, cluster(year)
margins, dydx(htt) at(lCornStCarry_c = (-1 0 1))
* Soybean allocation
reg lsx c.htt##c.lSoyStCarry_c  c.t c.t#c.t c.gtt c.prec c.prec#c.prec fr ib17.fips ib2022.year, cluster(year)
margins, dydx(htt) at(lSoyStCarry_c = (-1 0 1))

*-------------------------------------------------------------------------------
* A2.8  Lagged-weather specification (ERS allocation)
*-------------------------------------------------------------------------------
tsset fips year
eststo clear
eststo: reg lx  c.t c.t#c.t c.gtt c.htt         c.prec c.prec#c.prec fr ib17.fips ib2022.year, cluster(year)
eststo: reg lx  c.t c.t#c.t c.gtt        cL.htt c.prec c.prec#c.prec fr ib17.fips ib2022.year, cluster(year)
eststo: reg lx  c.t c.t#c.t c.gtt c.htt  cL.htt c.prec c.prec#c.prec fr ib17.fips ib2022.year, cluster(year)
eststo: reg lsx c.t c.t#c.t c.gtt c.htt         c.prec c.prec#c.prec fr ib17.fips ib2022.year, cluster(year)
eststo: reg lsx c.t c.t#c.t c.gtt        cL.htt c.prec c.prec#c.prec fr ib17.fips ib2022.year, cluster(year)
eststo: reg lsx c.t c.t#c.t c.gtt c.htt  cL.htt c.prec c.prec#c.prec fr ib17.fips ib2022.year, cluster(year)
esttab, keep(htt L.htt) se b(%9.4f) star(* 0.10 ** 0.05 *** 0.01) ///
    mtitles("CornC" "CornL" "CornCL" "SoyC" "SoyL" "SoyCL")

*-------------------------------------------------------------------------------
* A2.9  Robustness to time trends (HDD coefficient per outcome)
*-------------------------------------------------------------------------------
foreach y in lp lx lspd lsx {
    di _n "==================== OUTCOME: `y' ===================="
    qui reg `y' c.gtt c.htt c.prec c.prec#c.prec fr ib17.fips ib2022.year, cluster(year)
    di "Baseline           : b=" %7.4f _b[htt] " se=" %7.4f _se[htt]
    qui reg `y' c.gtt c.htt c.prec c.prec#c.prec fr ib17.fips ib2022.year i.fips#c.t, cluster(year)
    di "State linear trends: b=" %7.4f _b[htt] " se=" %7.4f _se[htt]
    qui reg `y' c.gtt c.htt c.prec c.prec#c.prec fr ib17.fips ib2022.year i.fips#c.t i.fips#c.t#c.t, cluster(year)
    di "State quad trends  : b=" %7.4f _b[htt] " se=" %7.4f _se[htt]
}

*-------------------------------------------------------------------------------
* A2.10  Price-offset check: production in value (lp/lspd) vs quantity (lpb/lspb)
*-------------------------------------------------------------------------------
foreach pair in "lp lpb" "lspd lspb" {
    tokenize "`pair'"
    qui reg `1' c.t c.t#c.t c.gtt c.htt c.prec c.prec#c.prec fr ib17.fips ib2022.year, cluster(year)
    di "`1' (value)   : b=" %7.4f _b[htt] " se=" %7.4f _se[htt]
    qui reg `2' c.t c.t#c.t c.gtt c.htt c.prec c.prec#c.prec fr ib17.fips ib2022.year, cluster(year)
    di "`2' (quantity): b=" %7.4f _b[htt] " se=" %7.4f _se[htt]
}

*-------------------------------------------------------------------------------
* A2.11  Robustness to alternative heat thresholds (28 / 29 / 30 C)
*    Rebuild HDD at each threshold on the same bin scale as baseline htt (..45C).
*-------------------------------------------------------------------------------
cap drop htt28 htt30
gen htt28 = 0
forval i = 28/45 { replace htt28 = htt28 + time`i'C }
gen htt30 = 0
forval i = 30/45 { replace htt30 = htt30 + time`i'C }
foreach h in htt28 htt htt30 {
    di _n "================ HDD threshold: `h' ================"
    foreach y in lp lx lspd lsx {
        qui reg `y' c.t c.t#c.t c.gtt c.`h' c.prec c.prec#c.prec fr ib17.fips ib2022.year, cluster(year)
        di "`y' : b=" %7.4f _b[`h'] " se=" %7.4f _se[`h']
    }
}

*-------------------------------------------------------------------------------
* A2.12  Robustness to alternative clustering (year / state / two-way)
*-------------------------------------------------------------------------------
foreach y in lp lx lspd lsx {
    di _n "==== `y' ===="
    qui reg `y' c.t c.t#c.t c.gtt c.htt c.prec c.prec#c.prec fr ib17.fips ib2022.year, cluster(year)
    di "by year : b=" %7.4f _b[htt] " se=" %7.4f _se[htt]
    qui reg `y' c.t c.t#c.t c.gtt c.htt c.prec c.prec#c.prec fr ib17.fips ib2022.year, cluster(fips)
    di "by state: b=" %7.4f _b[htt] " se=" %7.4f _se[htt]
    qui reg `y' c.t c.t#c.t c.gtt c.htt c.prec c.prec#c.prec fr ib17.fips ib2022.year, vce(cluster fips year)
    di "two-way : b=" %7.4f _b[htt] " se=" %7.4f _se[htt]
}

* end of file
