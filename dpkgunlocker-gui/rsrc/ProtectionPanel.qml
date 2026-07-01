import org.kde.plasma.core as PlasmaCore
import org.kde.kirigami as Kirigami
import QtQuick
import QtQuick.Controls
import QtQuick.Layouts
import org.kde.plasma.components as PC


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
        anchors.left:parent.left
        width:parent.width-10
        enabled:true
        Kirigami.InlineMessage {
            id: messageLabel
            visible:protectionStackBridge.showProtectionStatusMessage.show
            text:getMessageText(protectionStackBridge.showProtectionStatusMessage.msgCode)
            type:getMessageType(protectionStackBridge.showProtectionStatusMessage.type)
            Layout.minimumWidth:555
            Layout.fillWidth:true
            Layout.topMargin: 40
        }

        RowLayout{
            id: optionsGrid
            Layout.topMargin: messageLabel.visible?0:50

            PC.CheckBox {
                id:disableProtectionCb
                text:i18nd("dpkg-unlocker","Enable system metapackage protection")
                checked:protectionStackBridge.metaProtectionEnabled
                font.pointSize: 10
                focusPolicy: Qt.NoFocus
                Keys.onReturnPressed: disableProtectionCb.toggled()
                Keys.onEnterPressed: disableProtectionCb.toggled()
                onToggled:{
                   protectionStackBridge.getProtectionChange(checked)
                }

                Layout.alignment:Qt.AlignLeft
                Layout.bottomMargin:15
            }
        }
    }

    function getMessageText(code){

        switch (code){
            case 6:
                return i18nd("dpkg-unlocker","System metapackage protection is enabled")
            case 7:
                return i18nd("dpkg-unlocker","System metapackage protection is disable")
            case 8:
                return i18nd("dpkg-unlocker","System metapackage protection change successfully")
            case -10:
                return i18nd("dpkg-unlocker","Error activating system metapackage protection")
            case -11:
                return i18nd("dpkg-unlocker","Error disabling system metapackage protection")
            default:
                return ""
        }

    }

    function getMessageType(type){

        switch (type){
            case 0:
                return Kirigami.MessageType.Positive
            case 1:
                return Kirigami.MessageType.Error
            case 2:
                return Kirigami.MessageType.Warning
            case 3:
            default:
                return Kirigami.MessageType.Information
        }

    } 

} 
