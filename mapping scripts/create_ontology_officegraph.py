import json
from rdflib import Graph, Namespace, RDF, RDFS, XSD, Literal
import os
import time
import pickle

ic = Namespace("https://interconnectproject.eu/example/")
saref = Namespace("https://saref.etsi.org/core/")
s4ener = Namespace("https://saref.etsi.org/saref4ener/")
s4bldg = Namespace("https://saref.etsi.org/saref4bldg/")
om = Namespace("http://www.wurvoc.org/vocabularies/om-1.8/")

class time_replacement_counter():
	def __init__(self):
		self.counter = 0

	def next_counter(self):
		self.counter += 1
		return str(self.counter-1)

class MeasurementGraph():
	"""docstring for MeasurementGraph"""
	def __init__(self):
		self.g = Graph()
		self.g.bind("ic", "https://interconnectproject.eu/example/")
		self.g.bind("saref", "https://saref.etsi.org/core/")
		self.g.bind("s4ener", "https://saref.etsi.org/saref4ener/") #removed version number
		self.g.bind("s4bldg", "https://saref.etsi.org/saref4bldg/") #removed version number
		self.g.bind("om", "http://www.wurvoc.org/vocabularies/om-1.8/")
		self.time_counter = time_replacement_counter()


	# def big_feature_switch(self, feature_name):


	def add_message(self, message):
		self.add_timestamp(message)
		# if (int(self.timestamp_str[6]) == 3) and (int(self.timestamp_str[8:10]) < 15): #use to only get 2 weeks
		for feature in message:
			# print(feature, message[feature])
			self.add_property(feature, message[feature])

	def add_timestamp(self, message):
		try: 
			self.timestamp = Literal(message["message_timestamp"][:16], datatype=XSD.dateTime)	#skipping everything after minute
			# self.timestamp_str = message["message_timestamp"]
			self.timestamp_str = self.time_counter.next_counter()
		except:
			print("Missing timestamp!!")
			exit(0)

	def add_device_essentials(self, all_messages, device_name_dict):
		self.device = None
		for message in all_messages:
			try: 
				dev = str(ic["device_"+all_messages[0]["device_serial_number"]])
				self.device = ic[device_name_dict[dev]]
				# self.device_str = all_messages[0]["device_serial_number"]
				self.device_str = device_name_dict[dev]
				break
			except:
				print("Missing device in message!")
		if self.device == None:
			print("No device found!")
			exit(1)
		self.building_added = False
		self.room_added = False

		self.feat_interest = None
		for message in all_messages:
			try:
				if message["data_room"] != 'urn:Room:SmartThings:':						###check it is not a placeholder (or similar)
					self.feat_interest = ic["room_"+message["data_room"].replace(':', "-")]				###CHECK, might not always be unique?
					break
			except:
				pass
		if self.feat_interest == None:
			self.room_found = False
			for message in all_messages:
				try:
					self.feat_interest = ic["building"+message["data_building"].replace(':', "-")]
					break
				except:
					pass
		else:
			self.room_found = True



	def add_property(self, feature, value):
		if value == None: return 0
		elif feature =="device_manufacturer_description":
			self.g.add((self.device, saref.hasManufacturer, Literal(value, datatype=XSD.string)))
		elif feature =="device_model_description":
			self.g.add((self.device, saref.hasModel, Literal(value, datatype=XSD.string)))
		elif feature =="device_parent_serial_number":
			self.g.add((self.device, ic.hasParentSerialNumber, Literal(value, datatype=XSD.string)))
		elif feature =="device_serial_number":
			self.g.add((self.device, RDF.type, s4ener.Device))
			self.g.add((s4ener.Device, RDFS.subClassOf, saref.Device))
			self.g.add((self.device, s4ener.serialNumber, Literal(value, datatype=XSD.string)))
		elif feature =="device_type_description":
			self.g.add((self.device, ic.hasDeviceType, Literal(value, datatype=XSD.string)))
		elif feature =="data_room" and self.room_found:
			if not self.room_added:
				self.g.add((self.device, s4bldg.isContainedIn, self.feat_interest))								#allow for device changing rooms?
				self.g.add((self.feat_interest, s4bldg.contains, self.device))
				self.g.add((self.feat_interest, RDF.type, s4bldg.BuildingSpace))
				self.room_added = True
		elif feature =="data_building":	
			if not self.building_added:																	
				if self.room_found: #check if room is not None
					self.g.add((ic["building_"+value], s4bldg.hasSpace, self.feat_interest))
					self.g.add((self.feat_interest, s4bldg.isSpaceOf, ic["building_"+value.replace(":", "-")]))
				else:
					self.g.add((self.device, s4bldg.isContainedIn, self.feat_interest))
					self.g.add((self.feat_interest, s4bldg.contains, self.device))
				self.g.add((ic["building_"+value], RDF.type, s4bldg.Building))
				self.building_added = True
		elif feature =="data_temp_c":
			self.measurement_template("_temp_", value, XSD.float, om.degreeCelsius, saref.Temperature)
		elif feature =="data_humidity_per":
			self.measurement_template("_humidity_", value, XSD.float, om.percent, saref.Humidity)
		elif feature =="data_co2_ppm":
			self.measurement_template("_co2_", value, XSD.float, om.partsPerMillion, ic.CO2Level)
		elif feature =="data_status":
			self.measurement_template("_status_", value, XSD.int, om.bit, ic.DeviceStatus)
		elif feature =="data_battery_level":
			if float(value) <= 1.0:															#THIS IS AN ASSUMPTION
				value = value * 100
			self.measurement_template("_battery_lvl_", value, XSD.float, om.percent, ic.BatteryLevel)
		elif feature =="data_contact":
			self.measurement_template("_contact_", value, XSD.int, om.bit, ic.Contact)
		elif feature =="data_motion":
			self.measurement_template("_motion_", value, XSD.int, om.bit, saref.Motion)
		elif feature =="data_thermostat_heating_setpoint":
			self.measurement_template("_heating_setpoint_", value, XSD.float, om.degreeCelsius, ic.thermostatHeatingSetpoint)
		elif feature =="data_thermostat_cooling_setpoint":
			self.measurement_template("_cooling_setpoint_", value, XSD.float, om.degreeCelsius, saref.thermostatCoolingSetpoint)
		elif feature =="data_power_w":
			self.measurement_template("power", value, XSD.float, om.watt, saref.Power)
		elif feature =="data_people_count":
			self.measurement_template("people_counter", value, XSD.int, ic.people, saref.Occupancy)
		elif feature =="data_running_time_sec":
			self.measurement_template("running_time", value, XSD.int, om.second, ic.RunningTime)			#should be om.second-time, but gives error with the dash
		elif feature =="data_tamper":
			self.measurement_template("tamper", value, XSD.int, om.bit, saref.TamperStatus)
		elif feature =="data_water":
			self.measurement_template("water", value, XSD.int, om.bit, saref.WaterStatus)
		else:
			# print("could not find feature:", feature)
			pass

	def measurement_template(self, uri_add, value, datatype, unit_of_measure, meas_property):
		# prop = ic["property_"+self.device_str+"_"+uri_add+"_"+self.timestamp_str] #each property instance is unique
		prop = ic["property_"+self.device_str+"_"+uri_add]
		# meas = ic["measurement_"+self.device_str+"_"+uri_add+"_"+self.timestamp_str[:19].replace(':', "")] #remove times smaller then seconds replace ':' due too URI formatting
		meas = ic["measurement_"+self.device_str+"_"+uri_add+"_"+self.timestamp_str] #uses counter instead of real time string
		self.g.add((self.device, saref.measuresProperty, prop))
		self.g.add((self.device, saref.makesMeasurement, meas))
		self.g.add((meas, RDF.type, saref.Measurement))
		self.g.add((meas, saref.hasValue, Literal(value, datatype=datatype)))
		self.g.add((meas, saref.hasTimestamp, self.timestamp))
		self.g.add((meas, saref.isMeasuredIn, unit_of_measure))
		self.g.add((meas, saref.relatesToProperty, prop))
		self.g.add((prop, RDF.type, meas_property))
		# self.g.add((meas_property, RDFS.subClassOf, saref:Property))

	def save_to_file(self, new_graph_name):
		self.g.serialize(destination=new_graph_name, format='ttl')
		print("created: ", new_graph_name)

def get_filenames(path_to):
	filenames = os.listdir(path_to)
	# for filename in os.listdir(path_to): print(filename)
	return filenames

if __name__ == '__main__':
	airwits_flag = True #41 not mapped because of JSON corruptions
	calumino_flag= False
	samsung_flag = False

	if airwits_flag:
		path_to = "airwits/"
		# save_path="airwits_graphs/"
		save_path="airwits_graphs_short_names/"
	if calumino_flag:
		path_to = "calumino/"
		# save_path="calumino_graphs/"
		save_path="calumino_graphs_short_names/"
	if samsung_flag:	
		path_to = "samsung/"
		# save_path="samsung_graphs/"
		save_path="samsung_graphs_short_names/"
	# device_filenames = ["C2E8A0.txt"] #for testing

	with open('dev_name_dict.pkl', 'rb') as fp:
		device_name_dict = pickle.load(fp)

	device_filenames = get_filenames(path_to)
	len_old = len(device_filenames)

	graph_filenames = get_filenames(save_path)
	for graph_fn in graph_filenames: #remove graphs that have already been created.
		fake_device_name = graph_fn[:-4]+'.txt'
		if fake_device_name in device_filenames:
			device_filenames.remove(fake_device_name)

	if len(device_filenames) == 0:
		print("all datasets have been mapped!")
		exit()

	print("starting mapping of", len(device_filenames), "datasets. (skipping", len_old-len(device_filenames), "datasets)")

	# device_filenames = device_filenames[:2] #for testing with less files


	finished_i = 0
	finished_j = 0
	n_messages_list = []
	for device_fn in device_filenames:
		begin = time.time()
		new_graph_name = device_fn[:-4]+".ttl"
		g = MeasurementGraph()
		with open(path_to+device_fn, 'r') as device_file:
			try:
				all_messages = json.load(device_file)
				n_messages_list.append(len(all_messages))
				print("started mapping:", device_fn, "- containing", len(all_messages), "messages.")
				# exit()
				finished_i+= 1
				finished_j+= 1
				if finished_j == 100:
					finished_j = 0
					print(finished_i)
			except:
				# print("error with file:", device_file)
				# exit()
				continue
			g.add_device_essentials(all_messages, device_name_dict)
			for message in all_messages:
				g.add_message(message)
		g.save_to_file(save_path+new_graph_name)
		end = time.time()
		print("duration of mapping & saving:", end - begin)
	print(finished_i)
	print("average number of messages per device:", (sum(n_messages_list)/len(n_messages_list)))
