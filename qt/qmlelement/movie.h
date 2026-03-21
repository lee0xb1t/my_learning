#ifndef MOVIE_H
#define MOVIE_H
#include <QObject>
#include <QString>
#include <QtQml>

class Movie : public QObject
{
    Q_OBJECT
    Q_PROPERTY(QString title READ title WRITE setTitle NOTIFY titleChanged)
    Q_PROPERTY(QString mainCharacter READ mainCharacter WRITE setMainCharacter NOTIFY mainCharacterChanged)
    // QML_ELEMENT
public:
    explicit Movie(QObject *parent = nullptr);

    QString mainCharacter();
    void setMainCharacter(const QString &newMainCharacter);

    QString title() const;
    void setTitle(const QString &newTitle);

signals:
    void titleChanged();
    void mainCharacterChanged();

private:
    QString m_mainCharacter;
    QString m_title;
};

#endif // MOVIE_H
