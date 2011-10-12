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
#ifndef UDJ_SERVER_CONNECTION_HPP
#define UDJ_SERVER_CONNECTION_HPP

#include "ConfigDefs.hpp"
#include <QSqlDatabase>
#include <QObject>
#include <map>

class QNetworkAccessManager;
class QNetworkReply;
class QNetworkCookieJar;

namespace UDJ{


/**
 * Set's up a connectin to the UDJ server and facilitates all communication.
 * with the server.
 */
class UDJServerConnection : public QObject{
Q_OBJECT
public:
  /** @name Constructor(s) and Destructor */
  //@{

  /**
   * \brief Constructs a UDJServerConnection.
   */
	UDJServerConnection(QObject *parent=NULL);
  /**
   * \brief Constructs all necessary clean up when deallocating the
   * UDJServerConnection.
   */
	~UDJServerConnection();

  //@}

  /** @name Connection Controlls */
  //@{

  /**
   * \brief Starts the connection to the server.
   */
	void startConnection(const QString& username, const QString& password);

  //@}

  /** \brief Connection Query Functions */
  //@{

  /**
   * \brief Retrieves the database stoing all the music information.
   *
   * @return The database storing all music information.
   */
	inline QSqlDatabase getMusicDB(){
		return musicdb;
	}	

  /**
   * \brief Retrieves the id of the party associated with this server 
   * connection.
   *
   * @return The id of the party this connection is associated with.
   */
	inline partyid_t  getPartyId(){
		return partyId;
	}

  /**
   * \brief Gets the name of the table in the musicdb that contains information
   * about the music library associated with the server conneciton.
   *
   * @return The name of the table in the musicdb that contains information
   * about the music library associated with the server connection.
   */
	static const QString& getLibraryTableName(){
    static const QString libraryTableName = "library";
    return libraryTableName;
	}

  /**
   * \brief Gets the name of the table in the musicdb that contains information
   * about the playlist associated with the server conneciton.
   *
   * @return The name of the table in the musicdb that contains information
   * about the playlist associated with the server connection.
   */
	inline QString getMainPlaylistTableName(){
		return "main_playlist_view";
	}

  /**
   * \brief Gets the name of the table in the musicdb that contains information
   * about the partiers associated with the server conneciton.
   *
   * @return The name of the table in the musicdb that contains information
   * about the partiers associated with the server connection.
   */
	inline QString getPartiersTableName(){
		return "my_partiers";
	}

  //@}

  /** @name Modifiers */
  //@{
  /**
   * \brief Adds a song to the library associated with this server connection.
   *
   * @param songName Name of the song to be added to the library.
   * @param artistName Name of the artist of the song to be added to the
   * the library.
   * @param albumName The name of the album of the song to be added to the
   * library.
   * @param filePath The filePath of the song to be added to the library.
   * @return True if the song was sucessfully added, false otherwise.
   */
	bool addSongToLibrary(
		const QString& songName,
		const QString& artistName,
		const QString& ablumName,
		const QString& filePath);
	
  /**
   * \brief Removes all songs from the library associated with this conneciton.
   *
   * @return True if the clearing of the library was sucessful, false otherwise.
   */
	bool clearMyLibrary();
	
  /**
   * \brief Alters the vote count associated with a specific song.
   *
   * @param plId Id of the song whose vote count is to be altered.
   * @param difference The amount by which the vote count should be altered.
   * @return True if the altering was sucessful, false otherwise.
   */
	bool alterVoteCount(playlistid_t plId, int difference);

  /**
   * \brief Adds the specified song to the playlist.
   *
   * @param libraryId Id of the song to add to the playlist.
   * @return True if the addition of the song was sucessful, false otherwise.
   */
	bool addSongToPlaylist(playlistid_t libraryId);

  /**
   * \brief Removes the specified song from the playlist.
   *
   * @param libraryId Id of the song to remove the playlist.
   * @return True if the removal of the song was sucessful, false otherwise.
   */
	bool removeSongFromPlaylist(playlistid_t plId);

  /**
   * Kicks the given user from the party associated with this connection.
   *
   * @param toKick The id of the partier to kick.
   * @return True if kicking the partier was successful, false otherwise.
   */
	bool kickUser(partierid_t toKick);


  //@}

signals:

  /**
   * \brief Emitted when a partier leaves.
   *
   * @param partierId Id of the partier who left.
   */
	void partierLeft(partierid_t partierId);

  /**
   * \brief Emitted when a partier joins the party.
   *
   * @param partierId Id of the partier who joined.
   */
	void partierJoined(partierid_t partierId);

  /**
   * \brief Emitted when a song is added to the main playlist.
   *
   * @param libraryId Library id of the song added to the playlist.
   */
	void songAddedToMainPlaylist(libraryid_t libraryId);
  
  /**
   * \brief Emitted when the vote count for song in the playlist is changed.
   *
   * @param  playlistId Id of the song in the playlist whose vote count was
   * changed.
   */
	void voteCountChanged(playlistid_t playlistId);

  void connectionEstablished();
  
  void unableToConnect(const QString& errMessage);

  //@}

private slots:
  void recievedReply(QNetworkReply *reply);

private:
  /** @name Private Members */
  //@{

  /** \brief The database containing all the information associated with this 
   * server connection
   */
	QSqlDatabase musicdb;
  
  /** \brief Id of the party associated with this conneciton */
	partyid_t partyId;

  QNetworkAccessManager *netAccessManager;

  QNetworkCookieJar *cookieJar;

  //@}

  /** @name Private Function */
  //@{

  /**
   * \brief Retrieves the name of the connection to the musicdb.
   *
   * @return The name of the connection to the musicdb.
   */
  static const QString& getMusicDBConnectionName(){
    static const QString musicDBConnectionName("musicdbConn");
    return musicDBConnectionName;
  }

  /**
   * \brief Retrieves the name of the music database.
   *
   * @return The name of the the music database.
   */
  static const QString& getMusicDBName(){
    static const QString musicDBName("musicdb");
    return musicDBName;
  }

  static const QString& getLoginCookieName(){
    static const QString loginCookieName("loggedIn");
    return loginCookieName;
  }

  static const QString & getServerPortNumber(){
    /** 
     * This port number is a memorial to Keith Nusbaum, my father. I loved him
     * deeply and he was taken from this world far too soon. Never-the-less 
     * we all continue to benefit from his good deeds. Without him, I wouldn't 
     * be here, and there would be no UDJ. Please, don't change this port 
     * number. Keep the memory of my father alive.
     * K = 10 % 10 = 0
     * e = 4  % 10 = 4
     * i = 8  % 10 = 8
     * t = 19 % 10 = 9
     * h = 7  % 10 = 7
     * Port 4897, the Keith Nusbaum Memorial Port
     */
    static const QString serverPortNumber = "4897";
    return serverPortNumber;

  }
  
  static const QString& getServerUrlPath(){
    static const QString SERVER_URL_PATH= 
      "http://0.0.0.0:" + getServerPortNumber();
    return SERVER_URL_PATH;
  }

  static const QUrl& getServerUrl(){
    static const QUrl SERVER_URL(getServerUrlPath());
    return SERVER_URL;
  }
  
  static const QUrl& getAuthUrl(){
    static const QUrl AUTH_URL(getServerUrlPath() + "/auth");
    return AUTH_URL;
  }

  static const QUrl& getLibAddSongUrl(){
    static const QUrl LIB_ADD_URL(getServerUrlPath() + "/library");
    return LIB_ADD_URL;
  }

  static const QString& getCreateLibraryQuery(){
    static const QString createLibQuerey = "CREATE TABLE IF NOT EXISTS " + getLibraryTableName() +
    "(id INTEGER PRIMARY KEY AUTOINCREMENT, "
    "server_lib_id INTEGER DEFAULT -1, "
   	"song TEXT NOT NULL, artist TEXT, album TEXT, filePath TEXT);";
    return createLibQuerey;

  }

  void authenticate(const QString& username, const QString& password);

  void handleAuthReply(QNetworkReply* reply);
 
  bool haveValidLoginCookie();

  libraryid_t addSongToLocalDB(
		const QString& songName,
		const QString& artistName,
		const QString& ablumName,
		const QString& filePath);

  void addSongOnServer(
		const QString& songName,
		const QString& artistName,
		const QString& ablumName,
    const libraryid_t hostid);

  void handleAddSongReply(QNetworkReply *reply);

  void updateServerIds(
    const std::map<libraryid_t, libraryid_t>& hostToServerIdMap);

  //@}



};


} //end namespace
#endif //UDJ_SERVER_CONNECTION_HPP
