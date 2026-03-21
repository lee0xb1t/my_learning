#include <QGuiApplication>
#include <QQmlApplicationEngine>
#include <QtQml>
#include "movie.h"

int main(int argc, char *argv[])
{
    QGuiApplication app(argc, argv);

    qmlRegisterType<Movie>("com.lee", 1, 0, "Movie");

    QQmlApplicationEngine engine;
    QObject::connect(
        &engine,
        &QQmlApplicationEngine::objectCreationFailed,
        &app,
        []() { QCoreApplication::exit(-1); },
        Qt::QueuedConnection);
    engine.loadFromModule("qmlelement", "Main");

    return QCoreApplication::exec();
}
