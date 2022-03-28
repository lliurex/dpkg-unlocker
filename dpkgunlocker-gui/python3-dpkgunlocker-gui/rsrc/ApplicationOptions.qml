import QtQuick 2.15
import QtQuick.Controls 2.15
import QtQuick.Layouts 1.15
import QtQuick.Dialogs 1.3

GridLayout{
    id: optionsGrid
    columns: 2
    flow: GridLayout.LeftToRight
    columnSpacing:10

    Rectangle{
        width:180
        height:430
        border.color: "#d3d3d3"

        GridLayout{
            id: menuGrid
            rows:3 
            flow: GridLayout.TopToBottom
            rowSpacing:0

            MenuOptionBtn {
                id:infoPanel
                optionText:i18nd("dpkg-unlocker","Information")
                optionIcon:"/usr/share/icons/breeze/actions/16/go-home.svg"
                Connections{
                    function onMenuOptionClicked(){
                        optionsLayout.currentIndex=0;
                    }
                }
            }

            MenuOptionBtn {
                id:detailsItem
                optionText:i18nd("dpkg-unlocker","Unlock process")
                optionIcon:"/usr/share/icons/breeze/apps/16/utilities-terminal.svg"
                enabled:false
                Connections{
                    function onMenuOptionClicked(){
                        optionsLayout.currentIndex=1;
                    }
                }
            }

            MenuOptionBtn {
                id:helpItem
                optionText:i18nd("dpkg-unlocker","Help")
                optionIcon:"/usr/share/icons/breeze/actions/16/help-contents.svg"
                Connections{
                    function onMenuOptionClicked(){
                        dpkgUnlockerBridge.openHelp();
                    }
                }
            }
        }
    }
    GridLayout{
        id: layoutGrid
        rows:2 
        flow: GridLayout.TopToBottom
        rowSpacing:0

        StackLayout {
            id: optionsLayout
            currentIndex:dpkgUnlockerBridge.currentOptionsStack
            implicitHeight: 300
            Layout.alignment:Qt.AlignHCenter
            InformationPanel{
                id:informationPanel
            }
            KonsolePanel{
                id:konsolePanel
            }
        }

        RowLayout{
            id:feedbackRow
            spacing:10
            Layout.bottomMargin:15
            Layout.fillWidth:true

            ColumnLayout{
                id:feedbackColumn
                Layout.fillWidth:true
                spacing:5
                Text{
                    id:feedBackText
                    text:getFeedBackText(dpkgUnlockerBridge.feedBackCode)
                    visible:false
                    font.family: "Quattrocento Sans Bold"
                    font.pointSize: 10
                    Layout.alignment:Qt.AlignHCenter
                }
                ProgressBar{
                    id:feedBackBar
                    indeterminate:true
                    visible:false
                    Layout.fillWidth:true
                }
            }
    
            Button {
                id:unlockBtn
                visible:true
                focus:true
                display:AbstractButton.TextBesideIcon
                icon.name:"dialog-ok.svg"
                text:i18nd("dpkg-unlocker","Unlock")
                Layout.preferredHeight:40
                Layout.rightMargin:10
                enabled:dpkgUnlockerBridge.isThereALock
                Keys.onReturnPressed: unlockBtn.clicked()
                Keys.onEnterPressed: unlockBtn.clicked()
                onClicked:{
                    unlockDialog.open()
                }
            }
        }
    }
    UnlockDialog{
        id:unlockDialog
        dialogTitle:"Dpkg-Unlocker"+" - "+i18nd("dpkg-unlocker","Services Information")
        dialogMsg:i18nd("dpkg-unlocker","Do you want to run the unlock process?")
        Connections{
            target:unlockDialog
            function onDialogApplyClicked(){
                unlockBtn.enabled=false
                feedBackText.visible=true
                feedBackBar.visible=true
                detailsItem.enabled=true
                applyChanges()
                dpkgUnlockerBridge.launchUnlockProcess()
                unlockDialog.close()
                
            }
            function onDiscardDialogClicked(){
                unlockDialog.close()
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
   
    function applyChanges(){
        delay(100, function() {
            if (dpkgUnlockerBridge.endProcess){
                timer.stop()
                feedBackText.visible=false
                feedBackBar.visible=false
                
            }else{
                if (dpkgUnlockerBridge.endCurrentCommand){
                    dpkgUnlockerBridge.getNewCommand()
                    var newCommand=dpkgUnlockerBridge.currentCommand
                    konsolePanel.runCommand(newCommand)
                }
            }
          })
    } 
 
    function getFeedBackText(code){

        var msg="";
        switch (code){
            case 1:
                msg=i18nd("dpkg-unlocker","Removing Lliurex-Up lock file...");
                break;
            case 2:
                msg=i18nd("dpkg-unlocker","Removing Dpkg lock file...");
                break;
            case 3:
                msg=i18nd("dpkg-unlocker","Removing Apt lock file...");
                break;
             case 4:
                msg=i18nd("dpkg-unlocker","Fixing the system...");
                break;
           
            default:
                break;
        }
        return msg;

    }

    
}

