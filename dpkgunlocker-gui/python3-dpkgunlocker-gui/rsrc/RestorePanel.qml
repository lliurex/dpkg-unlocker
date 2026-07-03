import QtQuick 2.15
import QtQuick.Controls 2.15
import QtQuick.Layouts 1.15
import org.kde.plasma.core 2.1 as PlasmaCore
import org.kde.kirigami 2.16 as Kirigami


Rectangle{
    color:"transparent"

    ColumnLayout{
        id: mainContent
        anchors.fill:parent
        anchors.rightMargin:5
        anchors.bottomMargin:10
        spacing:10

        Text{ 
            text:i18nd("dpkg-unlocker","Restore installation services")
            font.family: "Quattrocento Sans Bold"
            font.pointSize: 16
        }

        Kirigami.InlineMessage {
            id: messageLabel
            visible:restoreStackBridge.showRestoreStatusMessage.show
            text:getMessageText(restoreStackBridge.showRestoreStatusMessage.msgCode)
            type:getMessageType(restoreStackBridge.showRestoreStatusMessage.type)
            Layout.fillWidth:true
        }

        Text{
            id:informationText
            text:i18nd("dpkg-unlocker","This option attemps to restore the services involves in the package installation, if the installation has been interrupted before the package configuration has finished .\nUse this option with caution.")
            horizontalAlignment:Text.AlignJustify
            wrapMode:Text.WordWrap
            font.pointSize: 10
            Layout.fillWidth:true
            Layout.alignment:Qt.AlignLeft
        }

        Item{
            Layout.fillHeight:true
        }
    }

    function getMessageText(code){

        switch (code){
            case 10:
                return i18nd("dpkg-unlocker","Restoration of services has finished successfully")
            case -12:
                return i18nd("dpkg-unlocker","Restoration of services has finished with errors")
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
