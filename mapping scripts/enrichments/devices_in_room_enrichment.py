import pandas as pd
from rdflib import Graph, Namespace, RDF, RDFS, XSD, Literal
import re
import pickle

ic = Namespace("https://interconnectproject.eu/example/")
saref = Namespace("https://saref.etsi.org/core/")
s4ener = Namespace("https://saref.etsi.org/saref4ener/")
s4bldg = Namespace("https://saref.etsi.org/saref4bldg/")
device_not_in_dic_counter = 0

def create_rooms_dict(room_files, device_name_dict, device_not_in_dic_counter):
	new_rooms_dict = {"device_URI": [], "floor_URI": [], "support_zone_URI": [], "room_number": []}
	descr_of_room_id = "Kamer nummer " #if "Linked Thing" includes the room number, this is used to find it.
	for room_file in room_files:
		room_df = pd.read_csv(room_file, sep=";")
		floor_number = re.findall(r'\d+',room_file)[0] #works with filenames that include only one digit, which is the floor number
		floor_URI = ic["VL_floor_"+floor_number]
		for device, linked_thing in zip(room_df["Device Serial"], room_df["Linked Thing"]):
			linked_thing = str(linked_thing).replace(":", "")
			# new_rooms_dict["device_URI"].append(ic["device_"+device.replace(' ', '_')])
			# print()
			try:
				new_rooms_dict["device_URI"].append(ic[device_name_dict[str(ic["device_"+device.replace(' ', '_')])]])
			except:
				device_not_in_dic_counter+=1
				continue
				new_rooms_dict["device_URI"].append(ic["device_"+device.replace(' ', '_')])
			new_rooms_dict["floor_URI"].append(floor_URI)

			support_zone = room_df.loc[room_df['Device Serial'] == device]["Description"].to_string(index=False)
			if support_zone.startswith("VL"):
				new_rooms_dict["support_zone_URI"].append(ic["zone_"+support_zone.replace(' ', '_')])
			else:
				new_rooms_dict["support_zone_URI"].append("")

			if linked_thing.find(descr_of_room_id) != -1:
				new_rooms_dict["room_number"].append(linked_thing[linked_thing.find(descr_of_room_id)+len(descr_of_room_id):])
				if new_rooms_dict["support_zone_URI"][-1] == "":
					new_rooms_dict["support_zone_URI"][-1] = ic["zone_"+linked_thing[:linked_thing.find(descr_of_room_id)-1].replace(' ', '_')]
			else:
				new_rooms_dict["room_number"].append('')

			if new_rooms_dict["support_zone_URI"][-1] == "":
				if linked_thing != "" and linked_thing != "nan":
					linked_thing = linked_thing.replace(' ', '_')
					new_rooms_dict["support_zone_URI"][-1] = ic["zone_"+linked_thing.replace(' ', '_')]
				elif support_zone != "" and support_zone != "nan":
					support_zone = support_zone.replace(' ', '_')
					new_rooms_dict["support_zone_URI"][-1] = ic["zone_"+support_zone.replace(' ', '_')]

			if support_zone == "":
				print("room not found")
				exit()
	return new_rooms_dict, device_not_in_dic_counter

def create_rooms_graph(rooms_dict, new_graph_fn="devices_in_rooms_November.ttl"):
	g = Graph()
	g.bind("ic", "https://interconnectproject.eu/example/")
	g.bind("saref", "https://saref.etsi.org/core/")
	g.bind("s4ener", "https://saref.etsi.org/saref4ener/")
	g.bind("s4bldg", "https://saref.etsi.org/saref4bldg/")

	for device, floor, support_zone, room_number in zip(rooms_dict["device_URI"], rooms_dict["floor_URI"], rooms_dict["support_zone_URI"], rooms_dict["room_number"]):
		g.add((support_zone, RDF.type, s4bldg.BuildingSpace))
		g.add((support_zone, s4bldg.contains, device))
		g.add((device, s4bldg.isContainedIn, support_zone))
		g.add((support_zone, RDFS.comment, Literal("support_zone")))
		g.add((support_zone, s4bldg.isSpaceOf, floor))
		if room_number != "":
			g.add((ic["roomname_"+str(room_number)], RDF.type, s4bldg.BuildingSpace))
			g.add((ic["roomname_"+str(room_number)], s4bldg.contains, device))
			g.add((device, s4bldg.isContainedIn, ic["roomname_"+str(room_number)]))
			g.add((ic["roomname_"+str(room_number)], RDFS.comment, Literal("room")))
			g.add((ic["roomname_"+str(room_number)], s4bldg.isSpaceOf, floor))
	for floor in rooms_dict["floor_URI"]:
		g.add((floor, RDF.type, s4bldg.BuildingSpace))
		g.add((floor, s4bldg.isSpaceOf, ic["VL_building"]))
	g.add((ic["VL_building"], RDF.type, s4bldg.Building))

	g.serialize(destination=new_graph_fn, format='ttl')

with open('dev_name_dict.pkl', 'rb') as fp:
    device_name_dict = pickle.load(fp)

# print(device_name_dict)

room_files = ["room_tables/Videolabfloor1_export.csv","room_tables/Videolabfloor2_export.csv","room_tables/Videolabfloor3_export.csv","room_tables/Videolabfloor4_export.csv","room_tables/Videolabfloor5_export.csv","room_tables/Videolabfloor6_export.csv","room_tables/Videolabfloor7_export.csv"]

rooms_dict, device_not_in_dic_counter = create_rooms_dict(room_files, device_name_dict, device_not_in_dic_counter)

create_rooms_graph(rooms_dict)

print("couldn't find", device_not_in_dic_counter, "device names in the dictionary.")