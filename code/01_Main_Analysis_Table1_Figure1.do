*===============================================================================
* 01_Main_Analysis_Table1_Figure1.do
* Paper: Weather Extremes, Production Value, and Export Allocations
*        (Corn and Soybeans, U.S. Midwest, 2000-2022)
*
* Reproduces:  Main Manuscript Table 1  (weather effects on production value
*                                        and the ERS state export allocation)
*              Main Manuscript Figure 1 (residualized HDD vs log ERS allocation)
*
* Input:  Historical_Corn_Soybean_Analysis_Data_2000_2022.dta (state-year panel, 12 Midwest states)
* Output: output/Table1_main.rtf
*         output/Figure1_identifying_variation.png
*
* Notes:  Baseline spec = state FE + year FE, SE clustered by year.
*         The quadratic time trend (t, t^2) is collinear with year FE and is
*         dropped automatically; it is kept in the command only for transparency.
*===============================================================================

version 15
clear all
set more off

* ---- One editable path: point this at the folder that holds the .dta files ----
global root  "/Users/atifrao/OneDrive - Kansas State University/1 PhD Study/Kansas/KSU Study/Research/PhD Proposal/1st/Data Files"
global out   "${root}/Code Files/output"
cap mkdir "${out}"

* esttab (estout) is used to write the results table
cap which esttab
if _rc ssc install estout, replace

*-------------------------------------------------------------------------------
* 1. Load data and keep the 12 estimation states
*-------------------------------------------------------------------------------
use "${root}/Historical_Corn_Soybean_Analysis_Data_2000_2022.dta", clear
keep if inlist(fips,17,18,19,20,26,27,29,31,38,39,46,55)
xtset fips year

*-------------------------------------------------------------------------------
* 2. Weather variables (already stored in the historical data; rebuilt here for transparency)
*    time*C = hours in each 1C bin over the growing season (bins run 0C..45C).
*      GDD (gtt): cumulative exposure 0-28 C
*      HDD (htt): cumulative exposure >= 29 C
*      Prec / prec_sq: growing-season precipitation and its square
*      Fr (fr): freezing days
*-------------------------------------------------------------------------------
* Summing Growing Temp Days (0C to 28C)

drop gtt htt
gen gtt = 0
forval i = 0/28 {
    replace gtt = gtt + time`i'C
}

* Summing Heating Temp Days (29C to 44C)
gen htt = 0
forval i = 29/44 {
    replace htt = htt + time`i'C
}



cap drop prec_sq
gen prec_sq = prec^2

label variable gtt  "GDD (0-28 C)"
label variable htt  "HDD (>= 29 C)"
label variable prec "Precipitation"
label variable fr   "Freezing days"

*-------------------------------------------------------------------------------
* 3. TABLE 1 - Weather effects on production value and the ERS allocation
*    Outcomes: lp (corn prod value), lx (corn ERS), lspd (soy prod), lsx (soy ERS)
*    All logs. State + year FE. SE clustered by year.
*-------------------------------------------------------------------------------
eststo clear
eststo corn_prod: reg lp   c.t c.t#c.t c.gtt c.htt c.prec c.prec#c.prec fr ib17.fips ib2022.year, cluster(year)
eststo corn_ers : reg lx   c.t c.t#c.t c.gtt c.htt c.prec c.prec#c.prec fr ib17.fips ib2022.year, cluster(year)
eststo soy_prod : reg lspd c.t c.t#c.t c.gtt c.htt c.prec c.prec#c.prec fr ib17.fips ib2022.year, cluster(year)
eststo soy_ers  : reg lsx  c.t c.t#c.t c.gtt c.htt c.prec c.prec#c.prec fr ib17.fips ib2022.year, cluster(year)

esttab corn_prod corn_ers soy_prod soy_ers using "${out}/Table1_main.rtf", replace ///
    keep(gtt htt prec fr) order(gtt htt prec fr) ///
    b(%9.6f) se(%9.6f) star(* 0.10 ** 0.05 *** 0.01) ///
    nocons label nonumber ///
    mtitles("Corn Prod" "Corn ERS" "Soy Prod" "Soy ERS") ///
    stats(N r2 r2_a, labels("Observations" "R2" "Adj. R2")) ///
    addnotes("Standard errors clustered by year in parentheses." ///
             "State and year fixed effects included; * p<0.10, ** p<0.05, *** p<0.01.")

*-------------------------------------------------------------------------------
* 4. FIGURE 1 - Identifying variation in the ERS allocation response to heat
*    Residualize HDD and the log allocation on state FE, year FE, and the same
*    covariates, then plot. By Frisch-Waugh-Lovell the slope equals the HDD
*    coefficient in the allocation column of Table 1.
*-------------------------------------------------------------------------------
* Corn
qui reg htt c.t c.t#c.t c.gtt c.prec c.prec#c.prec fr ib17.fips ib2022.year
predict htt_res_c, resid
qui reg lx  c.t c.t#c.t c.gtt c.prec c.prec#c.prec fr ib17.fips ib2022.year
predict lx_res, resid

twoway (scatter lx_res htt_res_c, mcolor(navy%40) msize(small)) ///
       (lfit    lx_res htt_res_c, lcolor(navy) lwidth(medthick)), ///
    title("(a) Corn", size(medium)) ///
    xtitle("HDD, residual") ytitle("Log corn ERS allocation, residual") ///
    legend(off) graphregion(color(white)) name(g_corn, replace)

* Soybean
qui reg htt c.t c.t#c.t c.gtt c.prec c.prec#c.prec fr ib17.fips ib2022.year
predict htt_res_s, resid
qui reg lsx c.t c.t#c.t c.gtt c.prec c.prec#c.prec fr ib17.fips ib2022.year
predict lsx_res, resid

twoway (scatter lsx_res htt_res_s, mcolor(maroon%40) msize(small)) ///
       (lfit    lsx_res htt_res_s, lcolor(maroon) lwidth(medthick)), ///
    title("(b) Soybean", size(medium)) ///
    xtitle("HDD, residual") ytitle("Log soybean ERS allocation, residual") ///
    legend(off) graphregion(color(white)) name(g_soy, replace)

graph combine g_corn g_soy, graphregion(color(white)) ysize(3) xsize(7)
graph export "${out}/Figure1_identifying_variation.png", replace width(2200)

* end of file
