import pickle

dev_model_dict = {}
model_counter_dict = {}

with open("dev_and_model.csv", 'r') as dev_and_model:
	# print(dev_and_model.readline()[:-1])
	print(dev_and_model.readline()[2:-4].split('\" , \"'))
	for line in dev_and_model.readlines():
		[dev, model] = line[2:-4].split('\" , \"')
		model = model.replace(' ', '_')
		try:
			model_counter_dict[model] += 1
		except:
			model_counter_dict[model] = 1
		print(dev, model.replace('/', '_')+'_'+str(model_counter_dict[model]))
		dev_model_dict[dev] = model.replace('/', '_')+'_'+str(model_counter_dict[model])

with open('dev_name_dict.pkl', 'wb') as fp:
    pickle.dump(dev_model_dict, fp)