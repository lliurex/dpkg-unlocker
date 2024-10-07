import QtQuick
import QtQuick.Controls
import QtQml.Models
import org.kde.plasma.components as Components



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

     } 

}

