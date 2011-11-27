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
#include "JSONHelper.hpp"
#include <QNetworkReply>
#include "DataStore.hpp"
#include "qt-json/json.h"

namespace UDJ{

const QByteArray JSONHelper::getJSONForLibAdd(
  const lib_song_t &song,
  const library_song_id_t &id)
{
  bool ok;
  return getJSONForLibAdd(song, id, ok);
}

const QByteArray JSONHelper::getJSONForLibAdd(
  const lib_song_t &song,
  const library_song_id_t &id,
  bool &success)
{
  const std::vector<lib_song_t> songs(1, song);  
  const std::vector<library_song_id_t> ids(1, id);  
  return getJSONForLibAdd(songs, ids, success);
}

const QByteArray JSONHelper::getJSONForLibAdd(
  const std::vector<lib_song_t> &songs,
  const std::vector<library_song_id_t> &ids)
{
  bool ok;
  return getJSONForLibAdd(songs, ids, ok);
}


const QByteArray JSONHelper::getJSONForLibAdd(
  const std::vector<lib_song_t>& songs,
  const std::vector<library_song_id_t>& ids,
  bool &success)
{
  typedef std::vector<lib_song_t>::const_iterator song_iterator;
  typedef std::vector<library_song_id_t>::const_iterator id_iterator;
  QVariantList toAdd;
  for(song_iterator it=songs.begin(); it!=songs.end(); ++it){
    QVariantMap songToAdd;
    songToAdd["song"] = it->songName;
    songToAdd["artist"] = it->artistName;
    songToAdd["album"] = it->albumName;
    toAdd.append(songToAdd);
  }
  QVariantList idMaps;
  for(id_iterator it=ids.begin(); it!=ids.end(); ++it){
    QVariantMap idMap;
    idMap["server_id"] = QVariant::fromValue(DataStore::getInvalidServerId());
    idMap["client_id"] = QVariant::fromValue(*it);
    idMaps.append(idMap);
  }

  QVariantMap addObject;
  addObject["to_add"] = toAdd;
  addObject["id_maps"] = idMaps;

  return QtJson::Json::serialize(QVariant(addObject),success);
}

const std::map<library_song_id_t, library_song_id_t>
  JSONHelper::getHostToServerLibIdMap(QNetworkReply *reply)
{
  std::map<library_song_id_t, library_song_id_t> toReturn;
  QByteArray responseData = reply->readAll(); 
  std::cout << "Response Data " << QString(responseData).toStdString() <<std::endl;
  QVariantList songsAdded = QtJson::Json::parse(responseData).toList();
  QVariantMap currentSong;
  for(int i=0;i<songsAdded.size(); ++i){
    currentSong = songsAdded.at(i).toMap();
    toReturn[currentSong["client_id"].value<library_song_id_t>()] = 
      currentSong["server_id"].value<library_song_id_t>();
  }
  return toReturn;
}







} //end namespace UDJ
