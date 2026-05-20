import network
wlan = network.WLAN(network.STA_IF)
wlan.active(True)
wlan.connect('TU_RED', 'TU_PASSWORD')
import mip
mip.install("aioble")