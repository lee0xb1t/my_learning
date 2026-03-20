cmake_minimum_required(VERSION 3.16)

project(buttons VERSION 0.1 LANGUAGES CXX)

set(CMAKE_AUTOMOC ON)
set(CMAKE_CXX_STANDARD_REQUIRED ON)
set(QT_QML_OUTPUT_DIRECTORY  ${CMAKE_BINARY_DIR})

find_package(Qt6 6.2 COMPONENTS Quick REQUIRED)

qt_add_library(buttons STATIC)
qt_add_qml_module(buttons
    URI buttons
    VERSION 1.0
    QML_FILES MyItemControls.qml
    SOURCES myitem.cpp myitem.h
)

set_target_properties(buttons PROPERTIES
    MACOSX_BUNDLE_GUI_IDENTIFIER my.example.com
    MACOSX_BUNDLE_BUNDLE_VERSION ${PROJECT_VERSION}
    MACOSX_BUNDLE_SHORT_VERSION_STRING ${PROJECT_VERSION_MAJOR}.${PROJECT_VERSION_MINOR}
    MACOSX_BUNDLE TRUE
    WIN32_EXECUTABLE TRUE
)

target_compile_definitions(buttons
    PRIVATE $<$<OR:$<CONFIG:Debug>,$<CONFIG:RelWithDebInfo>>:QT_QML_DEBUG>)
target_link_libraries(buttons
    PRIVATE Qt6::Quick)

target_include_directories(buttons PUBLIC ${CMAKE_CURRENT_SOURCE_DIR})

