import org.kde.plasma.core 2.1 as PlasmaCore
import org.kde.kirigami 2.6 as Kirigami
import QtQuick 2.6
import QtQuick.Controls 2.6
import QtQuick.Layouts 1.12
import org.kde.plasma.components 3.0 as PC3


Rectangle{
    color:"transparent"
    Text{ 
        text:i18nd("dpkg-unlocker","System metapackage protection")
        font.family: "Quattrocento Sans Bold"
        font.pointSize: 16
    }

    GridLayout{
        id:generalLayout
        rows:2
        flow: GridLayout.TopToBottom
        rowSpacing:10
        Layout.fillWidth: true
        anchors.left:parent.left
        enabled:true
        Kirigami.InlineMessage {
            id: messageLabel
            visible:dpkgUnlockerBridge.showProtectionStatusMessage[0]
            text:getMessageText(dpkgUnlockerBridge.showProtectionStatusMessage[1])
            type:getMessageType(dpkgUnlockerBridge.showProtectionStatusMessage[2])
            Layout.minimumWidth:555
            Layout.maximumWidth:555
            Layout.topMargin: 40
        }

        RowLayout{
            id: optionsGrid
            Layout.topMargin: messageLabel.visible?0:50

            PC3.CheckBox {
                id:disableProtectionCb
                text:i18nd("dpkg-unlocker","Enable system metapackage protection")
                checked:dpkgUnlockerBridge.metaProtectionEnabled
                font.pointSize: 10
                focusPolicy: Qt.NoFocus
                Keys.onReturnPressed: disableProtectionCb.toggled()
                Keys.onEnterPressed: disableProtectionCb.toggled()
                onToggled:{
                   dpkgUnlockerBridge.getProtectionChange(checked)
                }

                Layout.alignment:Qt.AlignLeft
                Layout.bottomMargin:15
            }
        }
    }

    function getMessageText(code){

        var msg=""
        switch (code){
            case 6:
                msg=i18nd("dpkg-unlocker","System metapackage protection is enabled");
                break;
            case 7:
                msg=i18nd("dpkg-unlocker","System metapackage protection is disable");
                break;
            case 8:
                msg=i18nd("dpkg-unlocker","System metapackage protection change successfully")
                break;
            case -10:
                msg=i18nd("dpkg-unlocker","Error activating system metapackage protection");
                break;
            case -11:
                msg=i18nd("dpkg-unlocker","Error disabling system metapackage protection");
                break;
            default:
                break;
        }
        return msg;

    }

    function getMessageType(type){

        switch (type){
            case "Info":
                return Kirigami.MessageType.Information
            case "Success":
                return Kirigami.MessageType.Positive
            case "Error":
                return Kirigami.MessageType.Error
            case "Warning":
                return Kirigami.MessageType.Warning
        }

    } 

} 
