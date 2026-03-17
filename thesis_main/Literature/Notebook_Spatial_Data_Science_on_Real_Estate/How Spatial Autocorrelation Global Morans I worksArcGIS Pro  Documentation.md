# How Spatial Autocorrelation (Global Moran's I) works—ArcGIS Pro | Documentation


Back to Top

In this topic

Calculations

Interpretation

Output

Best practices

Example applications

Additional resources

The

to evaluate the significance of that index.

P-values

Calculations

Feature values Deviations Cross-products

A=50

B=40

A=8

B=6

-2

-4

A=20

B=2

-8

-80

Interpretation

When the

p-value

returned by this tool is statistically significant, you can reject the null hypothesis. The following table summarizes the interpretation of the results:

The p-value is not statistically significant.

You cannot reject the null hypothesis. It is quite possible that the spatial distribution of feature values is the result of random spatial processes. The observed spatial pattern of feature values could very well be one of many, many possible versions of complete spatial randomness (CSR).

Note:

High/Low Clustering (General G)

tool and the

tool is complete spatial randomness. The

tool is different, however.

Output

geoprocessing messages

Best practices

The following considerations should be made when using this tool:

The  Input Feature Class  parameter value should contain at least 30 features. Results will not be reliable with less than 30 features.

Ensure that the specified  Conceptualization of Spatial Relationships  parameter value is appropriate.

standardize

.

Results from the

The Analysis of Spatial Association by Use of Distance Statistics

, and the analysis of SIDS they present.

If the  Conceptualization of Spatial Relationships  parameter's  Inverse Distance  option is used, and the inverted distances are very small.

The  Standardization  parameter is not set to the  Row  option but should be. Whenever your data has been aggregated, unless the aggregation scheme relates directly to the field you are analyzing, specify the  Row  option.

Example applications

The following are example applications of the tool:

Additional resources

The Analysis of Spatial Association by Use of Distance Statistics

." Geographical Analysis 24, no. 3. 1992.

Goodchild, Michael F.

. Catmog 47, Geo Books. 1986.

Griffith, Daniel.

. Resource Publications in Geography, Association of American Geographers. 1987.

The ESRI Guide to GIS Analysis, Volume 2.

ESRI Press, 2005.

Feedback on this topic?

In this topic

Calculations

Interpretation

Output

Best practices

Example applications

Additional resources

