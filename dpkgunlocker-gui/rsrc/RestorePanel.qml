import org.kde.plasma.core as PlasmaCore
import org.kde.kirigami as Kirigami
import QtQuick
import QtQuick.Controls
import QtQuick.Layouts

Rectangle{
    color:"transparent"
    Text{ 
        text:i18nd("dpkg-unlocker","Restore installation services")
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
            visible:restoreStackBridge.showRestoreStatusMessage[0]
            text:getMessageText(restoreStackBridge.showRestoreStatusMessage[1])
            type:getMessageType(restoreStackBridge.showRestoreStatusMessage[2])
            Layout.minimumWidth:555
            Layout.fillWidth:true
            Layout.topMargin: 40
        }

        RowLayout{
            id: optionsGrid
            Layout.topMargin: messageLabel.visible?0:50
            Layout.fillWidth:true
            
            Text{
                id:informationText
                text:i18nd("dpkg-unlocker","This option attemps to restore the services involves in the package installation, if the installation has been interrupted before the package configuration has finished .\nUse this option with caution.")
                horizontalAlignment:Text.AlignJustify
                wrapMode:Text.WordWrap
                font.family: "Quattrocento Sans Bold"
                font.pointSize: 10
                Layout.preferredWidth:555
                Layout.fillWidth:true
                Layout.alignment:Qt.AlignLeft
                Layout.rightMargin:5
                Layout.bottomMargin:15
            }
        }
    }

    function getMessageText(code){

        var msg=""
        switch (code){
            case 10:
                msg=i18nd("dpkg-unlocker","Restoration of services has finished successfully");
                break;
            case -12:
                msg=i18nd("dpkg-unlocker","Restoration of services has finished with errors");
                break;
            default:
                break;
        }
        return msg;

    }

    function getMessageType(type){

        switch (type){
            case "Success":
                return Kirigami.MessageType.Positive
            case "Error":
                return Kirigami.MessageType.Error
          }

    } 

} 
