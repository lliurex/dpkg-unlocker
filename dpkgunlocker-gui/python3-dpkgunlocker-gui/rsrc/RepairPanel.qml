import org.kde.plasma.core 2.1 as PlasmaCore
import org.kde.kirigami 2.16 as Kirigami
import QtQuick 2.15
import QtQuick.Controls 2.15
import QtQuick.Layouts 1.15
import org.kde.plasma.components 3.0 as PC3


Rectangle{
    color:"transparent"
    Text{ 
        text:i18nd("dpkg-unlocker","Stabilize installation services")
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
            visible:dpkgUnlockerBridge.showRepairStatusMessage[0]
            text:getMessageText(dpkgUnlockerBridge.showRepairStatusMessage[1])
            type:getMessageType(dpkgUnlockerBridge.showRepairStatusMessage[2])
            Layout.minimumWidth:555
            Layout.fillWidth:true
            Layout.topMargin: 40
        }

        RowLayout{
            id: optionsGrid
            Layout.topMargin: messageLabel.visible?0:50

            Text{
                id:informationText
                text:i18nd("dpkg-unlocker","This option attemps to stabilize the services involves in the package installation, if the installation has been interrupted before the package configuration has finished .\nUse this option with caution.")
                horizontalAlignment:Text.AlignJustify
                wrapMode:Text.WordWrap
                font.family: "Quattrocento Sans Bold"
                font.pointSize: 10
                Layout.preferredWidth:555
                Layout.alignment:Qt.AlignLeft
                Layout.bottomMargin:15
            }
        }
    }

    function getMessageText(code){

        var msg=""
        switch (code){
            case 13:
                msg=i18nd("dpkg-unlocker","Stabilization of services has finished successfully");
                break;
            case -12:
                msg=i18nd("dpkg-unlocker","Stabilization of services has finished with errors");
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
