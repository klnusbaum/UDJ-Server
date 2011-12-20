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
#include "LibraryView.hpp"
#include "DataStore.hpp"
#include <QSqlRelationalTableModel>
#include <QHeaderView>
#include <QContextMenuEvent>
#include <QMenu>
#include <QSqlRecord>
#include <set>
	

namespace UDJ{


LibraryView::LibraryView(DataStore *dataStore, QWidget* parent):
  QTableView(parent),
  dataStore(dataStore)
{
  libraryModel = 
    new QSqlRelationalTableModel(this, dataStore->getDatabaseConnection());
  libraryModel->setTable(DataStore::getLibraryTableName());
  libraryModel->select();
  setEditTriggers(QAbstractItemView::NoEditTriggers);
  verticalHeader()->hide();
  horizontalHeader()->setStretchLastSection(true);
  setModel(libraryModel);
  setSelectionBehavior(QAbstractItemView::SelectRows);
  setContextMenuPolicy(Qt::CustomContextMenu);
  createActions();
  connect(this, SIGNAL(customContextMenuRequested(const QPoint&)),
    this, SLOT(handleContextMenuRequest(const QPoint&)));
  connect(dataStore, SIGNAL(libSongsModified()), this, SLOT(refresh()));
}

void LibraryView::refresh(){
  libraryModel->select();
}

void LibraryView::createActions(){
  deleteSongAction = new QAction(getDeleteContextMenuItemName(), this);
  addToAvailableMusicAction = new QAction(
    getAddToAvailableContextMenuItemName(), this);
  connect(
    deleteSongAction, 
    SIGNAL(triggered()), 
    this, 
    SLOT(deleteSongs()));
  connect(
    addToAvailableMusicAction, 
    SIGNAL(triggered()), 
    this, 
    SLOT(addSongToAvailableMusic()));
}
  

void LibraryView::handleContextMenuRequest(const QPoint &pos){
  QMenu contextMenu(this);
  if(dataStore->isCurrentlyHosting()){
    contextMenu.addAction(addToAvailableMusicAction);
  }
  contextMenu.addAction(addToPlaylistAction);
  contextMenu.addAction(deleteSongAction);
  contextMenu.exec(QCursor::pos());
}

std::vector<library_song_id_t> LibraryView::getSelectedSongs(){
  QModelIndexList selected = selectedIndexes();
  std::vector<library_song_id_t> selectedIds;
  std::set<int> rows;
  for(
    QModelIndexList::const_iterator it = selected.begin();
    it != selected.end();
    ++it
  )
  {
    rows.insert(it->row()); 
  }
  for(
    std::set<int>::const_iterator it = rows.begin();
    it != rows.end();
    ++it
  )
  {
    QSqlRecord libRecordToAdd = libraryModel->record(*it);
    selectedIds.push_back(libRecordToAdd.value(
      DataStore::getLibIdColName()).value<library_song_id_t>());
  }
  return selectedIds;
}

void LibraryView::addSongToAvailableMusic(){
  dataStore->addSongsToAvailableSongs(getSelectedSongs());
}

void LibraryView::deleteSongs(){
  dataStore->removeSongsFromLibrary(getSelectedSongs());
}


}//end namespace
