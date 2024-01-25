# OfficeGraph

OfficeGraph is a large, real world knowledge graph containing measurements taken by 444 IoT devices, over 11 months, in a seven story office building. The devices are made up of 17 different sensor models, which make measurements of many different properties.

This is a zipped version of OfficeGraph. Instead of one file containing the entire knowledge graph the zipped folders contains a separate file for each individual device. Each file contains all the measurements made by the device.

The _devices in room_ enrichment adds more information about which devices are located in which rooms, and on which floor those rooms are.<br>
The _Wikidata days_ enrichment provides a link to Wikidata, by matching the dates of the measurements to those dates' entities in Wikidata.<br>
The _graph learning_ enrichment provides additional properties that have beneficial effects on the learning process when using graph embedding models.<br>
The enrichments are included in separate files, with the graph learning enrichment only containing the enrichments for the devices on the 7th floor, which were used in the machine learning experiment (the code of this experiment is available [here](https://github.com/RoderickvanderWeerdt/semantic-enrichment-of-IoT-graphs/tree/main/OfficeGraph).

All scripts used to create the dataset from the original json files are available in the [mapping scripts](https://github.com/RoderickvanderWeerdt/OfficeGraph/tree/main/mapping%20scripts) folder and an example of the raw data is supplied in the [mapping example](https://github.com/RoderickvanderWeerdt/OfficeGraph/tree/main/mapping%20example) folder.

## About OfficeGraph

OfficeGraph is expressed in the [saref](https://saref.etsi.org) ontology, a domain standard model specifically created to model measurements of different IoT devices. The main structure we used from saref can be seen in the follow figure.
![Office Graph Main Structure](https://github.com/RoderickvanderWeerdt/OfficeGraph/blob/main/img/officeGraph_overview.png)
For each individual device the “device template” creates triples for all consistent information about the device, such as the device type and model. For each individual measurement the “measurement template” creates triples to describe the measurement, its value, unit of measurement and timestamp. The device instance and measurement instances are connected in two ways, directly through the saref:makesMeasurement property, and indirectly through the sasref:Property instance. The latter describes what has been measured, such as temperature or humidity.
In addition to the saref ontology we use two of its extensions. [saref4bldg](https://saref.etsi.org/saref4bldg/v1.1.2/), which provides classes used to describe the relation between devices and rooms, and between rooms and buildings. The other extension is [saref4ener](https://saref.etsi.org/saref4ener/v1.1.2/), which provides additional classes for information about the device. As suggested in the saref documentation the om1.8 ontology is used to represent the units of measure of the measurements.

## Using OfficeGraph

- **Zenodo**: The dataset is archieved on Zenodo, including the raw json files used to create OfficeGraph. [DOI 10.5281/zenodo.10245814](https://zenodo.org/records/10566775)<br/>
- **Live SPARQL endpoint**: OfficeGraph is available as a live triplestore and can be queries throug a [YASGUI editor](https://data.interconnect.labs.vu.nl/yasgui/index.html), and directly with the endpoint: [https://data.interconnect.labs.vu.nl/sparql](https://data.interconnect.labs.vu.nl/sparql).<br/>
- **Jupyter notebook examples**: Examples of using the endpoint are available in this repository: [Data analytics cases](https://github.com/RoderickvanderWeerdt/OfficeGraph/tree/main/data%20analytics%20use%20cases).<br/>


The resource paper describing this dataset is currently under submission.


Shield: [![CC BY 4.0][cc-by-shield]][cc-by]

This work is licensed under a
[Creative Commons Attribution 4.0 International License][cc-by].

[![CC BY 4.0][cc-by-image]][cc-by]

[cc-by]: http://creativecommons.org/licenses/by/4.0/
[cc-by-image]: https://i.creativecommons.org/l/by/4.0/88x31.png
[cc-by-shield]: https://img.shields.io/badge/License-CC%20BY%204.0-lightgrey.svg
