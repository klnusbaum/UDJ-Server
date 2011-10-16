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

#include "ActivityList.hpp"
#include "MusicLibrary.hpp"
#include <QStandardItemModel>
#include <QStandardItem>
#include <QHeaderView>

namespace UDJ{

ActivityList::ActivityList(MusicLibrary *library, QWidget *parent):
  QTreeView(parent), library(library)
{
 setupUi(); 
}


void ActivityList::setupUi(){
  QStandardItemModel *itemModel = new QStandardItemModel(this);
  itemModel->appendRow(new QStandardItem(tr("Library")));
  itemModel->appendRow(new QStandardItem(tr("Party")));
  itemModel->appendRow(new QStandardItem(tr("Playlist")));
  setModel(itemModel);
  header()->hide();
}



}// end namespace UDJ
