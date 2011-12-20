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
#include <QDateTime>
#include <QObject>
#include <vector>
#include <QNetworkRequest>

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
   * \brief Retrieves the id of the event associated with this server 
   * connection.
   *
   * @return The id of the event this connection is associated with.
   */
	inline event_id_t  getEventId(){
    //TODO really need to save this to persistent storage
		return eventId;
	}

  inline bool getIsHosting(){
    return isHostingEvent;
  }

  //@}

  /** @name Modifiers */
  //@{
	
public slots:

  void addLibSongOnServer(
		const QString& songName,
		const QString& artistName,
		const QString& ablumName,
    const int duration,
    const library_song_id_t hostid);

  void deleteLibSongOnServer(library_song_id_t toDeleteId);

  void addSongToAvailableSongs(library_song_id_t songToAdd);
  void addSongsToAvailableSongs(
    const std::vector<library_song_id_t>& songsToAdd);

  void createEvent(
    const QString& partyName,
    const QString& password);

  void endEvent();

  void getActivePlaylist();

  void addSongToActivePlaylist(
    client_request_id_t requestId, 
    library_song_id_t songId);

  void addSongsToActivePlaylist(
    const std::vector<client_request_id_t>& requestIds, 
    const std::vector<library_song_id_t>& songIds);

  void setCurrentSong(playlist_song_id_t currentSong);

  //@}

signals:

  /** @name Signals */
  //@{

  void connectionEstablished();
  
  void unableToConnect(const QString errMessage);

  void songsAddedToLibOnServer(const std::vector<library_song_id_t> addedIds);

  void songDeletedFromLibOnServer(
    const library_song_id_t deletedId);

  void eventCreated();

  void eventCreationFailed(const QString errMessage);

  void eventEnded();

  void eventEndingFailed(const QString errMessage);

  void songsAddedToAvailableMusic(
    const std::vector<library_song_id_t> songAdded);

  void newActivePlaylist(const QVariantList newPlaylist);

  void songsAddedToActivePlaylist(const std::vector<client_request_id_t> ids);

  void currentSongSet();

  void currentSongSetError();

  //@}


private slots:
  void recievedReply(QNetworkReply *reply);


private:
  /** @name Private Members */
  //@{

  bool isLoggedIn;
  bool isHostingEvent;
  

  /** \brief Id of the event associated with this conneciton */
  event_id_t eventId;

  QNetworkAccessManager *netAccessManager;

  QByteArray ticket_hash;
  user_id_t  user_id;

  QDateTime timeTicketIssued;

  void setLoggedIn(QByteArray ticket, QByteArray userId);

  void prepareJSONRequest(QNetworkRequest &request);


  //@}

  /** @name Private Function */
  //@{

  QUrl getLibAddSongUrl() const;

  QUrl getLibDeleteSongUrl(library_song_id_t toDelete) const;

  QUrl getAddSongToAvailableUrl() const;

  QUrl getEndEventUrl() const;

  QUrl getActivePlaylistUrl() const;

  QUrl getActivePlaylistAddUrl() const;

  QUrl getCurrentSongUrl() const;

  bool isLibDeleteUrl(QString path) const;

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
      "http://localhost:" + getServerPortNumber() + "/udj/";
    return SERVER_URL_PATH;
  }

  static const QUrl& getServerUrl(){
    static const QUrl SERVER_URL(getServerUrlPath());
    return SERVER_URL;
  }
  
  static const QUrl& getAuthUrl(){
    static const QUrl AUTH_URL(getServerUrlPath() + "auth");
    return AUTH_URL;
  }

  static const QUrl& getCreateEventUrl(){
    static const QUrl CREAT_EVENT_URL(getServerUrlPath() + "events/event");
    return CREAT_EVENT_URL;
  }


  static const QByteArray& getAPIVersionHeaderName(){
    static const QByteArray API_VERSION_HEAER_NAME = "X-Udj-Api-Version";
    return API_VERSION_HEAER_NAME;
  }

  static const QByteArray& getAPIVersion(){
    static const QByteArray API_VERSION = "0.2";
    return API_VERSION;
  }

  static const QByteArray& getTicketHeaderName(){
    static const QByteArray ticketHeaderName = "X-Udj-Ticket-Hash";
    return ticketHeaderName;
  }

  static const QByteArray& getUserIdHeaderName(){
    static const QByteArray userIdHeaderName = "X-Udj-User-Id";
    return userIdHeaderName;
  }

  static const char* getActivePlaylistRequestIdsPropertyName(){
    static const char* activePlaylistRequestIdsPropertyName = "request_ids";
    return activePlaylistRequestIdsPropertyName;
  }


  void authenticate(const QString& username, const QString& password);

  void handleAuthReply(QNetworkReply* reply);

  void handleAddLibSongsReply(QNetworkReply *reply);

  void handleDeleteLibSongsReply(QNetworkReply *reply);

  void handleCreateEventReply(QNetworkReply *reply);

  void handleEndEventReply(QNetworkReply *reply);

  void handleAddAvailableSongReply(QNetworkReply *reply);

  void handleRecievedActivePlaylist(QNetworkReply *reply);

  void handleRecievedActivePlaylistAdd(QNetworkReply *reply);

  void handleRecievedCurrentSongSet(QNetworkReply *reply);

  //@}



};


} //end namespace
#endif //UDJ_SERVER_CONNECTION_HPP
