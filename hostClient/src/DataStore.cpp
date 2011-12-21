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
#include <QThread>
#include <QTimer>
#include <tag.h>
#include <tstring.h>
#include <fileref.h>

namespace UDJ{


DataStore::DataStore(UDJServerConnection *serverConnection, QObject *parent)
 :QObject(parent),serverConnection(serverConnection)
{
  serverConnection->setParent(this);
  activePlaylistRefreshTimer = new QTimer(this);
  activePlaylistRefreshTimer->setInterval(5000);
  eventName = "";
  setupDB();
  connect(
    serverConnection,
    SIGNAL(
      songsAddedToLibOnServer(const std::vector<library_song_id_t>)
    ),
    this,
    SLOT(
      setLibSongsSynced(const std::vector<library_song_id_t>)
    )
  );

  connect(
    serverConnection,
    SIGNAL(
      songDeletedFromLibOnServer(library_song_id_t)
    ),
    this,
    SLOT(
      setLibSongSynced(library_song_id_t)
    )
  );


  connect(
    serverConnection,
    SIGNAL(eventCreated()),
    this,
    SIGNAL(eventCreated()));

  connect(
    serverConnection,
    SIGNAL(eventCreated()),
    activePlaylistRefreshTimer,
    SLOT(start()));

  connect(
    serverConnection,
    SIGNAL(eventCreationFailed(const QString)),
    this,
    SIGNAL(eventCreationFailed(const QString)));

  connect(serverConnection, SIGNAL(eventEnded()), this, SIGNAL(eventEnded()));
  connect(
    serverConnection, 
    SIGNAL(eventEnded()), 
    activePlaylistRefreshTimer, 
    SLOT(stop()));
  connect(serverConnection, SIGNAL(eventEnded()), this, SLOT(eventCleanUp()));
  connect(
    serverConnection, 
    SIGNAL(eventEndingFailed(const QString)), 
    this, 
    SIGNAL(eventEndingFailed(const QString)));

  connect(
    serverConnection,
    SIGNAL(songsAddedToAvailableMusic(const std::vector<library_song_id_t>)),
    this,
    SLOT(setAvailableSongsSynced(const std::vector<library_song_id_t>)));

  connect(
    serverConnection,
    SIGNAL(songRemovedFromAvailableMusicOnServer(const library_song_id_t)),
    this,
    SLOT(setAvailableSongSynced(const library_song_id_t)));


  connect(
    serverConnection,
    SIGNAL(newActivePlaylist(const QVariantList)),
    this,
    SLOT(setActivePlaylist(const QVariantList)));

  connect(
    serverConnection,
    SIGNAL(songsAddedToActivePlaylist(const std::vector<client_request_id_t>)),
    this,
    SLOT(setPlaylistAddRequestsSynced(const std::vector<client_request_id_t>)));

  connect(activePlaylistRefreshTimer,
    SIGNAL(timeout()),
    this,
    SLOT(refreshActivePlaylist()));

  connect(
    serverConnection,
    SIGNAL(currentSongSet()),
    this,
    SLOT(refreshActivePlaylist()));
  syncLibrary();
  connect(
    this,
    SIGNAL(eventCreated()),
    this,
    SLOT(eventCleanUp())); 
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
		"Error creating available music",
  	setupQuery.exec(getCreateAvailableMusicQuery()),
		setupQuery)
	EXEC_SQL(
		"Error creating available music",
  	setupQuery.exec(getCreateAvailableMusicViewQuery()),
		setupQuery)
	EXEC_SQL(
		"Error creating available music",
  	setupQuery.exec(getCreatePlaylistAddRequestsTableQuery()),
		setupQuery)
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
  emit libSongsModified();
}

void DataStore::addSongToLibrary(Phonon::MediaSource song){
  QString fileName = song.fileName();
  QString songName;
  QString artistName;
  QString albumName;
  int duration;
  TagLib::FileRef f(fileName.toStdString().c_str());
  if(!f.isNull() && f.tag() && f.audioProperties()){
    TagLib::Tag *tag = f.tag();
    songName =	TStringToQString(tag->title());
    artistName = TStringToQString(tag->artist());
    albumName = TStringToQString(tag->album());
    duration = f.audioProperties()->length();
  }
  else{
    //TODO throw error
    return;
  }

  library_song_id_t hostId =-1;
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
		"Failed to add song library" << songName.toStdString(), 
		addQuery,
    hostId,
    library_song_id_t)
  if(hostId != -1){
	  serverConnection->addLibSongOnServer(
      songName, artistName, albumName, duration, hostId);
  }
}

void DataStore::removeSongsFromLibrary(std::vector<library_song_id_t> toRemove){
  QVariantList toDelete;
  for(
    std::vector<library_song_id_t>::const_iterator it= toRemove.begin();
    it!=toRemove.end();
    ++it)
  {
    toDelete << QVariant::fromValue<library_song_id_t>(*it);
  }
  QSqlQuery bulkDelete(database);
  bulkDelete.prepare("UPDATE " + getLibraryTableName() +  " "
    "SET " + getLibIsDeletedColName() + "=1, "+
    getLibSyncStatusColName() + "=" + 
      QString::number(getLibNeedsDeleteSyncStatus()) + " "
    "WHERE " + getLibIdColName() + "= ?"); 
  bulkDelete.addBindValue(toDelete);
  EXEC_BULK_QUERY("Error removing songs from library", 
    bulkDelete)
  if(bulkDelete.lastError().type() == QSqlError::NoError){
    emit libSongsModified();
    syncLibrary();
  }
}

void DataStore::addSongToAvailableSongs(library_song_id_t toAdd){
  std::vector<library_song_id_t> toAddVector(1, toAdd);
  addSongsToAvailableSongs(toAddVector);
}

void DataStore::addSongsToAvailableSongs(
  const std::vector<library_song_id_t>& song_ids)
{
  for(
    std::vector<library_song_id_t>::const_iterator it = song_ids.begin();
    it != song_ids.end();
    ++it
  )
  {
    QSqlQuery addQuery(
      "INSERT INTO "+ getAvailableMusicTableName()+ " ("+
      getAvailableEntryLibIdColName() +") " +
      "VALUES ( :libid );", 
      database);
    
    library_song_id_t added_lib_id = -1;
    addQuery.bindValue(
      ":libid", 
      QVariant::fromValue<const library_song_id_t>(*it));
	  EXEC_INSERT(
		  "Failed to add song to available music" << *it, 
		  addQuery,
      added_lib_id, 
      library_song_id_t)
  }
  syncAvailableMusic();
}

void DataStore::removeSongsFromAvailableMusic(
  const std::vector<library_song_id_t>& song_ids)
{
  if(song_ids.size() < 1){
    return;
  }
  QVariantList toDelete;
  for(
    std::vector<library_song_id_t>::const_iterator it = song_ids.begin();
    it!=song_ids.end();
    ++it)
  {
    toDelete << QVariant::fromValue<library_song_id_t>(*it);
  }
  QSqlQuery bulkUpdate(database);
  bulkUpdate.prepare(
    "UPDATE " + getAvailableMusicTableName() + " " 
    "SET " + getAvailableEntrySyncStatusColName() + " = " + 
      QString::number(getAvailableEntryNeedsDeleteSyncStatus()) + ", " +
    getAvailableEntryIsDeletedColName() + "=1 "+
    " WHERE "  + getAvailableEntryLibIdColName() + " = ? ;");
  bulkUpdate.addBindValue(toDelete);

  EXEC_BULK_QUERY("Error inserting songs into add queue for active playlist", 
    bulkUpdate)
  if(bulkUpdate.lastError().type() == QSqlError::NoError){
    syncAvailableMusic();
  }
}




void DataStore::addSongToActivePlaylist(library_song_id_t libraryId){
  std::vector<library_song_id_t> toAdd(1, libraryId);
  addSongsToActivePlaylist(toAdd);
}

void DataStore::addSongsToActivePlaylist(
  const std::vector<library_song_id_t>& libIds)
{
  QVariantList toInsert;
  for(
    std::vector<library_song_id_t>::const_iterator it= libIds.begin();
    it!=libIds.end();
    ++it)
  {
    toInsert << QVariant::fromValue<library_song_id_t>(*it);
  }
  QSqlQuery bulkInsert(database);
  bulkInsert.prepare("INSERT INTO " + getPlaylistAddRequestsTableName() + 
    "(" + getPlaylistAddLibIdColName() + ") VALUES( ? );");
  bulkInsert.addBindValue(toInsert);
  EXEC_BULK_QUERY("Error inserting songs into add queue for active playlist", 
    bulkInsert)
  syncPlaylistAddRequests();
}

void DataStore::removeSongFromActivePlaylist(playlist_song_id_t plId){
  std::vector<library_song_id_t> toRemove(1, plId);
  removeSongsFromActivePlaylist(toRemove);
}

void DataStore::removeSongsFromActivePlaylist(
  const std::vector<library_song_id_t>& pl_ids)
{

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
  nextSongQuery.next();
  if(!nextSongQuery.isValid()){
    return Phonon::MediaSource("");
  }
  QString filePath = nextSongQuery.value(0).toString();
  playlist_song_id_t  currentSongId  = 
    nextSongQuery.value(1).value<playlist_song_id_t>();
  
  serverConnection->setCurrentSong(currentSongId);
  return Phonon::MediaSource(filePath);
}

void DataStore::setCurrentSong(playlist_song_id_t songToPlay){
  QSqlQuery getSongQuery(
    "SELECT " + getLibFileColName() + "  FROM " +
    getActivePlaylistViewName() + " WHERE " + 
    getActivePlaylistIdColName() + " = " + QString::number(songToPlay) + ";", 
    database);
  EXEC_SQL(
    "Getting song for manual playlist set failed.",
    getSongQuery.exec(),
    getSongQuery)
  getSongQuery.next();
  if(getSongQuery.isValid()){
    QString filePath = getSongQuery.value(0).toString();
    emit manualSongChange(Phonon::MediaSource(filePath));
    serverConnection->setCurrentSong(songToPlay);
  }
}

void DataStore::createNewEvent(
  const QString& name, 
  const QString& password)
{
  eventName = name;
  serverConnection->createEvent(name, password);
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
      serverConnection->deleteLibSongOnServer(
        currentRecord.value(getLibIdColName()).value<library_song_id_t>());
    }
  }
}

void DataStore::setLibSongSynced(library_song_id_t song){
  std::vector<library_song_id_t> songVector(1,song);
  setLibSongsSynced(songVector);
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
    EXEC_SQL(
      "Error setting song to synced",
      setSyncedQuery.exec(
        "UPDATE " + getLibraryTableName() + " " +
        "SET " + getLibSyncStatusColName() + "=" + QString::number(syncStatus) +
        " WHERE "  +
        getLibIdColName() + "=" + QString::number(songs[i]) + ";"),
      setSyncedQuery)
  }
  emit libSongsModified();
}

void DataStore::endEvent(){
  serverConnection->endEvent();
}

void DataStore::setAvailableSongSynced(const library_song_id_t songs){
  std::vector<library_song_id_t> songVector(1,songs);
  setAvailableSongsSynced(songVector);
}

void DataStore::setAvailableSongsSynced(
  const std::vector<library_song_id_t> songs)
{
  setAvailableSongsSyncStatus(songs, getAvailableEntryIsSyncedStatus());
}

void DataStore::setAvailableSongsSyncStatus(
  const std::vector<library_song_id_t> songs,
  const avail_music_sync_status_t syncStatus)
{
  QSqlQuery setSyncedQuery(database);
  for(int i=0; i< songs.size(); ++i){
    DEBUG_MESSAGE("execing sync")
    EXEC_SQL(
      "Error setting song to synced",
      setSyncedQuery.exec(
        "UPDATE " + getAvailableMusicTableName() + " " +
        "SET " + getAvailableEntrySyncStatusColName() + "=" + 
        QString::number(syncStatus) +
        " WHERE "  +
        getAvailableEntryLibIdColName() + "=" + QString::number(songs[i]) + ";"),
      setSyncedQuery)
  }
  emit availableSongsModified();
}

void DataStore::syncAvailableMusic(){
  QSqlQuery getUnsyncedSongs(database);
  EXEC_SQL(
    "Error querying for unsynced songs",
    getUnsyncedSongs.exec(
      "SELECT * FROM " + getAvailableMusicTableName() + " WHERE " + 
      getAvailableEntrySyncStatusColName() + "!=" + 
      QString::number(getAvailableEntryIsSyncedStatus()) + ";"),
    getUnsyncedSongs)

  std::vector<library_song_id_t> toAdd;
  std::vector<library_song_id_t> toDelete;
  while(getUnsyncedSongs.next()){  
    QSqlRecord currentRecord = getUnsyncedSongs.record();
    if(currentRecord.value(getAvailableEntrySyncStatusColName()) == 
      getAvailableEntryNeedsAddSyncStatus())
    {
      toAdd.push_back(currentRecord.value(
        getAvailableEntryLibIdColName()).value<library_song_id_t>());
    }
    else if(currentRecord.value(getLibSyncStatusColName()) ==
      getLibNeedsDeleteSyncStatus())
    {
      toDelete.push_back(currentRecord.value(
        getAvailableEntryLibIdColName()).value<library_song_id_t>());
    }
  }
  if(toAdd.size() > 0){
    serverConnection->addSongsToAvailableSongs(toAdd);
  }
  if(toDelete.size() > 0){
    serverConnection->removeSongsFromAvailableMusic(toDelete);
  }
}

void DataStore::eventCleanUp(){
  QSqlQuery tearDownQuery(database);
  EXEC_SQL(
    "Error deleteing contents of AvailableMusic",
    tearDownQuery.exec(getDeleteAvailableMusicQuery()),
    tearDownQuery
  )
  emit availableSongsModified();
  EXEC_SQL(
    "Error deleteing contents of AvailableMusic",
    tearDownQuery.exec(getClearActivePlaylistQuery()),
    tearDownQuery
  )
  emit activePlaylistModified();
  EXEC_SQL(
    "Error deleteing contents of AvailableMusic",
    tearDownQuery.exec(getDeleteAddRequestsQuery()),
    tearDownQuery
  )
}

void DataStore::clearActivePlaylist(){
  QSqlQuery deleteActivePlayilstQuery(database);
  EXEC_SQL(
    "Error clearing active playlist table.",
    deleteActivePlayilstQuery.exec(getClearActivePlaylistQuery()),
    deleteActivePlayilstQuery)
}

void DataStore::addSong2ActivePlaylistFromQVariant(
  const QVariantMap &songToAdd, int priority)
{
  QSqlQuery addQuery(
    "INSERT INTO "+getActivePlaylistTableName()+ 
    "("+
    getActivePlaylistIdColName() + ","+
    getActivePlaylistLibIdColName() + ","+
    getDownVoteColName() + ","+
    getUpVoteColName() + "," +
    getPriorityColName() + "," +
    getTimeAddedColName() +"," +
    getAdderIdColName() + ")" +
    " VALUES ( :id , :libid , :down , :up, :pri , :time , :adder );", 
    database);
 
  addQuery.bindValue(":id", songToAdd["id"]);
  addQuery.bindValue(":libid", songToAdd["lib_song_id"]);
  addQuery.bindValue(":down", songToAdd["down_votes"]);
  addQuery.bindValue(":up", songToAdd["up_votes"]);
  addQuery.bindValue(":pri", priority);
  addQuery.bindValue(":time", songToAdd["time_added"]);
  addQuery.bindValue(":adder", songToAdd["adder_id"]);

  long insertId;
	EXEC_INSERT(
		"Failed to add song library" << songToAdd["song"].toString().toStdString(),
		addQuery,
    insertId,
    long)
}

void DataStore::setActivePlaylist(const QVariantList newSongs){
  clearActivePlaylist();
  for(int i=0; i<newSongs.size(); ++i){
    addSong2ActivePlaylistFromQVariant(newSongs[i].toMap(), i); 
  }
  emit activePlaylistModified();
}

void DataStore::refreshActivePlaylist(){
  serverConnection->getActivePlaylist();
}

void DataStore::syncPlaylistAddRequests(){
  QSqlQuery needsSyncQuery(database);
	EXEC_SQL(
		"Error getting add requests that need syncing", 
		needsSyncQuery.exec("SELECT * FROM " + getPlaylistAddRequestsTableName() +
      " where " + getPlaylistAddSycnStatusColName() + " = " +
      QString::number(getPlaylistAddNeedsSync()) + ";"
     ), 
		needsSyncQuery)	
  if(!needsSyncQuery.isActive()){
    //TODO handle error here
    return;
  }
  std::vector<library_song_id_t> songIds;
  std::vector<client_request_id_t> requestIds;
  while(needsSyncQuery.next()){
    songIds.push_back(needsSyncQuery.record().value(
      getPlaylistAddLibIdColName()).value<library_song_id_t>());
    requestIds.push_back(needsSyncQuery.record().value(
      getPlaylistAddIdColName()).value<client_request_id_t>());
  }
  serverConnection->addSongsToActivePlaylist(requestIds, songIds);
}

void DataStore::setPlaylistAddRequestsSynced(
  const std::vector<client_request_id_t> requestIds)
{
  QVariantList toUpdate;
  for(
    std::vector<client_request_id_t>::const_iterator it= requestIds.begin();
    it!=requestIds.end();
    ++it)
  {
    toUpdate << QVariant::fromValue<client_request_id_t>(*it);
  }
  QSqlQuery needsSyncQuery(database);
  needsSyncQuery.prepare(
    "UPDATE " + getPlaylistAddRequestsTableName() +  
    " SET " + getPlaylistAddSycnStatusColName() + " = " +
    QString::number(getPlaylistAddIsSynced()) + " where " +
    getPlaylistAddIdColName() + " = ? ;");
  needsSyncQuery.addBindValue(toUpdate);
  EXEC_BULK_QUERY(
    "Error setting active playlist add requests as synced" << std::endl <<
    "vector size was: " << requestIds.size(),
    needsSyncQuery)
  refreshActivePlaylist();  
}

} //end namespace
