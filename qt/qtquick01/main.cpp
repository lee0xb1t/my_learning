#include <QGuiApplication>
#include <QQmlApplicationEngine>
#include <QQuickStyle>
#include "tablemodel.h"

int main(int argc, char *argv[])
{
    QGuiApplication app(argc, argv);

    QQmlApplicationEngine engine;
    QQuickStyle::setStyle("Fusion");
    QObject::connect(
        &engine,
        &QQmlApplicationEngine::objectCreationFailed,
        &app,
        []() { QCoreApplication::exit(-1); },
        Qt::QueuedConnection);

    engine.addImportPath(":/");
    engine.loadFromModule("qtquick02", "Main");

    return QCoreApplication::exec();
}
