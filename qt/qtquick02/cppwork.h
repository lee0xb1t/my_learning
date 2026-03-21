#ifndef CPPWORK_H
#define CPPWORK_H
#include <QObject>

class CppWork : public QObject
{
    Q_OBJECT
public:
    explicit CppWork(QObject *parent = nullptr);

    Q_INVOKABLE void regularMethod();
    Q_INVOKABLE QString regularMethodWithArgs(QString name, int age);

signals:

public slots:
    void cppSlot();
};

#endif // CPPWORK_H
