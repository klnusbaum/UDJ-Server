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
#include "MusicLibrary.hpp"
#include "qt-json/json.h"

namespace UDJ{

const QByteArray JSONHelper::getLibraryEntryJSON(
  const QString& songName,
  const QString& artistName,
  const QString& albumName,
  const libraryid_t& hostId,
  const bool isDeleted)
{
  bool success=true;
  return getLibraryEntryJSON(
    songName,
    artistName, 
    albumName, 
    hostId, 
    isDeleted,
    success);
}

const QByteArray JSONHelper::getLibraryEntryJSON(
  const QString& songName,
  const QString& artistName,
  const QString& albumName,
  const libraryid_t& hostId,
  bool isDeleted,
  bool &success)
{
  QVariantMap songData;
  songData["song"] = songName;
  songData["artist"] = artistName;
  songData["album"] = albumName;
  songData["host_lib_id"] = QVariant::fromValue<libraryid_t>(hostId);
  songData["server_lib_id"] = 
    QVariant::fromValue<libraryid_t>(MusicLibrary::getInvalidServerId());
  songData["is_deleted"] = isDeleted ? "true" : "false";
  
  QVariantList toAddData;
  toAddData.append(songData);
  
  return QtJson::Json::serialize(QVariant(toAddData),success);

}


const std::map<libraryid_t, libraryid_t>
  JSONHelper::getHostToServerLibIdMap(QNetworkReply *reply)
{
  std::map<libraryid_t, libraryid_t> toReturn;
  QByteArray responseData = reply->readAll(); 
  QVariantList songsAdded = QtJson::Json::parse(responseData).toList();
  QVariantMap currentSong;
  for(int i=0;i<songsAdded.size(); ++i){
    currentSong = songsAdded.at(i).toMap();
    toReturn[currentSong["host_lib_id"].value<libraryid_t>()] = 
      currentSong["server_lib_id"].value<libraryid_t>();
  }
  return toReturn;
}







} //end namespace UDJ
