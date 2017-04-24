# Can download files needed from here
	#https://www.senate.gov/legislative/Public_Disclosure/database_download.htm

import os
import csv
import xml.etree.ElementTree as ET

# set up function to get xml files you want to use
def get_filepaths(directory):
	# got this function from here http://stackoverflow.com/questions/3207219/how-to-list-all-files-of-a-directory
 #    This function will generate the file names in a directory 
 #    tree by walking the tree either top-down or bottom-up. For each 
 #    directory in the tree rooted at directory top (including top itself), 
 #    it yields a 3-tuple (dirpath, dirnames, filenames).
	xml_paths = []  # List which will store all of the full filepaths.

	# Walk the tree.
	for root, directories, files in os.walk(directory):
		for filename in files:
			# Join the two strings in order to form the full filepath.
			filepath = os.path.join(root, filename)
			if ".xml" in filepath:
				xml_paths.append(filepath)  # Add it to the list.

	return xml_paths  # Self-explanatory.


# creates list of files to use
xml_paths = get_filepaths("xmls_to_use")

# sets up container for contents of each xml
list_of_xml_reads = []

# sets up function to remove last line of string
# from here 
	# http://stackoverflow.com/questions/18682965/python-remove-last-line-from-string/18683105#18683105
def remove_last_line_from_string(s):
    return s[:s.rfind('\n')]

# trims header and footer of xml and inserts into container
for xml_path in xml_paths:
	with open(xml_path, "r", encoding="UTF-16") as xml:
		xml_read = xml.read()
		xml_clean_read = xml_read.split("\n",4)[4];
		xml_clean_read = remove_last_line_from_string(xml_clean_read)
		list_of_xml_reads.append(xml_clean_read)

# adds header and footer to container of xml contents that wraps them all
list_of_xml_reads.insert(0, "<?xml version='1.0' encoding='UTF-16'?>\n<PublicFilings>")
list_of_xml_reads.append("</PublicFilings>")


# joins the list of xml contents into one string that can be parsed as xml
large_xml_contents = "\n".join(list_of_xml_reads)


#parse xml
parser = ET.XMLParser(encoding="UTF-16")
root = ET.fromstring(large_xml_contents, parser=parser)

# create variable for all individual fillings
all_filings = root.findall("./Filing")

# filters filings within root
for filing in all_filings:
	# format for filters: IF location in tree DOES NOT EQUAL what we want it to be REMOVE the filing FROM ROOT
	if filing.attrib["Year"] != "2017":
		root.remove(filing)
		continue
	if filing.attrib["Period"] != "1st Quarter (Jan 1 - Mar 31)":
		root.remove(filing)
		continue
	# Because there are multiple issues in one filing, below filter is example of how to filter where at least one of the issues is coded as BANKING or FINANCIAL INSTITUTIONS/INVESTMENTS/SECURITIES
	codes = []
	for issue in filing.findall("Issues/Issue"):
		codes.append(issue.attrib["Code"])
	if "BANKING" not in codes and "FINANCIAL INSTITUTIONS/INVESTMENTS/SECURITIES" not in codes:
		root.remove(filing)
		continue

# set up data that should go in csv
filing_dicts = []
longest_issues = [0,0]

# from each filing in filtered root, gets data from tree that we want to place in csv
	# note how different variables require parsing data tree in different ways
for ind1, filing in enumerate(root.findall("./Filing")):
	d = {}
	d["code"] = filing.attrib["ID"]
	d["year"] = filing.attrib["Year"]
	d["received"] = filing.attrib["Received"]
	d["amount"] = filing.attrib["Amount"]
	d["type"] = filing.attrib["Type"]
	d["period"] = filing.attrib["Period"]
	d["registrant_name"] = filing.find("Registrant").attrib["RegistrantName"]
	d["registrant_desc"] = filing.find("Registrant").attrib["GeneralDescription"]
	d["client_name"] = filing.find("Client").attrib["ClientName"]
	d["client_desc"] = filing.find("Client").attrib["GeneralDescription"]
	d["client_contact_full_name"] = filing.find("Client").attrib["ContactFullname"]
	# loop takes all issues in one filing and creates new columns for them in csv
	for ind2, issue in enumerate(filing.findall("Issues/Issue")):
		if ind2>longest_issues[0]:
			# if this filing has the most issues, it puts the indicies into longest_issues
			longest_issues = [ind2, ind1]
		issue_code_number = "issue_code_" + str(ind2)
		issue_specific_number = "issue_specific_" + str(ind2)
		d[issue_code_number] = issue.attrib["Code"]
		d[issue_specific_number] = issue.attrib["SpecificIssue"]
	filing_dicts.append(d)


# names csv file to write to
out_file_name = "2017_Q1_BANKING_AND_FINANCE.csv"


#writes csv file 
with open(out_file_name, "w") as csvfile:	
	fieldnames = filing_dicts[longest_issues[1]].keys()
	writer = csv.DictWriter(csvfile, fieldnames = fieldnames)
	writer.writeheader()
	for filing in filing_dicts:
		writer.writerow(filing)
