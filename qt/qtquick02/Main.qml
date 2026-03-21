import QtQuick

Window {
    width: 640
    height: 480
    visible: true
    title: qsTr("Hello World")

    Rectangle {
        color: "red"
        width: 50
        height: 50

        MouseArea {
            anchors.fill: parent
            onClicked: {
                BWork.regularMethod()
                console.log(BWork.regularMethodWithArgs("name", 18))
                BWork.cppSlot()
            }
        }
    }
}
