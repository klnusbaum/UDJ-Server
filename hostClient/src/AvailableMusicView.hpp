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
#ifndef AVAILABLE_MUSIC_VIEW_HPP
#define AVAILABLE_MUSIC_VIEW_HPP
#include <QTableView>
#include "ConfigDefs.hpp"

class QSqlRelationalTableModel;

namespace UDJ{

class DataStore;

class AvailableMusicView : public QTableView{
Q_OBJECT
public:
  AvailableMusicView(DataStore *dataStore, QWidget *parent=0);
private:
  DataStore *dataStore;
  QSqlRelationalTableModel *availableMusicModel;  
private slots:
  void updateView();
};


} //end namespace
#endif //AVAILABLE_MUSIC_VIEW_HPP
