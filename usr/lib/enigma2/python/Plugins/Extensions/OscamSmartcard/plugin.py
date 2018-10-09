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
from Components.Pixmap import Pixmap
#from skin import parseColor
from enigma import ePicLoad
import gettext, base64, os, time, glob, urllib2
from os import environ, listdir, remove, rename, system, popen
from Tools.Directories import fileExists, resolveFilename, SCOPE_LANGUAGE, SCOPE_PLUGINS
from boxbranding import *
from datetime import datetime

plugin='[OscamSmartcard] '
null =' >/dev/null 2>&1'

def architectures():
	hardwaretype = popen('uname -m').read().strip()
	hostname = popen('uname -n').read().strip()
	kernelversion = popen('uname -r').read().strip()
	ossystem = popen('uname -s').read().strip()
	return ossystem,kernelversion,hardwaretype,hostname

arch = architectures()[2]
#extrainfo=(architectures()[3] +' - ' + architectures()[0] + ' - ' + architectures()[1]).title()
extrainfo=(architectures()[3]  + ' - ' + architectures()[1])

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
config.plugins.OscamSmartcard.Camstart = ConfigSelection(default="openmips", choices = [
				("openmips", "Script SoftCamstart (openMips)"),
				("openatv", "Python SoftCamstart (openATV)")
				])
config.plugins.OscamSmartcard.systemclean = ConfigSelection(default = True, choices = [
				(True, ' ')
				])
config.plugins.OscamSmartcard.ConfigPath = ConfigSelection(default="/etc/tuxbox/config/", choices = [
				("/usr/keys/", "/usr/keys/ (openATV)"),
				("/etc/tuxbox/config/", "/etc/tuxbox/config/ (openMips)")
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
config.plugins.OscamSmartcard.emu  = ConfigSelection(default= False, choices = [
				(False, _("No")),
				(True, _("Yes"))
				])
config.plugins.OscamSmartcard.hasciplus  = ConfigSelection(default="no", choices = [
				("no", _("No")),
				("ciplusV13", _("CI+ V13")),
				("ciplusV14", _("CI+ V14"))
				])

cardlist = [("none", _("None"))]


class OscamSmartcard(ConfigListScreen, Screen):
	skin ="""<screen name="OscamSmartcard-Setup" position="center,center" size="1280,720" flags="wfNoBorder" backgroundColor="black">
  <eLabel name="bg" position="40,40" zPosition="-2" size="1200,640" backgroundColor="black" transparent="0" />
  <widget name="config" position="55,299" size="595,210" scrollbarMode="showOnDemand" transparent="1" backgroundColor="black" zPosition="1" />
  <widget name="Title" position="60,48" size="590,50" zPosition="1" font="Regular; 40" halign="left" backgroundColor="black" transparent="1" />
  <eLabel font="Regular; 20" zPosition="1" foregroundColor="black" halign="center" position="375,648" size="200,33" text="Exit" transparent="1" backgroundColor="red" />
  <eLabel font="Regular; 20" zPosition="1" foregroundColor="white" halign="center" position="60,648" size="200,33" text="Exit" transparent="1" backgroundColor="green" />
  <eLabel font="Regular; 20" zPosition="1" foregroundColor="black" halign="center" position="670,648" size="200,33" text="Exit" transparent="1" backgroundColor="yellow" />
  <eLabel font="Regular; 20" zPosition="1" foregroundColor="white" halign="center" position="965,648" size="200,33" text="Exit" transparent="1" backgroundColor="blue" />
  <eLabel position="670,645" zPosition="0" size="200,33" backgroundColor="yellow" />
  <eLabel position="60,645" zPosition="0" size="200,33" backgroundColor="green" />
  <eLabel position="375,645" zPosition="0" size="200,33" backgroundColor="red" />
  <eLabel position="965,645" zPosition="0" size="200,33" backgroundColor="blue" />
  <widget name="oscamsmartcardhelperimage" position="671,209" size="330,300" zPosition="3" backgroundColor="black" transparent="1" />
  <widget name="HELPTEXT" position="670,518" size="544,110" zPosition="1" font="Regular; 20" halign="left" backgroundColor="black" transparent="1" />
  <widget name="HEADER" position="60,114" size="590,180" zPosition="1" font="Regular; 20" halign="left" backgroundColor="black" transparent="1" />
  <widget name="INFOTXT" position="60,518" size="590,110" zPosition="1" font="Regular; 20" halign="left" backgroundColor="black" transparent="1" />
  <eLabel text="OscamSmartcard EOL" position="874,45" size="360,20" zPosition="1" font="Regular; 15" halign="right" backgroundColor="black" transparent="1" />
<ePixmap pixmap="/usr/lib/enigma2/python/Plugins/Extensions/OscamSmartcard/images/oscamsmartcard.png" position="958,75" size="275,250" alphatest="blend" zPosition="2" />
</screen>"""

	def __init__(self, session, args = None, picPath = None):
		self.config_lines = []
		Screen.__init__(self, session)
		self.session = session
		self.picPath = picPath
		self.Scale = AVSwitch().getFramebufferScale()
		self.PicLoad = ePicLoad()
		self["oscamsmartcardhelperimage"] = Pixmap()
		self["HELPTEXT"] = Label()
		self["HEADER"] = Label()
		self["Title"] = Label()
		self["Title"].setText("OscamSmartcard " + _("Setup"))
		self["INFOTXT"] = Label()
		self["INFOTXT"].setText(_(""))


		list = []
		self.headers = _("Oscamsmartcard wurde ersatzlos eingestellt.\n\nWendet euch an Oberschlaumeier Gigablue-CAM aus dem www.gigablue-support.org Forum.\n\
Das Plugin kann deinstalliert werden.\n\
Eure Oscam-Einstellungen bleiben erhalten.\nbyby UT") + "\n\n" + _("press color button or lame for exit")


		ConfigListScreen.__init__(self, list)
		self["HEADER"].setText(self.headers)
		self["INFOTXT"].setText("")
		self["actions"] = ActionMap(["OkCancelActions","DirectionActions", "InputActions", "ColorActions", "SetupActions"], {"red": self.exit,"yellow": self.exit,"blue": self.exit,"green": self.exit,"ok": self.exit,"cancel": self.exit}, -1)
		self.exit




	def selectionChanged(self):
		self["HELPTEXT"].setText(self["config"].getCurrent()[2])
		self["HEADER"].setText(self.headers)

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



	def exit(self):
		self.close()


def main(session, **kwargs):
	session.open(OscamSmartcard,"/usr/lib/enigma2/python/Plugins/Extensions/OscamSmartcard/images/oscamsmartcard.png")
def Plugins(**kwargs):
	return PluginDescriptor(name="Oscam Smartcard v2.5", description=_("Configuration tool for OScam"), where = PluginDescriptor.WHERE_PLUGINMENU, icon="plugin.png", fnc=main)
