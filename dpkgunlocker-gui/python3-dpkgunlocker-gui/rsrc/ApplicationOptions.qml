import QtQuick 2.15
import QtQuick.Controls 2.15
import QtQuick.Layouts 1.15
import QtQuick.Dialogs 1.3
import org.kde.plasma.components 3.0 as PC3

RowLayout{
    id: optionsGrid
    spacing:10

    Rectangle{
        width:220
        Layout.fillHeight:true
        border.color: palette.mid

        ColumnLayout{
            id: menuGrid
            anchors.fill:parent
            spacing:0

            MenuOptionBtn {
                id:servicesOption
                optionText:i18nd("dpkg-unlocker","Services")
                optionIcon:"actions/24/run-build.svg"
                onMenuOptionClicked:mainStackBridge.manageTransitions(0)
            }

            MenuOptionBtn {
                id:restoreOption
                optionText:i18nd("dpkg-unlocker","Restore services")
                optionIcon:"actions/24/tools.svg"
                enabled:restoreStackBridge.runningRestoreCommand || (!serviceStackBridge.areLiveProcess && !serviceStackBridge.isThereALock)
                onMenuOptionClicked:mainStackBridge.manageTransitions(1)
            }

            MenuOptionBtn {
                id:detailsOption
                optionText:i18nd("dpkg-unlocker","Details process")
                optionIcon:"apps/24/utilities-terminal.svg"
                visible:mainStackBridge.enableKonsole
                onMenuOptionClicked:mainStackBridge.manageTransitions(2)
            }

            MenuOptionBtn {
                id:protectionOption
                optionText:i18nd("dpkg-unlocker","Metapackage protection")
                optionIcon:"status/24/security-high.svg"
                visible:protectionStackBridge.showProtectionOption
                onMenuOptionClicked:mainStackBridge.manageTransitions(3)
            }
          

            MenuOptionBtn {
                id:helpOption
                optionText:i18nd("dpkg-unlocker","Help")
                optionIcon:"actions/24/help-contents.svg"
                onMenuOptionClicked:mainStackBridge.openHelp()
            }

            Item {
                Layout.fillHeight:true
            }
        }
    }
    ColumnLayout{
        id: layoutGrid
        Layout.fillWidth: true
        Layout.fillHeight: true
        Layout.leftMargin:5
        Layout.rightMargin:15
        spacing:10

        StackLayout {
            id: optionsLayout
            currentIndex:mainStackBridge.currentOptionsStack
            Layout.fillHeight:true
            Layout.fillWidth:true
            Layout.alignment:Qt.AlignHCenter

            ServicesPanel{
                id:servicesPanel
            }
            RestorePanel{
                id:restorePanel
            }
            KonsolePanel{
                id:konsolePanel
            }
            ProtectionPanel{
                id:protectionPanel
            }

        }

        RowLayout{
            id:feedbackRow
            spacing:10
            Layout.topMargin:5
            Layout.bottomMargin:15
            Layout.fillWidth:true

            Item{
                Layout.fillWidth:true
            }

            ColumnLayout{
                id:feedbackColumn
                spacing:5
                Layout.alignment:Qt.AlignHCenter

                Text{
                    id:feedBackText
                    text:getFeedBackText(mainStackBridge.feedBackCode)
                    visible:mainStackBridge.showProgressBar
                    font.pointSize: 10
                    horizontalAlignment:Text.AlignHCenter
                    Layout.alignment:Qt.AlignHCenter
                }
                Item{
                    id:feedBackBar
                    visible:mainStackBridge.showProgressBar
                    implicitWidth:200
                    implicitHeight:5
                    Layout.alignment:Qt.AlignHCenter

                    Rectangle{
                        anchors.fill:parent
                        color:"#E0E0E0"
                        clip:true

                        Rectangle{
                            id:bar
                            width:parent.width*0.2
                            height:parent.height
                            color:"#2196F3"
                            x:0
                        }    
                    }
                    Timer{
                        id:pbTimer
                        running:feedBackBar.visible
                        repeat:true
                        interval:60
                        onTriggered:{
                            bar.x+=4;
                            if (bar.x > feedBackBar.width){
                                bar.x=-bar.width
                            }
                        }
                    }
                }
            }

            Item{
                Layout.fillWidth:true
            }
       
            PC3.Button {
                id:unlockBtn
                visible:true
                focus:true
                display:AbstractButton.TextBesideIcon
                icon.name:"dialog-ok"
                text:getLabel(optionsLayout.currentIndex)
                enabled:getStatus(optionsLayout.currentIndex)
                Keys.onReturnPressed: unlockBtn.clicked()
                Keys.onEnterPressed: unlockBtn.clicked()
                onClicked:{
                    mainStackBridge.openDialog()
                }
            }
        }
    }

    UnlockDialog{
        id:unlockDialog
        dialogTitle:{
            switch(optionsLayout.currentIndex){
                case 0:
                    return "Dpkg-Unlocker"+" - "+i18nd("dpkg-unlocker","Services Information")
                case 1:
                    return "Dpkg-Unlocker"+" - "+i18nd("dpkg-unlocker","Restore services")
                case 3:
                    return "Dpkg-Unlocker"+" - "+i18nd("dpkg-unlocker","System metapackage protection")
                default:
                    return ""
            }
        }
        dialogMsg:{
            switch(optionsLayout.currentIndex){
                case 0:
                    i18nd("dpkg-unlocker","Do you want to run the unlock process?")
                    break
                case 1:
                    i18nd("dpkg-unlocker","Do you want to run the services restore process?")
                    break
                case 3:
                    if (!protectionStackBridge.metaProtectionEnabled){
                        i18nd("dpkg-unlocker","Do you want to disable system metapackage protection?\nDisabling this protection can cause certain applications to be uninstalled\nautomatically and cause system inconsistencies")
                    }else{
                        i18nd("dpkg-unlocker","Do you want to enable system metapackage protection?")
                    }
                    break
                default:
                    ""
                    break;
            }
        }
        dialogVisible:mainStackBridge.showDialog
        btnAcceptVisible:optionsLayout.currentIndex!==3?false:true
        btnDiscardText:optionsLayout.currentIndex!==3?i18nd("dpkg-unlocker","Apply"):i18nd("dpkg-unlocker","Discard")
        btnDiscardIcon:optionsLayout.currentIndex!==3?"dialog-ok":"delete"

        Connections{
            target:unlockDialog
            function onDialogApplyClicked(){
                if (optionsLayout.currentIndex==3){
                    protectionStackBridge.changeProteccionStatus()
                }
            }

            function onDiscardDialogClicked(){
                switch(optionsLayout.currentIndex){
                    case 0:
                        protectionOption.enabled=false
                        applyChanges()
                        serviceStackBridge.launchUnlockProcess()
                        break;
                   case 1:
                        protectionOption.enabled=false
                        applyChanges()
                        restoreStackBridge.launchRestoreProcess()
                        break;
                    case 3:
                         protectionStackBridge.discardChangeProtectionStatus()
                }
            }

            function onCancelDialogClicked(){
                if (optionsLayout.currentIndex==2){
                    if (mainStackBridge.showPendingChangesDialog){
                        mainStackBridge.cancelAction()
                    }else{
                        protectionStackBridge.discardChangeProtectionStatus()
                    }
                }else{
                    mainStackBridge.cancelAction()
                }
            }

        }
    }

    Timer{
        id:processTimer
        interval:100
        repeat:true
        onTriggered:{
            if (mainStackBridge.endProcess){
                protectionOption.enabled=true
                processTimer.stop()
            }else{
                if (mainStackBridge.endCurrentCommand){
                    mainStackBridge.getNewCommand()
                    var newCommand=mainStackBridge.currentCommand
                    konsolePanel.runCommand(newCommand)
                }  
            }
        }
    }

    function applyChanges(){
        processTimer.restart()
    }

    function getLabel(code){

        switch(code){
            case 0:
                return i18nd("dpkg-unlocker","Unlock")
            case 1:
                return i18nd("dpkg-unlocker","Restore")
            case 3:
                return i18nd("dpkg-unlocker","Apply")
            case 2:
                if (mainStackBridge.processLaunched=="Unlock"){
                    return i18nd("dpkg-unlocker","Unlock")
                }else{
                    return i18nd("dpkg-unlocker","Restore")
                }
            default:
                return i18nd("dpkg-unlocker","Unlock")
        }

    }

    function getStatus(code){

        switch(code){
            case 0:
                if (serviceStackBridge.runningUnlockCommand || restoreStackBridge.runningRestoreCommand){
                    return false
                }else{
                    return serviceStackBridge.isThereALock
                }
            case 1:
                if (serviceStackBridge.runningUnlockCommand || restoreStackBridge.runningRestoreCommand){
                    return false
                }else{
                    if ((!serviceStackBridge.areLiveProcess)&&(!serviceStackBridge.isThereALock)){
                        return true
                    }else{
                        return false
                    }
                }
            case 3:
                return protectionStackBridge.isProtectionChange
            default:
                return false
        }
    
    }
 
    function getFeedBackText(code){

        switch (code){
            case 1:
               return i18nd("dpkg-unlocker","Removing Lliurex-Up lock file...")
               break
            case 2:
                return i18nd("dpkg-unlocker","Removing Dpkg lock file...")
                break
            case 3:
                return i18nd("dpkg-unlocker","Removing Apt lock file...")
                break
             case 4:
                return i18nd("dpkg-unlocker","Fixing the system...")
                break
            case 9:
                return i18nd("dpkg-unlocker","Restoring the services...")
                break
            default:
                return ""
        }

    }
    
}

