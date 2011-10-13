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
    SIGNAL(serverIdsUpdate(const std::map<libraryid_t, libraryid_t>)),
    this,
    SLOT(updateServerIds(const std::map<libraryid_t, libraryid_t>)));
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

	/*EXEC_SQL(
		"Error creating party table",
		setupQuery.exec("CREATE TABLE IF NOT EXISTS parties "
		"(id INTEGER PRIMARY KEY AUTOINCREMENT, "
		"name TEXT NOT NULL);"),
		setupQuery)*/

	/*setupQuery.exec("select id from parties where name='defaultParty'");
	setupQuery.next();
	partyId = setupQuery.value(0).value<partyid_t>();*/
	
	//TODO enforce currentParty refering to a party in the party table
	/*EXEC_SQL(
		"Error creating users table",
		setupQuery.exec("CREATE TABLE IF NOT EXISTS users "
		"(id INTEGER PRIMARY KEY AUTOINCREMENT, "
		"first_name TEXT NOT NULL, "
		"last_name TEXT NOT NULL, "
		"gender TEXT NOT NULL, "
		"birthday TEXT, "
		"inParty INTEGER CHECK (inParty = 0 OR inParty = 1), "
		"hostingParty INTEGER CHECK (hostingParty = 0 OR hostingParty = 1), "
		"currentParty INTEGER);"),
		setupQuery)


	EXEC_SQL(
		"Error creating partiers view",
  	setupQuery.exec("CREATE VIEW IF NOT EXISTS my_partiers "
    "AS SELECT "
    "id, "
		"first_name "
    "FROM users where currentParty = " +QString::number(partyId) +";"),
		setupQuery)

	EXEC_SQL(
		"Error creating delete trigger for kicking partiers.",
		setupQuery.exec("CREATE TRIGGER IF NOT EXISTS kickPartier "
		"INSTEAD OF DELETE ON my_partiers "
		"BEGIN "
		"UPDATE users SET inParty=0, currentParty=-1 "
		"where users.id = old.id; "
		"END;"),
		setupQuery)*/
	

	EXEC_SQL(
		"Error creating library table", 
		setupQuery.exec(getCreateLibraryQuery()), 
		setupQuery)	

	EXEC_SQL(
		"Error creating mainplaylist table.", 
		setupQuery.exec("CREATE TABLE IF NOT EXISTS mainplaylist "
   	"(id INTEGER PRIMARY KEY AUTOINCREMENT, "
   	"libraryId INTEGER REFERENCES library (id) ON DELETE CASCADE, "
   	"voteCount INTEGER DEFAULT 1, "
   	"timeAdded TEXT DEFAULT CURRENT_TIMESTAMP);"),
		setupQuery)	

	EXEC_SQL(
		"Error creating main_playlist_view view.",
  	setupQuery.exec("CREATE VIEW IF NOT EXISTS main_playlist_view "
    "AS SELECT "
    "mainplaylist.id AS plId, "
    "mainplaylist.libraryId AS libraryId, "
    "library.server_lib_id AS server_lib_id, "
    "library.song AS song, "
    "library.artist AS artist, "
    "library.album AS album, "
    "library.filePath AS filePath, "
    "mainplaylist.voteCount AS voteCount, "
    "mainplaylist.timeAdded AS timeAdded "
    "FROM mainplaylist INNER JOIN library ON "
    "mainplaylist.libraryId = library.id ORDER BY mainplaylist.voteCount DESC, mainplaylist.timeAdded;"),
		setupQuery)

	EXEC_SQL(
		"Error creating update trigger for main_playlist_view.",
  	setupQuery.exec("CREATE TRIGGER IF NOT EXISTS updateVotes INSTEAD OF "
    "UPDATE ON main_playlist_view BEGIN "
    "UPDATE mainplaylist SET voteCount=new.voteCount "
    "WHERE  mainplaylist.id = old.plId;"
    "END;"),
		setupQuery)

	EXEC_SQL(
		"Error creating delete trigger for main_playlist_view.",
		setupQuery.exec("CREATE TRIGGER IF NOT EXISTS deleteSongFromPlaylist "
		"INSTEAD OF DELETE ON main_playlist_view "
		"BEGIN "
		"DELETE FROM mainplaylist "
		"where mainplaylist.id = old.plId; "
		"END;"),
		setupQuery)

	EXEC_SQL(
		"Error creating insert trigger for main_playlist_view.",
  	setupQuery.exec("CREATE TRIGGER IF NOT EXISTS insertOnPlaylist INSTEAD OF "
    "INSERT ON main_playlist_view BEGIN "
    "INSERT INTO mainplaylist "
    "(libraryId) VALUES (new.libraryId);"
    "END;"),
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

  libraryid_t hostId = MusicLibrary::getInvalidHostId();
  QSqlQuery addQuery("INSERT INTO library "
    "(song, artist, album, filePath) VALUES ( ?, ?, ?, ?)", database);
  
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
  const std::map<libraryid_t, libraryid_t> hostToServerIdMap)
{
  QSqlQuery updateQuery(database);
	updateQuery.prepare(
		"UPDATE library "
		"SET server_lib_id = ? "
		"WHERE id = ? ;"
		);
  for(
    std::map<libraryid_t, libraryid_t>::const_iterator it = 
      hostToServerIdMap.begin();
    it != hostToServerIdMap.end();
    ++it
  )
  { 
    //std::cout << "about to update with " << it->second << " and " << it->first
      //<< std::endl;
	  updateQuery.bindValue(0, QVariant::fromValue<libraryid_t>(it->second));
	  updateQuery.bindValue(1, QVariant::fromValue<libraryid_t>(it->first));
    //std::cout << "0: " << updateQuery.boundValue(0).toString().toStdString() <<
      //" 1: " << updateQuery.boundValue(1).toString().toStdString() << std::endl;
	  EXEC_SQL(
		  "Updating server id didn't work!", 
		  updateQuery.exec(), 
		  updateQuery);
   
  }
}

bool MusicLibrary::alterVoteCount(playlistid_t plId, int difference){
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

bool MusicLibrary::addSongToPlaylist(libraryid_t libraryId){
	QSqlQuery insertQuery("INSERT INTO " + getMainPlaylistTableName() +" "
		"(libraryId) VALUES ( ? );", database);
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

bool MusicLibrary::removeSongFromPlaylist(playlistid_t plId){
	QSqlQuery removeQuery("DELETE FROM " + getMainPlaylistTableName() + " "
		"WHERE plId = ? ;", database);
	removeQuery.addBindValue(QVariant::fromValue(plId));
	
	EXEC_SQL(
		"Remove from playlist failed", 
		removeQuery.exec(),
		removeQuery)
	//TODO this value should be based on above result
  //TODO inform the server of the song being removed from the playlist
	return true;
}

bool MusicLibrary::kickUser(partierid_t toKick){
	QSqlQuery removeQuery("DELETE FROM " + getPartiersTableName() + " "
		"WHERE id = ? ;", database);
	removeQuery.addBindValue(QVariant::fromValue(toKick));
	EXEC_SQL(
		"Kicking partier failed", 
		removeQuery.exec(),
		removeQuery)
	//TODO this value should be based on above result
  //TODO inform the server of the user being kicked
	return true;
	
}

QSqlDatabase MusicLibrary::getDatabaseConnection(){
  return database;
}


} //end namespace
