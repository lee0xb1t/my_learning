#include <QGuiApplication>
#include <QQmlApplicationEngine>
#include <QQmlContext>
#include "cppwork.h"

int main(int argc, char *argv[])
{
    QGuiApplication app(argc, argv);

    CppWork cppwork;

    QQmlApplicationEngine engine;

    engine.rootContext()->setContextProperty("BWork", &cppwork);

    QObject::connect(
        &engine,
        &QQmlApplicationEngine::objectCreationFailed,
        &app,
        []() { QCoreApplication::exit(-1); },
        Qt::QueuedConnection);
    engine.loadFromModule("qtquick02", "Main");

    return QCoreApplication::exec();
}
