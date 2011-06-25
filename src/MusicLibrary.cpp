#include "MusicLibrary.hpp"
#include <QDesktopServices>
#include <QDir>
#include <QSqlQuery>
#include <iostream>
#include <QSqlError>

namespace UDJ{


MusicLibrary::MusicLibrary(QWidget* parent):QSqlTableModel(
  parent, 
  QSqlDatabase::addDatabase("QSQLITE", getMusicDBConnectionName()))
{
  metaDataGetter = new Phonon::MediaObject(0);
  QDir dbDir(QDesktopServices::storageLocation(QDesktopServices::DataLocation));  
  if(!dbDir.exists()){
    //TODO handle if this fails
    dbDir.mkpath(dbDir.absolutePath());
  }
  database().setDatabaseName(dbDir.absoluteFilePath(getMusicDBName()));
  database().open(); 
  QSqlQuery setupQuery(database());
  setupQuery.exec("CREATE TABLE IF NOT EXISTS library "
  "(id INTEGER PRIMARY KEY AUTOINCREMENT, "
  "song TEXT NOT NULL, artist TEXT, album TEXT, filePath TEXT)");  
}

MusicLibrary::~MusicLibrary(){
  delete metaDataGetter;
}

void MusicLibrary::setMusicLibrary(QList<Phonon::MediaSource> songs, QProgressDialog& progress){
  QSqlQuery workQuery(musicdb);
  workQuery.exec("DELETE FROM library");
  for(int i =0; i<songs.size(); ++i){
    progress.setValue(i);
    if(progress.wasCanceled()){
      break;
    }
    addSong(songs[i]);
  }
}

void MusicLibrary::addSong(Phonon::MediaSource song){
  metaDataGetter->setCurrentSource(song);
  QSqlQuery addQuery("INSERT INTO library "
    "(song, artist, album, filePath) VALUES ( ?, ?, ?, ?)", database());
  
  addQuery.addBindValue(getSongName(song));
  addQuery.addBindValue(getArtistName(song));
  addQuery.addBindValue(getAlbumName(song));
  addQuery.addBindValue(song.fileName());
  bool worked = addQuery.exec();
  if(!worked){
    std::cerr << "Failed to add song " << getSongName(song).toStdString() << std::endl;
    std::cerr << addQuery.lastError().text().toStdString() <<std::endl;
  }
}

QString MusicLibrary::getSongName(Phonon::MediaSource song) const{
  QStringList metaData = metaDataGetter->metaData(Phonon::TitleMetaData);  
  if(metaData.size() != 0){
    return metaData[0];
  }
  else{
    QFileInfo songFile(song.fileName());
    return songFile.fileName();
  }
}

QString MusicLibrary::getArtistName(Phonon::MediaSource song) const{
  QStringList metaData = metaDataGetter->metaData(Phonon::ArtistMetaData);
  if(metaData.size() != 0 && metaData[0] != ""){
    return metaData[0];
  }
  else{
    return "Unknonwn";
  }
}

QString MusicLibrary::getAlbumName(Phonon::MediaSource song) const{
  QStringList metaData = metaDataGetter->metaData(Phonon::AlbumMetaData);
  if(metaData.size() != 0 && metaData[0] != ""){
      return metaData[0];
  }
  else{
    return "Unknonwn";
  }
}

} //end namespace
