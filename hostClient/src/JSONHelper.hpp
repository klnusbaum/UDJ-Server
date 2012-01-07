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
#ifndef JSON_HELPER_HPP
#define JSON_HELPER_HPP
#include "ConfigDefs.hpp"
#include <vector>
#include <QVariantList>

class QNetworkReply;

namespace UDJ{

typedef struct {
  library_song_id_t id;
  QString songName;
  QString artistName;
  QString albumName;
  int duration;
} lib_song_t;

/** \brief Class used to help serialize and deserialize JSON messages */
class JSONHelper{

public:

  /** @name Converter Functions */
  //@{

  
  /**
   * \brief Creates the JSON necessary for doing a request to add a song
   * to the library.
   *
   * @param song The id of the song to be added
   * @return A bytearray contianing the JSON for the song add request.
   */
  static const QByteArray getJSONForLibAdd(const lib_song_t &song);
  
  /**
   * \brief Creates the JSON necessary for doing a request to add a song
   * to the library.
   *
   * @param song The id of the song to be added.
   * @param success A boolean whose value will be set to true if the JSON
   * was able to be successfully generated and false otherwise.
   * @return A bytearray contianing the JSON for the song add request.
   */
  static const QByteArray getJSONForLibAdd(
    const lib_song_t &song,
    bool &success);

  /**
   * \brief Creates the JSON necessary for doing a request to add the given
   * songs to the library.
   *
   * @param songs The ids of the songs to be added.
   * @return A bytearray contianing the JSON for the song add request.
   */
  static const QByteArray getJSONForLibAdd(
    const std::vector<lib_song_t> &songs);

  /**
   * \brief Creates the JSON necessary for doing a request to add the given
   * songs to the library.
   *
   * @param songs The ids of the songs to be added.
   * @param success A boolean whose value will be set to true if the JSON
   * was able to be successfully generated and false otherwise.
   * @return A bytearray contianing the JSON for the song add request.
   */
  static const QByteArray getJSONForLibAdd(
    const std::vector<lib_song_t>& songs,
    bool &success);

  /**
   * \brief Gets the JSON necesary for creating an event.
   *
   * @param eventName The name of the event.
   * @param password The password for the event.
   * @param latitude The latitude of the event. 
   * @param longitude The longitude of the event.
   * @return A bytearray containing the generated JSON.
   */
  static const QByteArray getCreateEventJSON(
    const QString& eventName,
    const QString& password="", 
    float latitude=getInvalidLat(),
    float longitude=getInvalidLong());

  /**
   * \brief Gets the JSON necesary for creating an event.
   *
   * @param eventName The name of the event.
   * @param password The password for the event.
   * @param latitude The latitude of the event. 
   * @param longitude The longitude of the event.
   * @param success A boolean whose value will be set to true if the JSON
   * was able to be successfully generated and false otherwise.
   * @return A bytearray containing the generated JSON.
   */
  static const QByteArray getCreateEventJSON(
    const QString& eventName,
    const QString& password, 
    float latitude,
    float longitude,
    bool &success);

  /**
   * \brief Gets the JSON needed for adding a song to the list of available 
   * songs.
   *
   * @param toAdd The id of the song to be added to the list of available songs.
   * @return A bytearray containing the JSON needed to add the given song
   * to the list of available music.
   */
  static const QByteArray getAddToAvailableJSON(const library_song_id_t& toAdd);

  /**
   * \brief Gets the JSON needed for adding a song to the list of available 
   * songs.
   *
   * @param toAdd The id of the song to be added to the list of available songs.
   * @param success A boolean whose value will be set to true if the JSON
   * was able to be successfully generated and false otherwise.
   * @return A bytearray containing the JSON needed to add the given song
   * to the list of available music.
   */
  static const QByteArray getAddToAvailableJSON(
    const library_song_id_t& toAdd, 
    bool &success);

  /**
   * \brief Gets the JSON needed for adding the given songs
   *  to the list of available songs.
   *
   * @param toAdd The ids of the songs to be added to the list of available 
   * songs.
   * @return A bytearray containing the JSON needed to add the given songs
   * to the list of available music.
   */
  static const QByteArray getAddToAvailableJSON(
    const std::vector<library_song_id_t>& toAdd);

  /**
   * \brief Gets the JSON needed for adding the given songs
   *  to the list of available songs.
   *
   * @param toAdd The ids of the songs to be added to the list of available 
   * songs.
   * @param success A boolean whose value will be set to true if the JSON
   * was able to be successfully generated and false otherwise.
   * @return A bytearray containing the JSON needed to add the given songs
   * to the list of available music.
   */
  static const QByteArray getAddToAvailableJSON(
    const std::vector<library_song_id_t>& toAdd, 
    bool &success);

  /**
   * \brief Gets the json needed to add the given songs to the active playlist. 
   *
   * @param requestIds The request ids for each request in the libIds vector.
   * @param libIds The ids of the songs to be added to the active playlist.
   * @return A bytearray containing the JSON needed for adding the given songs
   * to the active playlist.
   */
  static const QByteArray getAddToActiveJSON(
    const std::vector<client_request_id_t>& requestIds,
    const std::vector<library_song_id_t>& libIds);

  /**
   * \brief Gets the json needed to add the given songs to the active playlist. 
   *
   * @param requestIds The request ids for each request in the libIds vector.
   * @param libIds The ids of the songs to be added to the active playlist.
   * @param success A boolean whose value will be set to true if the JSON
   * was able to be successfully generated and false otherwise.
   * @return A bytearray containing the JSON needed for adding the given songs
   * to the active playlist.
   */
  static const QByteArray getAddToActiveJSON(
    const std::vector<client_request_id_t>& requestIds,
    const std::vector<library_song_id_t>& libIds,
    bool &success);

  /**
   * \brief Given a server reply, get's the library Ids that were successuflly
   * updated on the server.
   *
   * @param reply The reply from the server.
   * @return A vector containing all the library id's of the songs that were 
   * updated on the server.
   */
  static const std::vector<library_song_id_t>
    getUpdatedLibIds(QNetworkReply *reply);

  /**
   * \brief Get's the id of an event from the given server reply.
   * 
   * @param reply The reply from the server.
   * @return The event id in the servers response.
   */
  static event_id_t getEventId(QNetworkReply *reply);

  /**
   * \brief Gets the songs that were added to the list of available songs
   * on the server.
   *
   * @param reply The servers response.
   * @return A vector containing all the library ids that were added to the
   * list of available songs.
   */
  static const std::vector<library_song_id_t> getAddedAvailableSongs(
    QNetworkReply *reply);

  /**
   * \brief Gets the active playlist from the servers reply.
   *
   * @param reply The servers response.
   * @return A QVariantList containing all the songs in the active playlist in
   * their approriate order.
   */
  static const QVariantList getActivePlaylistFromJSON(QNetworkReply *reply);

  static const QVariantList getEventGoersJSON(QNetworkReply *reply);

  //@}

  /** @name Constants */
  //@{

  /**
   * \brief Gets the value indicating and invalid latitude value.
   *
   * @return The value indicating and invalid latitude value.
   */
  static const float& getInvalidLat(){
    static const float invalidLat = 100;
    return invalidLat;
  }

  /**
   * \brief Gets the value indicating and invalid longitude value.
   *
   * @return The value indicating and invalid longitude value.
   */
  static const float& getInvalidLong(){
    static const float invalidLong = 200;
    return invalidLong;
  }

  //@}

};


} //end namespace UDJ
#endif //JSON_HELPER_HPP
