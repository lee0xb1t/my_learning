import QtQuick

Window {
    width: 640
    height: 480
    visible: true
    title: qsTr("Hello World")

    Connections {
        target: Movie
        function onTitleChanged() {
            console.log("title changed:", Movie.title);
        }
        function onMainCharacterChanged() {
            console.log("main character changed:", Movie.mainCharacter);
        }
    }

    Row {
        Rectangle {
            width: 100
            height: 100
            color: "red"

            MouseArea {
                anchors.fill: parent
                onClicked: {
                    Movie.title = "test title"
                    Movie.mainCharacter = "test name"
                }
            }
        }
    }
}
