import QtQuick 2.15      
import QtQuick.Controls 2.15
import QtQuick.Layouts 1.15
import QtQuick.Dialogs 1.3
import org.kde.plasma.components 3.0 as PC3


Dialog {
    id: customDialog
    property alias dialogTitle:customDialog.title
    property alias dialogVisible:customDialog.visible
    property alias dialogMsg:dialogText.text
    signal dialogApplyClicked
    signal discardDialogClicked
    signal cancelDialogClicked

    visible:dialogVisible
    title:dialogTitle
    modality:Qt.WindowModal

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
      
        PC3.Button {
            id:dialogApplyBtn
            display:AbstractButton.TextBesideIcon
            icon.name:"dialog-ok"
            text: i18nd("dpkg-unlocker","Apply")
            focus:true
            font.family: "Quattrocento Sans Bold"
            font.pointSize: 10
            anchors.bottom:parent.bottom
            anchors.right:{
                if (dpkgUnlockerBridge.showPendingChangesDialog){
                    dialogDiscardBtn.left
                }else{
                    dialogCancelBtn.left
                }
            }
            anchors.rightMargin:10
            anchors.bottomMargin:5
            Keys.onReturnPressed: dialogApplyBtn.clicked()
            Keys.onEnterPressed: dialogApplyBtn.clicked()
            onClicked:dialogApplyClicked()
        }

        PC3.Button {
            id:dialogDiscardBtn
            display:AbstractButton.TextBesideIcon
            icon.name:"delete"
            text: i18nd("dpkg-unlocker","Discard")
            focus:true
            font.family: "Quattrocento Sans Bold"
            font.pointSize: 10
            anchors.bottom:parent.bottom
            anchors.right:{
                if (dpkgUnlockerBridge.showPendingChangesDialog){
                    dialogCancelBtn.left
                }else{
                    dialogApplyBtn.left
                }
            }
            visible:dpkgUnlockerBridge.showPendingChangesDialog
            anchors.rightMargin:10
            anchors.bottomMargin:5
            Keys.onReturnPressed: dialogDiscardBtn.clicked()
            Keys.onEnterPressed: dialogDiscardBtn.clicked()
            onClicked:discardDialogClicked()
        }

        PC3.Button {
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
            onClicked:cancelDialogClicked()
        }

    }
 }
