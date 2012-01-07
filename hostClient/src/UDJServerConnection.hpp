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
 * Set's up a connection to the UDJ server and facilitates all communication.
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

  /**
   * \brief Get's whether or not the user is currenlty hosting an event.
   *
   * @return True if the user is currently hosting an event. False otherwise.
   */
  inline bool getIsHosting(){
    return isHostingEvent;
  }

  //@}

public slots:

  /** @name Slots */
  //@{
	
  /**
   * \brief Adds a song to the library on the server.
   *
   * @param songName The name of the song.
   * @param artistName The name of the artist.
   * @param albumName The name of the album.
   * @param duration The length of the song in seconds.
   * @param hostid The id of the song on the host.
   */
  void addLibSongOnServer(
		const QString& songName,
		const QString& artistName,
		const QString& albumName,
    const int duration,
    const library_song_id_t hostid);

  /**
   * \brief Deletes a song from the library on the server.
   *
   * @param toDeleteId The host id of the song to delete from the library on the
   * server.
   */
  void deleteLibSongOnServer(library_song_id_t toDeleteId);

  /**
   * \brief Adds a given song to the list of available songs for an event on the
   * server.
   *
   * @param songToAdd Song to add to the list of available songs for an event
   * on the server.
   */
  void addSongToAvailableSongs(library_song_id_t songToAdd);

  /**
   * \brief Adds the given songs to the list of available songs for an event 
   * on the server.
   *
   * @param songsToAdd The songs to add to the list of available songs for an 
   * event on the server.
   */
  void addSongsToAvailableSongs(
    const std::vector<library_song_id_t>& songsToAdd);

  /**
   * \brief Remove the given songs from the list of available songs for an event
   * on the server.
   *
   * @param songsToRemove The songs to remove from the list of available 
   * songs for an event on the server.
   */
  void removeSongsFromAvailableMusic(
    const std::vector<library_song_id_t>& songsToRemove);

  /**
   * \brief Creates an event on the server.
   *
   * @param eventName The name of the event.
   * @param password The password of the event.
   */
  void createEvent(
    const QString& eventName,
    const QString& password);

  /**
   * \brief Ends the current event.
   */
  void endEvent();

  /**
   * \brief Retrieves the latest version of the active playlist from the server.
   */
  void getActivePlaylist();

  /**
   * \brief Adds the given song to the active playlist on the server.
   *
   * @param requestId The request id of this add request.
   * @param songId Id of the song to be added to the active playlist.
   */
  void addSongToActivePlaylist(
    client_request_id_t requestId, 
    library_song_id_t songId);

  /**
   * \brief Adds the given songs to the active playlist on the server.
   *
   * @param requestIds The request ids of this add request.
   * @param songIds Ids of the songs to be added to the active playlist.
   */
  void addSongsToActivePlaylist(
    const std::vector<client_request_id_t>& requestIds, 
    const std::vector<library_song_id_t>& songIds);

  /**
   * \brief Removes the given songs from the active playlist on the server.
   * 
   * @param playlistIds The ids of the playlist entries that should be remove.
   */
  void removeSongsFromActivePlaylist(
    const std::vector<playlist_song_id_t>& playlistIds);

  /**
   * \brief Set's the current song that the host is playing on the server.
   *
   * @param currentSong Id The current song that the host is playing.
   */
  void setCurrentSong(playlist_song_id_t currentSong);

  void getEventGoers();

  //@}

signals:

  /** @name Signals */
  //@{

  /**
   * \brief Emitted when a connection with the server has been established.
   */
  void connectionEstablished();
  
  /**
   * \brief Emitted when there was a failure to establish a connection with the
   * server.
   *
   * @param errMessage A message describing the error.
   */
  void unableToConnect(const QString errMessage);

  /**
   * \brief Emitted when songs are added to the library on the server.
   *
   * @param addedIds Ids of the songs that were added to the library on the 
   * server.
   */
  void songsAddedToLibOnServer(const std::vector<library_song_id_t> addedIds);

  /**
   * \brief Emitted when a song is deleted from the library on the server.
   *
   * @param deletedId Id of the song that was deleted from the library on the
   * server.
   */
  void songDeletedFromLibOnServer(
    const library_song_id_t deletedId);

  /**
   * \brief Emitted when an event is succesfully created.
   */
  void eventCreated();

  /**
   * \brief Emitted when an event was failed to be created.
   *
   * @param errMessage A message describing the error.
   */
  void eventCreationFailed(const QString errMessage);

  /**
   * \brief Emitted when an event is succesfully ended.
   */
  void eventEnded();

  /**
   * \brief Emitted when ending an event fails.
   *
   * @param errMessage A message describing the error.
   */
  void eventEndingFailed(const QString errMessage);

  /**
   * \brief Emitted when songs are succesfully added to the list of available
   * music for the event on the server.
   *
   * @param songsAdded The id's of the songs that were succesfully added to the
   * list of available music for the even on the server.
   */
  void songsAddedToAvailableMusic(
    const std::vector<library_song_id_t> songsAdded);

  /**
   * \brief Emitted when a song is removed from the list of available songs
   * for an event on the server.
   *
   * @param deletedId Id of the song that was deleted from the available music
   * for an event on the server.
   */
  void songRemovedFromAvailableMusicOnServer(const library_song_id_t deletedId);

  /**
   * \brief Emitted when a new version of the active playlist is retrieved from
   * the server.
   */
  void newActivePlaylist(const QVariantList newPlaylist);

  /**
   * \brief emitted when songs are succesfully added to the active playlist 
   * for an event on the server.
   *
   * @param ids the client request ids of the songs that were succesfully added
   * to the active playlist for an event on the server.
   */
  void songsAddedToActivePlaylist(const std::vector<client_request_id_t> ids);

  /**
   * \brief emitted when a song is succesfully remove from the active playlist 
   * for an event on the server.
   *
   * @param songId Playlist id of song that was succesfully removed
   * from the active playlist for an event on the server.
   */
  void songRemovedFromActivePlaylist(const playlist_song_id_t songId);

  /**
   * \brief Emitted when the current song that the host is playing is
   * succesfully set on the server.
   */
  void currentSongSet();

  /**
   * \brief Emitted when there in a error setting host is playing on the server.
   */
  void currentSongSetError();


  void newEventGoers(QVariantList eventGoers);

  //@}


private slots:

  /** @name Private Slots */
  //@{

  /**
   * \brief Handles a reply from the server.
   *
   * @param reply The reply from the server.
   */
  void recievedReply(QNetworkReply *reply);

  //@}


private:
  /** @name Private Members */
  //@{

  /** \brief Bool indicating whether or not the user is currently logged in. */
  bool isLoggedIn;
  /** 
   * \brief Bool indicating whether or not an event is currently being 
   * hosted.
   */
  bool isHostingEvent;

  /** \brief Id of the event associated with this conneciton */
  event_id_t eventId;

  /** \brief Manager for access to the network. */
  QNetworkAccessManager *netAccessManager;

  /** \brief Ticket hash that should be used for all requests. */
  QByteArray ticket_hash;

  /** \brief Id of the user that is currently logged in. */
  user_id_t  user_id;

  /**
   * \brief Time at which the current ticket has being used was issued by the
   * server.
   */
  QDateTime timeTicketIssued;

  /**
   * \brief Sets the status of the server connection to "logged in".
   *
   * @param ticket The ticket hash that should be used for all request made to
   * the server.
   * @param userId The id of the user that just logged in.
   */
  void setLoggedIn(QByteArray ticket, QByteArray userId);

  /**
   * \brief Prepares a network request that is going to include JSON.
   *
   * @param request Request to prepare.
   */
  void prepareJSONRequest(QNetworkRequest &request);


  //@}

  /** @name Private Function */
  //@{

  /**
   * \brief Get the url to be used for adding songs to the library on the 
   * server.
   *
   * @return The url to be used for adding songs to the library on the 
   * server.
   */
  QUrl getLibAddSongUrl() const;

  /**
   * \brief Get the url to be used for removing a song from the library on the 
   * server.
   *
   * @param toDelete The id of the song to delete from the library on the 
   * server.
   * @return The url to be used for adding songs to the library on the 
   * server.
   */
  QUrl getLibDeleteSongUrl(library_song_id_t toDelete) const;

  /**
   * \brief Get the url to be used for adding songs to the list of available
   * music for an event on the server.
   *
   * @return The url to be used for adding songs to the list of available
   * music for an event on the server.
   */
  QUrl getAddSongToAvailableUrl() const;

  /**
   * \brief Get the url to be used for removing a song from the list of
   * available music for an event on the server.
   *
   * @param toDelete The id of the song to be deleted from the list of 
   * availabe music for an event on the server.
   * @return The url to be used for removing a song from the list of
   * available music for an event on the server.
   */
  QUrl getAvailableMusicRemoveUrl(library_song_id_t toDelete) const;

  /**
   * \brief Get the url to be used for ending an event.
   *
   * @return The url to be used for ending an event.
   */
  QUrl getEndEventUrl() const;

  /**
   * \brief Get the url for retreiving the active playlist from the server.
   *
   * @return The for retreiving the active playlist from the server.
   */
  QUrl getActivePlaylistUrl() const;

  /**
   * \brief Get the url for adding songs to the active playlist on the server.
   *
   * @return The url for adding songs to the active playlist on the server.
   */
  QUrl getActivePlaylistAddUrl() const;

  /**
   * \brief Get the url for removing a song from the active playlist on the 
   * server.
   *
   * @return The url for removing a song from the active playlist on the 
   * server.
   */
  QUrl getActivePlaylistRemoveUrl(playlist_song_id_t toDelete) const;

  /**
   * \brief Get the url to be used for setting the current song on the server.
   *
   * @return The url to be used for setting the current song on the server.
   */
  QUrl getCurrentSongUrl() const;

  QUrl getUsersUrl() const;

  /**
   * \brief Determines whether or not a url path is a path which can be used 
   * for deleting a song from the library on the server.
   *
   * @param path The path whose identity is in question.
   * @return True if the url path is one which can be used for deleting a song
   * from the libray on the server. False otherwise.
   */
  bool isLibDeleteUrl(const QString& path) const;
 
  /**
   * \brief Determines whether or not a url path is a path which can be used 
   * for deleting a song from the list of available music on the server.
   *
   * @param path The path whose identity is in question.
   * @return True if the url path is one which can be used for deleting a song
   * from the list of available music on the server. False otherwise.
   */
  bool isAvailableMusicDeleteUrl(const QString& path) const;

  /**
   * \brief Determines whether or not a url path is a path which can be used 
   * for deleting a song from the active playlist on the server.
   *
   * @param path The path whose identity is in question.
   * @return True if the url path is one which can be used for deleting a song
   * from the acitve playlist on the server. False otherwise.
   */
  bool isActivePlaylistRemoveUrl(const QString& path) const;

  /** 
   * \brief Get the port number to be used when communicating with the server.
   *
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
   *
   * @return The port number to be used for communicating with the server.
   */
  static const QString & getServerPortNumber(){
    static const QString serverPortNumber = "4897";
    return serverPortNumber;
  }
  
  /**
   * \brief Gets the url path to the server in string form.
   * 
   * @return The url path to the server in string form.
   */
  static const QString& getServerUrlPath(){
    static const QString SERVER_URL_PATH= 
      "http://localhost:" + getServerPortNumber() + "/udj/";
    return SERVER_URL_PATH;
  }

  /**
   * \brief Gets the url path to the server in URL form.
   * 
   * @return The url path to the server in URL form.
   */
  static const QUrl& getServerUrl(){
    static const QUrl SERVER_URL(getServerUrlPath());
    return SERVER_URL;
  }
  
  /**
   * \brief Gets the url for authenticating with the server.
   *
   * @return The url for authenticating with the server.
   */
  static const QUrl& getAuthUrl(){
    static const QUrl AUTH_URL(getServerUrlPath() + "auth");
    return AUTH_URL;
  }

  /**
   * \brief Gets the url for creating an event on the server.
   *
   * @return The url for creating an event on the server.
   */
  static const QUrl& getCreateEventUrl(){
    static const QUrl CREAT_EVENT_URL(getServerUrlPath() + "events/event");
    return CREAT_EVENT_URL;
  }

  /**
   * \brief Get the header used for identifying the api version number.
   *
   * @return The header used for identifying the api version number.
   */
  static const QByteArray& getAPIVersionHeaderName(){
    static const QByteArray API_VERSION_HEAER_NAME = "X-Udj-Api-Version";
    return API_VERSION_HEAER_NAME;
  }

  /**
   * \brief Get the api version number to which this client is conforming.
   *
   * @return The api version number to which this client is conforming.
   */
  static const QByteArray& getAPIVersion(){
    static const QByteArray API_VERSION = "0.2";
    return API_VERSION;
  }

  /**
   * \brief Get the header used for identifying the ticket hash header.
   *
   * @return The header used for identifying the ticket hash header.
   */
  static const QByteArray& getTicketHeaderName(){
    static const QByteArray ticketHeaderName = "X-Udj-Ticket-Hash";
    return ticketHeaderName;
  }

  /**
   * \brief Get the header used for identifying the user id.
   *
   * @return The header used for identifying the user id.
   */
  static const QByteArray& getUserIdHeaderName(){
    static const QByteArray userIdHeaderName = "X-Udj-User-Id";
    return userIdHeaderName;
  }

  /**
   * \brief Get the property name used for storing request ids when performing 
   * in a reply when doing an addition to the active playlist.
   *
   * @return The property name used for storing request ids when performing 
   * in a reply when doing an addition to the active playlist.
   */
  static const char* getActivePlaylistRequestIdsPropertyName(){
    static const char* activePlaylistRequestIdsPropertyName = "request_ids";
    return activePlaylistRequestIdsPropertyName;
  }

  /**
   * \brief Perform authentication with the server.
   *
   * @param username The username.
   * @param password The password.
   */
  void authenticate(const QString& username, const QString& password);

  /**
   * \brief Handle a response from the server regarding authentication.
   *
   * @param reply Response from the server.
   */
  void handleAuthReply(QNetworkReply* reply);

  /**
   * \brief Handle a response from the server regarding adding songs to the
   * library.
   *
   * @param reply Response from the server.
   */
  void handleAddLibSongsReply(QNetworkReply *reply);

  /**
   * \brief Handle a response from the server regarding deleiting songs from the
   * library.
   *
   * @param reply Response from the server.
   */
  void handleDeleteLibSongsReply(QNetworkReply *reply);

  /**
   * \brief Handle a response from the server regarding event creation.
   *
   * @param reply Response from the server.
   */
  void handleCreateEventReply(QNetworkReply *reply);

  /**
   * \brief Handle a response from the server regarding ending an event.
   *
   * @param reply Response from the server.
   */
  void handleEndEventReply(QNetworkReply *reply);

  /**
   * \brief Handle a response from the server regarding adding songs to the
   * list of avaialble songs for an event.
   *
   * @param reply Response from the server.
   */
  void handleAddAvailableSongReply(QNetworkReply *reply);

  /**
   * \brief Handle a response from the server regarding removing songs from the
   * the list of available songs for an event.
   *
   * @param reply Response from the server.
   */
  void handleDeleteAvailableMusicReply(QNetworkReply *reply);

  /**
   * \brief Handle a response from the server regarding a new active playlist.
   *
   * @param reply Response from the server.
   */
  void handleRecievedActivePlaylist(QNetworkReply *reply);

  /**
   * \brief Handle a response from the server regarding the addition of a song
   * to the active playlist.
   *
   * @param reply Response from the server.
   */
  void handleRecievedActivePlaylistAdd(QNetworkReply *reply);

  /**
   * \brief Handle a response from the server regarding the removal of a song 
   * from the active playlist.
   *
   * @param reply Response from the server.
   */
  void handleRecievedActivePlaylistRemove(QNetworkReply *reply);

  /**
   * \brief Handle a response from the server regarding the setting of the 
   * current song that is being played.
   *
   * @param reply Response from the server.
   */
  void handleRecievedCurrentSongSet(QNetworkReply *reply);

  void handleRecievedNewEventGoers(QNetworkReply *reply);

  //@}

};


} //end namespace
#endif //UDJ_SERVER_CONNECTION_HPP
