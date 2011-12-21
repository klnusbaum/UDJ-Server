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
#include "DataStore.hpp"
#include <QStandardItemModel>
#include <QStandardItem>
#include <QHeaderView>

namespace UDJ{

ActivityList::ActivityList(DataStore *dataStore, QWidget *parent):
  QTreeView(parent), dataStore(dataStore)
{
  setupUi(); 
  connect(
    this,
    SIGNAL(clicked(const QModelIndex&)),
    this,
    SLOT(itemClicked(const QModelIndex&)));
}

void ActivityList::itemClicked(const QModelIndex& index){
  if(!index.parent().isValid()){
    QStandardItem *clickedItem = model->itemFromIndex(index);
    QString title = clickedItem->text();
    if(title == getLibraryTitle()){
      emit libraryClicked();
    }
    else if(title == getEventTitle()){
      emit eventClicked();
    }
  }
}

void ActivityList::setupUi(){
  model = new QStandardItemModel(this);
  model->appendRow(new QStandardItem(getLibraryTitle()));
  model->appendRow(new QStandardItem(getEventTitle()));
//  model->appendRow(new QStandardItem(getPlaylistTitle()));
  setModel(model);
  header()->hide();
}



}// end namespace UDJ
