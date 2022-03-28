import org.kde.plasma.core 2.1 as PlasmaCore
import org.kde.kirigami 2.16 as Kirigami
import QtQuick 2.15
import QtQuick.Controls 2.15
import QtQuick.Layouts 1.15
import QMLTermWidget 1.0


Rectangle{
    color:"transparent"
    Text{ 
        text:i18nd("dpkg-unlocker","Unlock process details")
        font.family: "Quattrocento Sans Bold"
        font.pointSize: 16
    }

    RowLayout{
        id:terminalLayout
        Layout.fillWidth: true
        anchors.verticalCenter:parent.verticalCenter

        Rectangle {
            width: 570
            height: 300

            QMLTermWidget {
                id: terminal
                anchors.fill: parent
                font.family: "Monospace"
                font.pointSize: 9
                colorScheme: "cool-retro-term"
                session: QMLTermSession{
                    id: mainsession
                    initialWorkingDirectory: "$HOME"
                }
                Component.onCompleted: {
                    mainsession.startShellProgram();
                    mainsession.sendText('setterm -cursor off;stty -echo;PS1="";clear\n');
                }

            }

            QMLTermScrollbar {
                terminal: terminal
                width: 20
                Rectangle {
                    opacity: 0.4
                    anchors.margins: 5
                    radius: width * 0.5
                    anchors.fill: parent
                }
            }
        
        }
    }
    
    function runCommand(command){
        mainsession.sendText(command)

    } 

} 
