import QtQuick 2.15
import QtQuick.Controls 2.15
import QtQuick.Layouts 1.15
import QtQuick.Dialogs 1.3
//import org.kde.plasma.components 3.0 as PC3

GridLayout{
    id: optionsGrid
    columns: 2
    flow: GridLayout.LeftToRight
    columnSpacing:10

    Rectangle{
        width:200
        Layout.minimumHeight:430
        Layout.preferredHeight:430
        Layout.fillHeight:true
        border.color: "#d3d3d3"

        GridLayout{
            id: menuGrid
            rows:5 
            flow: GridLayout.TopToBottom
            rowSpacing:0

            MenuOptionBtn {
                id:servicesOption
                //optionText:i18nd("dpkg-unlocker","Services")
                optionText:"Services"
                optionIcon:"/usr/share/icons/breeze/actions/22/run-build.svg"
                Connections{
                    function onMenuOptionClicked(){
                        mainStackBridge.manageTransitions(0)
                    }
                }
            }

            MenuOptionBtn {
                id:restoreOption
                //optionText:i18nd("dpkg-unlocker","Restore services")
                optionText:"Restore services"
                optionIcon:"/usr/share/icons/breeze/actions/22/tools.svg"
                enabled:{
                    if (restoreStackBridge.runningRestoreCommand){
                        true
                    }else{
                        if ((!serviceStackBridge.areLiveProcess)&&(!serviceStackBridge.isThereALock)){
                            true
                        }else{
                            false
                        }
                    }
                }
                Connections{
                    function onMenuOptionClicked(){
                        mainStackBridge.manageTransitions(1)
                    }
                }
            }
            MenuOptionBtn {
                id:detailsOption
                //optionText:i18nd("dpkg-unlocker","Details process")
                optionText:"Details process"
                optionIcon:"/usr/share/icons/breeze/apps/22/utilities-terminal.svg"
                enabled:false
                Connections{
                    function onMenuOptionClicked(){
                        mainStackBridge.manageTransitions(2)
                    }
                }
            }

            MenuOptionBtn {
                id:protectionOption
                //optionText:i18nd("dpkg-unlocker","Metapackage protection")
                optionText:"Metapackage protection"
                optionIcon:"/usr/share/icons/breeze/status/22/security-high.svg"
                visible:protectionStackBridge.showProtectionOption
                Connections{
                    function onMenuOptionClicked(){
                        mainStackBridge.manageTransitions(3)
                    }
                }
            }
          

            MenuOptionBtn {
                id:helpOption
                //optionText:i18nd("dpkg-unlocker","Help")
                optionText:"Help"
                optionIcon:"/usr/share/icons/breeze/actions/22/help-contents.svg"
                Connections{
                    function onMenuOptionClicked(){
                        mainStackBridge.openHelp();
                    }
                }
            }
        }
    }
    GridLayout{
        id: layoutGrid
        rows:3 
        flow: GridLayout.TopToBottom
        rowSpacing:0

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
            Layout.bottomMargin:15
            Layout.fillWidth:true

            ColumnLayout{
                id:feedbackColumn
                spacing:5
                Text{
                    id:feedBackText
                    text:getFeedBackText(mainStackBridge.feedBackCode)
                    visible:false
                    font.family: "Quattrocento Sans Bold"
                    font.pointSize: 10
                    Layout.alignment:Qt.AlignHCenter
                    Layout.bottomMargin:7
                }
                ProgressBar{
                    id:feedBackBar
                    indeterminate:true
                    visible:false
                    Layout.fillWidth:true
                }
            }
    
            //PC3.Button {
            Button{
                id:unlockBtn
                visible:true
                focus:true
                display:AbstractButton.TextBesideIcon
                //icon.name:"dialog-ok"
                icon.source:"/usr/share/icons/breeze/actions/22/dialog-ok"
                text:{
                    switch(optionsLayout.currentIndex){
                        case 0:
                            //i18nd("dpkg-unlocker","Unlock")
                            "Unlock"
                            break;
                        case 1:
                            //i18nd("dpkg-unlocker","Restore")
                            "Restore"
                            break;
                        case 3:
                            //i18nd("dpkg-unlocker","Apply")
                            "Apply"
                            break;
                        case 2:
                            if (mainStackBridge.processLaunched=="Unlock"){
                                //i18nd("dpkg-unlocker","Unlock")
                                "Unlock"
                            }else{
                                //i18nd("dpkg-unlocker","Restore")
                                "Restore"
                            }
                            break;
                        default:
                            //i18nd("dpkg-unlocker","Unlock")
                            "Unlock"
                            break
                    }
                }
                Layout.preferredHeight:40
                Layout.rightMargin:10
                enabled:{
                    switch(optionsLayout.currentIndex){
                        case 0:
                            if (restoreStackBridge.runningRestoreCommand){
                                false
                            }else{
                                serviceStackBridge.isThereALock
                            }
                            break;
                        case 1:
                            if (restoreStackBridge.runningRestoreCommand){
                                false
                            }else{
                                if ((!serviceStackBridge.areLiveProcess)&&(!serviceStackBridge.isThereALock)){
                                    true
                                }else{
                                    false
                                }
                            }
                            break;
                        case 3:
                            protectionStackBridge.isProtectionChange
                            break
                        default:
                            false
                            break;
                    }
                }
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
                    //"Dpkg-Unlocker"+" - "+i18nd("dpkg-unlocker","Services Information")
                    "Dpkg-Unlocker - Services Information"
                    break;
                case 1:
                    //"Dpkg-Unlocker"+" - "+i18nd("dpkg-unlocker","Restore services")
                    "Dpkg-Unlocker - Restore services"
                    break;
                case 3:
                    //"Dpkg-Unlocker"+" - "+i18nd("dpkg-unlocker","System metapackage protection")
                    "Dpkg-Unlocker - System metapackage protection"
                    break
                default:
                    ""
                    break;
            }
        }
        dialogMsg:{
            switch(optionsLayout.currentIndex){
                case 0:
                    //i18nd("dpkg-unlocker","Do you want to run the unlock process?")
                    "Do you want to run the unlock process?"
                    break
                case 1:
                    //i18nd("dpkg-unlocker","Do you want to run the services restore process?")
                    "Do you want to run the services restore process?"
                    break
                case 3:
                    if (!protectionStackBridge.metaProtectionEnabled){
                        //i18nd("dpkg-unlocker","Do you want to disable system metapackage protection?\nDisabling this protection can cause certain applications to be uninstalled\nautomatically and cause system inconsistencies")
                        "Do you want to disable system metapackage protection?\nDisabling this protection can cause certain applications to be uninstalled\nautomatically and cause system inconsistencies"
                    }else{
                        //i18nd("dpkg-unlocker","Do you want to enable system metapackage protection?")
                        "Do you want to enable system metapackage protection?"
                    }
                    break
                default:
                    ""
                    break;
            }
        }
        dialogVisible:mainStackBridge.showDialog
        Connections{
            target:unlockDialog
            function onDialogApplyClicked(){
                switch(optionsLayout.currentIndex){
                    case 0:
                        feedBackText.visible=true
                        feedBackBar.visible=true
                        detailsOption.enabled=true
                        protectionOption.enabled=false
                        applyChanges()
                        serviceStackBridge.launchUnlockProcess()
                        break;
                    case 1:
                        feedBackText.visible=true
                        feedBackBar.visible=true
                        detailsOption.enabled=true
                        protectionOption.enabled=false
                        applyChanges()
                        restoreStackBridge.launchRestoreProcess()
                        break;
                    case 3:
                        protectionStackBridge.changeProteccionStatus()
                        break;
                }
            }

            function onDiscardDialogClicked(){
                protectionStackBridge.discardChangeProtectionStatus()
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
            if (mainStackBridge.endProcess){
                timer.stop()
                feedBackText.visible=false
                feedBackBar.visible=false
                protectionOption.enabled=true
                
            }else{
                if (mainStackBridge.endCurrentCommand){
                    mainStackBridge.getNewCommand()
                    var newCommand=mainStackBridge.currentCommand
                    konsolePanel.runCommand(newCommand)
                }
            }
          })
    } 
 
    function getFeedBackText(code){

        var msg="";
        switch (code){
            case 1:
                //msg=i18nd("dpkg-unlocker","Removing Lliurex-Up lock file...");
                msg="Removing Lliurex-Up lock file...";
                break;
            case 2:
                //msg=i18nd("dpkg-unlocker","Removing Dpkg lock file...");
                msg="Removing Dpkg lock file...";
                break;
            case 3:
                //msg=i18nd("dpkg-unlocker","Removing Apt lock file...");
                msg="Removing Apt lock file...";
                break;
             case 4:
                //msg=i18nd("dpkg-unlocker","Fixing the system...");
                msg="Fixing the system...";
                break;
            case 9:
                //msg=i18nd("dpkg-unlocker","Restoring the services...");
                msg="Restoring the services...";
                break;
            default:
                break;
        }
        return msg;

    }

    
}

