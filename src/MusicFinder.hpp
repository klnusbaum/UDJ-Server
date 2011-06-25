#ifndef MUSIC_FINDER_HPP
#define MUSIC_FINDER_HPP

#include <QDir>
#include "phonon/mediasource.h"


namespace UDJ{


class MusicFinder{
public:
  static QList<Phonon::MediaSource> findMusicInDir(const QString& musicDir);
private:
  static bool isMusicFile(const QFileInfo& file);
  static const QRegExp& getMusicFileMatcher(){
    //static const QRegExp matcher("*.mp3|*.m4a|*.ogg|*.wav", Qt::CaseSensitive, QRegExp::Wildcard);
    static const QRegExp matcher("*.mp3", Qt::CaseSensitive, QRegExp::Wildcard);
    return matcher;
  }
}; 


} //end namespace
#endif //MUSIC_FINDER_HPP
