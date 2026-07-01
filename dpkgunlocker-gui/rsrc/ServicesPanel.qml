import org.kde.plasma.core as PlasmaCore
import org.kde.kirigami as Kirigami
import QtQuick
import QtQuick.Controls
import QtQuick.Layouts


Rectangle{
    color:"transparent"
    Text{ 
        text:i18nd("dpkg-unlocker","Services Information")
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
        height:parent.height-25
        enabled:true
        Kirigami.InlineMessage {
            id: messageLabel
            visible:serviceStackBridge.showServiceStatusMesage.show
            text:getMessageText(serviceStackBridge.showServiceStatusMesage.msgCode)
            type:getMessageType(serviceStackBridge.showServiceStatusMesage.type)
            Layout.minimumWidth:555
            Layout.fillWidth:true
            Layout.topMargin: 40
        }

        RowLayout{
           id: optionsGrid
           Layout.topMargin: messageLabel.visible?0:50

           ServicesList{
                id:servicesList
                Layout.fillHeight:true
                Layout.fillWidth:true
                servicesModel:serviceStackBridge.servicesModel
            }
        }
    }

    function getMessageText(code){

        switch (code){
            case 0:
                return i18nd("dpkg-unlocker","All processes seem correct. Nothing to do")
            case 5:
                return i18nd("dpkg-unlocker","Unlocking process finished successfully")
            case 11:
                return i18nd("dpkg-unlocker","Some process are running. Wait a moment")
             case 12:
                return i18nd("dpkg-unlocker","Detected some blocked process")
            case -6:
                return i18nd("dpkg-unlocker","Error fixing the system")
            case -7:
                return i18nd("dpkg-unlocker","Error removing Apt lock file")
            case -8:
                return i18nd("dpkg-unlocker","Error removing Dpg lock file")
            case -9:
                return i18nd("dpkg-unlocker","Error removing Lliurex-Up lock file")
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
