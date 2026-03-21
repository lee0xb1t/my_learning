import QtQuick
import com.lee 1.0

Window {
    width: 640
    height: 480
    visible: true
    title: qsTr("Hello World")

    Movie {
        id: movieId
        title: "test title"
        mainCharacter: "test name"

        onTitleChanged: {
            console.log("title changed:", title)
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
                    movieId.title = "1"
                    movieId.mainCharacter = "test1"
                    console.log(movieId.title, movieId.mainCharacter)
                }
            }
        }
    }
}
