#include "cppsignalsender.h"

CppSignalSender::CppSignalSender(QObject *parent)
    : QObject(parent)
    , m_timer(new QTimer(this))
    , m_value(0)
{
    connect(
        m_timer, &QTimer::timeout,
        [=]() {
            ++this->m_value;
            emit this->cppTimer(QString::number(m_value));
        }
    );

    m_timer->start(1000);
}

void CppSignalSender::cppSlot() {
    emit this->callQml("Call from c++");
}
