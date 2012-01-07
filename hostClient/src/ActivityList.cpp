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
#include <QSqlQuery>
#include <QSqlRecord>

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
  if(index == libraryItem->index()){
    emit libraryClicked();
  }
  else if(index == eventItem->index()){
    emit eventClicked();
  }
  else if(index == newSongListItem->index()){
    addNewSongList();
  }
}

void ActivityList::setupUi(){
  libraryItem = new QStandardItem(getLibraryTitle());
  libraryItem->setEditable(false);

  eventItem = new QStandardItem(getEventTitle());
  eventItem->setEditable(false);

  songListRoot = new QStandardItem(getSongListTitle());
  songListRoot->setEditable(false);


  model = new QStandardItemModel(this);
  model->appendRow(libraryItem);
  model->appendRow(eventItem);
  model->appendRow(songListRoot);

  QSqlQuery songLists = dataStore->getSongLists();
  QSqlRecord currentRecord;
  int i =0;
  while(songLists.next()){
    currentRecord = songLists.record();
    QStandardItem *toInsert = new QStandardItem(
      currentRecord.value(DataStore::getSongListNameColName()).toString());
    toInsert->setData(currentRecord.value(DataStore::getSongListIdColName()));
    songListRoot->setChild(i++, toInsert);
  }
  newSongListItem = new QStandardItem(getNewSongListTitle());
  newSongListItem->setEditable(false);
  songListRoot->setChild(i,newSongListItem);

  setModel(model);
  header()->hide();
  expand(songListRoot->index());
}

void ActivityList::addNewSongList(){
  std::cout << "adding new list" << std::endl;
  QStandardItem *newSongList = new QStandardItem(tr("New Song List"));
  songListRoot->insertRow(0, newSongList);
  setCurrentIndex(newSongList->index());
  edit(newSongList->index());
}




}// end namespace UDJ
