import QtQuick
import QtQuick.Controls
import QtQml.Models
import QtQuick.Layouts
import org.kde.plasma.components as PC
import org.kde.kirigami as Kirigami


PC.ItemDelegate {
    id: listServiceItem

    property string serviceId
    property int statusCode
    hoverEnabled: false
    height: 85

    contentItem: RowLayout {
        id: mainRowLayout
        spacing: 10
        
        Image {
            id:serviceLockedIcon
            source: statusCode===0?"padlock_open":"padlock_closed"
            sourceSize.width: 64
            sourceSize.height: 64
            Layout.alignment: Qt.AlignVCenter
            cache: false
            mipmap: true
            smooth: true
            fillMode: Image.PreserveAspectFit

        }

        Column{
            id: serviceText
            Layout.fillWidth:true
            Layout.alignment: Qt.AlignVCenter
            spacing:5

            Text{
                id:serviceName
                text:serviceId
                font.pointSize: 11
            }
            Text{
                id:serviceDescription
                text:getText(statusCode)
                font.pointSize: 10
            }
        }

        Kirigami.Icon {
            id:serviceErrorIcon
            source:statusCode===2?"data-error":"data-success"
            Layout.preferredWidth: 32
            Layout.preferredHeight: 32
            Layout.alignment: Qt.AlignVCenter
        }
    }

    function getText(statusCode){

        switch(statusCode){
            case 0:
               return i18nd("dpkg-unlocker","Unlocked")
            case 1:
               return i18nd("dpkg-unlocker","Locked: Currently executing")
            case 2:
               return i18nd("dpkg-unlocker","Locked: Not process found")
            case 3:
               return i18nd("dpkg-unlocker","Locked: Apt currently executing")
            case 4:
               return i18nd("dpkg-unlocker","Locked: Apt daemon currently executing")
            default:
               return " "
        }
    }

}
