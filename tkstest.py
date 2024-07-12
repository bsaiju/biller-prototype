import tkinter as tk
from tkinter import ttk
from tkinter.ttk import *
from tksheet import Sheet
from tabulate import tabulate
import json
import os
from datetime import datetime, timedelta
import calendar
import copy
import subprocess

template_info_json = {"key": {
    "Speech and Language Services": {},
    "Date": "BOOGIE",
    "License No": [],
    "NPI No": [],
    "Tax ID": [],
    "Patient Information": {
        "Patient Name": "",
        "Birthdate": "",
        "Sex": "",
        "Address": "",
        "City": "",
        "State/Zip": "",
        "Phone Number": "",
        "Policyholder": "",
        "Relation to subscriber": "",
        "Referring Physician": "",
        "Insurance Carrier": "",
        "Policyholder's Employer": "",
        "Insurance Plan Number": ""
    },
    "Diagnosis": [],
    "ICD-10": "",
    "CPT CODE": "",
    "Attendance":  {
        "Description": "",
        "Amount": "",
    },
	"OT": {
		"Description": "",
		"Amount": "",
		"License No": [],
		"CPT CODE": [],
		"Diagnosis": [],
	},
	"Accup": {
		"Date" : {
				"Diagnosis": "",
				"ICD-10": "",
				"Services": {
					"Description": [],
					"CPT": [],
					"Amount": []
				}
		}
	}
	
	}
}

template_att_json = {"name": {
	"Speech": {},
	"OT": {}
}}


class demo(tk.Tk):
	def __init__(self):
		tk.Tk.__init__(self)
		self.grid_columnconfigure(0, weight = 1)
		self.grid_rowconfigure(0, weight = 1)
		self.frame = tk.Frame(self)
		self.frame.grid_columnconfigure(0, weight = 1)
		self.frame.grid_rowconfigure(0, weight = 1)
		the_data = ["Name: ", "Month: ", "Year: ", "Day: ", "Phone: "]
		self.sheet = Sheet(self.frame,data = [[f"{r}"] for r in the_data])
		add_cli_btn = ttk.Button(self, text ="Add Client", command = self.add_cli_win)
		add_cli_btn.grid(row =1, column=0, sticky="nswe")
		bill_btn = ttk.Button(self, text = "Billing", command = self.bill_win)
		bill_btn.grid(row = 2, column=0, sticky="nswe")
		exit_button = ttk.Button(self, text="Exit", command=self.destroy)
		exit_button.grid(row=1, column=1, sticky="nswe")
		delete_cli_btn = ttk.Button(self, text="Delete Client", command = self.del_cli_win)
		delete_cli_btn.grid(row=3, column=0, sticky="nswe")
		edit_cli_btn = ttk.Button(self, text= "Edit Client", command= self.edit_cli_win)
		edit_cli_btn.grid(row=3, column=1, sticky="nswe")
		
		#SEARCH BAR FUNCTIONALITY
		#FROM https://stackoverflow.com/questions/57507667/creating-a-search-bar-with-cascading-functionality-with-python
		# self.entry = tk.Entry(self)
		# self.listbox = tk.Listbox(self)
		# self.vsb = tk.Scrollbar(self, command=self.listbox.yview)
		# self.listbox.configure(yscrollcommand=self.vsb.set)
		
		# self.entry.grid(row=5, column=0, sticky="nswe")

		#36 is about the height of the top column
		self.sheet.height_and_width(height = 36+self.sheet.get_row_heights()[0]*(len(self.sheet.get_row_heights())), width = 150)
		self.sheet.enable_bindings()
		self.sheet.grid(row=0, column = 0, sticky="nswe")
		self.frame.grid(row=0, column=0, sticky="nswe")
		edit_att_btn =  ttk.Button(self, text = "Edit Speech Attendance", command = lambda: self.edit_attendance("Speech"))
		edit_att_btn.grid(row=2, column = 1, sticky = "nswe")
		edit_att_btn =  ttk.Button(self, text = "Edit OT Attendance", command = lambda: self.edit_attendance("OT"))
		edit_att_btn.grid(row=2, column = 2, sticky = "nswe")
		

	def add_client(self, window):
		the_sheet = window.sheet.get_sheet_data(
			get_displayed=False, get_header=False,
			get_index=False, get_index_displayed=False,
			get_header_displayed=True, only_rows=None,
			only_columns=None)
		new_cli_json = copy.deepcopy(template_info_json)
		the_sheet = flatten_list(the_sheet)
		ind = [(index, word) for index, word in enumerate(the_sheet) if "License No" in word]
		# print("LEN OF IND IS ", len(ind))
		# print("IND IS ", ind)
		index = ind[0][0]+3
		modulo_index = 0
		#GETTING PATIENT INFO
		while(the_sheet[index] != "Patient Information"):
			# new_cli_json["key"][ind[0]].append(the_sheet[index])
			# index +=1
			# new_cli_json["key"][the_sheet[the_sheet.index(ind[0])+1]].append(the_sheet[index])
			# index +=1
			if(the_sheet[index] != "\n"):
				new_cli_json["key"][the_sheet[ind[0][0]+(modulo_index%3)]].append(the_sheet[index])
			modulo_index += 1
			index +=1
		modulo_index = 0
		index = ind[1][0]+3
		#GETTING OT INFO
		while(the_sheet[index] != "Accupuncture Services"):
			if(the_sheet[index] != "\n"):
				new_cli_json["key"]["OT"][the_sheet[ind[1][0]+(modulo_index%3)]].append(the_sheet[index])
			index += 1
			modulo_index += 1
		#get to diagnosis, icd-10 row and assigns each one
		new_cli_json["key"]["Accup"][the_sheet[index+2]] = new_cli_json["key"]["Accup"].pop("Date")
		full_date = the_sheet[index+2]
		index += 3
		new_cli_json["key"]["Accup"][full_date][the_sheet[index]] = the_sheet[index+3]
		index +=1
		new_cli_json["key"]["Accup"][full_date][the_sheet[index]] = the_sheet[index+3]
		index += 5
		# @ Description
		modulo_index = 0
		while(the_sheet[index+3+modulo_index] != "END"):
			if(the_sheet[index+3+modulo_index] != "\n"):
				new_cli_json["key"]["Accup"][full_date]["Services"][the_sheet[index + (modulo_index%3)]].append(the_sheet[index +3+ modulo_index])
			modulo_index+=1
		ind = [word for word in the_sheet if "Patient Name: " in word]
		index = the_sheet.index(ind[0])
		while(the_sheet[index] != "\n"):
			new_cli_json["key"]["Patient Information"][the_sheet[index].split(": ")[0]] = the_sheet[index].split(": ")[1]
			index+=1
		ind = [(index,word) for index, word in enumerate(the_sheet) if "Diagnosis" in word]
		new_cli_json["key"][ind[0][1]].append(the_sheet[ind[0][0]+2])
		new_cli_json["key"][the_sheet[ind[0][0]+1]] = the_sheet[ind[0][0]+3]
		new_cli_json["key"][ind[1][1]].append(the_sheet[ind[1][0]+2])
		new_cli_json["key"][the_sheet[ind[1][0]+1]] = the_sheet[ind[1][0]+3]

		ind = [(index, word) for index, word in enumerate(the_sheet) if "Description" in word]
		new_cli_json["key"]["Attendance"]["Description"] = the_sheet[ind[0][0]+2]
		new_cli_json["key"]["Attendance"]["Amount"] = the_sheet[ind[0][0]+3]

		new_cli_json["key"]["OT"]["Description"] = the_sheet[ind[1][0]+2]
		new_cli_json["key"]["OT"]["Amount"] = the_sheet[ind[1][0]+3]
		key = new_cli_json["key"]["Patient Information"]["Patient Name"]
		key += "@" + new_cli_json["key"]["Patient Information"]["Phone Number"]
		new_cli_json[key] = new_cli_json.pop("key")	
		if(not os.path.exists('./clients.json')):
			open("clients.json", "x")
		existing_data = []
		with open("clients.json", "r") as file:
			if(os.path.getsize("clients.json") != 0):
				existing_data = json.load(file)
				new_data = new_cli_json
				existing_data.update(new_data)
			else:
				existing_data = new_cli_json
		with open("clients.json", "w") as file:
			json.dump(existing_data, file, indent=4)
		self.openNewWindow()

	def add_cli_win(self):
		newWindow = tk.Toplevel(self)
		newWindow.title("Add a Client")
		newWindow.geometry(f"{len(add_cli_template())*28}x{len(add_cli_template())*22}")
		newWindow.sheet = Sheet(newWindow, data=[[f"{c}" for c in b]for b in add_cli_template()])
		newWindow.sheet.height_and_width(height = len(add_cli_template())*17, width = len(add_cli_template())*19)
		newWindow.sheet.enable_bindings()
		self.frame.grid(row=0, column=0, sticky="nswe")
		newWindow.sheet.grid(row=0, column=0, sticky="nswe")
		ttk.Button(newWindow, text="Add Client", command = lambda: self.add_client(newWindow)).grid(row = 1, column=0, sticky="nswe")
		ttk.Button(newWindow, text = "Exit", command = newWindow.destroy).grid(row = 2, column = 0, sticky="nswe")
		newWindow.geometry("")
	def delete_client(self, window):
		print("foo")

	def del_cli_win(self):
		newWindow = tk.Toplevel(self)
		newWindow.title("Delete Client")
		newWindow.geometry(f"{len(add_cli_template())*28}x{len(add_cli_template())*22}")
		self.frame.grid(row=0, column=0, sticky="nswe")

		sheet_info = self.sheet.get_sheet_data(
			get_displayed=False, get_header=False,
			get_index=False, get_index_displayed=False,
			get_header_displayed=True, only_rows=None,
			only_columns=None)
		name = sheet_info[0][0].split(": ")[1]
		month = sheet_info[1][0].split(": ")[1]
		year = sheet_info[2][0].split(": ")[1]
		day = sheet_info[3][0].split(": ")[1]
		phone = sheet_info[4][0].split(": ")[1]
		full_date = month+ "-" + day + "-" + year

		curr_cli_data, attendance = cli_data_list(name, full_date, phone)
		newWindow.geometry(f"{len(add_cli_template())*28}x{len(add_cli_template())*22}")
		newWindow.sheet = Sheet(newWindow, data=[[f"{c}" for c in b]for b in curr_cli_data])
		newWindow.sheet.height_and_width(height = len(add_cli_template())*22, width = len(add_cli_template())*28)
		newWindow.sheet.enable_bindings()
		self.frame.grid(row=0, column=0, sticky="nswe")
		newWindow.sheet.grid(row=0, column=0, sticky="nswe")
		ttk.Button(newWindow, text="Confirm", command = lambda: self.delete_client(newWindow)).grid(row = 1, column=0, sticky="nswe")
		ttk.Button(newWindow, text = "Exit", command = newWindow.destroy).grid(row = 2, column = 0, sticky="nswe")
	def woop(self):
		print("hi")
	def edit_client(self, window, curr_cli_data, name, phone, full_date):
		sheet_info = window.sheet.get_sheet_data(
			get_displayed=False, get_header=False,
			get_index=False, get_index_displayed=False,
			get_header_displayed=True, only_rows=None,
			only_columns=None)
		# print("TESTING", sheet_info)
		new_cli_json = copy.deepcopy(template_info_json)
		sheet_info = flatten_list(sheet_info)
		ind = [(index, word) for index, word in enumerate(sheet_info) if "License No" in word]
		index = ind[0][0]+3
		modulo_index = 0
		# print(new_cli_json)
		# print(template_info_json)
		# GETTING PATIENT INFO
		while(sheet_info[index] != "Patient Information"):
			# new_cli_json["key"][ind[0]].append(the_sheet[index])
			# index +=1
			# new_cli_json["key"][the_sheet[the_sheet.index(ind[0])+1]].append(the_sheet[index])
			# index +=1
			# print("")
			# print(sheet_info[index])
			# print("")
			if(sheet_info[index] != "\n"):
				new_cli_json["key"][sheet_info[ind[0][0]+(modulo_index%3)]].append(sheet_info[index])
			modulo_index += 1
			index +=1
		# while(sheet_info[index] != "\n" and sheet_info[index] != "Patient Information"):
		# 	if sheet_info[index] != "" : new_cli_json["key"][ind[0]].append(sheet_info[index])
		# 	index +=1
		# 	if sheet_info[index] != "" : new_cli_json["key"][sheet_info[sheet_info.index(ind[0])+1]].append(sheet_info[index])
		# 	index +=1
		# 	if sheet_info[index] != "" : new_cli_json["key"][sheet_info[sheet_info.index(ind[0])+2]].append(sheet_info[index])
		# 	index +=1

		# GETTING OT INFO
		modulo_index = 0
		index = ind[1][0]+3
		while(sheet_info[index] != "Accupuncture Services"):
			if(sheet_info[index] != "\n"):
				new_cli_json["key"]["OT"][sheet_info[ind[1][0]+(modulo_index%3)]].append(sheet_info[index])
			index += 1
			modulo_index += 1
		#get to diagnosis, icd-10 row and assigns each one
		new_cli_json["key"]["Accup"][sheet_info[index+5]] = new_cli_json["key"]["Accup"].pop("Date")
		full_date = sheet_info[index+5]
		index +=3
		new_cli_json["key"]["Accup"][full_date][sheet_info[index]] = sheet_info[index+3]
		print("sheet_info[index]", sheet_info[index])
		print("sheet_info", sheet_info)
		index +=1
		new_cli_json["key"]["Accup"][full_date][sheet_info[index]] = sheet_info[index+3]
		index += 5
		# @ Description
		modulo_index = 0
		while(sheet_info[index+3+modulo_index] != "END"):
			if(sheet_info[index+3+modulo_index] != "\n"):
				new_cli_json["key"]["Accup"][full_date]["Services"][sheet_info[index + (modulo_index%3)]].append(sheet_info[index +3+ modulo_index])
			modulo_index+=1
			
		# print("NEW CLI JSON", new_cli_json)
		ind = [word for word in sheet_info if "Patient Name: " in word]
		index = sheet_info.index(ind[0])
		while(sheet_info[index] != "\n"):
			new_cli_json["key"]["Patient Information"][sheet_info[index].split(": ")[0]] = sheet_info[index].split(": ")[1]
			index+=1
		ind = [(index,word) for index, word in enumerate(sheet_info) if "Diagnosis" in word]
		new_cli_json["key"][ind[0][1]].append(sheet_info[ind[0][0]+2])
		new_cli_json["key"][sheet_info[ind[0][0]+1]] = sheet_info[ind[0][0]+3]
		new_cli_json["key"][ind[1][1]].append(sheet_info[ind[1][0]+2])
		new_cli_json["key"][sheet_info[ind[1][0]+1]] = sheet_info[ind[1][0]+3]
		ind = [(index,word) for index, word in enumerate(sheet_info) if "Description" in word]
		new_cli_json["key"]["Attendance"]["Description"] = sheet_info[ind[0][0]+2]
		new_cli_json["key"]["Attendance"]["Amount"] =  sheet_info[ind[0][0]+3]
		new_cli_json["key"]["OT"]["Description"] = sheet_info[ind[1][0]+2]
		new_cli_json["key"]["OT"]["Amount"] = sheet_info[ind[1][0]+3]
		new_name = new_cli_json["key"]["Patient Information"]["Patient Name"]
		new_phone = new_cli_json["key"]["Patient Information"]["Phone Number"]
		old_key = name + "@" + phone
		new_key = new_name + "@" + new_phone
		new_cli_json[new_key] = new_cli_json.pop("key")
		# print(new_cli_json)
		if(not os.path.exists('./clients.json')):
			open("clients.json", "x")
		existing_data = []
		with open("clients.json", "r") as file:
			if(os.path.getsize("clients.json") != 0):
				existing_data = json.load(file)
				new_data = new_cli_json
				# print("a")
				if(new_cli_json[new_key]["Patient Information"]["Patient Name"] != name or new_cli_json[new_key]["Patient Information"]["Phone Number"] != phone):
					# print("f")
					if(new_key not in existing_data):
						newWindow = tk.Toplevel(self)
						newWindow.title("Error?")
						newWindow.geometry("500x300")
						label = Label(newWindow, wraplength= 500, text=f"The client you are trying to save does not exist in our records. Would you like to overwrite {name}@{phone}'s data or add this as a new client? Please also check that you have written the name and phone number correctly.")
						label.grid(row = 0, column = 0, sticky = "nswe")
						ttk.Button(newWindow, text="Overwrite", command = overwrite(existing_data, new_data, new_key, old_key)).grid(row = 1, column=0, sticky="nswe")
						ttk.Button(newWindow, text= "Add As New Client", command =existing_data.update(new_data)).grid(row = 2, column = 0, sticky="nswe")
				else:
					existing_data[old_key] = update_json(new_data, existing_data[old_key]).pop(old_key)
					# existing_data.update(new_data)s
				# print("NOOOOOOOOOOOOOO")
			else:
				# print("boo")
				existing_data = new_cli_json
		with open("clients.json", "w") as file:
			# print("bleet")
			json.dump(existing_data, file, indent=4)
		self.openNewWindow()

	def edit_cli_win(self):
		newWindow = tk.Toplevel(self)
		newWindow.title("Edit Client")
		# newWindow.geometry(f"{len(add_cli_template())*28}x{len(add_cli_template())*22}")
		self.frame.grid(row=0, column=0, sticky="nswe")

		sheet_info = self.sheet.get_sheet_data(
			get_displayed=False, get_header=False,
			get_index=False, get_index_displayed=False,
			get_header_displayed=True, only_rows=None,
			only_columns=None)
		name = sheet_info[0][0].split(": ")[1]
		month = sheet_info[1][0].split(": ")[1]
		year = sheet_info[2][0].split(": ")[1]
		day = sheet_info[3][0].split(": ")[1]
		phone = sheet_info[4][0].split(": ")[1]
		full_date = month+ "-" + day + "-" + year
		# print("FIRST")
		curr_cli_data, attendance_info = cli_data_list(name, full_date, phone)
		# print("SECOND")
		# newWindow.geometry(f"{len(add_cli_template())*28}x{len(add_cli_template())*22}")
		newWindow.geometry("")
		newWindow.sheet = Sheet(newWindow, data=[[f"{c}" for c in b]for b in curr_cli_data])
		newWindow.sheet.height_and_width(height = len(add_cli_template())*17, width = len(add_cli_template())*19)
		newWindow.sheet.enable_bindings()
		self.frame.grid(row=0, column=0, sticky="nswe")
		newWindow.sheet.grid(row=0, column=0, sticky="nswe")
		ttk.Button(newWindow, text="Save Edits", command = lambda: self.edit_client(newWindow, curr_cli_data, name, phone, full_date)).grid(row = 1, column=0, sticky="nswe")
		ttk.Button(newWindow, text = "Exit", command = newWindow.destroy).grid(row = 2, column = 0, sticky="nswe")

	def bill_win(self):
		newWindow = tk.Toplevel(self)
		newWindow.title("Billing")
		newWindow.geometry("")
		ttk.Button(newWindow, text="Individual Billing", command = self.indiv_bill_win).grid(row = 1, column=0, sticky="nswe")
		ttk.Button(newWindow, text= "Monthly Billing", command = self.month_bill_win).grid(row = 2, column = 0, sticky="nswe")
	def indiv_bill_win(self):
		newWindow = tk.Toplevel(self)
		newWindow.title("Individual Billing")
		newWindow.geometry("170x150")
		self.frame.grid(row=0, column=0, sticky="nswe")
		ttk.Button(newWindow, text="Create Speech Bill", command = lambda: self.create_bill("Speech")).grid(row =1, column=0, sticky="nswe")
		ttk.Button(newWindow, text = "Create OT Bill", command = lambda: self.create_bill("OT")).grid(row=1, column = 1, sticky="nwse")
		ttk.Button(newWindow, text = "Create Accupuncture Bill", command = lambda: self.create_bill("Accup")).grid(row=2, column = 0, sticky="nwse")
	def create_bill(self, service_type):
		sheet_info = self.sheet.get_sheet_data(
			get_displayed=False, get_header=False,
			get_index=False, get_index_displayed=False,
			get_header_displayed=True, only_rows=None,
			only_columns=None)
		name = sheet_info[0][0].split(": ")[1]
		year = sheet_info[2][0].split(": ")[1]
		month = sheet_info[1][0].split(": ")[1]
		day = sheet_info[3][0].split(": ")[1]
		phone = sheet_info[4][0].split(": ")[1]
		key = name + "@" + phone
		table_list = bill_list(name, month, year, phone, service_type)
		full_name = name.split(" ")
		name_abbr = ""
		for i in range(len(full_name)-1):
			name_abbr += full_name[i][0]
			name_abbr +=  "."
		name_abbr += full_name[-1]
		if(not os.path.exists(f'./clients/{name_abbr}')):
			if(not os.path.exists(f'./clients')):
				os.mkdir(f'./clients')
			os.mkdir(f'./clients/{name_abbr}')
		# print("sheet_info")
		# print(sheet_info)
		# print("table_list")
		# print(table_list)
		
		with open("clients.json", "r") as file:
                        if(os.path.getsize("clients.json") != 0):
                                existing_data = json.load(file)
		with open("attendance.json", "r") as file:
                        if(os.path.getsize("attendance.json") != 0):
                                current_attendance = json.load(file)
		# print("existing data")
		# print(existing_data)		

		# print("attendance_cuureetn")
		# print(current_attendance)
		
		patient_name = name
		license_no = existing_data[key]['License No']
		npi_no = existing_data[key]['NPI No']
		tax_id = existing_data[key]['Tax ID']
		birthdate = existing_data[key]['Patient Information']['Birthdate']
		sex = existing_data[key]['Patient Information']['Sex']
		address = existing_data[key]['Patient Information']['Address']
		city = existing_data[key]['Patient Information']['City']
		state_zip = existing_data[key]['Patient Information']['State/Zip']
		phone_number = existing_data[key]['Patient Information']['Phone Number']
		policyholder = existing_data[key]['Patient Information']['Policyholder']
		relation_to_subscriber = existing_data[key]['Patient Information']['Relation to subscriber']
		referring_physician = existing_data[key]['Patient Information']['Referring Physician']
		insurance_carrier = existing_data[key]['Patient Information']['Insurance Carrier']
		policyholder_employer = existing_data[key]['Patient Information']['Policyholder\'s Employer']
		insurance_plan_number = existing_data[key]['Patient Information']['Insurance Plan Number']
		diagnosis_icd10 = [existing_data[key]['Diagnosis'][0], existing_data[key]['ICD-10']]
		diagnosis_cpt = [[existing_data[key]['Diagnosis'][1]], [existing_data[key]['CPT CODE']]]
		attendance_records = current_attendance[key][service_type][month+"/"+year]
		att_desc = existing_data[key]['Attendance']['Description']
		att_amount = existing_data[key]['Attendance']['Amount']
		total = len(attendance_records)*float(existing_data[key]['Attendance']['Amount'])
		title = "Speech and Language Services"
		
		if(service_type == "OT"):
			license_no = existing_data[key]['OT']['License No']
			diagnosis_cpt = [existing_data[key]['OT']['Diagnosis'], existing_data[key]['OT']['CPT CODE']]
			att_desc = existing_data[key]['OT']['Description']
			att_amount = existing_data[key]['OT']['Amount']
			total = len(attendance_records)*float(att_amount)
			title = "Occupational Therapy Services"
		elif(service_type == "Accup"):
			print("")
			date = month +"-"+day+"-"+year
			diagnosis_icd10[0] = existing_data[key]["Accup"][date]["Diagnosis"]
			diagnosis_icd10[1] = existing_data[key]["Accup"][date]["ICD-10"]
			description = existing_data[key]["Accup"][date]["Services"]["Description"]
			cpt = existing_data[key]["Accup"][date]["Services"]["CPT"]
			amount = existing_data[key]["Accup"][date]["Services"]["Amount"]
			title = "Accupuncture Services"


		attendance_table = "".join(r"\texttt{" + str(count+1) + r"} & \texttt{" + attendance_records[count][2] + f"/{year}" + r"} & \texttt{11} & \texttt{" + diagnosis_cpt[1][0] + r"} & \texttt{" + att_desc + r"} & \texttt{" + att_amount + r"} & yes\\\hline" for count in range(len(attendance_records)))
		print("DA CPT", diagnosis_cpt)
		# LaTeX template with placeholders for variables
		latex_template = r'''\documentclass{scrartcl}
\usepackage{graphicx}
\usepackage{geometry}
\geometry{margin=1in}
\usepackage{array}
\usepackage[labelformat=empty]{caption}

\begin{document}

\begin{quote}
    \centering
    \large\textbf{%(title)s}
\end{quote}

\begin{table}[htb]
    \centering
	\begin{minipage}{0.47\textwidth}
		\centering
		\begin{tabular}{|p{7cm}|}
			\hline
			\texttt{Brain And Body Autism Center}\\
			\texttt{711 Borello Way}\\
			\texttt{Mountain View, CA 94041}\\
			Ph: \texttt{650-519-7779}\\
			Email: \texttt{priyaautismcenter@gmail.com}\\
			\hline
		\end{tabular}
	\end{minipage}
	\hfill
	\begin{minipage}{0.47\textwidth}
		\centering
		\caption{Provider Information}
		\begin{tabular}{|c|c|c|} 
			\hline 
			License No. & NPI No. & Tax ID \\
			\hline
			%(table_license_npi_tax)s
		\end{tabular}
	\end{minipage}
\end{table}

\begin{table}[htbp]
    \centering
	\caption{Patient Information}
    \begin{tabular}{|>{\raggedright\arraybackslash}p{4cm}|>{\raggedright\arraybackslash}p{4cm}|>{\raggedright\arraybackslash}p{4cm}|} 
        \hline 
        Patient Name: \texttt{%(patient_name)s} & Birthdate: \texttt{%(birthdate)s} & Sex: \texttt{%(sex)s} \\
        \hline
        Address: \texttt{%(address)s} & City: \texttt{%(city)s} & State/Zip: \texttt{%(state_zip)s} \\
        \hline
        Phone Number: \texttt{%(phone_number)s} & Policyholder: \texttt{%(policyholder)s} & Relation to Subscriber: \texttt{%(relation_to_subscriber)s} \\
        \hline
        Referring Physician: \texttt{%(referring_physician)s} & Insurance Carrier: \texttt{%(insurance_carrier)s} & \\
        \hline
        Policyholder's Employer: \texttt{%(policyholder_employer)s} & Insurance Plan Number: \texttt{%(insurance_plan_number)s} & \\
        \hline
    \end{tabular}
\end{table}

\begin{table}[htb]
    \centering
    \begin{minipage}{0.45\textwidth}
        \centering
		\caption{Diagnosis Information}
        \begin{tabular}{|p{3cm}|p{2cm}|} 
            \hline 
            Diagnosis & ICD-10 \\
            \hline
            \texttt{%(diagnosis_icd10)s} & \texttt{%(icd10)s} \\
            \hline
        \end{tabular}
    \end{minipage}
    \hfill
    \begin{minipage}{0.45\textwidth}
        \centering
		\caption{Treatment Code}
        \begin{tabular}{|p{4cm}|p{3cm}|}  
            \hline 
            Diagnosis & CPT Code \\
            \hline
            %(D_CPT)s
        \end{tabular}
    \end{minipage}
\end{table}

\clearpage

\begin{quote}
    \centering
    \large\textbf{Attendance}
\end{quote}

\begin{table}[htb]
    \centering
	\caption{Attendance Record}
	\resizebox{\textwidth}{!}{\begin{tabular}{|c|c|c|c|c|c|c|}
			\hline 
			Number & Date of Services & Place of Service & CPT Code & Description & Amount & Paid \\
			\hline
			%(attendance_records)s
			\hline
			\multicolumn{6}{|r|}{Total} & \texttt{%(total)s} \\
			\hline
	\end{tabular}}
\end{table}

\vspace{20mm}

\vspace{5mm}
\begin{figure}[htb]
    \centering
	\caption{Authorized Signature}
    \includegraphics[width=0.5\textwidth]{Priya Sign.pdf}
\end{figure}

\end{document}
'''

		# Format the LaTeX template with actual values
		# print("LICENSE NO", license_no)
		# print("NPI NO", npi_no)
		# print("TAX ID", tax_id)
		# license_npi_tax = r"\texttt{"+ license_no[0] + "} & " + r"\texttt{" + npi_no[0] + "}" + r"& \texttt{" + tax_id[0] + "}\\\\\hline"
		# license_npi_tax_part_2 = [r"\texttt{"+ license_no[i+1] + "} & & \\\\" for i in range(len(license_no)-1)]
		# license_npi_tax_part_2 = "".join(license_npi_tax_part_2)
		# license_npi_tax += license_npi_tax_part_2
		license_npi_tax = [r"\texttt{"+ (license_no[i] if i < len(license_no) else "") + r"} & \texttt{" + (npi_no[i] if i < len(npi_no) else "") + r"} & \texttt{" + (tax_id[i] if i < len(tax_id) else "") + "}\\\\\hline" for i in range(max(len(existing_data[key]["OT"]["License No"]), len(existing_data[key]["NPI No"]), len(existing_data[key]["Tax ID"])))]
		print("LOOK HERE", license_npi_tax)
		# print("LICENSE_NPI_TAX", license_npi_tax)
		latex_content = latex_template % {
			"title": title,
		    "table_license_npi_tax": "".join([r"\texttt{"+ (license_no[i] if i < len(license_no) else "") + r"} & \texttt{" + (npi_no[i] if i < len(npi_no) else "") + r"} & \texttt{" + (tax_id[i] if i < len(tax_id) else "") + "}\\\\\hline" for i in range(max(len(license_no), len(npi_no), len(tax_id)))]),
		    "patient_name": patient_name,
		    "birthdate": birthdate,
		    "sex": sex,
		    "address": address,
		    "city": city,
		    "state_zip": state_zip,
		    "phone_number": phone_number,
		    "policyholder": policyholder,
		    "relation_to_subscriber": relation_to_subscriber,
		    "referring_physician": referring_physician,
		    "insurance_carrier": insurance_carrier,
		    "policyholder_employer": policyholder_employer,
		    "insurance_plan_number": insurance_plan_number,
			    "diagnosis_icd10": diagnosis_icd10[0],
		    # "diagnosis_cpt": diagnosis_cpt[0],
		    "icd10": diagnosis_icd10[1],
		    # "cptcode": diagnosis_cpt[1],
			"D_CPT": "".join([r"\texttt{" + (diagnosis_cpt[0][i] if i < len(diagnosis_cpt[0]) else "")+ r"} & \texttt{"+ (diagnosis_cpt[1][i] if i < len(diagnosis_cpt[1]) else "") + r"} \\\hline" for i in range(max(len(diagnosis_cpt[0]), len(diagnosis_cpt[1])))]),
		    "attendance_records": attendance_table,
		    "total": total
			}		





		if(service_type == "OT"):
			# Define the TeX file name
			TexFileName = f"./clients/{name_abbr}/{name_abbr} OT {month}-{year}.tex"
			# Create a new LaTeX file with the blanks filled
			with open(TexFileName, 'w') as TexFile:
				# Fill the LaTeX template with data from the row
				TexFile.write(latex_content)
				# Compile the LaTeX file into PDF using pdflatex
		else:
			# Define the TeX file name
			TexFileName = f"./clients/{name_abbr}/{name_abbr} {month}-{year}.tex"
			# Create a new LaTeX file with the blanks filled
			with open(TexFileName, 'w') as TexFile:
				# Fill the LaTeX template with data from the row
				TexFile.write(latex_content)
				# Compile the LaTeX file into PDF using pdflatex
		
		subprocess.call(['pdflatex', '-output-directory', f"./clients/{name_abbr}", TexFileName], shell=False)

		self.openNewWindow()

	def month_bill_win(self):
		newWindow = tk.Toplevel(self)
		newWindow.title("Monthly Billing")
		newWindow.geometry("170x150")
		self.frame.grid(row=0, column=0, sticky="nswe")
	def openNewWindow(self):
		newWindow = tk.Toplevel(self)
		newWindow.title("Done!")
		newWindow.geometry("200x200")
		Label(newWindow,text ="Done!").pack()
		exit_button = ttk.Button(newWindow, text="Exit", command=newWindow.destroy)
		exit_button.pack(pady=20)
	def edit_attendance(self, att_type):
		newWindow = tk.Toplevel(self)
		newWindow.title("Edit Attendance")
		newWindow.geometry(f"{len('Date of Monday: ')*13}x{5*24}")
		sheet_info = self.sheet.get_sheet_data(
			get_displayed=False, get_header=False,
			get_index=False, get_index_displayed=False,
			get_header_displayed=True, only_rows=None,
			only_columns=None)
		if(not os.path.exists('./attendance.json')):
			open("attendance.json", "x")
		if(os.path.getsize("attendance.json") == 0):
			att_data = {}
		else:
			with open("attendance.json", "r") as file:
				att_data = json.load(file)
		name = sheet_info[0][0].split(": ")[1]
		cal = calendar.monthcalendar(int(sheet_info[2][0].split(": ")[1]), int(sheet_info[1][0].split(": ")[1]))
		weeks = []
		for week in cal:
			week_list = [str(day) if day != 0 else "" for day in week]
			weeks.append(week_list)
		newWindow.sheet = Sheet(newWindow, data=[["","","","","","",""], ["","","","","","",""], ["","","","","","",""], ["","","","","","",""], ["","","","","","",""]])
		monthyear = sheet_info[1][0].split(": ")[1] + "/" + sheet_info[2][0].split(": ")[1]
		phone = sheet_info[4][0].split(": ")[1]
		key = name + "@" + phone
		for i in range(0,5):
			for j in range(0, 7):
				if(weeks[i][j] != ""):
					newWindow.sheet.checkbox_cell(r = i, c = j, state = "normal", text = sheet_info[1][0].split(": ")[1] + "/" +weeks[i][j])
					if(key in att_data):
						if(monthyear in att_data[key][att_type]):
							if([i, j, sheet_info[1][0].split(": ")[1] + "/" +weeks[i][j]] in att_data[key][att_type][monthyear]):
								newWindow.sheet.click_checkbox(i, j, checked = None)
			
		newWindow.sheet.height_and_width(height = 180, width = 825)
		newWindow.sheet.enable_bindings()
		self.frame.grid(row=0, column=0, sticky="nswe")
		newWindow.sheet.grid(row=0, column=0, sticky="nswe")
		ttk.Button(newWindow, text = "Save", command = lambda: save_att(newWindow.sheet, name, monthyear, phone, att_type)).grid(row = 1, column = 0, sticky="nswe")
		ttk.Button(newWindow, text = "Exit", command = newWindow.destroy).grid(row = 2, column = 0, sticky="nswe")

def update_json(new_data, existing_data):
	for key, value in new_data.items():
		if isinstance(value, dict):
			print(existing_data.get(key, {}))
			existing_data[key] = update_json(value, existing_data.get(key, {}))
		elif isinstance(value, list):
			# print("LIST")
			# print(key, " & ", value)
			# print("old & new")
			existing_data[key] = value
		else:
			existing_data[key] = value
	return existing_data


def overwrite(existing_data, new_data, new_key, old_key):
	# print("ovie")
	existing_data[new_key] = new_data.pop(new_key)
	existing_data.pop(old_key)

def add_cli_template():
	zeroeth = [["Speech and Language Services"]]
	
	first =  [['License No', 'NPI No', 'Tax ID'], ["", "", ""]]
	
	second = [["Patient Information"]]
	third = [["Patient Name: ", "Birthdate: ", "Sex: "], ["Address: ", "City: ", "State/Zip: "], ["Phone Number: ", "Policyholder: ", "Relation to subscriber: "], ["Referring Physician: ", "Insurance Carrier: Aetna"], ["Policyholder\'s Employer: ", "Insurance Plan Number: "]] 

	fourth = [["Diagnosis", "ICD-10"], ["Autism", "F84.0"]]

	fifth = [["Diagnosis", "CPT CODE"], ["Treatment of speech, language, voice, communication, and//or auditory processing disorder; individual", "92507 // GN"]]

	sixth =[["Attendance"]]

	seventh = [["Description", "Amount"], ["", ""], ["", ""]]

	eighth = [["Occupational Therapy Services"]]

	ninth = [["Attendance"]]

	tenth = [["Description", "Amount"],["", ""]]

	eleventh = [["License No", "CPT CODE", "Diagnosis"], ["", "", ""]]
	
	twelfth = [["Accupuncture Services"]]
	
	thirteenth = [["Date", "Diagnosis", "ICD-10"], ["", "", ""]]
	
	fourteenth = [["Description", "CPT", "Amount"], ["", "", ""]]
	fifteenth = [["END"]]
	
	return zeroeth+["\n"]+first+["\n"]+second+["\n"]+third+["\n"]+fourth+["\n"]+fifth+["\n"]+sixth+["\n"]+seventh+["\n"]+eighth+["\n"]+ninth+["\n"]+tenth+["\n"]+eleventh+["\n"]+twelfth+["\n"]+thirteenth+["\n"]+fourteenth+["\n"]+fifteenth


# def data_n_template_combine(name, month, year):
# 	with open("clients.json", "r") as file:
# 		if(os.path.getsize("clients.json") != 0):
# 			existing_data = json.load(file)
# 	with open("attendance.json", "r") as file:
# 		if(os.path.getsize("attendance.json") != 0):
# 			current_attendance = json.load(file)
# 	current_cli_data = 
# 	if name in existing_data:
# 		for num in range(existing_data[name]["License No"]):
# 			print("foo")

def cli_data_list(name, full_date, phone):
	# print("first test")
	if(not os.path.exists('./clients.json')):
			f = open("clients.json", "x")
			f.close()
	with open("clients.json", "r") as file:
			cli_data = json.load(file)
	# print("segundo")
	if(not os.path.exists('./attendance.json')):
			open("attendance.json", "x")
	with open("attendance.json", "r") as file:
			att_data = json.load(file)
	key = name + "@" + phone
	zeroeth = [["Speech and Language Services"]]

	# first = [tabulate(table, tablefmt='simple_grid', maxcolwidths=[None, None])]
	first = [['License No', 'NPI No', 'Tax ID']] 
	first.extend([[[cli_data[key]["License No"][0]][0], [cli_data[key]["NPI No"][0]][0], [cli_data[key]["Tax ID"][0]][0]]])
	first.extend([[cli_data[key]["License No"][i+1]][0], "\n", "\n"] for i in range(len(cli_data[key]["License No"])-1))
	# second = [tabulate(table, tablefmt='simple_grid', maxcolwidths=[None, None, None])]

	second = [["Patient Information"]]
	third = [["Patient Name: " + name, "Birthdate: " + cli_data[key]["Patient Information"]["Birthdate"], "Sex: " + cli_data[key]["Patient Information"]["Sex"]], ["Address: " + cli_data[key]["Patient Information"]["Address"], "City: " + cli_data[key]["Patient Information"]["City"], "State/Zip: " + cli_data[key]["Patient Information"]["State/Zip"]], ["Phone Number: " + cli_data[key]["Patient Information"]["Phone Number"], "Policyholder: " + cli_data[key]["Patient Information"]["Policyholder"], "Relation to subscriber: " + cli_data[key]["Patient Information"]["Relation to subscriber"]], ["Referring Physician: " + cli_data[key]["Patient Information"]["Referring Physician"], "Insurance Carrier: " + cli_data[key]["Patient Information"]["Insurance Carrier"]], ["Policyholder's Employer: " + cli_data[key]["Patient Information"]["Policyholder's Employer"], "Insurance Plan Number: " + cli_data[key]["Patient Information"]["Insurance Plan Number"]]]

	# fourth = [tabulate(table, tablefmt='simple_grid', maxcolwidths=[len("Policyholder\'s Employer: "), len("Insurance Carrier: "), len("Insurance Plan")])]

	fourth = [["Diagnosis", "ICD-10"], [cli_data[key]["Diagnosis"][0], cli_data[key]["ICD-10"]]]
	# fifth = [tabulate(table, tablefmt='simple_grid', maxcolwidths=[15, None])]

	fifth = [["Diagnosis", "CPT CODE"], [cli_data[key]["Diagnosis"][1], cli_data[key]["CPT CODE"]]]

	sixth = [["Attendance"]]

	seventh = [["Description", "Amount"], [cli_data[key]["Attendance"]["Description"], cli_data[key]["Attendance"]["Amount"]]]

	eighth = [["Occupational Therapy Services"]]

	ninth = [["Attendance"]]

	tenth = [["Description", "Amount"],[cli_data[key]["OT"]["Description"], cli_data[key]["OT"]["Amount"]]]

	eleventh = [["License No", "CPT CODE", "Diagnosis"]]
	eleventh.extend([cli_data[key]["OT"]["License No"][i] if cli_data[key]["OT"]["License No"][i] else "", cli_data[key]["OT"]["CPT CODE"][i] if cli_data[key]["OT"]["CPT CODE"][i] else "", [cli_data[key]["OT"]["Diagnosis"][i]][0]] if [cli_data[key]["OT"]["Diagnosis"][i]][0] else "" for i in range(max(len(cli_data[key]["OT"]["License No"]), len(cli_data[key]["OT"]["CPT CODE"]), len(cli_data[key]["OT"]["Diagnosis"]))))
	if("--" not in full_date):
		if(full_date in cli_data[key]["Accup"]):
			twelfth = [["Accupuncture Services"]]
			
			thirteenth = [["Date", "Diagnosis", "ICD-10"], [full_date, cli_data[key]["Accup"][full_date]["Diagnosis"], cli_data[key]["Accup"][full_date]["ICD-10"]]]
			
			fourteenth = [["Description", "CPT", "Amount"]]
			fourteenth.extend([cli_data[key]["Accup"][full_date]["Services"]["Description"][i], cli_data[key]["Accup"][full_date]["Services"]["CPT"][i], cli_data[key]["Accup"][full_date]["Services"]["Amount"][i]] for i in range(len(cli_data[key]["Accup"][full_date]["Services"]["Description"])))

			fifteenth = [["END"]]
		else:
			twelfth = [["Accupuncture Services"]]
			
			thirteenth = [["Date", "Diagnosis", "ICD-10"], ["", "", ""]]
			
			fourteenth = [["Description", "CPT", "Amount"], ["", "", ""]]

			fifteenth = [["END"]]
	else:
		twelfth = [[""]]
		thirteenth = [[""]]
		fourteenth = [[""]]
		fifteenth = [[""]]

	return zeroeth+["\n"]+first+["\n"]+second+["\n"]+third+["\n"]+fourth+["\n"]+fifth+["\n"]+sixth+["\n"]+seventh+["\n"]+eighth+["\n"]+ninth+["\n"]+tenth+["\n"]+eleventh+["\n"]+twelfth+["\n"]+thirteenth+["\n"]+fourteenth+["\n"]+fifteenth, cli_data[key]["Attendance"]


def flatten_list(nested_list):
    flat_list = []
    for sublist in nested_list:
        if isinstance(sublist, list):
            flat_list.extend(flatten_list(sublist))
        else:
            flat_list.append(sublist)
    return flat_list

def bill_list(name, month, year, phone, service_type):
	if(not os.path.exists('./clients.json')):
			open("clients.json", "x")
	with open("clients.json", "r") as file:
			cli_data = json.load(file)
	if(not os.path.exists('./attendance.json')):
			open("attendance", "x")
	with open("attendance.json", "r") as file:
			att_data = json.load(file)
	key = name + "@" + phone
	zeroeth = ["Speech and Language Services"]

	table = [['Date', 'This is the date']]
	first = [tabulate(table, tablefmt='simple_grid', maxcolwidths=[None, None])]

	table = [['License No', 'NPI No', 'Tax ID'], [1, 2, 3]] 
	# table.extend([[cli_data[key]["License No"][i]][0], [cli_data[key]["NPI No"][i]][0], [cli_data[key]["Tax ID"][i]][0]] for i in range(len(cli_data[key]["License No"])))
	table.extend([[[cli_data[key]["License No"][0]][0], [cli_data[key]["NPI No"][0]][0], [cli_data[key]["Tax ID"][0]][0]]])
	table.extend([[cli_data[key]["License No"][i+1]][0], "\n", "\n"] for i in range(len(cli_data[key]["License No"])-1))
	second = [tabulate(table, tablefmt='simple_grid', maxcolwidths=[None, None, None])]

	third = ["Patient Information"]
	table = [["Patient Name: " + name, "Birthdate: " + cli_data[key]["Patient Information"]["Birthdate"], "Sex: " + cli_data[key]["Patient Information"]["Sex"]], ["Address: " + cli_data[key]["Patient Information"]["Address"], "City: " + cli_data[key]["Patient Information"]["City"], "State/Zip: " + cli_data[key]["Patient Information"]["State/Zip"]], ["Phone Number: " + cli_data[key]["Patient Information"]["Phone Number"], "Policyholder: " + cli_data[key]["Patient Information"]["Policyholder"], "Relation to subscriber: " + cli_data[key]["Patient Information"]["Relation to subscriber"]], ["Referring Physician: " + cli_data[key]["Patient Information"]["Referring Physician"], "Insurance Carrier: " + cli_data[key]["Patient Information"]["Insurance Carrier"]], ["Policyholder's Employer: " + cli_data[key]["Patient Information"]["Policyholder's Employer"], "Insurance Plan Number: " + cli_data[key]["Patient Information"]["Insurance Plan Number"]]]

	fourth = [tabulate(table, tablefmt='simple_grid', maxcolwidths=[len("Policyholder\'s Employer: "), len("Insurance Carrier: "), len("Insurance Plan")])]

	table = [["Diagnosis", "ICD-10"], [cli_data[key]["Diagnosis"][0], cli_data[key]["ICD-10"]]]
	fifth = [tabulate(table, tablefmt='simple_grid', maxcolwidths=[15, None])]

	table = [["Diagnosis", "CPT CODE"], [cli_data[key]["Diagnosis"][1], cli_data[key]["CPT CODE"]]]
	sixth = [tabulate(table, tablefmt='simple_grid', maxcolwidths=[15, None])]

	table = [["Number", "Dates of Services", "CPT CODE", "Description", "Amount", "Paid"]]
	table.extend([i+1, att_data[key][service_type][month+"/"+year][i][2], cli_data[key]["CPT CODE"], cli_data[key]["Attendance"]["Description"], cli_data[key]["Attendance"]["Amount"], "yes"] for i in range(len(att_data[key][service_type][month+"/"+year])))

	seventh = ["Attendance"]
	eighth = [tabulate(table, tablefmt='simple_grid', maxcolwidths=[11, 11, 11, 11, 11])]


	return zeroeth + ["\n"] + first + ["\n"] + second + ["\n"] + third + ["\n"] + fourth + ["\n"] + fifth + ["\n"] + sixth + ["\n"] + seventh + ["\n"] + eighth + ["\n"]

def save_att(the_sheet, name, monthyear, phone, att_type):
	# cli_att_json = copy.deepcopy(template_att_json)
	key = name + "@" + phone
	cli_att_json = template_att_json.copy()
	if(not os.path.exists('./attendance.json')):
			open("attendance.json", "x")
	with open("attendance.json", "r") as file:
		if(os.path.getsize("attendance.json") != 0):
				existing_data = json.load(file)
		else:
			existing_data = {}
	att_sheet = the_sheet.get_sheet_data(
		get_displayed=True, get_header=False,
		get_index=False, get_index_displayed=False,
		get_header_displayed=True, only_rows=None,
		only_columns=None)
	cli_att_json[key] = cli_att_json.pop("name")
	if(monthyear not in cli_att_json[key][att_type]):
		cli_att_json[key][att_type][monthyear] = []
	cli_att_json[key][att_type][monthyear].clear()
	for x in range(len(att_sheet)):
		for y in range(len(att_sheet[x])):
			if(att_sheet[x][y] != ""):
				if(the_sheet.checkbox(x, y, checked = None, state = None, check_function = "", text = None)["checked"]):
					day = [x,y,the_sheet.checkbox(x, y, checked = None, state = None, check_function = "", text = None)["text"]]
					cli_att_json[key][att_type][monthyear].append(day)
	if(key not in existing_data):
		existing_data[key] = cli_att_json[key]
	elif(monthyear not in existing_data[key][att_type]):
		existing_data[key][att_type][monthyear] = cli_att_json[key][att_type][monthyear]
	else:
		existing_data[key][att_type][monthyear].clear()
		for item in cli_att_json[key][att_type][monthyear]:
			existing_data[key][att_type][monthyear].append(item)
	with open("attendance.json", "w") as file:
		json.dump(existing_data, file, indent=4)

	newWindow = tk.Toplevel()
	newWindow.title("Done!")
	newWindow.geometry("200x200")
	Label(newWindow,text ="Done!").pack()
	exit_button = ttk.Button(newWindow, text="Exit", command=newWindow.destroy)
	exit_button.pack(pady=20)

if __name__ == "__main__":
	app = demo()
	app.mainloop()
