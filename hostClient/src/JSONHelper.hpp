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
#include <map>

class QNetworkReply;

namespace UDJ{


class JSONHelper{

public:
  static const QByteArray getLibraryEntryJSON(
	  const QString& songName,
	  const QString& artistName,
	  const QString& albumName,
	  const libraryid_t& hostId,
    const bool isDeleted=false);

  static const QByteArray getLibraryEntryJSON(
	  const QString& songName,
	  const QString& artistName,
	  const QString& albumName,
	  const libraryid_t& hostId,
    const bool isDeleted,
    bool &success);

  static const std::map<libraryid_t, libraryid_t>
    getHostToServerLibIdMap(QNetworkReply *reply);

};


} //end namespace UDJ
#endif //JSON_HELPER_HPP
