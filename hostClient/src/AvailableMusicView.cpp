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
#include "AvailableMusicView.hpp"
#include "DataStore.hpp"
#include "Utils.hpp"
#include <QSqlRelationalTableModel>
#include <QAction>
#include <QMenu>
#include <QModelIndex>
#include <QSqlRecord>
#include <QHeaderView>
#include <set>


namespace UDJ{


AvailableMusicView::AvailableMusicView(DataStore *dataStore, QWidget *parent):
  QTableView(parent),
  dataStore(dataStore)
{
  setEditTriggers(QAbstractItemView::NoEditTriggers);
  availableMusicModel = 
    new QSqlRelationalTableModel(this, dataStore->getDatabaseConnection());
  setModel(availableMusicModel);
  availableMusicModel->setTable(DataStore::getAvailableMusicViewName());
  availableMusicModel->select();
  horizontalHeader()->setStretchLastSection(true);
  setSelectionBehavior(QAbstractItemView::SelectRows);
  setContextMenuPolicy(Qt::CustomContextMenu);
  createActions();
  connect(this, SIGNAL(customContextMenuRequested(const QPoint&)),
    this, SLOT(handleContextMenuRequest(const QPoint&)));
  connect(
    dataStore,
    SIGNAL(availableSongsModified()),
    this,
    SLOT(updateView()));
  connect(
    this,
    SIGNAL(activated(const QModelIndex&)),
    this,
    SLOT(addSongToActivePlaylist(const QModelIndex&)));
}

void AvailableMusicView::createActions(){
  removeFromAvailableMusic = new QAction(getRemoveMenuItemName(), this); 
  addToActivePlaylist = new QAction(getAdd2ActivePlaylistMenuItemName(), this);
  connect(
    removeFromAvailableMusic,
    SIGNAL(triggered()),
    this,
    SLOT(removeSongsFromAvailableMusic()));
  connect(
    addToActivePlaylist,
    SIGNAL(triggered()),
    this,
    SLOT(addSongsToActivePlaylist()));
}

void AvailableMusicView::handleContextMenuRequest(const QPoint &pos){
  QMenu contextMenu(this);
  contextMenu.addAction(addToActivePlaylist);
  contextMenu.addAction(removeFromAvailableMusic);
  contextMenu.exec(QCursor::pos());
}

void AvailableMusicView::addSongsToActivePlaylist(){
  dataStore->addSongsToActivePlaylist(Utils::getSelectedIds<library_song_id_t>(
    this,
    availableMusicModel,
    DataStore::getActivePlaylistLibIdColName()));
}

void AvailableMusicView::removeSongsFromAvailableMusic(){
  dataStore->removeSongsFromAvailableMusic(
    Utils::getSelectedIds<library_song_id_t>(
      this,
      availableMusicModel,
      DataStore::getActivePlaylistLibIdColName()));
}

void AvailableMusicView::updateView(){
  availableMusicModel->select();
}

void AvailableMusicView::addSongToActivePlaylist(const QModelIndex& index){
  QSqlRecord songToPlayRecord = availableMusicModel->record(index.row());
  QVariant data = 
    songToPlayRecord.value(DataStore::getAvailableEntryLibIdColName());
  dataStore->addSongToActivePlaylist(data.value<library_song_id_t>());
}

} //end namespace
