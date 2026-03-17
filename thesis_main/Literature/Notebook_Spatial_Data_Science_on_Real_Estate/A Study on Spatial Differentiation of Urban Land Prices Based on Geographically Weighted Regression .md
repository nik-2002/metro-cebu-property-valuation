# A Study on Spatial Differentiation of Urban Land Prices Based on Geographically Weighted Regression Models - International Journal for Housing Science and Its Applications


Skip to content

Menu

On this page

Research article

Volume 45, Issue 4

Pages: 1

-15

Download

A Study on Spatial Differentiation of Urban Land Prices Based on Geographically Weighted Regression Models

By:

Qiuyu Liu

,

Lina Zhang

,

Hui Wang

,

Huangzhen Lv

,

Yakai He

,

Yan Wang

School of Business, The Chinese University of Hong Kong, HKSAR, 999077, Hong Kong

Chinese Academy of Agricultural Mechanization Sciences Group Co., Ltd., Beijing, 100083, China

Published: 30/12/2024

I. Introduction

1,2

].

3-5

6-9

]. In contrast, the spatial variable coefficient regression model, i.e., geographically weighted regression (GWR), allows different spatial relationships to exist in different geographic spaces, which largely reveals the spatial dependence and spatial non-smoothness of geographic phenomena [

10-12

13-15

].

Mou et al. [

].

II. A. 1) Analysis of space data structures

II. A. 2) Trend analysis

To observe trends that exist in a particular direction, a line of best fit can be made through the projected points. If the line is flat, it indicates that no trend exists. Trend analysis is a simple and intuitive way to understand the spatial distribution of things.

].

II. A. 4) Spatial heterogeneity

II. B. Steps in geostatistical analysis

Geostatistics is a method of unbiased valuation of regionalized variables at future sampling points using the structural nature of the raw data and the semivariance function. Geostatistical analysis is generally divided into the following 3 steps:

Calculate the value of the variance function and fit the variance function curve.

II. B. 1) Variational functions

Figure 1 Variograms model

II. B. 2) Kriging space interpolation

].  \[\label{GrindEQ__7_} \bar{Z}(X_{o} )=\sum _{i=1}^{n}\lambda _{i} Z(X_{i} ) . \tag{7}\]

Taking the point interpolation as an example, the kriging system equations can be derived based on unbiased estimation and variance minimization:  \[\label{GrindEQ__8_} \sum _{i=1}^{n}\lambda _{i} \gamma (X_{i} ,X_{j} )+\psi =\gamma (X_{i} ,X_{o} )\sum _{i=1}^{n}\lambda _{i} =1 . \tag{8}\]

By combining the above two equations, the weighting coefficients can be calculated, and once the weighting coefficients are determined, an estimate of the interpolated  \(\bar{Z}(X_{o} )\)  can be obtained.

II. C. Geographically weighted regression models

II. C. 1) Principles of GWR modeling

]. The extended geographically weighted regression model is as follows:  \[\label{GrindEQ__9_} y_{i} =\beta _{0} (u_{i} ,v_{i} )+\sum _{k}\beta _{k} (u_{i} ,v_{i} )x_{ik} +\varepsilon _{i} ,i=1,2,……,n . \tag{9}\]

In the above equation,  \(W(u_{i} ,v_{i} )\)  represents the weight matrix of sample point  \(i\)  as follows:  \[\label{GrindEQ__12_} W(u_{i} ,v_{i} )=\left\{\begin{array}{cccc} {w_{i1} } & {0} & {…} & {0} \\ {0} & {w_{i2} } & {…} & {0} \\ {…} & {…} & {…} & {…} \\ {0} & {0} & {…} & {w_{in} } \end{array}\right\} . \tag{12}\]

The Bi-square function defines the spatial weight of the data points outside bandwidth  \(b\)  as 0, and the spatial weight of sample point  \(j\)  is derived by a finite Gaussian function within bandwidth  \(b\)  of regression point  \(i\) . As the bandwidth gets smaller, the spatial weights decay faster with increasing distance, and as the bandwidth gets larger, the spatial weights decay slower with increasing distance. As the distance approaches bandwidth  \(b\) , the spatial weights of nearby data points converge to 0, so that there is no steep change as an inverse function of distance.

III. Characterization of spatial differentiation of land prices in typical cities

III. A. Overview of the study area and data

III. A. 1) Overview of the study area

III. A. 2) Data sources and processing

Figure 2 Distribution of residential land price samples in the study area

III. B. 1) Analysis of spatial data structures

Table 2 Descriptive statistical analysis of urban land price   Number of samples   Minimum   Maximum   Mean   Standard deviation   107   4051.2   352241.8   12553   5875.49   Skewness   Kurtosis   First quartile   Median   Third quartile   1.1795   3.7852   8281   11521   15223  Figure 3 Spatial data distribution of land prices in the study area

III. B. 2) Trend analysis

Figure 5 Land price trend in the study area

Figure 6 A local scatter plot of the study area

III. C. Geostatistics-based analysis of spatial differentiation of land prices

Figure 7 Digital model of land price in the study area

IV. A. Impact analysis of spatial differentiation of land prices based on LR modeling

The linear regression model expression is given below:  \[\begin{aligned} \label{GrindEQ__18_} Y_{i} =&6331.7552-3.2285X_{ZGD} -0.1601X_{XX} +0.4771X_{GJ} -1.5502X_{YY} \notag \\ &{-0.5233X_{SH} -0.3245X_{LD} -2.1596RJL}. \end{aligned} \tag{18}\]

IV. B. Impact analysis of spatial differentiation of land prices based on GWR modeling

IV. B. 1) GWR Modeling

IV. B. 2) GWR model calculations

Table 5 Descriptive statistics of GWR model calculation results   Parameter   Min   Q\(\_1\)   Median   Q\(\_3\)   Max   Mean   S   Intercept   3873.32   5265.41   6061.29   6726.50   7312.49   5898.98   928.95   D-ZGD   -6.5386   -5.0107   -4.1366   -2.1446   4.6564   -3.1362   2.6974   D-XX   -2.1882   -0.696   0.0324   0.245   1.4253   -0.2954   0.9007   D-DJ   -1.7898   -0.1021   0.4522   1.0644   2.3889   0.4718   0.864   D-YY   -3.0454   -2.5582   -2.1929   -1.3136   0.2589   -1.8208   0.9578   D-SH   -1.2632   -0.9151   -0.2869   0.1584   1.975   -0.2977   0.6823   D-LD   -2.5056   -0.5659   -0.3715   -0.2812   -0.0178   -0.5246   0.4687   RJL   -197.550   111.9701   140.5295   179.8499   232.0199   122.5385   89.6968   Table 6 Significance after Monto Carlo test   Parameter   P   significance level   Intercept   0.0000   ***   D-ZGD   0.0048   **   D-XX   0.0355   *   D-DJ   0.4552   n/s   D-YY   0.0388   *   D-SH   0.1665   n/s   D-LD   0.1261   n/s   RJL   0.0018   ***

Influence of main roads on residential land prices

Figure 8 Road impact on residential land price

Impact of Schools on Residential Land Prices

Figure 9 School impact on residential land price

Relationship between plot ratio and land price

Figure 10 Volume rate impact on residential land price

V. Conclusion

Funding

References

Qiu R, Xu W, Zhang J, Staenz K. Modeling and simulating industrial land-use evolution in Shanghai, China. Journal of Geographical Systems. 2018 Jan;20:57-83.

Chen F, Leung Y, Wang Q, Zhou Y. Spatial non-stationarity test of regression relationships in the multiscale geographically weighted regression model. Spatial Statistics. 2024 Jun 13:100846.

An P, Li C, Duan Y, Ge J, Feng X. Inter-metropolitan land price characteristics and pattern in the Beijing-Tianjin-Hebei urban agglomeration, China. Plos one. 2021 Sep 1;16(9):e0256710.

Lan F, Wu Q, Zhou T, Da H. Spatial effects of public service facilities accessibility on housing prices: A case study of Xi’an, China. Sustainability. 2018 Nov 29;10(12):4503.

Submit Article

Article Processing Charges

