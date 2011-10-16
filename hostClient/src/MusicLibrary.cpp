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
#include <QDesktopServices>
#include <QDir>
#include <QSqlQuery>
#include <QVariant>

namespace UDJ{


MusicLibrary::MusicLibrary(UDJServerConnection *serverConnection, QObject *parent)
 :QObject(parent),serverConnection(serverConnection)
{
  metaDataGetter = new Phonon::MediaObject(this);
  setupDB();
  connect(
    serverConnection,
    SIGNAL(serverIdsUpdate(const std::map<library_song_id_t, library_song_id_t>)),
    this,
    SLOT(updateServerIds(const std::map<library_song_id_t, library_song_id_t>)));
}

void MusicLibrary::setupDB(){
  //TODO do all of this stuff in a seperate thread and return right away.
  QDir dbDir(QDesktopServices::storageLocation(QDesktopServices::DataLocation));  
  if(!dbDir.exists()){
    //TODO handle if this fails
    dbDir.mkpath(dbDir.absolutePath());
  }
  database = QSqlDatabase::addDatabase("QSQLITE", getMusicDBConnectionName());
  database.setDatabaseName(dbDir.absoluteFilePath(getMusicDBName()));
  database.open(); 

  QSqlQuery setupQuery(database);

	EXEC_SQL(
		"Error creating library table", 
		setupQuery.exec(getCreateLibraryQuery()), 
		setupQuery)	

	EXEC_SQL(
		"Error creating playlist table.", 
		setupQuery.exec(getCreatePlaylistQuery()),
		setupQuery)	

	EXEC_SQL(
		"Error creating playlist view.",
  	setupQuery.exec(getCreatePlaylistViewQuery()),
		setupQuery)

	EXEC_SQL(
		"Error creating update trigger for playlist view.",
  	setupQuery.exec(getPlaylistUpdateTriggerQuery()),
		setupQuery)

	EXEC_SQL(
		"Error creating delete trigger for playlist view.",
		setupQuery.exec(getPlaylistDeleteTriggerQuery()),
		setupQuery)

	EXEC_SQL(
		"Error creating insert trigger for playlist view.",
  	setupQuery.exec(getPlaylistInsertTriggerQuery()),
		setupQuery)
}

void MusicLibrary::clearMyLibrary(){
  QSqlQuery workQuery(database);
  workQuery.exec("DELETE FROM " + getLibraryTableName());
  //TODO inform the server of the cleared library
}

void MusicLibrary::setMusicLibrary(QList<Phonon::MediaSource> songs, QProgressDialog& progress){
	clearMyLibrary();
  //TODO tell the server to clear the library as well.
  for(int i =0; i<songs.size(); ++i){
    progress.setValue(i);
    if(progress.wasCanceled()){
      break;
    }
    addSong(songs[i]);
  }
  emit songsAdded();
}

void MusicLibrary::addSong(Phonon::MediaSource song){
  metaDataGetter->setCurrentSource(song);
  QString songName =	getSongName(song);
  QString artistName = getArtistName(song);
  QString albumName = getAlbumName(song);
  QString fileName = song.fileName();

  library_song_id_t hostId = MusicLibrary::getInvalidHostId();
  QSqlQuery addQuery("INSERT INTO "+getLibraryTableName()+ 
    "("+
    getLibSongColName() + ","+
    getLibArtistColName() + ","+
    getLibAlbumColName() + ","+
    getLibFileColName() + ") VALUES ( ?, ?, ?, ?)", database);
  
  addQuery.addBindValue(songName);
  addQuery.addBindValue(artistName);
  addQuery.addBindValue(albumName);
  addQuery.addBindValue(fileName);
	EXEC_INSERT(
		"Failed to add song " << songName.toStdString(), 
		addQuery,
    hostId)
  //TODO should do error checking at this point and make sure hostId is valid
	serverConnection->addLibSongOnServer(songName, artistName, albumName, hostId);
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

void MusicLibrary::updateServerIds(
  const std::map<library_song_id_t, library_song_id_t> hostToServerIdMap)
{
  QSqlQuery updateQuery(database);
	updateQuery.prepare(
		"UPDATE " + getLibraryTableName() + " "
		"SET " + getServerLibIdColName() + " = ? "
		"WHERE " +getLibIdColName() + " = ? ;"
		);
  for(
    std::map<library_song_id_t, library_song_id_t>::const_iterator it = 
      hostToServerIdMap.begin();
    it != hostToServerIdMap.end();
    ++it
  )
  { 
    //std::cout << "about to update with " << it->second << " and " << it->first
      //<< std::endl;
	  updateQuery.bindValue(0, QVariant::fromValue<library_song_id_t>(it->second));
	  updateQuery.bindValue(1, QVariant::fromValue<library_song_id_t>(it->first));
    //std::cout << "0: " << updateQuery.boundValue(0).toString().toStdString() <<
      //" 1: " << updateQuery.boundValue(1).toString().toStdString() << std::endl;
	  EXEC_SQL(
		  "Updating server id didn't work!", 
		  updateQuery.exec(), 
		  updateQuery);
   
  }
}

bool MusicLibrary::alterVoteCount(playlist_song_id_t plId, int difference){
	QSqlQuery updateQuery(
		"UPDATE main_playlist_view "
		"SET voteCount = (voteCount + ?) "
		"WHERE plId = ? ", 
		database);
	updateQuery.addBindValue(difference);
	updateQuery.addBindValue(QVariant::fromValue(plId));
	EXEC_SQL(
		"Updating vote count didn't work!", 
		updateQuery.exec(), 
		updateQuery);
	//TODO return value should be based on success of above query.
  //TODO inform the server of the altered vote count
	return true;
}

bool MusicLibrary::addSongToPlaylist(library_song_id_t libraryId){
	QSqlQuery insertQuery("INSERT INTO " + getPlaylistTableName() +" "
		"("+getPlaylistLibIdColName()+") VALUES ( ? );", database);
	insertQuery.addBindValue(QVariant::fromValue(libraryId));
	
	EXEC_SQL(
		"Adding to playlist failed", 
		insertQuery.exec(),
		insertQuery)
	//TODO this value should instead be based on the result of the
	//above sql query.
  //TODO inform the server of the song being added from the playlist
	return true;
}

bool MusicLibrary::removeSongFromPlaylist(playlist_song_id_t plId){
	QSqlQuery removeQuery("DELETE FROM " + getPlaylistTableName() + " "
		"WHERE " + getPlaylistIdColName() +" = ? ;", database);
	removeQuery.addBindValue(QVariant::fromValue(plId));
	
	EXEC_SQL(
		"Remove from playlist failed", 
		removeQuery.exec(),
		removeQuery)
	//TODO this value should be based on above result
  //TODO inform the server of the song being removed from the playlist
	return true;
}

QSqlDatabase MusicLibrary::getDatabaseConnection(){
  return database;
}

Phonon::MediaSource MusicLibrary::getNextSongToPlay(){
  QSqlQuery nextSongQuery("SELECT " + getLibFileColName() + " FROM " +
    getPlaylistViewName() + " LIMIT 1;");
  EXEC_SQL(
    "Getting next song failed",
    nextSongQuery.exec(),
    nextSongQuery)
  //TODO handle is this returns false
  nextSongQuery.first();
  return Phonon::MediaSource(nextSongQuery.value(0).toString());
}

Phonon::MediaSource MusicLibrary::takeNextSongToPlay(){
  QSqlQuery nextSongQuery(
    "SELECT " + getLibFileColName() + ", " + getPlaylistIdColName() +" FROM " +
    getPlaylistViewName() + " LIMIT 1;");
  EXEC_SQL(
    "Getting next song in take failed",
    nextSongQuery.exec(),
    nextSongQuery)
  nextSongQuery.first();
  QString filePath = nextSongQuery.value(0).toString();
  playlist_song_id_t  toDeleteId  = nextSongQuery.value(1).value<playlist_song_id_t>();
  
  QSqlQuery deleteNextSongQuery(
    "DELETE FROM " + getPlaylistViewName() + " WHERE " + 
    getPlaylistIdColName() + "=" +QString::number(toDeleteId) + ";");
  EXEC_SQL(
    "Error deleting song in takeNextSong",
    deleteNextSongQuery.exec(),
    deleteNextSongQuery)
  return Phonon::MediaSource(filePath);
}

} //end namespace
