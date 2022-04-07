import org.kde.plasma.core 2.1 as PlasmaCore
import QtQuick 2.15
import QtQuick.Controls 2.15
import QtQuick.Layouts 1.15
import QtQuick.Window 2.15
import QtQuick.Dialogs 1.3

ApplicationWindow {

    property bool closing: false
    id:mainWindow
    visible: true
    title: "Dpkg Unlocker"
    color:"#eff0f1"
    property int margin: 1
    width: mainLayout.implicitWidth + 2 * margin
    height: mainLayout.implicitHeight + 2 * margin
    minimumWidth: mainLayout.Layout.minimumWidth + 2 * margin
    minimumHeight: mainLayout.Layout.minimumHeight + 2 * margin
    maximumWidth: mainLayout.Layout.maximumWidth + 2 * margin
    maximumHeight: mainLayout.Layout.maximumHeight + 2 * margin
    Component.onCompleted: {
        x = Screen.width / 2 - width / 2
        y = Screen.height / 2 - height / 2
    }
    onClosing: {
        close.accepted=closing;
        dpkgUnlockerBridge.closeApplication()
        delay(100, function() {
            if (dpkgUnlockerBridge.closeGui){
                closing=true,
                timer.stop(),           
                mainWindow.close();
            }else{
                closing=false;
            }
        })
        
    }
    
    ColumnLayout {
        id: mainLayout
        anchors.fill: parent
        anchors.margins: margin
        Layout.minimumWidth:780
        Layout.maximumWidth:780
        Layout.minimumHeight:550
        Layout.maximumHeight:550

        RowLayout {
            id: bannerBox
            Layout.alignment:Qt.AlignTop
            Layout.minimumHeight:120
            Layout.maximumHeight:120

            Image{
                id:banner
                source: "/usr/lib/python3/dist-packages/dpkgunlockergui/rsrc/banner.png"
            }
        }

        StackLayout {
            id: stackLayout
            currentIndex:dpkgUnlockerBridge.currentStack
            implicitWidth: 780
            Layout.alignment:Qt.AlignHCenter
            Layout.leftMargin:0
            Layout.fillWidth:true
            Layout.fillHeight: true

            Loading{
                id:loading
            }

            ApplicationOptions{
                id:applicationOptions
            }

        }

    }

    Timer{
        id:timer
    }

    function delay(delayTime,cb){
        timer.interval=delayTime;
        timer.repeat=true;
        timer.triggered.connect(cb);
        timer.start()
    }


}

