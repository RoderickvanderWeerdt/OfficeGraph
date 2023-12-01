from rdflib import Graph, Namespace, RDF, RDFS, XSD, Literal, URIRef
from datetime import datetime

round_value_decimal = 1

saref = Namespace("https://saref.etsi.org/core/")
ic = Namespace("https://interconnectproject.eu/example/")

import os

def get_files_by_ext(path_to, ext, add_path):
	filenames = []
	for fn in [doc for doc in os.listdir(path_to)]:
		if fn.endswith(ext):
			if add_path: filenames.append(path_to+fn)
			else: filenames.append(fn)
	print("found", len(filenames), "files of type \"{}\"".format(ext))
	return filenames

def get_turtle_files(path_to, add_path=False):
	return get_files_by_ext(path_to, ".ttl", add_path)

class Measurent():
	def __init__(self, meas_uri, device_uri):
		self.meas_uri = meas_uri
		self.device_uri = device_uri
		self.timestamp = None
		self.value = None
		# self.previous = None
		# self.next = None

	def set_timestamp(self, timestamp):
		self.timestamp = timestamp.value
		self.calc_rounded_timestamp()

	def set_value(self, val):
		self.value = val.value
		self.calc_rounded_value()

	def calc_rounded_timestamp(self): #removes the minutes, in order to get an "hour bucket" timestamp
		self.timestamp_rounded = datetime(self.timestamp.year, self.timestamp.month, self.timestamp.day, self.timestamp.hour)

	def calc_rounded_value(self):
		self.value_rounded = round(self.value, round_value_decimal)

def is_work_day(td):
	if td.weekday() <= 4: return True
	else: return False

def is_work_hours(td):
	if is_work_day(td) and td.hour >= 9 and td.hour <17:
		# print(td)
		return 1
	else:
		return 0

def add_extra_triples(graph_fn, new_graph_name, add_timestamp, add_rounded_val, add_sequence):
	g = Graph()
	g.parse(graph_fn)

	knows_query = """
	PREFIX saref: <https://saref.etsi.org/core/>

	SELECT DISTINCT ?dev ?meas ?timestamp ?val
	WHERE {
	    ?dev saref:makesMeasurement ?meas .
	    ?meas saref:hasTimestamp ?timestamp .
	    ?meas saref:hasValue ?val
	}"""

	measurements = []
	qres = g.query(knows_query)
	for row in qres:
	    measurements.append(Measurent(row.meas, row.dev))
	    measurements[-1].set_timestamp(row.timestamp)
	    measurements[-1].set_value(row.val)

	measurements.sort(key= lambda x: x.timestamp)

	g = Graph()
	g.bind("saref", "https://saref.etsi.org/core/")
	g.bind("ic", "https://interconnectproject.eu/example/")

	# entity_csv_lines = ["rounded_timestamp,timestamp_uri,workhours"]
	entities = []
	previous_meas = None
	for measurement in measurements:
		if add_sequence:
			if previous_meas != None:
				# measurement.previous = previous_meas.meas_uri
				# previous_meas.next = measurement.meas_uri
				g.add((measurement.meas_uri, ic.previous_node, previous_meas.meas_uri))
				g.add((previous_meas.meas_uri, ic.next_node, measurement.meas_uri))
			previous_meas = measurement

		if add_timestamp:
			timestamp_str = str(measurement.timestamp_rounded).replace(':', '').replace(' ', '_')
			g.add((measurement.meas_uri, ic.measuredAtTime, ic[timestamp_str]))
			g.add((ic[timestamp_str], ic.measuredDuring, measurement.meas_uri))

		if add_rounded_val:
			rounded_val = "rounded_value_"+str(measurement.value_rounded)
			g.add((measurement.meas_uri, ic.hasRoundedValue, ic[rounded_val]))
			g.add((ic[rounded_val], ic.ofMeasurement, measurement.meas_uri))

		# entity_csv_lines.append(str(measurement.timestamp_rounded)+","+str(ic[timestamp_str])+","+str(is_work_hours(measurement.timestamp)))
		entities.append(measurement.timestamp_rounded)


	g.serialize(destination=new_graph_name, format='turtle')
	print("created: ", new_graph_name)

	return entities
	# entity_csv_lines_header = entity_csv_lines[0]
	# entity_csv_lines = list(set(entity_csv_lines[1:]))
	# entity_csv_lines = [entity_csv_lines_header]+entity_csv_lines
	# with open(new_entity_fn, 'w') as csv_file:
	# 	for line in entity_csv_lines:
	# 		csv_file.write(line+'\n')

def add_extra_triples_folder(folder_name, folder_name_extra, new_entity_fn, add_timestamp=True, add_rounded_val=True, add_sequence=True):
	ttl_files = get_turtle_files(folder_name)
	# print(ttl_files)

	all_entities = []
	for graph_fn in ttl_files:
		new_graph_name = graph_fn[:-4] + "_extra.ttl"
		entities = add_extra_triples(folder_name+graph_fn, folder_name_extra+new_graph_name, add_timestamp, add_rounded_val, add_sequence)
		all_entities = list(set(all_entities+entities))
	print(len(all_entities))
	entity_csv_lines = ["rounded_timestamp,timestamp_uri,workhours"]
	for entity in all_entities:
		timestamp_str = str(entity).replace(':', '').replace(' ', '_')
		entity_csv_lines.append(str(entity)+","+str(ic[timestamp_str])+","+str(is_work_hours(entity)))
	with open(new_entity_fn, 'w') as csv_file:
		for line in entity_csv_lines:
			csv_file.write(line+'\n')

if __name__ == '__main__':
	if True:
		folder_name = "floor7_graphs/"
		folder_name_extra = "floor7_graphs_extra_001/"
		folder_name_extra = "floor7_graphs_extra/"
		new_entity_fn = "entities.csv"
		big_graph_name = "big_graph_001.ttl"
		big_graph_name = "big_graph.ttl"
	else:
		# graph_fn = "urn_Device_SmartThings_a1694cb0-55ba-4a3d-9f11-d9456faac8c0.ttl"
		# graph_fn = "samsung_graphs_short_names/"+"urn_Device_SmartThings_9e5f409b-3052-4b07-b19d-8534ad93cdf0.ttl"
		new_entity_fn="entityfile_small.csv"
		folder_name = "small_graphs/"
		folder_name_extra = "small_graphs_extra/"
		big_graph_name = "small_graph.ttl"
		# ttl_files = ["urn_Device_SmartThings_a1694cb0-55ba-4a3d-9f11-d9456faac8c0.ttl", "urn_Device_SmartThings_9e5f409b-3052-4b07-b19d-8534ad93cdf0.ttl"]


	add_extra_triples_folder(folder_name, folder_name_extra, new_entity_fn, True, True, True) #enriched version
	# add_extra_triples_folder(folder_name, folder_name_extra, new_entity_fn, True, False, False) #basic version


	g = Graph()
	ttl_files = get_turtle_files(folder_name)
	for graph_fn in ttl_files:
		g.parse(folder_name+graph_fn)
		new_graph_name = graph_fn[:-4] + "_extra.ttl"
		g.parse(folder_name_extra+new_graph_name)
		print("added", graph_fn, "to the graph.")
	g.serialize(destination=big_graph_name, format='turtle')
