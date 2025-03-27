import QtQuick
import QtQuick.Controls
import QtQml.Models
import org.kde.plasma.components as Components


//Components.ListItem{
Rectangle{ 
 id: listServiceItem
    property string serviceId
    property int statusCode
    enabled:true
    color:"transparent"
    height:85

    Item{
        id: menuItem
        height:visible?70:0
        width:parent.width-serviceLockedIcon.width-serviceErrorIcon.width
        Image {
            id:serviceLockedIcon
            source:{
                if (statusCode==0){
                    "/usr/lib/python3/dist-packages/dpkgunlockergui/rsrc/padlock_open.svg"
                }else{
                    "/usr/lib/python3/dist-packages/dpkgunlockergui/rsrc/padlock_closed.svg"
                }

            }
            anchors.left:parent.left
            anchors.verticalCenter:parent.verticalCenter

        }

        Column{
            id: serviceText
            width:parent.width-serviceErrorIcon.width
            anchors.left:serviceLockedIcon.right
            anchors.leftMargin:5
            anchors.verticalCenter:parent.verticalCenter
            spacing:5

            Text{
                id:serviceName
                text:serviceId
                font.family: "Quattrocento Sans Bold"
                font.pointSize: 11
            }
            Text{
                id:serviceDescription
                text:getText(statusCode)
                font.family: "Quattrocento Sans Bold"
                font.pointSize: 10
            }
        }
        Image {
            id:serviceErrorIcon
            source:{
                if (statusCode==2){
                    "/usr/share/icons/breeze/status/24/data-error.svg"
                }else{
                    "/usr/share/icons/breeze/status/24/data-success.svg"
                }

            }
            anchors.left:serviceText.right
            anchors.rightMargin:5
            anchors.verticalCenter:parent.verticalCenter

        }


    }

    function getText(statusCode){

        var msg=""
        switch(statusCode){
            case 0:
                msg=i18nd("dpkg-unlocker","Unlocked")
                break;
            case 1:
                msg=i18nd("dpkg-unlocker","Locked: Currently executing")
                break;
            case 2:
                msg=i18nd("dpkg-unlocker","Locked: Not process found")
                break;
            case 3:
                msg=i18nd("dpkg-unlocker","Locked: Apt currently executing")
                break;
            case 4:
                msg=i18nd("dpkg-unlocker","Locked: Apt daemon currently executing")
                break;
            default:
                break;
        }
        return msg
    }

}
