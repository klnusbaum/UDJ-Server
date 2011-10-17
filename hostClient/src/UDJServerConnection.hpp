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
   * \brief Retrieves the id of the party associated with this server 
   * connection.
   *
   * @return The id of the party this connection is associated with.
   */
	inline partyid_t  getPartyId(){
		return partyId;
	}

  //@}

  /** @name Modifiers */
  //@{
	
  /**
   * \brief Removes all songs from the library associated with this conneciton.
   *
   * @return True if the clearing of the library was sucessful, false otherwise.
   */
	bool clearMyLibrary();
	

  void addLibSongOnServer(
		const QString& songName,
		const QString& artistName,
		const QString& ablumName,
    const library_song_id_t hostid);

  void createNewParty(
    const QString& name,
    const QString& password,
    const QString& location);


  //@}

signals:

  /** @name Signals */
  //@{

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
	void songAddedToMainPlaylist(library_song_id_t libraryId);
  
  /**
   * \brief Emitted when the vote count for song in the playlist is changed.
   *
   * @param  playlistId Id of the song in the playlist whose vote count was
   * changed.
   */
	void voteCountChanged(playlist_song_id_t playlistId);

  void connectionEstablished();
  
  void unableToConnect(const QString& errMessage);

  void serverIdsUpdate(const std::map<library_song_id_t, library_song_id_t> 
    hostToServerIdMap);

  void partyCreated();
  //@}


private slots:
  void recievedReply(QNetworkReply *reply);

private:
  /** @name Private Members */
  //@{

  bool isLoggedIn;

  /** \brief Id of the party associated with this conneciton */
	partyid_t partyId;

  QNetworkAccessManager *netAccessManager;

  QNetworkCookieJar *cookieJar;


  //@}

  /** @name Private Function */
  //@{

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


  void authenticate(const QString& username, const QString& password);

  void handleAuthReply(QNetworkReply* reply);
 
  bool haveValidLoginCookie();

  void handleAddSongReply(QNetworkReply *reply);


  //@}



};


} //end namespace
#endif //UDJ_SERVER_CONNECTION_HPP
