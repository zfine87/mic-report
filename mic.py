#General System Imports
import sys
import csv
import urllib.request

#Web Request Imports
import requests
from requests.auth import HTTPBasicAuth
from requests.auth import HTTPDigestAuth

#tkinter GUI Imports
from tkinter import *
import tkinter.filedialog

filename = ""
print_f = ""

class Event:
	def __init__(self, mic, b_list, m_list, date, link, length):
		self.b_list = rosterify(b_list, length)
		self.mic = mic
		self.m_list = [x.lower() for x in m_list]
		self.date = date
		self.link = link
		self.id = link.split('=')[-1]
		self.length = length

	def name_list(self):
		l = []
		for each in self.b_list:
			l.append(each.name)
		return l


class Brother:
	def __init__(self, name, hours):
		self.name = name.lower()
		self.hours = hours


def rosterify(s, l):
	#Turn brother and hour data into brother object
	b_list = []
	name = ''
	s = s.split("\n")
	for each in s:
		each = each.strip(",")
		name = ''
		try: 
			float(each.split(" ")[-1])
		except ValueError:
		 	x = each.split(' ')
		 	for i in range (0, len(x)):
		 		name += (x[i] + " ")
		 	b_list.append(Brother(name, float(l)))
		else:
			x = each.split(' ')
			for i in range (0, len(x)-1):
		 		name += (x[i] + " ")
			b_list.append(Brother(name, float(x[-1])))

	return b_list[0:len(b_list)]


def parse_csv(r):
	#Timestamp, MIC, Date, Length, Roster, Makeups, Link
	global print_f
	data = []
	for item in r:
		s = item.split(',')
		data.append(s)
	b_list = ''
	for i in data[4]:
		b_list += i + ','
	print_f = ("Event: " + data[2][0] + "\n")
	return Event(data[1][0], b_list, data[5], data[3][0], data[6][0], data[7][0])


def parse_source(link):

	roster = []

	#Parse APOOnline data from the events webpage
	username = 'zach@delbenegroup.com'
	password = 'Crzd1245!'

	loginurl = 'http://www.apoonline.org/alpharho/memberhome.php?'
	dataurl = link
	formdata = {
    'email': username,
    'password': password,
    'submit' : 'Login'
	}	

	session = requests.session()
	r = session.post(loginurl, data = formdata, allow_redirects=False)

	action = 'eventsignup'
	eventid = '156263'
	formdata = {
    'action': action,
    'eventid' : eventid
	}	
	r2 = session.get(dataurl, data = formdata)
	s = str(r2.text)
	s = s.split("Comment")[-1]
	s = s.split("?action=profile&userid=")
	for i in range(0, len(s)):
		x = s[i].split(">")[1]
		roster.append(x.split('<')[0].lower())

	# s = str(r2.text).split("Tip('Sign-ups Lock')'")[0]
	# s = s.split("Event Coordinator")[0]
	# s = s.split('UnTip()')[-1]
	# s = s.split("<li>")
	# for i in range(1, len(s)):
	# 	s[i] = s[i].split("<")[0]
	# hours = find_hours(s[1:len(s)]))


	return roster[1:len(roster)]
	

# def find_hours(h):
# 	l = []
# 	for each in h:
# 		if h.count("Service Hour"):
# 			l.append(('General Service', float(h[0])))
# 		if h.count("Service To F"):
# 			l.append(('Fraternity Service', float(h[0])))
# 		if h.count("Flag Event"):
# 			l.append(('Flag Credit', float(h[0])))


def calculate_hours(event, roster):
	global print_f
	prints = []
	full_a = []
	part_a = []
	not_a = []
	#Calculate the hours a brother should be given for an event given info from MIC report and APOOnline
	mic_roster = event.name_list()
	#print(event.m_list)
	for brother in roster:
		if brother not in mic_roster:
			if brother not in event.m_list:
				#Give Negative Hours
				#event.b_list.append(Brother(brother + " DID NOT ATTEND", float(event.length)))
				not_a.append(brother + " DID NOT ATTEND")

	prints.append("Length of Event: " + event.length)
	for each in event.b_list:
		if each.hours != float(event.length):
			part_a.append(each.name + "only attended the event for " + str(each.hours) + " hours.")
		else:
			full_a.append(each.name)

	prints.append("On: " + event.date)
	prints.append('')
	prints.append("Full Attendees:")
	for each in full_a:
		prints.append(each)
	prints.append('')
	prints.append("Partial Attendees")
	for each in part_a:
		prints.append(each)
	prints.append('')
	prints.append("Did Not Attend")
	for each in not_a:
		prints.append(each)
	strs = "\n"

	print_f += strs.join(prints)

def main():
	global filename

	try:
		f = open(filename, 'rt')
		r = csv.reader(f)
		next(r)
		for row in r:
			event = parse_csv(row)
			online_roster = parse_source(event.link)
			calculate_hours(event, online_roster)
	finally:
		f.close()
		window.set_var(root)


class Window:       
    def __init__(self, master): 
        global print_f
        self.filename=StringVar()
        self.outputs = StringVar()
        csvfile=Label(root, text="File").grid(row=1, column=0)
        bar=Entry(master, textvariable=self.filename).grid(row=1, column=1) 

        #Buttons  
        y=7
        self.cbutton= Button(root, text="OK", command=main)
        y+=1
        self.cbutton.grid(row=10, column=3, sticky = W + E)
        self.bbutton= Button(root, text="Browse", command=self.browsecsv)
        self.bbutton.grid(row=1, column=3)

    def browsecsv(self):
    	global filename
    	from tkinter.filedialog import askopenfilename

    	Tk().withdraw() 
    	filename = askopenfilename()
    	self.filename.set(filename)

    def set_var(self, master):
    	global print_f
    	output = Text(master, wrap=WORD, width = 60, height=40)
    	output.grid(row=11, column=0)
    	scrollbar = Scrollbar(master,orient=VERTICAL)
    	scrollbar.grid(row=11, column=1,sticky=(N,S))
    	output['yscrollcommand'] = scrollbar.set
    	output.insert('1.0', print_f)
    	scrollbar.config(command=output.yview)


root = Tk()
window=Window(root)
root.mainloop()