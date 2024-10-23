import QtQuick
import QtQuick.Controls
import QtQuick.Layouts
import QtQuick.Dialogs
import org.kde.plasma.components as PC


Dialog {
    id: customDialog
    property alias dialogTitle:customDialog.title
    property alias dialogVisible:customDialog.visible
    property alias dialogMsg:dialogText.text
    signal dialogApplyClicked
    signal discardDialogClicked
    signal cancelDialogClicked
    property bool xButton

    visible:dialogVisible
    title:dialogTitle
    modal:true
    anchors.centerIn: Overlay.overlay

    background:Rectangle{
        color:"#ebeced"
        border.color:"#b8b9ba"
        border.width:1
        radius:5.0
    }


    onVisibleChanged:{
        if (!this.visible && xButton){
            if (mainStackBridge.showDialog){
                cancelDialogClicked()
            }
        }else{
            xButton=true
        }
    }

    contentItem: Rectangle {
        color: "#ebeced"
        implicitWidth: 550
        implicitHeight: 105
        anchors.topMargin:5
        anchors.leftMargin:5

        Image{
            id:dialogIcon
            source:"/usr/share/icons/breeze/status/64/dialog-warning.svg"

        }
        
        Text {
            id:dialogText
            text:dialogMsg
            font.family: "Quattrocento Sans Bold"
            font.pointSize: 10
            anchors.left:dialogIcon.right
            anchors.verticalCenter:dialogIcon.verticalCenter
            anchors.leftMargin:10
        
        }
      
        PC.Button {
            id:dialogApplyBtn
            display:AbstractButton.TextBesideIcon
            icon.name:"dialog-ok"
            text: i18nd("dpkg-unlocker","Apply")
            focus:true
            font.family: "Quattrocento Sans Bold"
            font.pointSize: 10
            anchors.bottom:parent.bottom
            anchors.right:{
                if (protectionStackBridge.showPendingChangesDialog){
                    dialogDiscardBtn.left
                }else{
                    dialogCancelBtn.left
                }
            }
            anchors.rightMargin:10
            anchors.bottomMargin:5
            Keys.onReturnPressed: dialogApplyBtn.clicked()
            Keys.onEnterPressed: dialogApplyBtn.clicked()
            onClicked:{
                xButton=false
                dialogApplyClicked()
            }
        }

        PC.Button {
            id:dialogDiscardBtn
            display:AbstractButton.TextBesideIcon
            icon.name:"delete"
            text: i18nd("dpkg-unlocker","Discard")
            focus:true
            font.family: "Quattrocento Sans Bold"
            font.pointSize: 10
            anchors.bottom:parent.bottom
            anchors.right:{
                if (protectionStackBridge.showPendingChangesDialog){
                    dialogCancelBtn.left
                }else{
                    dialogApplyBtn.left
                }
            }
            visible:protectionStackBridge.showPendingChangesDialog
            anchors.rightMargin:10
            anchors.bottomMargin:5
            Keys.onReturnPressed: dialogDiscardBtn.clicked()
            Keys.onEnterPressed: dialogDiscardBtn.clicked()
            onClicked:{
                xButton:false
                discardDialogClicked()
            }
        }

        PC.Button {
            id:dialogCancelBtn
            display:AbstractButton.TextBesideIcon
            icon.name:"dialog-cancel"
            text: i18nd("dpkg-unlocker","Cancel")
            focus:true
            font.family: "Quattrocento Sans Bold"
            font.pointSize: 10
            anchors.bottom:parent.bottom
            anchors.right:parent.right
            anchors.rightMargin:5
            anchors.bottomMargin:5
            Keys.onReturnPressed: dialogCancelBtn.clicked()
            Keys.onEnterPressed: dialogCancelBtn.clicked()
            onClicked:{
                xButton:false
                cancelDialogClicked()

            }
        }

    }
 }
