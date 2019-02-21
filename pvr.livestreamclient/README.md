# IPTV Simple PVR
IPTV LiveStream TV and Radio PVR client addon for [Kodi] (http://kodi.tv)

## Build instructions

### Linux

1. `git clone git@159.89.43.103:tvstream/livestream_client.git pvr.livestreamclient`
2. `cd pvr.livestreamclient && mkdir build && cd build`
3. `cmake -DADDONS_TO_BUILD=pvr.livestreamclient -DADDON_SRC_PREFIX=../.. -DCMAKE_BUILD_TYPE=Debug -DCMAKE_INSTALL_PREFIX=../../kodi/addons -DPACKAGE_ZIP=1 ../../kodi/project/cmake/addons`
4. `make`
