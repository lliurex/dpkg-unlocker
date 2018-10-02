#!/bin/bash

xgettext --join-existing ./dpkgunlocker-gui/python3-dpkgunlocker-gui/Core.py -o ./translations/dpkg-unlocker.pot
xgettext --join-existing ./dpkgunlocker-gui/python3-dpkgunlocker-gui/MainWindow.py -o ./translations/dpkg-unlocker.pot
xgettext --join-existing ./dpkgunlocker-gui/python3-dpkgunlocker-gui/ProcessBox.py -o ./translations/dpkg-unlocker.pot
xgettext --join-existing ./dpkgunlocker-gui/python3-dpkgunlocker-gui/rsrc/dpkgunlocker.ui -o ./translations/dpkg-unlocker.pot