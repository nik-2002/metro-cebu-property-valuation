# **Chapter 2 | Review of Related Literature** 

## **2.1 Purpose**

This chapter reviews the existing literature on data‑driven property valuation in the Philippines, with Cebu as the focus. It explains the main ideas we use, the usual factors that affect value, and how tools like RPPI/REPI and BIR zonal values describe price movements.

We also connect these ideas to Cebu’s recent housing situation so the discussion is not too abstract. In the end, we point out a gap: there are still very few Cebu‑specific, multi‑source, property‑level models that are simple to run and repeat. Our study seeks to help fill this gap. The next sections start with basic concepts, then move to the Cebu context, and then to the models and results we build on.

## **2.2 Core concepts**

Market value is the most probable price under fair, open‑market conditions on the valuation date. Market price is the amount actually paid in a specific deal. These two can differ in practice (Philippine Valuation Standards \[PVS\], 2018). An appraisal is a written opinion of value for a specific property and date. It uses market‑based approaches such as the sales comparison, income, and cost approaches. Land valuation focuses on the land part only and sets aside the improvements (PVS, 2018). Highest and Best Use (HBU) is the use that is legally allowed, physically possible, financially feasible, and gives the highest value (International Valuation Standards \[IVS\], 2020).

The Bureau of Internal Revenue (BIR) issues zonal values mainly for tax bases, such as capital gains tax (CGT) and documentary stamp tax (DST). These values are not live market prices (BIR, n.d.). For market‑level context, the Bangko Sentral ng Pilipinas (BSP) publishes the Residential Real Estate Price Index (RREPI, often called RPPI), with sub‑indices including Metro Cebu. The Real Estate Price Index (REPI) is a proposed Philippine framework that aims to address gaps in zonal‑based valuation (BSP, 2025; National Statistical Coordination Board \[NSCB\], n.d.).

In this study we treat indices and official schedules as context, not as appraisals. RREPI/RPPI show how prices move over time. REPI seeks to measure prices using more transaction sources. Local Government Unit (LGU) assessments and BIR zonal values are mainly administrative benchmarks and not real‑time prices (BSP, 2025; Domingo & Fulleros, 2005; NSCB, n.d.; Eurostat, 2013; BIR, n.d.; PVS, 2018). These basic ideas provide the terms we use when we discuss Cebu and Philippine housing in the next section.

## **2.3 Cebu and PH context**

Residential prices continued to rise through Q2 2025, but the growth was slower than in late 2024\. House prices moved more steadily than condo prices. Cebu generally followed the pattern of Areas Outside the National Capital Region (AONCR), with stronger movements near major employment centers (BSP, 2025). Cebu’s demand reflects Information Technology–Business Process Management (IT‑BPM) jobs, tourism recovery, and remittances. Access projects like the Cebu Bus Rapid Transit (BRT) and expressway corridors also help support land values. At the same time, zoning rules and flood risk still influence how different areas behave (Cebu Daily News, 2024; Cushman & Wakefield, 2024).

Higher borrowing costs and higher inflation in 2024–2025 affected housing affordability and how developers timed their projects in both the National Capital Region (NCR) and AONCR. Listing data and market reports show wider price differences across barangays in Cebu (Philippine News Agency, 2025; Cushman & Wakefield, 2024). This broader view helps explain why some drivers matter more than others in Cebu. The next subsection moves from these overall trends to the main property‑level drivers that other studies have found.

## **2.4 Main drivers of value**

Given this setting, the literature points to several main drivers of land and property values. Price levels tend to be higher when access is better and travel time is shorter to Central Business Districts (CBDs), ports or the airport, and mass‑transit or major roads. This pattern appears along Cebu’s BRT and expressway corridors (Determinants of Land Values in Cebu City, 2020; Cebu Daily News, 2024). Neighborhood services and utilities, such as schools, hospitals, retail, and basic water and power, raise desirability. Noise and safety issues reduce it (Determinants of Land Values in Cebu City, 2020).

Site traits such as lot area, usable shape and frontage, corner exposure, slope or elevation, and flood or landslide risk affect both value and how easy it is to sell a lot (Determinants of Land Values in Cebu City, 2020; Top 10 Factors on Property Value in PH, n.d.). Where there are building improvements, floor area, build quality, age, layout, parking, and maintenance condition also matter in many studies (Malpezzi, 2003). Title clarity, right‑of‑way and easements, and zoning compliance help reduce uncertainty and discounts (PVS, 2018; IVS, 2020). Interest rates, inflation, and local supply and demand conditions change buyer budgets and price differences. Recent RREPI/RPPI reports and news articles reflect these shifts (BSP, 2025; Philippine News Agency, 2025; Cushman & Wakefield, 2024).

These drivers later become the concrete variables that models use as predictors. The next subsection looks at how different studies, in the Philippines and abroad, actually build price models using these kinds of inputs.

## 

## **2.5 Modeling lenses and related work**

Classical work on property valuation treats price as the result of many attributes. Hedonic regression models show how structural and locational features enter the price, usually in a linear or log‑linear form (Rosen, 1974; Malpezzi, 2003). Spatial econometrics adds terms for neighborhood effects when nearby prices move together. This is important in dense cities where locations influence each other (Anselin, 1988). For the Philippines, studies on Metro Manila use hedonic and spatial models and find that structural variables, environmental or service variables, and spatial spillovers all help explain variation in prices and rents (Dann et al., 2020).

More recent Philippine work starts to add machine learning. One study for Central Pangasinan combines BIR zonal values, the BSP price index, and a construction cost index, then compares multiple linear regression with Random Forest. The tree‑based model has lower error (Viray, 2023). Another paper tests the effect of adding government indicators to standard features and finds that these public indicators improve machine‑learning valuation accuracy (Ramolete et al., 2023). A preprint on Manila listings compares linear models with gradient boosting and reports that gradient boosting performs best after feature selection (Perdio et al., 2023).

International reviews and case studies show a similar pattern. Machine‑learning models, especially tree‑based ensembles such as Random Forest and gradient boosting, often perform better than hedonic regressions in terms of prediction error. Hedonic models remain easier to interpret and explain (Breiman, 2001; Friedman, 2001; Chen & Guestrin, 2016; Sharma et al., 2024; Weng, 2022; Utomo et al., 2024; Moreno‑Foronda et al., 2025). Taken together, these studies give us a menu of features and methods. The next subsection sums up what they tend to agree on before we state the remaining gap.

## 

## **2.6 What the literature agrees on**

Across sources, several points are consistently highlighted. Access to jobs and transport matters a lot. Areas near major roads or BRT nodes tend to have higher prices. Basic services and neighborhood amenities raise value. Flood and slope risk lower it. Clear title and zoning reduce discounts. Submarkets exist inside cities, so barangay or corridor effects still show up even after we control for other variables (Determinants of Land Values in Cebu City, 2020; PVS, 2018; BSP, 2025). These patterns are consistent across both hedonic and machine‑learning studies and prepare us to identify what is still missing.

## **2.7 The gap**

Taken together, these studies show that there is still no Cebu‑focused, multi‑source model that works at the property level and is easy to run. RREPI/RPPI give trends. REPI sketches a national framework. Prior Philippine studies using machine learning are either limited in coverage or focus on other cities. None of them deliver an open, repeatable tool for Cebu pricing (BSP, 2025; Domingo & Fulleros, 2005; Ramolete et al., 2023). Our thesis responds to this by designing and testing a practical valuation model for Cebu that follows these lessons but is grounded in local data.

## **2.8 Bridge to methods**

To sum up, the literature gives us the key concepts, Cebu context, main drivers, and a set of modeling approaches that work reasonably well. It also shows the gap in Cebu‑specific tools that can be used in practice. Next, Chapter 3 explains our data, how we build features (location, access, risk, title, structure, market context), and the models we will test using the ideas above.

