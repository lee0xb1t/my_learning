import QtQuick

Window {
    width: 640
    height: 480
    visible: true
    title: qsTr("Hello World")

    Connections {
        id: connId
        target: CppSender
        function onCallQml(param) {
            console.log("On call qml:", param);
        }

        function onCppTimer(val) {
            console.log("On cpp timer:", val)
        }
    }

    Row {
        Rectangle {
            color: "red"
            width: 100
            height: 100

            MouseArea {
                anchors.fill: parent
                onClicked: {
                    CppSender.cppSlot()
                }
            }
        }
    }

    // Row {
    //     Rectangle {
    //         width: 100
    //         height: 100
    //         color: "red"
    //         MouseArea {
    //             id: redRectMAId
    //             anchors.fill: parent
    //         }
    //     }

    //     Rectangle {
    //         width: 100
    //         height: 100
    //         color: "green"
    //         Connections {
    //             target: redRectMAId
    //             function onClicked() {
    //                 console.log("Green rectangle is clicked!")
    //             }
    //         }
    //     }

    //     Rectangle {
    //         width: 100
    //         height: 100
    //         color: "blue"
    //         Connections {
    //             target: redRectMAId
    //             function onClicked() {
    //                 console.log("Blue rectangle is clicked!")
    //             }
    //         }
    //     }
    // }
}
