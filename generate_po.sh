#!/bin/bash

xgettext --join-existing -L python ./dpkgunlocker-gui/dpkg-unlocker-gui -o ./translations/dpkg-unlocker/dpkg-unlocker.pot
xgettext --join-existing -kde -ki18nd:2 ./dpkgunlocker-gui/rsrc/ApplicationOptions.qml -o ./translations/dpkg-unlocker/dpkg-unlocker.pot
xgettext --join-existing -kde -ki18nd:2 ./dpkgunlocker-gui/rsrc/ServicesPanel.qml -o ./translations/dpkg-unlocker/dpkg-unlocker.pot
xgettext --join-existing -kde -ki18nd:2 ./dpkgunlocker-gui/rsrc/KonsolePanel.qml -o ./translations/dpkg-unlocker/dpkg-unlocker.pot
xgettext --join-existing -kde -ki18nd:2 ./dpkgunlocker-gui/rsrc/ProtectionPanel.qml -o ./translations/dpkg-unlocker/dpkg-unlocker.pot
xgettext --join-existing -kde -ki18nd:2 ./dpkgunlocker-gui/rsrc/ListDelegateServiceItem.qml -o ./translations/dpkg-unlocker/dpkg-unlocker.pot
xgettext --join-existing -kde -ki18nd:2 ./dpkgunlocker-gui/rsrc/RestorePanel.qml -o ./translations/dpkg-unlocker/dpkg-unlocker.pot
xgettext --join-existing -kde -ki18nd:2 ./dpkgunlocker-gui/rsrc/Loading.qml -o ./translations/dpkg-unlocker/dpkg-unlocker.pot
xgettext --join-existing -kde -ki18nd:2 ./dpkgunlocker-gui/rsrc/UnlockDialog.qml -o ./translations/dpkg-unlocker/dpkg-unlocker.pot
