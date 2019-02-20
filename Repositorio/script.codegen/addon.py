import xbmcaddon
import xbmcgui
import requests
import xbmc
import fcntl, socket, struct

addon       = xbmcaddon.Addon()
addonname   = addon.getAddonInfo('name')


def getHwAddr(ifname):
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    info = fcntl.ioctl(s.fileno(), 0x8927,  struct.pack('256s',ifname[:15]))
    return ':'.join(['%02x' % ord(char) for char in info[18:24]])


mac_address = getHwAddr('eth0')
url = "http://honey-kong-www.j0cpeqen0.at.d2c.io/iptv/generate_alias_code?mac_address={}".format(mac_address)
try:
    response = requests.get(url).json()
    xbmcgui.Dialog().ok(addonname, response['message'], '',"CODIGO: " + response['number'])
except:
    xbmcgui.Dialog().ok("Error", "Ocurrio un error al generar el codigo, intenta mas tarde.")
