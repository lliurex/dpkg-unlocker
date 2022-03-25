import org.kde.plasma.core 2.1 as PlasmaCore
import org.kde.kirigami 2.16 as Kirigami
import QtQuick 2.15
import QtQuick.Controls 2.15
import QtQuick.Layouts 1.15


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
        Layout.fillWidth: true
        anchors.left:parent.left
        enabled:true
        Kirigami.InlineMessage {
            id: messageLabel
            visible:dpkgUnlockerBridge.showServiceStatusMesage[0]
            text:getMessageText(dpkgUnlockerBridge.showServiceStatusMesage[1])
            type:getMessageType(dpkgUnlockerBridge.showServiceStatusMesage[2])
            Layout.minimumWidth:570
            Layout.maximumWidth:570
            Layout.topMargin: 40
        }

        RowLayout{
            id: optionsGrid
            Layout.topMargin: messageLabel.visible?0:50

           ServicesList{
                id:servicesList
                servicesModel:dpkgUnlockerBridge.servicesModel
            }
        }
    }

    Timer{
        id:timer
    }

    function delay(delayTime,cb){
        timer.interval=delayTime;
        timer.repeat=true;
        timer.triggered.connect(cb);
        timer.start()
    }


    function getMessageText(code){

        var msg="";
        switch (code){
            case 0:
                msg=i18nd("dpkg-unlocker","All processes seem correct. Nothing to do");
                break;
            case 5:
                msg=i18nd("dpkg-unlocker","Unlocking process finished successfully");
                break;
            case 11:
                msg=i18nd("dpkg-unlocker","Some process are running. Wait a moment");
                break;
             case 12:
                msg=i18nd("dpkg-unlocker","Detected some blocked process");
                break;
            case -6:
                msg=i18nd("dpkg-unlocker","Error fixing the system");
                break;
            case -7:
                msg=i18nd("dpkg-unlocker","Error removing Apt lock file");
                break;
            case -8:
                msg=i18nd("dpkg-unlocker","Error removing Dpg lock file");
                break;
            case -9:
                msg=i18nd("dpkg-unlocker","Error removing Lliurex-Up lock file");
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
        }

    } 

    function applyChanges(){
        synchronizePopup.open()
        synchronizePopup.popupMessage=i18nd("dpkg-unlocker", "Apply changes. Wait a moment...")
        delay(500, function() {
            if (dpkgUnlockerBridge.closePopUp){
                synchronizePopup.close(),
                timer.stop()
            }
          })
    } 

} 