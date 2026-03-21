#include "cppwork.h"
#include <QDebug>

CppWork::CppWork(QObject *parent) : QObject(parent) {

}

void CppWork::regularMethod() {
    qDebug() << "This is regular method!";
}

QString CppWork::regularMethodWithArgs(QString name, int age) {
    qDebug() << "This is regular method with args!";
    qDebug() << name;
    qDebug() << age;
    return name;
}

void CppWork::cppSlot() {
    qDebug() << "This is cppSlot!";
}
