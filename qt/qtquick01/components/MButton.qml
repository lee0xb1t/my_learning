import QtQuick 2.15

Item {
    id: rootId

    property alias buttonText: textId.text
    signal buttonClicked

    width: rectId.width
    height: rectId.height

    Rectangle {
        id: rectId
        width: textId.implicitWidth * 2
        height: textId.implicitHeight * 2
        color: "dodgerblue"
        border {
            width: 2
            color: "#ccc"
        }

        Text {
            id: textId
            text: "Button"
            anchors.centerIn: parent
        }

        MouseArea {
            anchors.fill: parent
            onClicked: {
                rootId.buttonClicked()
            }
        }
    }
}
