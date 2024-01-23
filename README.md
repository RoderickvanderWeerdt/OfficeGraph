# OfficeGraph

OfficeGraph is a large, real world knowledge graph containing measurements taken by 444 IoT devices, over 11 months, in a seven story office building. The devices are made up of 17 different sensor models, which make measurements of many different properties.

This is a zipped version of OfficeGraph. Instead of one file containing the entire knowledge graph the zipped folders contains a separate file for each individual device. Each file contains all the measurements made by the device.

The _devices in room_ enrichment adds more information about which devices are located in which rooms, and on which floor those rooms are.<br>
The _Wikidata days_ enrichment provides a link to Wikidata, by matching the dates of the measurements to those dates' entities in Wikidata.<br>
The _graph learning_ enrichment provides additional properties that have beneficial effects on the learning process when using graph embedding models.<br>
The enrichments are included in separate files, with the graph learning enrichment only containing the enrichments for the devices on the 7th floor, which were used in the machine learning experiment (the code of this experiment is avaible [here](https://github.com/RoderickvanderWeerdt/semantic-enrichment-of-IoT-graphs/tree/main/OfficeGraph).

All scripts used to create the dataset from the original json files are available in the _mapping scripts_ folder. 

The resource paper describing this dataset is currently under submission.

Shield: [![CC BY 4.0][cc-by-shield]][cc-by]

This work is licensed under a
[Creative Commons Attribution 4.0 International License][cc-by].

[![CC BY 4.0][cc-by-image]][cc-by]

[cc-by]: http://creativecommons.org/licenses/by/4.0/
[cc-by-image]: https://i.creativecommons.org/l/by/4.0/88x31.png
[cc-by-shield]: https://img.shields.io/badge/License-CC%20BY%204.0-lightgrey.svg
