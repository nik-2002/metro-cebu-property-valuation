# Spatial Autocorrelation (Global Moran's I) (Spatial Statistics)—ArcGIS Pro | Documentation


Back to Top

In this topic

Summary

Illustration

Usage

Parameters

Environments

Summary

Illustration

Usage

messages

The

and

p-value

aggregating the incident data

. You can also use the

Optimized Hot Spot Analysis

tool to analyze the spatial pattern of incident data.

Note:

environment is set to a

Caution:

Ensure that

you project the data

When

. The following are additional tips:

Distance band (sphere of influence)

.

Result

Generate Spatial Weights Matrix

tool. To use these additional options, construct a

spatial weights matrix file

Map layers can be specified as the  Input Feature Class  parameter value. When using a layer with a selection, only the selected features will be included in the analysis.

If you provide a  Weights Matrix File  parameter value with a  .swm  extension, it is expected that a spatial weights matrix file will be created using the

Generate Spatial Weights Matrix

tool; otherwise, an

Weights will be used as is. Missing feature-to-feature relationships will be treated as zeros.

Generate Spatial Weights Matrix

tool.

Running an analysis with an

. First, put the ASCII weights into a

Generate Spatial Weights Matrix

Note:

Row standardization

Modeling spatial relationships

help topic.

Caution:

Parameters

Label Explanation Data Type Input Feature Class

Feature Layer Input Field

Specifies whether a graphical summary of result will be created as an  .html  file.

Checked—A graphical summary will be created.

Unchecked—No graphical summary will be created. This is the default.

Boolean Conceptualization of Spatial Relationships

Specifies how spatial relationships among features will be defined.

Get spatial weights from file — Spatial relationships are defined by a specified spatial weights file. The path to the spatial weights file is specified by the  Weights Matrix File  parameter.

String Distance Method

Euclidean — The straight-line distance between two points (as the crow flies) will be used. This is the default.

String Standardization

None — No standardization of spatial weights will be applied.

.

Double Weights Matrix File (Optional)

Long

Derived Output

Label Explanation Data Type Index

The

.

Double PValue

The

p-value

.

An HTML file with a graphical summary of results.

File Derived Input Dataset

The input features of the tool.

Feature Layer

Feature Layer Input_Field

Specifies whether a graphical summary of result will be created as an  .html  file.

Boolean Conceptualization_of_Spatial_Relationships

Specifies how spatial relationships among features will be defined.

GET_SPATIAL_WEIGHTS_FROM_FILE — Spatial relationships are defined by a specified spatial weights file. The path to the spatial weights file is specified by the  Weights_Matrix_File  parameter.

String Distance_Method

EUCLIDEAN_DISTANCE — The straight-line distance between two points (as the crow flies) will be used. This is the default.

String Standardization

NONE — No standardization of spatial weights will be applied.

.

Double Weights_Matrix_File (Optional)

Long

Derived Output

Name Explanation Data Type Index

The

.

Double PValue

The

p-value

.

An HTML file with a graphical summary of results.

File Derived_Input_Dataset

The input features of the tool.

Feature Layer

Code sample

Environments

,

,

,

Special cases

Basic: Yes

Standard: Yes

Advanced: Yes

Related topics

An overview of the Analyzing Patterns toolset

Modeling spatial relationships

Find a geoprocessing tool

Spatial weights

Feedback on this topic?

In this topic

Summary

Illustration

Usage

Parameters

Environments

