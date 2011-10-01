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
#include <QDesktopServices>
#include <QDir>
#include <QSqlQuery>
#include <QVariant>
#include <QNetworkAccessManager>
#include <QNetworkCookieJar>
#include <QNetworkRequest>
#include <QNetworkReply>
#include <QBuffer>
#include "MusicLibrary.hpp"
#include "UDJServerConnection.hpp"
#include "JSONHelper.hpp"

namespace UDJ{

UDJServerConnection::UDJServerConnection(QObject *parent):QObject(parent){
  netAccessManager = new QNetworkAccessManager(this);
  cookieJar = netAccessManager->cookieJar();
  connect(netAccessManager, SIGNAL(finished(QNetworkReply*)),
    this, SLOT(recievedReply(QNetworkReply*)));
}

UDJServerConnection::~UDJServerConnection(){
	musicdb.close();
}

void UDJServerConnection::startConnection(
  const QString& username,
  const QString& password
)
{

  //TODO do all of this stuff in a seperate thread and return right away.
  QDir dbDir(QDesktopServices::storageLocation(QDesktopServices::DataLocation));  
  if(!dbDir.exists()){
    //TODO handle if this fails
    dbDir.mkpath(dbDir.absolutePath());
  }
  musicdb = QSqlDatabase::addDatabase("QSQLITE", getMusicDBConnectionName());
  musicdb.setDatabaseName(dbDir.absoluteFilePath(getMusicDBName()));
  musicdb.open(); 

  QSqlQuery setupQuery(musicdb);

	EXEC_SQL(
		"Error creating party table",
		setupQuery.exec("CREATE TABLE IF NOT EXISTS parties "
		"(id INTEGER PRIMARY KEY AUTOINCREMENT, "
		"name TEXT NOT NULL);"),
		setupQuery)

	setupQuery.exec("select id from parties where name='defaultParty'");
	setupQuery.next();
	partyId = setupQuery.value(0).value<partyid_t>();
	
	//TODO enforce currentParty refering to a party in the party table
	EXEC_SQL(
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
		setupQuery)
	

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
  authenticate(username, password);
}

bool UDJServerConnection::clearMyLibrary(){
  QSqlQuery workQuery(musicdb);
  workQuery.exec("DROP TABLE library");
  workQuery.exec(getCreateLibraryQuery());  
}

bool UDJServerConnection::addSongToLibrary(
	const QString& songName,
	const QString& artistName,
	const QString& albumName,
	const QString& filePath)
{
  libraryid_t hostid = 
    addSongToLocalDB(songName, artistName, albumName, filePath);
  if(hostid == MusicLibrary::getInvalidHostId()){
    return false;
  }
  addSongOnServer(songName, artistName, albumName, hostid);
  return true;
}

libraryid_t UDJServerConnection::addSongToLocalDB(
	const QString& songName,
	const QString& artistName,
	const QString& albumName,
	const QString& filePath)
{
  libraryid_t toReturn = MusicLibrary::getInvalidHostId();
  QSqlQuery addQuery("INSERT INTO library "
    "(song, artist, album, filePath) VALUES ( ?, ?, ?, ?)", musicdb);
  
  addQuery.addBindValue(songName);
  addQuery.addBindValue(artistName);
  addQuery.addBindValue(albumName);
  addQuery.addBindValue(filePath);
	EXEC_INSERT(
		"Failed to add song " << songName.toStdString(), 
		addQuery,
    toReturn)
	//TODO this should be based on what the above query returns.
	return toReturn;
}

void UDJServerConnection::addSongOnServer(
	const QString& songName,
	const QString& artistName,
	const QString& albumName,
	const libraryid_t hostId)
{
  bool success = true;

  const QByteArray songJSON = JSONHelper::getLibraryEntryJSON(
    songName, 
    artistName,
    albumName,
    hostId,
    false, 
    success);
  const QByteArray finalData = "to_add="+songJSON;
  QNetworkRequest addSongRequest(getLibAddSongUrl());
  netAccessManager->post(addSongRequest, finalData);
  std::cout << "Just posted add\n";
}

bool UDJServerConnection::alterVoteCount(playlistid_t plId, int difference){

	QSqlQuery updateQuery(
		"UPDATE main_playlist_view "
		"SET voteCount = (voteCount + ?) "
		"WHERE plId = ? ", 
		musicdb);
	updateQuery.addBindValue(difference);
	updateQuery.addBindValue(QVariant::fromValue(plId));
	EXEC_SQL(
		"Updating vote count didn't work!", 
		updateQuery.exec(), 
		updateQuery);
	//TODO return value should be based on success of above query.
	return true;
}

bool UDJServerConnection::addSongToPlaylist(libraryid_t libraryId){
	QSqlQuery insertQuery("INSERT INTO " + getMainPlaylistTableName() +" "
		"(libraryId) VALUES ( ? );", musicdb);
	insertQuery.addBindValue(QVariant::fromValue(libraryId));
	
	EXEC_SQL(
		"Adding to playlist failed", 
		insertQuery.exec(),
		insertQuery)
	//TODO this value should instead be based on the result of the
	//above sql query.
	return true;
}

bool UDJServerConnection::removeSongFromPlaylist(playlistid_t plId){
	QSqlQuery removeQuery("DELETE FROM " + getMainPlaylistTableName() + " "
		"WHERE plId = ? ;", musicdb);
	removeQuery.addBindValue(QVariant::fromValue(plId));
	
	EXEC_SQL(
		"Remove from playlist failed", 
		removeQuery.exec(),
		removeQuery)
	//TODO this value should be based on above result
	return true;
}

bool UDJServerConnection::kickUser(partierid_t toKick){
	QSqlQuery removeQuery("DELETE FROM " + getPartiersTableName() + " "
		"WHERE id = ? ;", musicdb);
	removeQuery.addBindValue(QVariant::fromValue(toKick));
	EXEC_SQL(
		"Kicking partier failed", 
		removeQuery.exec(),
		removeQuery)
	//TODO this value should be based on above result
	return true;
	
}

void UDJServerConnection::authenticate(
  const QString& username, 
  const QString& password)
{
  QNetworkRequest authRequest(getAuthUrl());
  QString data("username="+username+"&password="+password);
  QBuffer *dataBuffer = new QBuffer();
  dataBuffer->setData(data.toUtf8());
  QNetworkReply *reply = netAccessManager->post(authRequest, dataBuffer);
  dataBuffer->setParent(reply);
  std::cout << "Just posted request\n";
}
 
void UDJServerConnection::recievedReply(QNetworkReply *reply){
  std::cout << "Just reieved reply\n";
  if(reply->request().url().path() == getAuthUrl().path()){
    handleAuthReply(reply);
  }
  else if(reply->request().url().path() == getLibAddSongUrl().path()){
    handleAddSongReply(reply);
  }
  reply->deleteLater();
}

void UDJServerConnection::handleAuthReply(QNetworkReply* reply){
  if(haveValidLoginCookie()){
    emit connectionEstablished();
  }
  else{
    emit unableToConnect("Bad username and password");
  }
}

bool UDJServerConnection::haveValidLoginCookie(){
  QList<QNetworkCookie> authCookies = cookieJar->cookiesForUrl(getAuthUrl());
  for(int i =0; i<authCookies.size(); ++i){
    if(authCookies.at(i).name() == getLoginCookieName()){
      return true;
    }
  }
  return false;
}

void UDJServerConnection::handleAddSongReply(QNetworkReply *reply){
  std::map<libraryid_t, libraryid_t> hostToServerIdMap =
    JSONHelper::getHostToServerLibIdMap(reply);
  updateServerIds(hostToServerIdMap); 
}

void UDJServerConnection::updateServerIds(
  const std::map<libraryid_t, libraryid_t>& hostToServerIdMap)
{
  QSqlQuery updateQuery(musicdb);
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
    std::cout << "about to update with " << it->second << " and " << it->first
      << std::endl;
	  updateQuery.bindValue(0, QVariant::fromValue<libraryid_t>(it->second));
	  updateQuery.bindValue(1, QVariant::fromValue<libraryid_t>(it->first));
    std::cout << "0: " << updateQuery.boundValue(0).toString().toStdString() <<
      " 1: " << updateQuery.boundValue(1).toString().toStdString() << std::endl;
	  EXEC_SQL(
		  "Updating server id didn't work!", 
		  updateQuery.exec(), 
		  updateQuery);
   
  }
}


}//end namespace
