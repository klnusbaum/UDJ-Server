/**
 * Copyright 2011 Kurtis L. Nusbaum
 * 
 * This file is part of UDJ.
 * 
 * UDJ is free software: you can redistribute it and/or modify
 * it under the terms of the GNU General Public License as published by
 * the Free Software Foundation, either version 2 of the License, or
 * (at your option) any later version.
 * 
 * UDJ is distributed in the hope that it will be useful,
 * but WITHOUT ANY WARRANTY; without even the implied warranty of
 * MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
 * GNU General Public License for more details.
 * 
 * You should have received a copy of the GNU General Public License
 * along with UDJ.  If not, see <http://www.gnu.org/licenses/>.
 */
#include "MusicLibrary.hpp"
#include <QDir>
#include <QSqlQuery>

namespace UDJ{


MusicLibrary::MusicLibrary(QSqlDatabase musicdb, QWidget* parent)
  :QSqlTableModel(parent,musicdb)
{
  metaDataGetter = new Phonon::MediaObject(0);
  setTable("library");
  select();
  setHeaderData(0, Qt::Horizontal, "id");
  setHeaderData(1, Qt::Horizontal, "Song");
  setHeaderData(2, Qt::Horizontal, "Artist");
  setHeaderData(3, Qt::Horizontal, "Album");
  setHeaderData(4, Qt::Horizontal, "filepath");
}

MusicLibrary::~MusicLibrary(){
  delete metaDataGetter;
}

void MusicLibrary::setMusicLibrary(QList<Phonon::MediaSource> songs, QProgressDialog& progress){
  QSqlQuery workQuery(database());
  workQuery.exec("DROP TABLE library");
  workQuery.exec("CREATE TABLE IF NOT EXISTS library "
  "(id INTEGER PRIMARY KEY AUTOINCREMENT, "
  "song TEXT NOT NULL, artist TEXT, album TEXT, filePath TEXT)");  
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
	PRINT_SQLERROR("Failed to add song " << getSongName(song).toStdString(), addQuery)
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
