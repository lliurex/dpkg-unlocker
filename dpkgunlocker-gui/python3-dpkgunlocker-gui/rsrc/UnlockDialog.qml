import QtQuick 2.15      
import QtQuick.Controls 2.15
import QtQuick.Layouts 1.15
import QtQuick.Dialogs 1.3
import org.kde.plasma.components 3.0 as PC3
import org.kde.plasma.core 2.0 as PlasmaCore


Dialog {
    id: customDialog

    property alias dialogTitle:customDialog.title
    property alias dialogVisible:customDialog.visible
    property alias dialogMsg: dialogText.text

    property alias btnAcceptVisible:dialogApplyBtn.visible
    property alias btnAcceptText:dialogApplyBtn.text

    property alias btnDiscardText:dialogDiscardBtn.text
    property alias btnDiscardIcon:dialogDiscardBtn.icon.name


    signal dialogApplyClicked
    signal discardDialogClicked
    signal cancelDialogClicked
    property bool xButton

    visible:dialogVisible
    title:dialogTitle
    modality:Qt.WindowModal

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
        implicitHeight: 150
        anchors.topMargin:20
        anchors.leftMargin:5
        anchors.rightMargin:10


        RowLayout {
            id: contentLayout
            anchors.top: parent.top
            anchors.left: parent.left
            anchors.right: parent.right
            anchors.margins: 0
            spacing: 15

            PlasmaCore.IconItem {
                id:dialogIcon
                source:"dialog-warning"
                width: 64
                height: 64

            }
            
            Text {
                id:dialogText
                text:dialogMsg
                font.pointSize: 10
                Layout.preferredWidth:parent.widht-30
                wrapMode: Text.WordWrap        
            }
        }
      
        PC3.Button {
            id:dialogApplyBtn
            display:AbstractButton.TextBesideIcon
            icon.name:"dialog-ok"
            text: i18nd("dpkg-unlocker","Apply")
            focus:true
            font.pointSize: 10
            anchors.bottom:parent.bottom
            anchors.right:dialogDiscardBtn.left
            anchors.rightMargin:10
            anchors.bottomMargin:5
            Keys.onReturnPressed: dialogApplyBtn.clicked()
            Keys.onEnterPressed: dialogApplyBtn.clicked()
            onClicked:{
                xButton=false
                dialogApplyClicked()
            }
        }

        PC3.Button {
            id:dialogDiscardBtn
            display:AbstractButton.TextBesideIcon
            icon.name:"delete"
            text: i18nd("dpkg-unlocker","Discard")
            focus:true
            font.pointSize: 10
            anchors.bottom:parent.bottom
            anchors.right:dialogCancelBtn.left
            anchors.rightMargin:10
            anchors.bottomMargin:5
            Keys.onReturnPressed: dialogDiscardBtn.clicked()
            Keys.onEnterPressed: dialogDiscardBtn.clicked()
            onClicked:{
                xButton:false
                discardDialogClicked()
            }
        }

        PC3.Button {
            id:dialogCancelBtn
            display:AbstractButton.TextBesideIcon
            icon.name:"dialog-cancel"
            text: i18nd("dpkg-unlocker","Cancel")
            focus:true
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
