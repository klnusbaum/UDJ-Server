#include "UDJServerConnection.hpp"
#include <QDesktopServices>
#include <QDir>
#include <QSqlQuery>
#include <QVariant>

namespace UDJ{


UDJServerConnection::UDJServerConnection(){

}

UDJServerConnection::~UDJServerConnection(){
	musicdb.close();
}

void UDJServerConnection::startConnection(){
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
	EXEC_SQL(
		"Error adding this party to the party table.",
		setupQuery.exec("INSERT INTO parties (name) VALUES ( 'defaultParty' );"),
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
		"Error inserting partier 1",
		setupQuery.exec("INSERT INTO users (first_name, last_name, "
		"gender, birthday, inParty, hostingParty, currentParty) VALUES ("
		"'kurtis', 'nusbaum', 'male', '24/07/1989', 1, 0, " + QString::number(partyId) + ");"),
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
		"Error creating library table", 
		setupQuery.exec("CREATE TABLE IF NOT EXISTS library "
    "(id INTEGER PRIMARY KEY AUTOINCREMENT, "
   	"song TEXT NOT NULL, artist TEXT, album TEXT, filePath TEXT);"), 
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

bool UDJServerConnection::clearMyLibrary(){
  QSqlQuery workQuery(musicdb);
  workQuery.exec("DROP TABLE library");
  workQuery.exec("CREATE TABLE IF NOT EXISTS library "
  "(id INTEGER PRIMARY KEY AUTOINCREMENT, "
  "song TEXT NOT NULL, artist TEXT, album TEXT, filePath TEXT)");  
}

bool UDJServerConnection::addSongToLibrary(
	const QString& songName,
	const QString& artistName,
	const QString& albumName,
	const QString& filePath)
{

  QSqlQuery addQuery("INSERT INTO library "
    "(song, artist, album, filePath) VALUES ( ?, ?, ?, ?)", musicdb);
  
  addQuery.addBindValue(songName);
  addQuery.addBindValue(artistName);
  addQuery.addBindValue(albumName);
  addQuery.addBindValue(filePath);
	EXEC_SQL(
		"Failed to add song " << songName.toStdString(), 
		addQuery.exec(), 
		addQuery)
	//TODO this should be based on what the above query returns.
	return true;
}

bool UDJServerConnection::incrementVoteCount(playlistid_t plId, int difference){

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
		"WHERE plId =  ? ;", musicdb);
	removeQuery.addBindValue(QVariant::fromValue(plId));
	
	EXEC_SQL(
		"Remove from playlist failed", 
		removeQuery.exec(),
		removeQuery)
	//TODO this value should be based on above result
	return true;
}

}//end namespace
