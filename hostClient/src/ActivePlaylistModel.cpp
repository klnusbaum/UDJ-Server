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
#include "DataStore.hpp"
#include "ActivePlaylistModel.hpp"
#include <QSqlRecord>


namespace UDJ{


ActivePlaylistModel::ActivePlaylistModel(
  const QString& query, DataStore *dataStore, QObject *parent)
  :MusicModel(query, dataStore, parent)
{}

QVariant ActivePlaylistModel::data(const QModelIndex& item, int role) const{
  int timeAddedIndex = record().indexOf(DataStore::getTimeAddedColName());
  QVariant actualData = MusicModel::data(item, role);
  if(item.column() == timeAddedIndex && role == Qt::DisplayRole){
    return actualData.toString().section('T', 1);
  }
  else{
    return actualData;
  }

}


} //end namespace UDJ
