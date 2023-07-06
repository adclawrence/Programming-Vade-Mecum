import os
import re

class htmlpage:
	doctype = "<!DOCTYPE html>"
	def __init__(self,title="title"):
		self.title = title
		self.head = []
		self.style = []
		self.toc = []
		self.body = []
		
	def set_title(self,title):
		self.title = title
	
	def set_style(self,mode = "inline" ,css="progvm.css"):
		if mode == "external":
			self.style.append('<link rel="stylesheet" href="{}">'.format(css))
		else:
			cssfile = open(css,"r")
			csstext = cssfile.read()
			cssfile.close()
			self.style.append("<style>")
			self.style.append(csstext)
			self.style.append("</style>")
		
	def page(self):
		pagetext = []
		pagetext.append(self.doctype)
		pagetext.append("<html>\n<head>")
		pagetext.append("<title>" + self.title + "</title>")
		pagetext.extend(self.style)		
		pagetext.append("</head>\n<body>")
		pagetext.extend(self.toc)
		pagetext.extend(self.body)
		pagetext.append("</body>\n</head>")
		return "\n".join(pagetext)
	def set_body(self,textblock):
		self.body = textblock
	def append_body(self,text):
		self.body.append(text)
	def append_toc(self,text):
		self.toc.append(text)
	
def tag(tagname,text):
	return("<{0}>{1}</{0}>".format(tagname,text))
def heading(level,text,idno=0):
	id = "id" + str(idno)
	#return("<h{0}>{1}</h{0}>".format(level,text))
	return("<h{0} id=\"{2}\">{1}</h{0}>".format(level,text,id))

class subjectcontent:
	def __init__(self,subject):
		self.subject = subject
		self.contents = {}
	def add_item(self,subtopic,id):
		self.contents[id] = subtopic
	def get_content(self):
		return(self.contents)

#def checktext(plaintext):

##### MAIN #####

#find and read source file
vmfname = "programming reference.vm.txt"
if not os.path.isfile(vmfname):
	print("***'" + vmfname + "' file not found.Aborting!!!")
	exit()

vmprefix = vmfname[:vmfname.find(".")]
print(vmfname + "=>" + vmprefix)

#exit()

infile = open(vmfname,"r")
intext = infile.read()
infile.close()

#print(intext)
srclines = intext.split("\n")
outtext = []

bodytext = [] #for html file
plaintext = [] #for ordinary text file

#processing source text
print(heading(1,srclines[0]))
#bodytext.append(heading(1,srclines[0])) #moved 

plaintext.append(srclines[0])

id_ctr = 0

codeon = False
codetoggle = "~"

entity = {"&" : "&amp;", "<" : "&lt;", ">" : "&gt;"}
entset = "[" + "".join(entity.keys()) + "]"
print("reserved characters: {" + entset + "}")
hdrmrk = {">" : 2, ":" : 3}
rx = re.compile("(" + entset + ")")
#exit()

contents = {}

topic = ""
subtopic = ""
bodytext.append('<div class="main">')
for aline in srclines[1:]:
	if aline == codetoggle:
		codeon = not codeon
		if codeon:
			bodytext.append("<code>")
		else:
			bodytext.append("</code>")
		continue
	#end if codetoggle
	if aline == (codetoggle + codetoggle):
		if codeon:
			bodytext.append("</code><code>")
		else:
			bodytext.append("<code></code>")
		continue
	#end if double codetoggle
	if aline == "~~~":
		break
	plaintext.append(aline)
	
	if aline == "":
		bodytext.append("")
		continue

	if aline[0] in hdrmrk: #prevent empty string line before here
		#heading lines
		hdrlevel = hdrmrk[aline[0]]
		id_ctr += 1
		print(aline + " idno:" + str(id_ctr))
		linetext = aline[1:]
		result = rx.search(linetext) #check and replace entitiy chars
		if result:
			linetext =rx.sub(lambda x: entity[x.group(1)],linetext)
		outline = heading(hdrlevel,linetext,id_ctr)
		#content  items
		if hdrlevel == 2:
			topic = linetext
			if topic not in contents:
				contents[topic] = subjectcontent(topic)
		elif hdrlevel == 3:
			subtopic = linetext
			contents[topic].add_item(subtopic,id_ctr)
		print(f"{id_ctr}>{topic}:{subtopic}")
		print(outline) # (heading(3,aline[1:]))
	else:
		#outline = aline
		result = rx.search(aline) #check and replace entitiy chars
		if result: 
			outline = rx.sub(lambda x: entity[x.group(1)],aline)
		else:
			outline = aline
	bodytext.append(outline)
#end for aline
bodytext.append("</div>")
#print("\n".join(bodytext))


#write contents
toctext = []
toctext.append('<span class="nav">')
toctext.append(heading(1,srclines[0]))
for subject in contents:
	#print("*\t" + subject)
	toctext.append(f"<strong>{subject}</strong>: ")
	subtopics = contents[subject].get_content()
	for idno in subtopics:
		toctext.append(f'<a href="#id{idno}">{subtopics[idno]}</a>')
		print(f"-\t{idno}\t{subtopics[idno]}")
	toctext.append("<br>")
toctext.append("</span>")

bodytext.insert(0,"\n".join(toctext))
#bodytext.insert(0,heading(1,srclines[0]))
#output	
#html output
webpage = htmlpage("vade mecum")
webpage.set_style("external") # .set_style("external") for testing css styles
webpage.set_body(bodytext)
#webpage.append_toc("\n".join(toctext))



print(webpage.page())	

outfile = open(vmprefix + ".html","w")
outfile.write(webpage.page())
outfile.close

#plain text output
plainfile = open(vmprefix + ".txt","w")
plainfile.write("\n".join(plaintext))
plainfile.close

for subject in contents:
	print("*\t" + subject)
	subtopics = contents[subject].get_content()
	for idno in subtopics:
		print(f"-\t{idno}\t{subtopics[idno]}")
#print(toctext)
#print(webpage.toc)
print("\nend")