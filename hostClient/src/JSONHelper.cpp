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
    songToAdd["song"] = it->songName;
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
  QVariantList songsAdded = QtJson::Json::parse(responseData).toList();
  std::vector<library_song_id_t> toReturn(songsAdded.size());
  for(int i=0; i<songsAdded.size(); ++i){
    toReturn[i] = songsAdded[i].value<library_song_id_t>();
  }
  return toReturn;
  
}

} //end namespace UDJ
