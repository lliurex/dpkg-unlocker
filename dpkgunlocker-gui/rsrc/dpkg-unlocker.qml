import org.kde.plasma.core as PlasmaCore
import QtQuick
import QtQuick.Controls
import QtQuick.Layouts
import QtQuick.Window
import QtQuick.Dialogs

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
    Component.onCompleted: {
        x = Screen.width / 2 - width / 2
        y = Screen.height / 2 - height / 2
    }
    onClosing:(close)=> {
        close.accepted=closing;
        mainStackBridge.closeApplication()
        delay(100, function() {
            if (mainStackBridge.closeGui){
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
        Layout.minimumWidth:785
        Layout.preferredWidth:785
        Layout.minimumHeight:550

        RowLayout {
            id: bannerBox
            Layout.alignment:Qt.AlignTop
            
            Rectangle{
                color: "#000000"
                Layout.minimumWidth:mainLayout.width
                Layout.preferredWidth:mainLayout.width
                Layout.fillWidth:true
                Layout.minimumHeight:120
                Layout.maximumHeight:120
                Image{
                    id:banner
                    source: "/usr/lib/python3/dist-packages/dpkgunlockergui/rsrc/banner.png"
                    anchors.centerIn:parent
                }
            }
        }

        StackView {
            id: mainView
            property int currentView:mainStackBridge.currentStack
            Layout.minimumWidth:785
            Layout.preferredWidth: 785
            Layout.minimumHeight:430
            Layout.preferredHeight:430
            Layout.alignment:Qt.AlignHCenter|Qt.AlignVCenter
            Layout.leftMargin:0
            Layout.fillWidth:true
            Layout.fillHeight: true

            initialItem:loadingView

            onCurrentViewChanged:{
                mainView.clear()
                mainView.push(applicationOptionView)
            }
        }
         
        Component{
            id:loadingView
            Loading{
                id:loading
            }

         }

        Component{
            id:applicationOptionView
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

