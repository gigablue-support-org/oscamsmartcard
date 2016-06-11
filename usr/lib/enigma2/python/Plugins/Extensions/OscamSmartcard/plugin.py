from Plugins.Plugin import PluginDescriptor
from Screens.Screen import Screen
from Screens.MessageBox import MessageBox
from Screens.ChoiceBox import ChoiceBox
from Screens.Console import Console
from Screens.Standby import TryQuitMainloop
from Components.ActionMap import ActionMap
from Components.AVSwitch import AVSwitch
from Components.config import config, configfile, ConfigYesNo, ConfigSubsection, getConfigListEntry, ConfigSelection, ConfigNumber, ConfigText, ConfigInteger
from Components.ConfigList import ConfigListScreen
from Components.Label import Label
from Components.Language import language
from os import environ, listdir, remove, rename, system, popen
from skin import parseColor
from Components.Pixmap import Pixmap
from Components.Label import Label
import gettext
import base64
from enigma import ePicLoad
from Tools.Directories import fileExists, resolveFilename, SCOPE_LANGUAGE, SCOPE_PLUGINS
import os
import time
import glob
import urllib2
from boxbranding import *
#
ignore1='enigma2-plugin-softcams-oscamsmartcard'
ignore2='enigma2-plugin-pli-softcamsetup'
ignore3='enigma2-plugin-softcams-oscamstatus'
ignore4='enigma2-plugin-softcams-cccam.config'
ignore5='enigma2-plugin-softcams-mgcamd.config'
ignore6='enigma2-plugin-systemplugins-softcamstartup'
ignore7='enigma2-plugin-systemplugins-softcamstartup-src'
ignore8='softcam-feed-mipsel'
info = 'aHR0cDovL3d3dy5naWdhYmx1ZS1zdXBwb3J0Lm9yZy9kb3dubG9hZC9vc2NhbXNtYXJ0Y2FyZC92ZXJzaW9uLmluZm8='
srv = 'aHR0cDovL3d3dy5naWdhYmx1ZS1zdXBwb3J0Lm9yZy9kb3dubG9hZC9vc2NhbXNtYXJ0Y2FyZC8='
ipx = 'aHR0cDovLzE5Mi4xODUuNDEuMjc='
plugin='[OscamSmartcard] '
null =' >/dev/null 2>&1'
#
globals()
ImageTypeInfo = (getMachineBrand() + ' - '+  getMachineName()+ ' - ' + getImageDistro().title() + '-' + getImageVersion() + ' - Driver: ' + getDriverDate() )#.title()

def architectures():
	hardwaretype = popen('uname -m').read().strip()
	hostname = popen('uname -n').read().strip()
	kernelversion = popen('uname -r').read().strip()
	ossystem = popen('uname -s').read().strip()
	return ossystem,kernelversion,hardwaretype,hostname

arch = architectures()[2]
extrainfo=(architectures()[3] +': ' + architectures()[0]+' - '+architectures()[1]+' - '+ arch).title()
lang = language.getLanguage()
environ["LANGUAGE"] = lang[:2]
gettext.bindtextdomain("enigma2", resolveFilename(SCOPE_LANGUAGE))
gettext.textdomain("enigma2")
gettext.bindtextdomain("OscamSmartcard", "%s%s" % (resolveFilename(SCOPE_PLUGINS), "Extensions/OscamSmartcard/locale/"))
def _(txt):
	t = gettext.dgettext("OscamSmartcard", txt)
	if t == txt:
		t = gettext.gettext(txt)
	return t

def translateBlock(block):
	for x in TranslationHelper:
		if block.__contains__(x[0]):
			block = block.replace(x[0], x[1])
	return block

config.plugins.OscamSmartcard = ConfigSubsection()
config.plugins.OscamSmartcard.menufake = ConfigSelection(default="-", choices = [("-", "-")])

config.plugins.OscamSmartcard.Camstart = ConfigSelection(default="openmips", choices = [
				("openmips", _("Script SoftCamstart (openMips)")),
				("openatv", _("Python SoftCamstart (openATV)"))
				])
config.plugins.OscamSmartcard.systemclean = ConfigSelection(default="cleanall_yes", choices = [
				("cleanall_yes", _(' '))
				])
config.plugins.OscamSmartcard.ConfigPath = ConfigSelection(default="/etc/tuxbox/config/", choices = [
				("/usr/keys/", _("/usr/keys/ (openATV)")),
				("/etc/tuxbox/config/", _("/etc/tuxbox/config/ (openMips)"))
				])
config.plugins.OscamSmartcard.WebifPort = ConfigSelection(default="83", choices = [
				("83", _("83")),
				("8888", _("8888"))
				])
config.plugins.OscamSmartcard.oscambinary = ConfigSelection(default="no_binary_install", choices = [
				("no_binary_install", _("No")),
				("yes_binary_install", _("Yes"))
				])
config.plugins.OscamSmartcard.cccam  = ConfigSelection(default="no_cccam_import", choices = [
				("no_cccam_import", _("No")),
				("yes_cccam_import", _("Yes"))
				])
config.plugins.OscamSmartcard.emu  = ConfigSelection(default="no_emu", choices = [
				("no_emu", _("No")),
				("yes_emu", _("Yes"))
				])
config.plugins.OscamSmartcard.hasciplus  = ConfigSelection(default="no_ciplus", choices = [
				("no_ciplus", _("None")),
				("ciplusV13", _("CI+ V13")),
				("ciplusV14", _("CI+ V14"))
				])
		
cardlist = [
	("V13", "Sky V13"),
	("V13_fast", "Sky V13 Fastmode"),
	("V14", "Sky V14"),
	("V14_fast", "Sky V14 Fastmode"),
	("HD01", "HD+ HD01 white"),
	("HD02", "HD+ HD02 black"),
	("I02-Beta", "I02 Beta"),
	("I12-Beta", "I12 Beta"),
	("I12-Nagra", "I12 Nagra"),
	("V23", "KabelBW V23"),
	("ORF_ICE_crypto", "ORF ICE Cryptoworks 0D95"),
	("ORF_ICE_irdeto", "ORF ICE Irdeto 0648"),
	("SRG-V2", "SRG V2"),
	("SRG-V4", "SRG V4"),
	("SRG-V5", "SRG V5"),
	("UM01", "UnityMedia UM01"),
	("UM02", "UnityMedia UM02"),
	("UM03", "UnityMedia UM03"),
	("D01", "Kabel Deutschl. D01"),
	("D02", "Kabel Deutschl. D02"),
	("D09", "Kabel Deutschl. D09"),
	("KDG0x", "Kabel Deutschl. G02/G09"),
	("smartHD", "NC+ SmartHD+"),
	("MTV", "MTV"),
	("tivu", "Tivusat"),
	("JSC", "JSC-sports - Viaccess"),
	("RedlightHD", "Redlight Elite HD - Viaccess"),
	("default", "Standard 357/357 MHz"),
	("none", _("None"))
	]
config.plugins.OscamSmartcard.internalReader0 = ConfigSelection(default="none", choices = cardlist)
config.plugins.OscamSmartcard.internalReader1 = ConfigSelection(default="none", choices = cardlist)
config.plugins.OscamSmartcard.externalReader0 = ConfigSelection(default="none", choices = cardlist)
config.plugins.OscamSmartcard.externalReader1 = ConfigSelection(default="none", choices = cardlist)
class OscamSmartcard(ConfigListScreen, Screen):
	skin ="""
<screen name="OscamSmartcard-Setup" position="center,center" size="1280,720" flags="wfNoBorder" backgroundColor="#90000000">
	<eLabel name="new eLabel" position="40,40" zPosition="-2" size="1200,640" backgroundColor="black" transparent="0" />
	<eLabel font="Regular; 20" foregroundColor="white" backgroundColor="#20000000" halign="left" position="77,645" size="250,33" text="Cancel" transparent="1" />
	<eLabel font="Regular; 20" foregroundColor="white" backgroundColor="#20000000" halign="left" position="375,645" size="250,33" text="Start" transparent="1" />
	<eLabel font="Regular; 20" foregroundColor="white" backgroundColor="#20000000" halign="left" position="682,645" size="250,33" text="Reboot Box" transparent="1" />
	<eLabel font="Regular; 20" foregroundColor="white" backgroundColor="#20000000" halign="left" position="989,645" size="250,33" text="make clean" transparent="1" />
	<widget name="config" position="61,114" size="590,380" scrollbarMode="showOnDemand" transparent="1" backgroundColor="black" />
	<eLabel position="62,48" size="348,50" text="OscamSmartcard" font="Regular; 40" valign="center" transparent="1" backgroundColor="#20000000" />
	<eLabel position="417,48" size="451,50" text="Setup" foregroundColor="white" font="Regular; 40" valign="center" backgroundColor="#20000000" transparent="1" halign="left" />
	<eLabel position="665,640" size="5,40" backgroundColor="#e5dd00" />
	<eLabel position="360,640" size="5,40" backgroundColor="#61e500" />
	<eLabel position="60,640" size="5,40" backgroundColor="#e61700" />
	<eLabel position="965,640" size="5,40" backgroundColor="#0000ff" />
	<widget name="oscamsmartcardhelperimage" position="669,112" size="550,500" zPosition="1" backgroundColor="background" />
	<widget name="HELPTEXT" position="61,500" size="590,110" zPosition="1" font="Regular; 20" halign="left" valign="top" backgroundColor="black" transparent="1" />
    <eLabel text="OscamSmartcard 2.0 by arn354 and Undertaker" position="874,48" size="360,25" zPosition="1" font="Regular; 15" halign="right" valign="top" backgroundColor="#20000000" transparent="1" />
</screen>"""
	def __init__(self, session, args = None, picPath = None):
		self.config_lines = []
		Screen.__init__(self, session)
		self.session = session
		self.oscamconfigpath = config.plugins.OscamSmartcard.ConfigPath.value
		self.oscamcamstartvalue = config.plugins.OscamSmartcard.Camstart.value
		self.oscamuser = (self.oscamconfigpath + "oscam.user")
		self.oscamuserTMP = (self.oscamuser + ".tmp")
		self.oscamconf = (self.oscamconfigpath + "oscam.conf")
		self.oscamconfTMP = (self.oscamconf + ".tmp")
		self.oscamserver = (self.oscamconfigpath + "oscam.server")
		self.oscamserverTMP = (self.oscamserver + ".tmp")
		self.oscamdvbapi = (self.oscamconfigpath + "oscam.dvbapi")
		self.oscamdvbapiTMP = (self.oscamdvbapi + ".tmp")
		self.picPath = picPath
		self.Scale = AVSwitch().getFramebufferScale()
		self.PicLoad = ePicLoad()
		self["oscamsmartcardhelperimage"] = Pixmap()
		self["HELPTEXT"] = Label()
		if  self.onlinecheck() == False:
			list = []
			list.append(getConfigListEntry(_("Your STB is not connected to the Internet"), config.plugins.OscamSmartcard.menufake, _("press color button or lame for exit")))
			list.append(getConfigListEntry(_("press color button or lame for exit"), ))
			ConfigListScreen.__init__(self, list)
			self["actions"] = ActionMap(["OkCancelActions","DirectionActions", "InputActions", "ColorActions", "SetupActions"], {"red": self.exit,"yellow": self.exit,"blue": self.exit,"green": self.exit,"ok": self.exit,"cancel": self.exit}, -1)
			self.exit
		else:
			if arch != 'armv7l' and arch != 'mips' and arch != 'sh4' and arch != 'ppc' and arch != 'armv7ahf-vfp-neon':
				list = []
				list.append(getConfigListEntry(_("Warning"), config.plugins.OscamSmartcard.menufake, _("press color button or lame for exit")))
				list.append(getConfigListEntry((_("Unsupportet CPU") +' ' + arch +' '+ _("found")), ))
				list.append(getConfigListEntry(_(extrainfo), ))
				list.append(getConfigListEntry(_("press color button or lame for exit"), ))
				ConfigListScreen.__init__(self, list)
				self["actions"] = ActionMap(["OkCancelActions","DirectionActions", "InputActions", "ColorActions", "SetupActions"], {"red": self.exit,"yellow": self.exit,"blue": self.exit,"green":self.exit,"ok": self.exit,"cancel": self.exit}, -1)
				self.exit
			else:
				a=self.checkallcams()
				anzahl = len(a)
				if len(a)>0:
					list = []
					list.append(getConfigListEntry( ( _("Warning")  + " : " +str(anzahl) +' '+ _("valueless Softam found. Press GREEN to remove")   ), config.plugins.OscamSmartcard.systemclean, ( _("Remove all first.\notherwise Oscamsmartcard will not start\nPress GREEN to remove all") + '\n' + _("All config files are backed up automatically"))))
					i=0
					while i < len(a):
						title = a[i].replace("enigma2-plugin-softcams-",'')
						desc = a[i]
						xx = 'config.plugins.OscamSmartcard.installed'+str(i)
						xx = ConfigSelection(default="Yes", choices = [("Yes", _("Yes"))])
						list.append(getConfigListEntry(_(str(i+1) +".)  " + title), xx, _(desc)))
						i = i + 1
					ConfigListScreen.__init__(self, list)
					self["actions"] = ActionMap(["OkCancelActions","DirectionActions", "InputActions", "ColorActions", "SetupActions"], {"left": self.keyLeft,"down": self.keyDown,"up": self.keyUp,"right": self.keyRight,"red": self.exit,"yellow": self.reboot,"blue": self.exit,"green": self.systemcleaning,"cancel": self.exit}, -1)
					self.onLayoutFinish.append(self.UpdatePicture)
					if not self.selectionChanged in self["config"].onSelectionChanged:
						self["config"].onSelectionChanged.append(self.selectionChanged)
					self.selectionChanged()
				else:
					self.createoscamsmartcarddata()
					self.oscamsmartcarddata = "/tmp/data/"
					self.downloadurl()
					onlineavaible = self.newversion(arch)
					list = []
					if getImageDistro() =='openatv':
						camstartname='Openatv System'
						config.plugins.OscamSmartcard.Camstart.value = "openatv"
						config.plugins.OscamSmartcard.ConfigPath.value = "/usr/keys/"
					elif getImageDistro() =='openmips':
						camstartname='SoftcamManager'
						config.plugins.OscamSmartcard.Camstart.value = "openmips"
						config.plugins.OscamSmartcard.ConfigPath.value = "/etc/tuxbox/config/"
					else:
						camstartname='SoftcamManager'
						config.plugins.OscamSmartcard.Camstart.value = "openmips"
						config.plugins.OscamSmartcard.ConfigPath.value = "/etc/tuxbox/config/"
					
					list.append(getConfigListEntry("-------------------------------------- Auto Config----------------------------------------", config.plugins.OscamSmartcard.menufake, _("INFORMATION: make your selection and press GREEN\nAll config files are backed up automatically")))
					list.append(getConfigListEntry(_(ImageTypeInfo), ))
					list.append(getConfigListEntry((extrainfo), ))
					list.append(getConfigListEntry(( _("Config path set automatically to") + '\t: '+ config.plugins.OscamSmartcard.ConfigPath.value), ))
					list.append(getConfigListEntry(( _("Camstart set automatically to") + '\t: ' + camstartname), ))
					list.append(getConfigListEntry(( _("Oscam type set automatically to") + '\t: ' + arch), ))
					list.append(getConfigListEntry(( _("Cardreader found automatically")  + '\t: ' + str(self.readercheck()[4])  ), ))
					list.append(getConfigListEntry(("............................................. Manual Config .........................................."), ))
					list.append(getConfigListEntry(_("Select OScam WebifPort:"), config.plugins.OscamSmartcard.WebifPort, _("INFORMATION: Select OScam WebifPort\n\nOscam Webif will be accessible on the selected port.\ne.g. http:\\IPOFYOURBOX:83")))
					if self.readercheck()[0] == 'installed':
						list.append(getConfigListEntry(_("Internal Reader /dev/sci0:"), config.plugins.OscamSmartcard.internalReader0, _("INFORMATION: Internal Reader /dev/sci0\n\nAll STB's having only one cardslot.\nOn STB's having two cardslots it is mostly the lower cardslot.")))
					if self.readercheck()[1] == 'installed':
						list.append(getConfigListEntry(_("Internal Reader /dev/sci1:"), config.plugins.OscamSmartcard.internalReader1, _("INFORMATION: Internal Reader /dev/sci1\n\nOn STB's having two cardslots it is mostly the upper cardslot.")))
					if self.readercheck()[2] == 'installed':
						list.append(getConfigListEntry(_("External Reader /dev/ttyUSB0:"), config.plugins.OscamSmartcard.externalReader0, _("INFORMATION: External Reader /dev/ttyUSB0\n\nThis Reader can be used to configure for example a connected easymouse.")))
					if self.readercheck()[3] == 'installed':
						list.append(getConfigListEntry(_("External Reader /dev/ttyUSB1:"), config.plugins.OscamSmartcard.externalReader1, _("INFORMATION: External Reader /dev/ttyUSB1\n\nThis Reader can be used to configure for example a second connected easymouse.")))
					anzcc= self.cccamcheck()[1]
					anzus= self.cccamcheck()[5]
					anz35= self.cccamcheck()[3]
					cccport= self.cccamcheck()[6]
					if anzcc > 0 or anzus >0 or anz35 >0:
						list.append(getConfigListEntry(( _("CCcam.cfg found. Import your settings") ), config.plugins.OscamSmartcard.cccam, ( _("Oscamsmartcard found ") + str(anzcc+anz35) + _(" Server and ") + str(anzus) + " User in CCCam.cfg\n" + str(anzcc) + " x CCcam-Server\t" + str(anz35) +' x Camd35 Server\n' + str(anzus) + ' x Userlines (Friends)\tShareport: ' +cccport  )))
					list.append(getConfigListEntry(_("Oscam binary install"),config.plugins.OscamSmartcard.oscambinary,('INFORMATION: ' + _("install or update to the latest version") + '\n\n' +  _("installed")  + ' \t: ' + self.currentversion() + '\n' + _("online avaible") + '\t: ' + onlineavaible )))
					if getImageDistro() =='openatv':
						list.append(getConfigListEntry(_("Install oscam EMU Version:"), config.plugins.OscamSmartcard.emu, _("INFORMATION: install Oscam Emu Version\n\nSoftcam.key included")))
					list.append(getConfigListEntry(_("Which Ci+Module is installed:"), config.plugins.OscamSmartcard.hasciplus, _("INFORMATION: please select your CI+ Modul\n\n")))
					list.append(getConfigListEntry("---------------------------------------------------------------------------------------------------", ))
					ConfigListScreen.__init__(self, list)
					self["actions"] = ActionMap(["OkCancelActions", "DirectionActions", "InputActions", "ColorActions"], {"left": self.keyLeft,"down": self.keyDown,"up": self.keyUp,"right": self.keyRight,"red": self.exit,"yellow": self.reboot, "blue": self.rmconfig, "green": self.save,"cancel": self.exit}, -1)
					self.onLayoutFinish.append(self.UpdatePicture)
					if not self.selectionChanged in self["config"].onSelectionChanged:
						self["config"].onSelectionChanged.append(self.selectionChanged)
					self.selectionChanged()

	def selectionChanged(self):
		self["HELPTEXT"].setText(self["config"].getCurrent()[2])

	def GetPicturePath(self):
		try:
			returnValue = self["config"].getCurrent()[1].value
			path = "/usr/lib/enigma2/python/Plugins/Extensions/OscamSmartcard/images/" + returnValue + ".png"
			return path
		except:
			return "/usr/lib/enigma2/python/Plugins/Extensions/OscamSmartcard/images/no.png"

	def UpdatePicture(self):
		self.PicLoad.PictureData.get().append(self.DecodePicture)
		self.onLayoutFinish.append(self.ShowPicture)

	def ShowPicture(self):
		self.PicLoad.setPara([self["oscamsmartcardhelperimage"].instance.size().width(),self["oscamsmartcardhelperimage"].instance.size().height(),self.Scale[0],self.Scale[1],0,1,"#20000000"])
		self.PicLoad.startDecode(self.GetPicturePath())

	def DecodePicture(self, PicInfo = ""):
		ptr = self.PicLoad.getData()
		self["oscamsmartcardhelperimage"].instance.setPixmap(ptr)

	def keyLeft(self):
		ConfigListScreen.keyLeft(self)
		self.ShowPicture()

	def keyRight(self):
		ConfigListScreen.keyRight(self)
		self.ShowPicture()

	def keyDown(self):
		self["config"].instance.moveSelection(self["config"].instance.moveDown)
		self.ShowPicture()

	def keyUp(self):
		self["config"].instance.moveSelection(self["config"].instance.moveUp)
		self.ShowPicture()

	def reboot(self):
		restartbox = self.session.openWithCallback(self.restartSTB,MessageBox,_("Do you really want to reboot now?"), MessageBox.TYPE_YESNO)
		restartbox.setTitle(_("Restart STB"))

	def systemcleaning(self):
		systemclean = self.session.openWithCallback(self.systemclean,MessageBox,_(_("All Softcams will be deinstalled\nAre you sure ?")), MessageBox.TYPE_YESNO)
		systemclean.setTitle(_("System cleaning"))
		self.close()

	def showInfo(self):
		self.session.open(MessageBox, _("Information"), MessageBox.TYPE_INFO)

	def save(self):
		self.oscamconfigpath = config.plugins.OscamSmartcard.ConfigPath.value
		self.oscamcamstartvalue = config.plugins.OscamSmartcard.Camstart.value
		self.oscamuser = (self.oscamconfigpath + "oscam.user")
		self.oscamuserTMP = (self.oscamuser + ".tmp")
		self.oscamconf = (self.oscamconfigpath + "oscam.conf")
		self.oscamconfTMP = (self.oscamconf + ".tmp")
		self.oscamserver = (self.oscamconfigpath + "oscam.server")
		self.oscamserverTMP = (self.oscamserver + ".tmp")
		self.oscamdvbapi = (self.oscamconfigpath + "oscam.dvbapi")
		self.oscamdvbapiTMP = (self.oscamdvbapi + ".tmp")
		self.oscamservices = (self.oscamconfigpath + "oscam.services")
		self.oscamservicesTMP = (self.oscamservices + ".tmp")
		self.oscamcamstart = '/etc/oscamsmartcard.emu'
		self.oscamcamstartTMP = (self.oscamcamstart + ".tmp")
		for x in self["config"].list:
			if len(x) > 1:
					x[1].save()
			else:
					pass
		try:
			system('mkdir ' + config.plugins.OscamSmartcard.ConfigPath.value + ' > /dev/null 2>&1')
		except:
			pass
		self.makebackup()
		self.saveoscamserver()
		self.saveoscamdvbapi()
		self.saveoscamuser()
		self.saveoscamconf()
		self.saveoscamservices()
		self.saveoscamfiles()
		if config.plugins.OscamSmartcard.oscambinary.value == 'yes_binary_install':
			self.oscambinaryupdate()
		self.savecamstart()
		if getImageDistro() == 'openatv':
			system ('/usr/bin/oscam_oscamsmartcard -b -c /usr/keys > /dev/null 2>&1')
		elif getImageDistro() == 'openmips':
			system ('/etc/init.d/softcam start')
		else:
			self.session.open(MessageBox, _("Oscam is not running\nunknown OS"), MessageBox.TYPE_INFO,10)
			self.close()
		config.plugins.OscamSmartcard.save()        
		configfile.save()
		self.session.open(MessageBox, ( _("Oscam is now running") +'\n' + self.newversion(arch) + '\n' + getImageDistro()  +' ' + getImageVersion() ), MessageBox.TYPE_INFO,10)
		self.rmoscamsmartcarddata()
		self.close()

	def createoscamsmartcarddata(self):
		data = 'wget -O /tmp/data.zip '+ base64.b64decode(srv) +'data.zip ' + null
		popen(data)
		popen('unzip -o -q -d /tmp /tmp/data.zip')
		popen('rm /tmp/data.zip')

	def rmoscamsmartcarddata(self):
		popen('rm -rf /tmp/data')

	def saveoscamserver(self):
		try:
			self.appendconfFile(self.oscamsmartcarddata + "header.txt")
			if config.plugins.OscamSmartcard.emu.value =='yes_emu':
				self.appendconfFile(self.oscamsmartcarddata + "oscam.server_emu.txt")
			self.appendconfFile(self.oscamsmartcarddata + "oscam.server_" + config.plugins.OscamSmartcard.internalReader0.value + "_internalReader0.txt")
			self.appendconfFile(self.oscamsmartcarddata + "oscam.server_" + config.plugins.OscamSmartcard.internalReader1.value + "_internalReader1.txt")
			self.appendconfFile(self.oscamsmartcarddata + "oscam.server_" + config.plugins.OscamSmartcard.externalReader0.value + "_externalReader0.txt")
			self.appendconfFile(self.oscamsmartcarddata + "oscam.server_" + config.plugins.OscamSmartcard.externalReader1.value + "_externalReader1.txt")
			if config.plugins.OscamSmartcard.cccam.value =='yes_cccam_import':
				self.appendconfFile(self.oscamsmartcarddata + "cccamserver.txt")
			self.appendconfFile(self.oscamsmartcarddata + "footer.txt")
			xFile = open(self.oscamserverTMP, "w")
			for xx in self.config_lines:
				xFile.writelines(xx)
			xFile.close()
			o = open(self.oscamserver,"w")
			for line in open(self.oscamserverTMP):
				o.write(line)
			o.close()
			system('rm -rf ' + self.oscamserverTMP)
			self.config_lines = []
		except:
			self.session.open(MessageBox, _("Error creating oscam.server!"), MessageBox.TYPE_ERROR)
			self.config_lines = []

	def saveoscamdvbapi(self):
		try:
			self.appendconfFile(self.oscamsmartcarddata + "header.txt")
			if config.plugins.OscamSmartcard.hasciplus.value =='ciplusV14':
				self.appendconfFile(self.oscamsmartcarddata + "ciplusV14.txt")
			if config.plugins.OscamSmartcard.hasciplus.value =='ciplusV13':
				self.appendconfFile(self.oscamsmartcarddata + "ciplusV13.txt")
			self.appendconfFile(self.oscamsmartcarddata + "oscam.dvbapi_" + config.plugins.OscamSmartcard.internalReader0.value + ".txt")
			self.appendconfFile(self.oscamsmartcarddata + "oscam.dvbapi_" + config.plugins.OscamSmartcard.internalReader1.value + ".txt")
			self.appendconfFile(self.oscamsmartcarddata + "oscam.dvbapi_" + config.plugins.OscamSmartcard.externalReader0.value + ".txt")
			self.appendconfFile(self.oscamsmartcarddata + "oscam.dvbapi_" + config.plugins.OscamSmartcard.externalReader1.value + ".txt")
			if config.plugins.OscamSmartcard.cccam.value !='yes_cccam_import':
				self.appendconfFile(self.oscamsmartcarddata + "caidfinish.txt")
			self.appendconfFile(self.oscamsmartcarddata + "footer.txt")
	
			xFile = open(self.oscamdvbapiTMP, "w")
			for xx in self.config_lines:
				xFile.writelines(xx)
			xFile.close()
			o = open(self.oscamdvbapi,"w")
			for line in open(self.oscamdvbapiTMP):
				o.write(line)
			o.close()
			system('rm -rf ' + self.oscamdvbapiTMP)
			self.config_lines = []
		except:
			self.session.open(MessageBox, _("Error creating oscam.dvbapi!"), MessageBox.TYPE_ERROR)
			self.config_lines = []

	def saveoscamuser(self):
		try:
			self.appendconfFile(self.oscamsmartcarddata + "header.txt")
			self.appendconfFile(self.oscamsmartcarddata + "oscam.user.txt")
			if config.plugins.OscamSmartcard.cccam.value =='yes_cccam_import':
				self.appendconfFile(self.oscamsmartcarddata + "cccamuser.txt")
			self.appendconfFile(self.oscamsmartcarddata + "footer.txt")
			xFile = open(self.oscamuserTMP, "w")
			for xx in self.config_lines:
				xFile.writelines(xx)
			xFile.close()
			o = open(self.oscamuser,"w")
			for line in open(self.oscamuserTMP):
				if config.plugins.OscamSmartcard.internalReader0.value == 'I12-Beta':
					line = line.replace("betatunnel                    = 1833.FFFF:1702", "betatunnel                    = 1835.FFFF:1722,1833.FFFF:1702")
				if config.plugins.OscamSmartcard.internalReader1.value == 'I12-Beta':
					line = line.replace("betatunnel                    = 1833.FFFF:1702", "betatunnel                    = 1835.FFFF:1722,1833.FFFF:1702")
				if config.plugins.OscamSmartcard.externalReader0.value == 'I12-Beta':
					line = line.replace("betatunnel                    = 1833.FFFF:1702", "betatunnel                    = 1835.FFFF:1722,1833.FFFF:1702")
				if config.plugins.OscamSmartcard.externalReader1.value == 'I12-Beta':
					line = line.replace("betatunnel                    = 1833.FFFF:1702", "betatunnel                    = 1835.FFFF:1722,1833.FFFF:1702")
				if config.plugins.OscamSmartcard.internalReader0.value == 'D01':                                                                   
					line = line.replace("betatunnel                    = 1833.FFFF:1702", "betatunnel                    = 1834.FFFF:1722,1833.FFFF:1702")
				if config.plugins.OscamSmartcard.internalReader1.value == 'D01':                                                                   
					line = line.replace("betatunnel                    = 1833.FFFF:1702", "betatunnel                    = 1834.FFFF:1722,1833.FFFF:1702")
				if config.plugins.OscamSmartcard.externalReader0.value == 'D01':                                                                   
					line = line.replace("betatunnel                    = 1833.FFFF:1702", "betatunnel                    = 1834.FFFF:1722,1833.FFFF:1702")
				if config.plugins.OscamSmartcard.externalReader1.value == 'D01':                                                                   
					line = line.replace("betatunnel                    = 1833.FFFF:1702", "betatunnel                    = 1834.FFFF:1722,1833.FFFF:1702")
				if config.plugins.OscamSmartcard.internalReader0.value == 'D02':                                                                   
					line = line.replace("betatunnel                    = 1833.FFFF:1702", "betatunnel                    = 1834.FFFF:1722,1833.FFFF:1702")
				if config.plugins.OscamSmartcard.internalReader1.value == 'D02':                                                                   
					line = line.replace("betatunnel                    = 1833.FFFF:1702", "betatunnel                    = 1834.FFFF:1722,1833.FFFF:1702")
				if config.plugins.OscamSmartcard.externalReader0.value == 'D02':                                                                   
					line = line.replace("betatunnel                    = 1833.FFFF:1702", "betatunnel                    = 1834.FFFF:1722,1833.FFFF:1702")
				if config.plugins.OscamSmartcard.externalReader1.value == 'D02':                                                                   
					line = line.replace("betatunnel                    = 1833.FFFF:1702", "betatunnel                    = 1834.FFFF:1722,1833.FFFF:1702")
				o.write(line)
			o.close()
			system('rm -rf ' + self.oscamuserTMP)
			self.config_lines = []
		except:
			self.session.open(MessageBox, _("Error creating oscam.user!"), MessageBox.TYPE_ERROR)
			self.config_lines = []

	def saveoscamconf(self):
		try:
			self.appendconfFile(self.oscamsmartcarddata + "header.txt")
			if config.plugins.OscamSmartcard.emu.value =='yes_emu':
				self.appendconfFile(self.oscamsmartcarddata + "oscam.conf.emu.txt")
			else:
				self.appendconfFile(self.oscamsmartcarddata + "oscam.conf.txt")
			if config.plugins.OscamSmartcard.cccam.value =='yes_cccam_import':
				self.appendconfFile(self.oscamsmartcarddata + "cccamconfig.txt")
			self.appendconfFile(self.oscamsmartcarddata + "footer.txt")
			xFile = open(self.oscamconfTMP, "w")
			for xx in self.config_lines:
				xFile.writelines(xx)
			xFile.close()
			o = open(self.oscamconf,"w")
			for line in open(self.oscamconfTMP):
				line = line.replace("83", config.plugins.OscamSmartcard.WebifPort.value )
				o.write(line)
			o.close()
			system('rm -rf ' + self.oscamconfTMP)
			self.config_lines = []
		except:
			self.session.open(MessageBox, _("Error creating oscam.conf!"), MessageBox.TYPE_ERROR)
			self.config_lines = []

	def saveoscamservices(self):
		try:
			self.appendconfFile(self.oscamsmartcarddata + "header.txt")
			self.appendconfFile(self.oscamsmartcarddata + "oscam.services_" + config.plugins.OscamSmartcard.internalReader0.value + ".txt")
			self.appendconfFile(self.oscamsmartcarddata + "oscam.services_" + config.plugins.OscamSmartcard.internalReader1.value + ".txt")
			self.appendconfFile(self.oscamsmartcarddata + "oscam.services_" + config.plugins.OscamSmartcard.externalReader0.value + ".txt")
			self.appendconfFile(self.oscamsmartcarddata + "oscam.services_" + config.plugins.OscamSmartcard.externalReader1.value + ".txt")
			self.appendconfFile(self.oscamsmartcarddata + "oscam.services.txt")
			self.appendconfFile(self.oscamsmartcarddata + "footer.txt")
			xFile = open(self.oscamservicesTMP, "w")
			for xx in self.config_lines:
				xFile.writelines(xx)
			xFile.close()
			o = open(self.oscamservices,"w")
			for line in open(self.oscamservicesTMP):
				o.write(line)
			o.close()
			system('rm -rf ' + self.oscamservicesTMP)
			self.config_lines = []
		except:
			self.session.open(MessageBox, _("Error creating oscam.services!"), MessageBox.TYPE_ERROR)
			self.config_lines = []

	def saveoscamfiles(self):
			if config.plugins.OscamSmartcard.emu.value =='yes_emu':
				system('cp -f ' + self.oscamsmartcarddata + 'SoftCam.Key'  + ' ' + config.plugins.OscamSmartcard.ConfigPath.value)
			system('cp -f ' + self.oscamsmartcarddata + 'oscam.srvid'  + ' ' + config.plugins.OscamSmartcard.ConfigPath.value)
			system('cp -f ' + self.oscamsmartcarddata + 'oscam.srvid2'  + ' ' + config.plugins.OscamSmartcard.ConfigPath.value)
			system('cp -f ' + self.oscamsmartcarddata + 'oscam.provid' + ' ' + config.plugins.OscamSmartcard.ConfigPath.value)
			system('cp -f ' + self.oscamsmartcarddata + 'oscam.tiers'  + ' ' + config.plugins.OscamSmartcard.ConfigPath.value)

	def oscambinaryupdate(self):
		if self.newversion(arch) != _("Download not avaible"):
			system('killall -9 oscam_oscamsmartcard' + null)
			system('wget -q -O /tmp/oscam.tar.gz ' + self.downloadurl() +' ' +null)
			system('tar -xzf /tmp/oscam.tar.gz -C /tmp' + null)
			system('rm -f /usr/bin/oscam_oscamsmartcard' + null)
			system('mv /tmp/oscam /usr/bin/oscam_oscamsmartcard' + null)
			system('chmod 777 /usr/bin/oscam_oscamsmartcard')
			system('rm -f /tmp/oscam.tar.gz')

	def downloadurl(self):
		binary = 'oscam_oscamsmartcard'
		suffix = '.tar.gz'
		emu=''
		if getImageDistro() =='openatv':
			if config.plugins.OscamSmartcard.emu.value =='yes_emu':
				emu='_emu'
		if getImageDistro() =='openmips':
			if config.plugins.OscamSmartcard.emu.value =='yes_emu':
				emu='_emu'
		if arch == 'armv7l' or arch == 'mips' or arch == 'sh4' or arch == 'ppc' or arch == 'armv7ahf-vfp-neon':
			downloadurl = base64.b64decode(srv) + binary + '_' + arch + emu + suffix
		else:downloadurl = 'unknown_' + arch
		return downloadurl

	def newversion(self,arch):
		upgradeinfo = _("Download not avaible")
		if self.onlinecheck() == True:
			upgfile = '/tmp/upgrade.log'
			system('touch ' + upgfile)
			system('wget -O ' + upgfile + ' ' + base64.b64decode(info) + null )
			file = open(upgfile, "r")
			for line in file.readlines():
				line = line.strip().split(',')
				if line[0] == arch:
					upgradeinfo = line[1]
			file.close()
			os.remove(upgfile)
			return upgradeinfo
		return upgradeinfo

	def currentversion(self):
		if os.path.exists('/usr/bin/oscam_oscamsmartcard'):
			currentversion = _("Error") + ' : ' + _("file exists, but is not executable")
			f = popen('/usr/bin/oscam_oscamsmartcard -V')
			for line in f:
				if 'Version:' in line:
					line=line.strip().split()
					currentversion= line[1]
			f.close()
		else:
			currentversion=_("no oscam_oscamsmartcard found")
		return currentversion

	def checkallcams(self):
		liste=[]
		f = popen('opkg list-installed |grep -i softcam')
		for line in f:
			line=line.strip().split()
			if line[0] != ignore1 and line[0] != ignore2 and line[0] != ignore3 and line[0] !=ignore4  and line[0] !=ignore5 and line[0] !=ignore6 and line[0] !=ignore7 and line[0] !=ignore8:
				liste.append(line[0])
		f.close()
		return liste

	def readercheck(self):
		sci0 = 'not installed';
		sci1 = sci0
		usb0 = sci0
		usb1 = sci0
		anz = 0
		if os.path.exists('/dev/sci0'):
			sci0='installed'
			anz=anz+1
		if os.path.exists('/dev/sci1'):
			sci1='installed'
			anz=anz+1
		if os.path.exists('/dev/ttyUSB0'):
			usb0='installed'
			anz=anz+1
		if os.path.exists('/dev/ttyUSB1'):
			usb1='installed'
			anz=anz+1
		return sci0,sci1,usb0,usb1,anz

	def makebackup(self):
		dd = (time.strftime("%Y-%m-%d-%H-%M-%S"))
		x = glob.glob("/usr/keys/oscam.*")
		if len(x) >0:
			system('tar -czf /usr/keys/backup-oscamsmartcard-'+ dd +'.tar.gz /usr/keys/oscam.*')
			system('rm -f /usr/keys/oscam.*')
		y = glob.glob("/etc/tuxbox/config/oscam.*")
		if len(y) >0:
			system('tar -czf /etc/tuxbox/config/backup-oscamsmartcard-'+ dd +'.tar.gz /etc/tuxbox/config/oscam.*')
			system('rm -f /etc/tuxbox/config/oscam.*')

	def makeclean(self):
		a = self.checkallcams()
		if len(a) >0:
			i = 0
			while i < len(a):
				system('opkg remove --force-remove ' +a[i] + null)
				i = i + 1

	def savecamstart(self):
		try:
			if getImageDistro() =='openmips':
				system('/etc/init.d/softcam stop')
				system('/etc/init.d/cardserver stop')
				system('rm -f /etc/init.d/cardserver*')
				system('rm -f /etc/init.d/softcam*')
				system('touch /etc/init.d/softcam.None')
				system('touch /etc/init.d/cardserver.None')
				system('cp -f /tmp/data/softcam.OscamSmartcard /etc/init.d/softcam.OscamSmartcard')
				system('cp -f /tmp/data/cardserver.OscamSmartcard /etc/init.d/cardserver.OscamSmartcard')
				system('ln -sf /etc/init.d/softcam.OscamSmartcard /etc/init.d/softcam')
				system('ln -sf /etc/init.d/cardserver.None /etc/init.d/cardserver')
				system('chmod 777 /etc/init.d/softcam.*')
				system('chmod 777 /etc/init.d/cardserver.*')
				system('update-rc.d softcam  defaults ' + null)
				system('update-rc.d cardserver defaults ' + null)
			if getImageDistro() =='openatv':
				system('killall -9 oscam_oscamsmartcard' + null)
				system('rm -f /etc/oscamsmartcard.emu')
				system('cp -f /tmp/data/oscamsmartcard.emu /etc/oscamsmartcard.emu')
				config.softcam.actCam.setValue("OscamSmartcard")
				config.softcam.actCam2.setValue("None")
				config.softcam.save()
			self.config_lines = []
		except:
			self.session.open(MessageBox, _("Error creating oscam camstart files!"), MessageBox.TYPE_ERROR)
			self.config_lines = []

	def appendconfFile(self,appendFileName):
		skFile = open(appendFileName, "r")
		file_lines = skFile.readlines()
		skFile.close()
		for x in file_lines:
			self.config_lines.append(x)

	def systemclean(self, answer):
		if answer is True:
			self.makeclean()
			self.close()
		else:
			return

	def restartSTB(self, answer):
		if answer is True:
			system('reboot')
		else:
			return

	def onlinecheck(self):
		try:
			response=urllib2.urlopen(base64.b64decode(ipx),timeout=2)
			return True
		except urllib2.URLError as err: pass
		return False

	def exit(self):
		system('rm -rf /tmp/data')
		for x in self["config"].list:
			if len(x) > 1:
					x[1].cancel()
			else:
					pass
		self.close()

	def rmconfig(self):
		rmconfigset = self.session.openWithCallback(self.rmconfigset,MessageBox,_("Do you really want to remove all\noscam_smartcard configs, binary's and camstartfiles.\nNo backup !!"), MessageBox.TYPE_YESNO)
		rmconfigset.setTitle(_("remove current config"))

	def rmconfigset(self, answer):
		if answer is True:
			system('killall -9 oscam_oscamsmartcard ' + null)
			system('rm /usr/bin/oscam_oscamsmartcard' + null)
			system('rm -f /usr/keys/oscam.*' + null)
			system('rm -f /etc/tuxbox/config/oscam.*' + null)
			system('rm /etc/init.d/softcam /etc/init.d/softcam.None /etc/init.d/softcam.OscamSmartcard' + null)
			system('rm /etc/init.d/cardserver /etc/init.d/cardserver.None /etc/init.d/cardserver.OscamSmartcard' + null)
			system('rm -f /etc/oscamsmartcard.emu' + null)
			system('rm -rf /tmp/data' + null)
			system('rm -f /tmp/upgrade.log' + null)
			popen('rm -rf /tmp/.oscam' + null)
			self.valuedefaultsettings()
			self.close()
		else:
			return

	def valuedefaultsettings(self):
		config.plugins.OscamSmartcard.WebifPort.value = "83"
		config.plugins.OscamSmartcard.Camstart.value = "openmips"
		config.plugins.OscamSmartcard.systemclean.value = "cleanall_yes"
		config.plugins.OscamSmartcard.ConfigPath.value = "/etc/tuxbox/config/"
		config.plugins.OscamSmartcard.oscambinary.value = "no_binary_install"
		config.plugins.OscamSmartcard.cccam.value  = "no_cccam_import"
		config.plugins.OscamSmartcard.internalReader0.value = "none"
		config.plugins.OscamSmartcard.internalReader1.value = "none"
		config.plugins.OscamSmartcard.externalReader0.value = "none"
		config.plugins.OscamSmartcard.externalReader1.value = "none"
		config.plugins.OscamSmartcard.emu.value = "no_emu"
		config.plugins.OscamSmartcard.hasciplus.value = "no_ciplus"
		config.plugins.OscamSmartcard.save()        
		configfile.save()
		return

	def cccamcheck(self):
		cccsrv='';cccuser='';ccconfig='';cccport='12000'
		xc=0;yc=0;zc=0
		if os.path.exists('/etc/CCcam.cfg'):
			i=0;C='C';c='c';y=0; F='F';f='f';l='l';L='L'
			cclines= ('c:','C:')
			camd35lines = ('l:','L:')
			userline = ('f','F')
			datei = open("/etc/CCcam.cfg","r")
			for line in datei.readlines():
				line = line.strip().split('#')[0]
				line = line.split('{')[0]
				if line.startswith((c,C,l,L,F,f,'SERVER LISTEN PORT')):
					line=line.replace("\t"," ").replace(" :",":").replace(": ",":").replace(" :",":").replace(": ",":").replace("  "," ")
					if line.startswith(cclines) or line.startswith(camd35lines):
						if line.startswith(cclines) :protokoll='cccam'
						if line.startswith(camd35lines) :protokoll='cs357x'
						line = line.strip().split(":")
						line = line[1]
						line = line.split()
						if len(line)>3:
							i=i+1
							server = line[0]
							port = line[1];user = line[2];passwd = line[3]
							parts = server.split(".")
							end = str(parts[len(parts)-1])
							if "0" in end or "1" in end or "2" in end or "3" in end or "4" in end or "5" in end or "6" in end or "7" in end or "8" in end or "9" in end:
								servername ="IP"
							else:
								servername =parts[0]
							if protokoll=='cccam':
								xc +=1
								if servername == "IP":
									servername=server.replace(".","-")
								servername =  servername+"_"+str(xc)
								peer = '\n[reader]\nlabel\t\t\t = ' +servername + '\ndescription\t\t = ' + 'CCcam-Server: '+ server + ':' + port + '\nprotocol\t\t = ' + protokoll + '\n' + 'device\t\t\t = '+ server + ',' + port + '\n' +'user\t\t\t = ' + user + '\npassword\t\t = ' + passwd + '\ngroup\t\t\t = 1\ncccversion\t\t = 2.3.0\nccckeepalive\t\t = 1\nccchop\t\t\t = 9\naudisabled\t\t = 1\n'
							if protokoll=='cs357x':
								yc +=1
								if servername == "IP":
									servername=server.replace(".","-")
								servername = servername+"_"+str(yc)
								peer = '\n[reader]\nlabel\t\t\t = ' +servername + '\ndescription\t\t = ' + 'Camd35-Server: ' + server + ':' + port + '\nprotocol\t\t = ' + protokoll + '\n' + 'device\t\t\t = '+ server + ',' + port + '\n' +'user\t\t\t = ' + user + '\npassword\t\t = ' + passwd + '\ngroup\t\t\t = 1\naudisabled\t\t = 1\n'
							cccsrv += peer
					elif line.startswith(userline):
						zc=zc+1
						line = line.strip().split(":")
						line = line[1]
						line = line.split()
						if len(line)>1:
							cuser = line[0];cpass = line[1]
							user= '\n[account]\nuser\t\t\t = ' + line[0] + '\npwd\t\t\t = ' +line[1] + '\nuniq\t\t\t = 3\ngroup\t\t\t = 1\n'
							cccuser += user
					elif line.startswith('SERVER LISTEN PORT'):
						cccport = line.split(':')[1]
					ccconfig = '\n[cccam]\nport\t\t\t = '+cccport+'\nnodeid\t\t\t = \nversion\t\t\t = 2.3.0\nreshare\t\t\t = 2\nstealth\t\t\t = 1\n'
			datei.close()
			h = open(self.oscamsmartcarddata + "cccamconfig.txt","w")
			h.write(ccconfig)
			h.close()
			o = open(self.oscamsmartcarddata + "cccamserver.txt","w")
			o.write(cccsrv)
			o.close()
			p = open(self.oscamsmartcarddata + "cccamuser.txt","w")
			p.write(cccuser)
			p.close()
		return cccsrv,xc,cccuser,yc,ccconfig,zc,cccport

def main(session, **kwargs):
	session.open(OscamSmartcard,"/usr/lib/enigma2/python/Plugins/Extensions/OscamSmartcard/images/oscamsmartcard.png")
def Plugins(**kwargs):
	return PluginDescriptor(name="Oscam Smartcard v2.0", description=_("Configuration tool for OScam"), where = PluginDescriptor.WHERE_PLUGINMENU, icon="plugin.png", fnc=main)
