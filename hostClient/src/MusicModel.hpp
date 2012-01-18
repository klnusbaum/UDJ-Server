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
#ifndef LIBRARY_MODEL_HPP
#define LIBRARY_MODEL_HPP
#include <QSqlQueryModel>

namespace UDJ{

class DataStore;

class MusicModel : public QSqlQueryModel{
Q_OBJECT
public:

  MusicModel(const QString& query, DataStore *dataStore, QObject *parent);

  virtual QVariant data(const QModelIndex& item, int role) const;

public slots:

  void refresh();

  void refresh(QString query);

private:

  DataStore *dataStore;

  QString query;

};


}
#endif //LIBRARY_MODEL_HPP
