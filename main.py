import os, re
import xmltodict
import pandas as pd
from dicttoxml import dicttoxml
from xml.dom.minidom import parseString


def convert_xml_to_dict(file_path):
	# Convert XML to dictionary
	with open(file_path) as xml_file:
		xml_str = xml_file.read()
		xml_dict = xmltodict.parse(xml_str)

	return xml_dict


def get_value_for_key(key, dictionary):
    for k, v in dictionary.items():
        if k == key:
            return v
        elif isinstance(v, dict):
            result = get_value_for_key(key, v)
            if result is not None:
                return result
    return None


def process_data(data):
	result = {}

	# Copy data fields in result
	for key in xml_dict[list(xml_dict.keys())[0]].keys():
		if key != "listeAvis":
			result[key] = xml_dict[list(xml_dict.keys())[0]][key]

	result['listeAvis'] = []

	price_pattern = re.compile(r'\d+(?:\.\d+)?')

	# Filter and insert avis in result
	for avis in xml_dict['RCS-A_IMMAT']['listeAvis']['avis']:
		if avis.get('acte') and avis['acte'].get('vente'):
			origine_fonds = get_value_for_key('origineFonds', avis) or ''
			match = price_pattern.search(origine_fonds)
			if match:
				price = float(match.group(0))
				avis['prix'] = price

			result['listeAvis'].append(avis)

	return result


def convert_dict_to_xml(data):
	# Convert dictionary back to XML
	xml_bytes = dicttoxml(data, custom_root='RCS-A_IMMAT', attr_type=False, item_func=lambda x: 'avis')
	xml_str = xml_bytes.decode('utf-8')

	# Pretty-print the XML with 4-space indentation
	xml_dom = parseString(xml_str)
	xml_pretty = xml_dom.toprettyxml(indent='    ')

	return xml_pretty


def convert_dict_to_csv(data):
	df = pd.json_normalize(data['listeAvis'], sep='/')

	for col in df.columns:
		if '/' not in col:
			continue

		end_name = col.split('/')[-1]
		df.rename(columns = {col:end_name}, inplace = True)

	df.to_csv('result.csv', sep=';', encoding='utf-8-sig')


if __name__ == "__main__":
	files = [file for file in os.listdir() if '.xml' in file]
        
	print(*("{} - {}".format(index, file) for index, file in enumerate(files)),  sep="\n")
	file_idx = int(input("\nPlease select the input XML file by entering its corresponding number: "))
	xml_file_path = files[file_idx]

	xml_dict = convert_xml_to_dict(xml_file_path)
	result_dict = process_data(xml_dict)
	result_xml = convert_dict_to_xml(result_dict)
	result_csv = convert_dict_to_csv(result_dict)

	# Save XML to file
	with open('result.xml', 'w') as xml_file:
		xml_file.write(result_xml)
