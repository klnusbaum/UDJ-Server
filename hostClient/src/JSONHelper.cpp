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
#include <QNetworkRequest>
#include "MusicLibrary.hpp"
#include "qt-json/json.h"

namespace UDJ{

static const QByteArray getLibraryEntryJSON(
  const QString& songName,
  const QString& artistName,
  const QString& albumName,
  const libraryid_t hostId,
  bool isDeleted=false)
{
  bool success=true;
  return getLibraryEntryJSON(
    songName,
    artistName, 
    albumName, 
    hostId, 
    isDeleted,
    success)
}

const QByteArray JSONHelper::getLibraryEntryJSON(
  const QString& songName,
  const QString& artistName,
  const QString& albumName,
  const libraryid_t hostId,
  bool isDeleted,
  bool &success)
{
  QVariantMap toAddMap;
  QVariantMap songData;
  songData["song"] = songName;
  songData["artist"] = artistName;
  songData["album"] = album;
  songData["host_lib_id"] = QVariant::fromValue<libraryid_t>(hostId);
  songData["server_lib_id"] = 
    QVariant::fromValue<libraryid_t>(MusicLibrary::getInvalidServerId());
  songData["is_deleted"] = isDeleted ? "true" : "false";
  return QtJson::Json 

}


const std::map<libraryid_t, libraryid_t>
  JSONHelper::getHostToServerLibIdMap(QNetworkRequest *reply)
{
  std::map<libraryid_t, libraryid_t> toReturn;
  return toReturn;
}







} //end namespace UDJ
