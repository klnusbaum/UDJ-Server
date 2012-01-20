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
#include <QNetworkReply>
#include "JSONHelper.hpp"
#include "qt-json/json.h"

namespace UDJ{

const QByteArray JSONHelper::getJSONForLibAdd(const lib_song_t &song){
  bool ok;
  return getJSONForLibAdd(song, ok);
}

const QByteArray JSONHelper::getJSONForLibAdd(
  const lib_song_t &song,
  bool &success)
{
  const std::vector<lib_song_t> songs(1, song);  
  return getJSONForLibAdd(songs, success);
}

const QByteArray JSONHelper::getJSONForLibAdd(
  const std::vector<lib_song_t> &songs)
{
  bool ok;
  return getJSONForLibAdd(songs, ok);
}


const QByteArray JSONHelper::getJSONForLibAdd(
  const std::vector<lib_song_t>& songs,
  bool &success)
{
  typedef std::vector<lib_song_t>::const_iterator song_iterator;
  QVariantList toAdd;
  for(song_iterator it=songs.begin(); it!=songs.end(); ++it){
    QVariantMap songToAdd;
    songToAdd["id"] = QVariant::fromValue<library_song_id_t>(it->id);
    songToAdd["title"] = it->songName;
    songToAdd["artist"] = it->artistName;
    songToAdd["album"] = it->albumName;
    songToAdd["duration"] = it->duration;
    toAdd.append(songToAdd);
  }

  return QtJson::Json::serialize(QVariant(toAdd),success);
}

const std::vector<library_song_id_t> JSONHelper::getUpdatedLibIds(
  QNetworkReply *reply)
{
  QByteArray responseData = reply->readAll();
  QString responseString = QString::fromUtf8(responseData);
  bool success;
  QVariantList songsAdded = 
    QtJson::Json::parse(responseString, success).toList();
  if(!success){
    std::cerr << "Error parsing json from a response to an add library entry" <<
     "request" << std::endl <<
      responseString.toStdString() << std::endl;
  }
  
  std::vector<library_song_id_t> toReturn(songsAdded.size());
  for(int i=0; i<songsAdded.size(); ++i){
    toReturn[i] = songsAdded[i].value<library_song_id_t>();
  }
  return toReturn;
}
const QByteArray JSONHelper::getCreateEventJSON(
  const QString& eventName,
  const QString& password, 
  double latitude,
  double longitude)
{
  bool success;
  return getCreateEventJSON(eventName, password, latitude, longitude, success);
}

const QByteArray JSONHelper::getCreateEventJSON(
  const QString& eventName,
  const QString& password, 
  double latitude,
  double longitude,
  bool &success)
{
  QVariantMap eventToCreate;
  eventToCreate["name"] = eventName;
  if(password != ""){
    eventToCreate["password"] = password;
  }
  if(latitude != getInvalidLat() && longitude != getInvalidLong()){
    QVariantMap coords;
    coords["latitude"] = latitude;
    coords["longitude"] = longitude;
    eventToCreate["coords"] = coords;
  }
  return QtJson::Json::serialize(QVariant(eventToCreate),success);
}

const QByteArray JSONHelper::getAddToAvailableJSON(
  const library_song_id_t& toAdd)
{
  bool success;
  return getAddToAvailableJSON(toAdd, success);

}

const QByteArray JSONHelper::getAddToAvailableJSON(
  const library_song_id_t& toAdd, 
  bool &success)
{
  std::vector<library_song_id_t> toAddVector(1, toAdd);
  return getAddToAvailableJSON(toAddVector, success);
}

const QByteArray JSONHelper::getAddToAvailableJSON(
  const std::vector<library_song_id_t>& toAdd)
{
  bool success;
  return getAddToAvailableJSON(toAdd, success);
}

const QByteArray JSONHelper::getAddToAvailableJSON(
  const std::vector<library_song_id_t>& toAdd, 
  bool &success)
{
  QVariantList toSerialize;
  for(
    std::vector<library_song_id_t>::const_iterator it = toAdd.begin();
    it != toAdd.end();
    ++it
  )
  {
    toSerialize.append(QVariant::fromValue<library_song_id_t>(*it));
  }
  
  return QtJson::Json::serialize(toSerialize, success);
}

const QByteArray JSONHelper::getAddToActiveJSON(
  const std::vector<client_request_id_t>& requestIds,
  const std::vector<library_song_id_t>& libIds)
{
  bool success;
  return getAddToActiveJSON(requestIds, libIds, success);
}

const QByteArray JSONHelper::getAddToActiveJSON(
  const std::vector<client_request_id_t>& requestIds,
  const std::vector<library_song_id_t>& libIds,
  bool &success)
{
  QVariantList toSerialize;
  std::vector<library_song_id_t>::const_iterator songIt = libIds.begin();
  for(
    std::vector<client_request_id_t>::const_iterator requestIt = 
      requestIds.begin();
    requestIt != requestIds.end() && songIt != libIds.end();
    ++requestIt, ++songIt)
  {
    QVariantMap requestToAdd;
    requestToAdd["lib_id"] = QVariant::fromValue<library_song_id_t>(*songIt);
    requestToAdd["client_request_id"] = 
      QVariant::fromValue<client_request_id_t>(*requestIt);
    toSerialize.append(requestToAdd);
  }
  return QtJson::Json::serialize(toSerialize, success);
}


const std::vector<library_song_id_t> JSONHelper::getAddedAvailableSongs(
  QNetworkReply *reply)
{
  QByteArray responseData = reply->readAll();
  QString responseString = QString::fromUtf8(responseData);
  bool success;
  QVariantList addedSongs = QtJson::Json::parse(responseData, success).toList();
  if(!success){
    std::cerr << "Error processing result from add to available music" << 
      std::endl;
  }
  std::vector<library_song_id_t> toReturn;
  for(
    QVariantList::const_iterator it = addedSongs.begin();
    it != addedSongs.end();
    ++it
  )
  {
    toReturn.push_back(it->value<library_song_id_t>());
  }
  return toReturn;
}

event_id_t JSONHelper::getEventId(QNetworkReply *reply){
  QByteArray responseData = reply->readAll();
  QString responseString = QString::fromUtf8(responseData);
  bool success;
  QVariantMap eventCreated = 
    QtJson::Json::parse(responseString, success).toMap();
  if(!success){
    std::cerr << "Error parsing json from a response to an event creation" <<
     "request" << std::endl <<
      responseString.toStdString() << std::endl;
  }
  
  return eventCreated["event_id"].value<event_id_t>();
}

const QVariantList JSONHelper::getActivePlaylistFromJSON(QNetworkReply *reply){
  QByteArray responseData = reply->readAll();
  QString responseString = QString::fromUtf8(responseData);
  bool success;
  QVariantMap activePlaylist = 
    QtJson::Json::parse(responseString, success).toMap();
  if(!success){
    std::cerr << "Error parsing json from a response to an event creation" <<
     "request" << std::endl <<
      responseString.toStdString() << std::endl;
  }
  return activePlaylist["active_playlist"].toList();
}

const QVariantList JSONHelper::getEventGoersJSON(QNetworkReply *reply){
  QByteArray responseData = reply->readAll();
  QString responseString = QString::fromUtf8(responseData);
  bool success;
  QVariantList eventGoers = 
    QtJson::Json::parse(responseString, success).toList();
  return eventGoers;
}

const QVariantMap JSONHelper::getSingleEventInfo(QNetworkReply *reply){
  QByteArray responseData = reply->readAll();
  QString responseString = QString::fromUtf8(responseData);
  bool success;
  QVariantMap event = 
    QtJson::Json::parse(responseString, success).toMap();
  return event;
}


} //end namespace UDJ
