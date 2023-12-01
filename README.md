# OfficeGraph

OfficeGraph is a large, real world knowledge graph containing measurements taken by 444 IoT devices, over 11 months, in a seven story office building. The devices are made up of 17 different sensor models, which make measurements of many different properties.

This is a zipped version of OfficeGraph. Instead of one file containing the entire knowledge graph the zipped folders contains a separate file for each individual device. Each file contains all the measurements made by the device.
The enrichments are included in separate files, with the graph learning enrichment only containing the enrichments for the devices on the 7th floor, which were used in the machine learning experiment (the code of this experiment is avaible [here](https://github.com/RoderickvanderWeerdt/semantic-enrichment-of-IoT-graphs/tree/main/OfficeGraph).

All scripts used to create the dataset from the original json files are available in the _mapping scripts_ folder. 

The resource paper describing this dataset is currently under submission.
