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
#include "MusicModel.hpp"
#include "Utils.hpp"
#include <QAction>
#include <QMenu>
#include <QModelIndex>
#include <QSqlRecord>
#include <QHeaderView>
#include <QSortFilterProxyModel>
#include <set>


namespace UDJ{


AvailableMusicView::AvailableMusicView(DataStore *dataStore, QWidget *parent):
  QTableView(parent),
  dataStore(dataStore)
{
  setEditTriggers(QAbstractItemView::NoEditTriggers);
  availableMusicModel = new MusicModel(getDataQuery(), dataStore, this);
  proxyModel = new QSortFilterProxyModel(this);
  proxyModel->setSourceModel(availableMusicModel);

  setModel(proxyModel);
  setSortingEnabled(true);
  verticalHeader()->hide();
  horizontalHeader()->setStretchLastSection(true);
  configHeaders();
  setSelectionBehavior(QAbstractItemView::SelectRows);
  setContextMenuPolicy(Qt::CustomContextMenu);
  createActions();
  connect(this, SIGNAL(customContextMenuRequested(const QPoint&)),
    this, SLOT(handleContextMenuRequest(const QPoint&)));
  connect(
    this,
    SIGNAL(activated(const QModelIndex&)),
    this,
    SLOT(addSongToActivePlaylist(const QModelIndex&)));
  connect(
    dataStore,
    SIGNAL(availableSongsModified()),
    availableMusicModel,
    SLOT(refresh()));
}

void AvailableMusicView::configHeaders(){
  QSqlRecord record = availableMusicModel->record();
  int syncIndex =   
    record.indexOf(DataStore::getAvailableEntrySyncStatusColName());
  int libIdIndex =
    record.indexOf(DataStore::getAvailableEntryLibIdColName());
  int durationIndex = record.indexOf(DataStore::getLibDurationColName());
  setColumnHidden(syncIndex, true);
  setColumnHidden(libIdIndex, true);
  resizeColumnToContents(durationIndex);
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
    DataStore::getAvailableEntryLibIdColName(),
    proxyModel));
}

void AvailableMusicView::removeSongsFromAvailableMusic(){
  dataStore->removeSongsFromAvailableMusic(
    Utils::getSelectedIds<library_song_id_t>(
      this,
      availableMusicModel,
      DataStore::getAvailableEntryLibIdColName(),
      proxyModel));
}

void AvailableMusicView::addSongToActivePlaylist(const QModelIndex& index){
  QSqlRecord songToPlayRecord = 
    availableMusicModel->record(proxyModel->mapToSource(index).row());
  QVariant data = 
    songToPlayRecord.value(DataStore::getAvailableEntryLibIdColName());
  dataStore->addSongToActivePlaylist(data.value<library_song_id_t>());
}

} //end namespace
