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
#include "MusicModel.hpp"
#include "DataStore.hpp"
#include <QSqlRecord>


namespace UDJ{


MusicModel::MusicModel(
  const QString& query, DataStore *dataStore, QObject *parent)
  :QSqlQueryModel(parent),
  dataStore(dataStore),
  query(query)
{
  refresh();
}

void MusicModel::refresh(){
  setQuery(query, dataStore->getDatabaseConnection());
}

void MusicModel::refresh(QString newQuery){
  query = newQuery;
  setQuery(newQuery, dataStore->getDatabaseConnection());
}





QVariant MusicModel::data(const QModelIndex& item, int role) const{
  if(role == Qt::TextAlignmentRole){
    return QVariant(Qt::AlignLeft | Qt::AlignVCenter);
  }

  int durationColIndex = record().indexOf(DataStore::getLibDurationColName());
  QVariant actualData = QSqlQueryModel::data(item, role);
  if(item.column() == durationColIndex && role == Qt::DisplayRole){
    int seconds = actualData.toInt() % 60;
    int minutes = actualData.toInt() / 60;
    QString secondsString = seconds < 10 ? "0" + QString::number(seconds) :
      QString::number(seconds);
    return QString::number(minutes) + ":" + secondsString;
  }
  else{
    return actualData;
  }


}




} //end namespace UDJ
