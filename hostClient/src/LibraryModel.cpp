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
#include "LibraryModel.hpp"
#include "MusicLibrary.hpp"

namespace UDJ{


LibraryModel::LibraryModel(QObject *parent, MusicLibrary *library):
  QSqlTableModel(parent, library->getDatabaseConnection())
{
  setTable(MusicLibrary::getLibraryTableName());
  select();

	//Make this more dependent up what serverConnection is telling us.
  setHeaderData(0, Qt::Horizontal, "id");
  setHeaderData(1, Qt::Horizontal, "Song");
  setHeaderData(2, Qt::Horizontal, "Artist");
  setHeaderData(3, Qt::Horizontal, "Album");
  setHeaderData(4, Qt::Horizontal, "filepath");
  connect(library, SIGNAL(songsAdded()), this, SLOT(refresh()));
}

void LibraryModel::refresh(){
  select();
}

QString LibraryModel::getSongNameFromSource(const Phonon::MediaSource &source) const{
  QString filename = source.fileName();
  for(int i =0; i < rowCount(); ++i){
    if(data(index(i,4)).toString() == filename){
      return data(index(i,1)).toString();
    }
  }
  return "";
}


}

