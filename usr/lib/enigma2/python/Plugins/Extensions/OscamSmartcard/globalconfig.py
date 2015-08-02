#
message01=""
message02="install or update to the latest version"
message03="Config path set automatically to"
message04="Oscam binary install/update"
message05="OscamSmartcard is now running"
message06="online avaible"
message07="Oscam type set automatically to"
message08="Remove all first.\notherwise Oscamsmartcard will not start\nPress GREEN to remove all"
message09="Cardreader found automatically"
message10="Camstart set automatically to"
message11="file exists, but is not executable"
message12="Uninstall all Softcams ?"
message13="Warning"
message14="unused Softams,Config or others found"
message15="Error"
message16="All Softcams will be deinstalled\nAre you sure ?"
message17="found installed Softcams to be remove" 
message18="no other softcams found"
message19="no oscam_oscamsmartcard found"
message20="Ok Done\nOscamsmartcard is now running"
message21="remove"
message22="Oscam is not running\nunknown OS"
message23="press color button or lame for exit"
message24="Unsupportet CPU"
message25="found"
message26="-------------------------------------- Auto Config----------------------------------------"
message27="make your selection and press GREEN"
message28="All config files are backed up automatically"
message29="Download not avaible"
message30=""

infourl = 'http://www.gigablue-support.org/download/oscamsmartcard/version.info'
server = 'http://www.gigablue-support.org/download/oscamsmartcard/'
#server = 'https://github.com/gigablue-support-org/oscamsmartcard/blob/master/bin/'
#infourl = 'https://raw.githubusercontent.com/gigablue-support-org/oscamsmartcard/master/bin/version.info'



#ignore plugin's by makeclean
ignore1='enigma2-plugin-softcams-oscamsmartcard'
ignore2='enigma2-plugin-pli-softcamsetup'
ignore3='enigma2-plugin-softcams-oscamstatus'

#system
plugin='[OscamSmartcard] '
null =' >/dev/null 2>&1'
opkginstallcheck= 'opkg list-installed |grep -i softcam'
deinstall ='opkg remove --force-remove '
