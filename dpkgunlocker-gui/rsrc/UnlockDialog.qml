import QtQuick
import QtQuick.Controls
import QtQuick.Layouts
import org.kde.plasma.components as PC
import org.kde.kirigami as Kirigami


Popup {
    id: customDialog
    property alias dialogVisible:customDialog.visible
    property alias dialogMsg: dialogText.text

    property alias btnAcceptVisible:dialogApplyBtn.visible
    property alias btnAcceptText:dialogApplyBtn.text

    property alias btnDiscardText:dialogDiscardBtn.text
    property alias btnDiscardIcon:dialogDiscardBtn.icon.name


    signal dialogApplyClicked
    signal discardDialogClicked
    signal cancelDialogClicked

    visible:dialogVisible
    modal:true
    closePolicy:Popup.NoAutoClose
    anchors.centerIn: Overlay.overlay

    background:Rectangle{
        color:"#ebeced"
        border.color:"#b8b9ba"
        border.width:1
        radius:5.0
    }

    contentItem: Item {
        implicitWidth: 550
        implicitHeight: 125

        RowLayout {
            id: contentRow
            anchors.top: parent.top
            anchors.left: parent.left
            anchors.right: parent.right
            spacing: 15

            Kirigami.Icon {
                id:dialogIcon
                source:"dialog-warning"
                Layout.preferredWidth: 64
                Layout.preferredHeight: 64
            }
            
            Text {
                id:dialogText
                text:dialogMsg
                font.pointSize: 10
                Layout.fillWidth: true
                wrapMode: Text.WordWrap
                verticalAlignment: Text.AlignVCenter
                color: "#31363b"
            
            }
        }

        RowLayout {
            anchors.bottom: parent.bottom
            anchors.right: parent.right
            anchors.margins: 15
            spacing: 10
      
            PC.Button {
                id:dialogApplyBtn
                display:AbstractButton.TextBesideIcon
                icon.name:"dialog-ok"
                text: i18nd("dpkg-unlocker","Apply")
                focus:true
                font.pointSize: 10
                Keys.onReturnPressed: dialogApplyBtn.clicked()
                Keys.onEnterPressed: dialogApplyBtn.clicked()
                onClicked:{
                    dialogApplyClicked()
                }
            }

            PC.Button {
                id:dialogDiscardBtn
                display:AbstractButton.TextBesideIcon
                focus:true
                visible:true
                font.pointSize: 10
                Keys.onReturnPressed: dialogDiscardBtn.clicked()
                Keys.onEnterPressed: dialogDiscardBtn.clicked()
                onClicked:{
                    discardDialogClicked()
                }
            }

            PC.Button {
                id:dialogCancelBtn
                display:AbstractButton.TextBesideIcon
                icon.name:"dialog-cancel"
                text: i18nd("dpkg-unlocker","Cancel")
                focus:true
                font.pointSize: 10
                Keys.onReturnPressed: dialogCancelBtn.clicked()
                Keys.onEnterPressed: dialogCancelBtn.clicked()
                onClicked:{
                    cancelDialogClicked()
                }
            }
        }

    }
 }
