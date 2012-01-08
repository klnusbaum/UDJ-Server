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
#include <QStyledItemDelegate>
#include <QMenu>
#include <QAction>
#include <QTextEdit>

namespace UDJ{

ActivityList::ActivityList(DataStore *dataStore, QWidget *parent):
  QTreeView(parent), dataStore(dataStore)
{
  setupUi(); 
  createActions();
  connect(
    this,
    SIGNAL(clicked(const QModelIndex&)),
    this,
    SLOT(itemClicked(const QModelIndex&)));
  connect(
    model,
    SIGNAL(itemChanged(QStandardItem*)),
    this,
    SLOT(saveSongListToDb(QStandardItem*)));
  setContextMenuPolicy(Qt::CustomContextMenu);
  connect(this, SIGNAL(customContextMenuRequested(const QPoint&)),
    this, SLOT(handleContextMenuRequest(const QPoint&)));
}

void ActivityList::handleContextMenuRequest(const QPoint& point){
  QModelIndexList selected = selectedIndexes();
  QModelIndex singleSelect = selected[0];
  if(singleSelect.parent() == songListRoot->index() &&
    singleSelect != newSongListItem->index())
  {
    QMenu contextMenu(this);
    contextMenu.addAction(deleteSongListAction);
    if(dataStore->isCurrentlyHosting()){
      contextMenu.addAction(addSongListAction);
    }
    contextMenu.exec(QCursor::pos());
  }
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
  else if(index.parent() == songListRoot->index()){
    QStandardItem *selectedList = model->itemFromIndex(index);
    emit songListClicked(selectedList->data().value<song_list_id_t>());
  }
}

void ActivityList::createActions(){
  deleteSongListAction = new QAction(tr("Delete Song List"), this); 
  addSongListAction = new QAction(tr("Add To Available Music"), this);
  connect(
    deleteSongListAction,
    SIGNAL(triggered()),
    this,
    SLOT(deleteSelectedSongList()));
  connect(
    addSongListAction,
    SIGNAL(triggered()),
    this,
    SLOT(addSongListToAvailableMusic()));
}

void ActivityList::setupUi(){
  setSelectionMode(QAbstractItemView::SingleSelection);
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
  QStandardItem *newSongList = new QStandardItem(tr("New Song List"));
  songListRoot->insertRow(0, newSongList);
  setCurrentIndex(newSongList->index());
  edit(newSongList->index());
}


void ActivityList::saveSongListToDb(QStandardItem *toSave){
  QVariant data = toSave->data();
  QString name = toSave->text();
  if(data.isValid()){
    song_list_id_t id = data.value<song_list_id_t>();
    dataStore->setSongListName(id, name);
  } 
  else{
    song_list_id_t id = dataStore->insertSongList(name);   
    toSave->setData(QVariant::fromValue(id));
  }
}

void ActivityList::deleteSelectedSongList(){
  QModelIndexList selected = selectedIndexes();
  QModelIndex singleSelect = selected[0];
  QStandardItem *selectedSongList = model->itemFromIndex(singleSelect);
  dataStore->deleteSongList(selectedSongList->data().value<song_list_id_t>());
  songListRoot->removeRow(singleSelect.row()); 
}

void ActivityList::switchToLibrary(){
  setCurrentIndex(libraryItem->index());
  emit libraryClicked();
}

void ActivityList::addSongListToAvailableMusic(){
  QStandardItem *selectedSongList = model->itemFromIndex(
    this->selectedIndexes()[0]);
  dataStore->addSongListToAvailableMusic(
    selectedSongList->data().value<song_list_id_t>());
}


}// end namespace UDJ
