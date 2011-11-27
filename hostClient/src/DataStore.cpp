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
#include "DataStore.hpp"
#include <QDir>
#include <QDesktopServices>
#include <QDir>
#include <QSqlQuery>
#include <QVariant>
#include <QSqlRecord>

namespace UDJ{


DataStore::DataStore(UDJServerConnection *serverConnection, QObject *parent)
 :QObject(parent),serverConnection(serverConnection)
{
  metaDataGetter = new Phonon::MediaObject(this);
  setupDB();
  connect(
    serverConnection,
    SIGNAL(
      songsAddedOnServer(const std::vector<library_song_id_t>)
    ),
    this,
    SLOT(
      setLibSongsSynced(const std::vector<library_song_id_t>)
    )
  );

  connect(
    serverConnection,
    SIGNAL(eventCreated()),
    this,
    SIGNAL(eventCreated()));

  connect(
    serverConnection,
    SIGNAL(eventCreationFailed()),
    this,
    SIGNAL(eventCreationFailed()));

  syncLibrary();
}

void DataStore::setupDB(){
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
		"Error creating activePlaylist table.", 
		setupQuery.exec(getCreateActivePlaylistQuery()),
		setupQuery)	

	EXEC_SQL(
		"Error creating activePlaylist view.",
  	setupQuery.exec(getCreateActivePlaylistViewQuery()),
		setupQuery)

	EXEC_SQL(
		"Error creating update trigger for activePlaylist view.",
  	setupQuery.exec(getActivePlaylistUpdateTriggerQuery()),
		setupQuery)

	EXEC_SQL(
		"Error creating delete trigger for activePlaylist view.",
		setupQuery.exec(getActivePlaylistDeleteTriggerQuery()),
		setupQuery)

	EXEC_SQL(
		"Error creating insert trigger for activePlaylist view.",
  	setupQuery.exec(getActivePlaylistInsertTriggerQuery()),
		setupQuery)
}

void DataStore::clearMyLibrary(){
  QSqlQuery workQuery(database);
  workQuery.exec("DELETE FROM " + getLibraryTableName());
  //TODO inform the server of the cleared library
}

void DataStore::addMusicToLibrary(
  QList<Phonon::MediaSource> songs, QProgressDialog& progress)
{
  for(int i =0; i<songs.size(); ++i){
    progress.setValue(i);
    if(progress.wasCanceled()){
      break;
    }
    addSongToLibrary(songs[i]);
  }
  emit songsAdded();
}

void DataStore::addSongToLibrary(Phonon::MediaSource song){
  metaDataGetter->setCurrentSource(song);
  QString songName =	getSongName(song);
  QString artistName = getArtistName(song);
  QString albumName = getAlbumName(song);
  QString fileName = song.fileName();
  int duration = metaDataGetter->totalTime() /1000;

  library_song_id_t hostId;
  QSqlQuery addQuery(
    "INSERT INTO "+getLibraryTableName()+ 
    "("+
    getLibSongColName() + ","+
    getLibArtistColName() + ","+
    getLibAlbumColName() + ","+
    getLibFileColName() + "," +
    getLibDurationColName() +")" +
    "VALUES ( :song , :artist , :album , :file, :duration );", 
    database);
  
  addQuery.bindValue(":song", songName);
  addQuery.bindValue(":artist", artistName);
  addQuery.bindValue(":album", albumName);
  addQuery.bindValue(":file", fileName);
  addQuery.bindValue(":duration", duration);
	EXEC_INSERT(
		"Failed to add song " << songName.toStdString(), 
		addQuery,
    hostId)
	serverConnection->addLibSongOnServer(
    songName, artistName, albumName, duration, hostId);
}

QString DataStore::getSongName(Phonon::MediaSource song) const{
  QStringList metaData = metaDataGetter->metaData(Phonon::TitleMetaData);  
  if(metaData.size() != 0){
    return metaData[0];
  }
  else{
    QFileInfo songFile(song.fileName());
    return songFile.fileName();
  }
}

QString DataStore::getArtistName(Phonon::MediaSource song) const{
  QStringList metaData = metaDataGetter->metaData(Phonon::ArtistMetaData);
  if(metaData.size() != 0 && metaData[0] != ""){
    return metaData[0];
  }
  else{
    return "Unknonwn";
  }
}

QString DataStore::getAlbumName(Phonon::MediaSource song) const{
  QStringList metaData = metaDataGetter->metaData(Phonon::AlbumMetaData);
  if(metaData.size() != 0 && metaData[0] != ""){
      return metaData[0];
  }
  else{
    return "Unknonwn";
  }
}

bool DataStore::alterVoteCount(playlist_song_id_t plId, int difference){
  //TODO actually implement
	return true;
}

bool DataStore::addSongToActivePlaylist(library_song_id_t libraryId){
	QSqlQuery insertQuery("INSERT INTO " + getActivePlaylistTableName() +" "
		"("+getActivePlaylistLibIdColName()+") VALUES ( ? );", database);
	insertQuery.addBindValue(QVariant::fromValue(libraryId));
	
	EXEC_SQL(
		"Adding to playlist failed", 
		insertQuery.exec(),
		insertQuery)
	//TODO this value should instead be based on the result of the
	//above sql query.
  //TODO inform the server of the song being added from the activePlaylist
	return true;
}

bool DataStore::removeSongFromActivePlaylist(playlist_song_id_t plId){
	QSqlQuery removeQuery("DELETE FROM " + getActivePlaylistTableName() + " "
		"WHERE " + getActivePlaylistIdColName() +" = ? ;", database);
	removeQuery.addBindValue(QVariant::fromValue(plId));
	
	EXEC_SQL(
		"Remove from activePlaylist failed", 
		removeQuery.exec(),
		removeQuery)
	//TODO this value should be based on above result
  //TODO inform the server of the song being removed from the activePlaylist
	return true;
}

QSqlDatabase DataStore::getDatabaseConnection(){
  return database;
}

Phonon::MediaSource DataStore::getNextSongToPlay(){
  QSqlQuery nextSongQuery("SELECT " + getLibFileColName() + " FROM " +
    getActivePlaylistViewName() + " LIMIT 1;");
  EXEC_SQL(
    "Getting next song failed",
    nextSongQuery.exec(),
    nextSongQuery)
  //TODO handle is this returns false
  nextSongQuery.first();
  return Phonon::MediaSource(nextSongQuery.value(0).toString());
}

Phonon::MediaSource DataStore::takeNextSongToPlay(){
  QSqlQuery nextSongQuery(
    "SELECT " + getLibFileColName() + ", " + 
    getActivePlaylistIdColName() +" FROM " +
    getActivePlaylistViewName() + " LIMIT 1;", 
    database);
  EXEC_SQL(
    "Getting next song in take failed",
    nextSongQuery.exec(),
    nextSongQuery)
  nextSongQuery.first();
  QString filePath = nextSongQuery.value(0).toString();
  playlist_song_id_t  toDeleteId  = 
    nextSongQuery.value(1).value<playlist_song_id_t>();
  
  QSqlQuery deleteNextSongQuery(
    "DELETE FROM " + getActivePlaylistViewName() + " WHERE " + 
    getActivePlaylistIdColName() + "=" +QString::number(toDeleteId) + ";", 
    database);
  EXEC_SQL(
    "Error deleting song in takeNextSong",
    deleteNextSongQuery.exec(),
    deleteNextSongQuery)
  return Phonon::MediaSource(filePath);
}

void DataStore::createNewEvent(
  const QString& name, 
  const QString& password, 
  const QString& location)
{
  serverConnection->createNewEvent(name, password, location);
}

void DataStore::syncLibrary(){
  QSqlQuery getUnsyncedSongs(database);
  EXEC_SQL(
    "Error querying for unsynced songs",
    getUnsyncedSongs.exec(
      "SELECT * FROM " + getLibraryTableName() + " WHERE " + 
      getLibSyncStatusColName() + "!=" + 
      QString::number(getLibIsSyncedStatus()) + ";"),
    getUnsyncedSongs)

  while(getUnsyncedSongs.next()){  
    QSqlRecord currentRecord = getUnsyncedSongs.record();
    if(currentRecord.value(getLibSyncStatusColName()) == 
      getLibNeedsAddSyncStatus())
    {
	    serverConnection->addLibSongOnServer(
        currentRecord.value(getLibSongColName()).toString(),
        currentRecord.value(getLibArtistColName()).toString(),
        currentRecord.value(getLibAlbumColName()).toString(),
        currentRecord.value(getLibDurationColName()).toInt(),
        currentRecord.value(getLibIdColName()).value<library_song_id_t>());
    }
    else if(currentRecord.value(getLibSyncStatusColName()) ==
      getLibNeedsDeleteSyncStatus())
    {
      //TODO implement delete call here
    }
  }
}

void DataStore::setLibSongsSynced(const std::vector<library_song_id_t> songs){
  setLibSongsSyncStatus(songs, getLibIsSyncedStatus());
}

void DataStore::setLibSongsSyncStatus(
  const std::vector<library_song_id_t> songs,
  const lib_sync_status_t syncStatus)
{
  QSqlQuery setSyncedQuery(database);
  for(int i=0; i< songs.size(); ++i){
    std::cout << "Updaing status of song: " << songs[i] << std::endl;
    EXEC_SQL(
      "Error setting song to synced",
      setSyncedQuery.exec(
        "UPDATE " + getLibraryTableName() + " " +
        "SET " + getLibSyncStatusColName() + "=" + QString::number(syncStatus) +
        " WHERE "  +
        getLibIdColName() + "=" + QString::number(songs[i]) + ";"),
      setSyncedQuery)
   }
}
  

} //end namespace
