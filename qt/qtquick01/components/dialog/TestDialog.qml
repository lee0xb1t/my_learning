import QtQuick 2.15

Item {
    id: rootId
    width: 50
    height:20
    Rectangle {
        width: textId.implicitWidth * 1.5
        height: textId.implicitHeight * 1.5
        color: "pink"
        Text {
            id: textId
            text: "This is test dialog!"
            anchors.centerIn: parent
        }
    }
}
