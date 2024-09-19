# Interval Cracking

## Introduntion

This paper proposes interval cracking for interval data, demonstrating its effectiveness for both "native" interval data and complex geometries. We applied the interval cracking approach to a hospital admissions dataset[^1]. Additionally, interval cracking has been used to optimize spatial databases; we extended the existing SPLindex system[^2], which combines learned indexing, clustering, and dimensionality reduction. 




## Datasets:
The data and workload should be in this format for an example two-dimensional data set.

xmin, ymin, xmax, ymax.

1- Download Hospital Admissions Data [here](https://www.kaggle.com/datasets/ashishsahani/hospital-admissions-data)
(This dataset is being provided under creative commons License (Attribution-Non-Commercial-Share Alike 4.0 International (CC BY-NC-SA 4.0)) <a href="https://creativecommons.org/licenses/by-nc-sa/4.0/">https://creativecommons.org/licenses/by-nc-sa/4.0/</a>)

2- Download Water dataset [here](https://osmdata.openstreetmap.de/data/water-polygons.html)

3- Download Lakes and Roads datasets [here](https://spatialhadoop.cs.umn.edu/datasets.html)

## References:

[^1]: Bollepalli, S.C.; Sahani, A.K.; Aslam, N.; Mohan, B.; Kulkarni, K.; Goyal, A.; Singh, B.; Singh, G.; Mittal, A.; Tandon, R.; Chhabra, S.T.; Wander, G.S.; Armoundas, A.A. An Optimized Machine Learning Model Accurately Predicts In-Hospital Outcomes at Admission to a Cardiac Unit. Diagnostics 2022, 12, 241. https://doi.org/10.3390/diagnostics12020241

[^2]: M. Vahedi and H. Christiansen, “Splindex: A spatial polygon learned index,” in International Symposium on Methodologies for Intelligent Systems. Springer, 2024, pp. 271–281.

