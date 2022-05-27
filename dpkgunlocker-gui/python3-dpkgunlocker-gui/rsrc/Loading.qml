import QtQuick 2.6
import QtQuick.Controls 2.6
import QtQuick.Layouts 1.12

Rectangle{
    visible: true

    GridLayout{
        id: loadGrid
        rows: 4
        flow: GridLayout.TopToBottom
        anchors.centerIn:parent

        RowLayout{
            Layout.fillWidth: true
            Layout.alignment:Qt.AlignHCenter

            Rectangle{
                color:"transparent"
                width:30
                height:30
                
                AnimatedImage{
                    source: "/usr/lib/python3/dist-packages/dpkgunlockergui/rsrc/loading.gif"
                    transform: Scale {xScale:0.15;yScale:0.15}
                }
            }
        }

        RowLayout{
            Layout.fillWidth: true
            Layout.alignment:Qt.AlignHCenter

            Text{
                id:loadtext
                text:i18nd("lliurex-access-control", "Loading. Wait a moment...")
                font.family: "Quattrocento Sans Bold"
                font.pointSize: 10
                Layout.alignment:Qt.AlignHCenter
            }
        }
    }
}
