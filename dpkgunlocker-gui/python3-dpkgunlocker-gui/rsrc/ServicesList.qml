import QtQuick 2.6
import QtQuick.Controls 2.6
import QtQuick.Layouts 1.12
import QtQml.Models 2.8
import org.kde.plasma.components 2.0 as Components
import org.kde.kirigami 2.12 as Kirigami



Rectangle {
    property alias servicesModel:listService.model

    id:servicesTable
    visible: true
    width: 555; height: 250
    color:"white"
    border.color: "#d3d3d3"

    ListModel{
        id: servicesModel
    }    
    ListView{
        id: listService
        anchors.fill:parent
        height: parent.height
        model:servicesModel
        currentIndex:-1
        focus: true
        delegate: ListDelegateServiceItem{
            width:servicesTable.width
            serviceId:model.serviceId
            statusCode:model.statusCode
        }
        Kirigami.PlaceholderMessage { 
            id: loadingHint
            anchors.centerIn: parent
            width: parent.width - (units.largeSpacing * 4)
            visible:listService.count>0?false:true 
            text: i18nd("dpkg-unlocker","Loading. Wait a moment...")
        }

     } 

}

