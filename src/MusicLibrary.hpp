#ifndef MUSIC_LIBRARY_HPP
#define MUSIC_LIBRARY_HPP
#include <QSqlTableModel>
#include <QSqlDatabase>
#include <phonon/mediaobject.h>
#include <phonon/mediasource.h>
#include <QProgressDialog>

namespace UDJ{


class MusicLibrary : public QSqlTableModel{
Q_OBJECT
public:
  MusicLibrary(QWidget* parent=0);
  ~MusicLibrary();
  const QSqlDatabase& getDatabase() const;

  void setMusicLibrary(QList<Phonon::MediaSource> songs, QProgressDialog& progress);

  void addSong(Phonon::MediaSource song);

  static const QString& getMusicDBConnectionName(){
    static const QString musicDBConnectionName("musicdbConn");
    return musicDBConnectionName;
  }

  static const QString& getMusicDBName(){
    static const QString musicDBName("librarydb");
    return musicDBName;
  }
  

private:
  QSqlDatabase musicdb;
  Phonon::MediaObject* metaDataGetter;
  
  QString getSongName(Phonon::MediaSource song) const;
  QString getArtistName(Phonon::MediaSource song) const;
  QString getAlbumName(Phonon::MediaSource song) const;
};


} //end namespace
#endif //MUSIC_LIBRARY_HPP
