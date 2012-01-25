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
#include "ActivePlaylistView.hpp"
#include "MusicModel.hpp"
#include "Utils.hpp"
#include <QHeaderView>
#include <QSqlRecord>
#include <QAction>
#include <QMenu>
#include <QContextMenuEvent>

namespace UDJ{

ActivePlaylistView::ActivePlaylistView(DataStore* dataStore, QWidget* parent):
  QTableView(parent),
  dataStore(dataStore)
{
  setContextMenuPolicy(Qt::CustomContextMenu);
  setEditTriggers(QAbstractItemView::NoEditTriggers);
  model = new MusicModel(getDataQuery(), dataStore, this);
  verticalHeader()->hide();
  horizontalHeader()->setStretchLastSection(true);
  createActions();
  setModel(model);
  setSelectionBehavior(QAbstractItemView::SelectRows);
  configureHeaders();
  connect(
    dataStore,
    SIGNAL(activePlaylistModified()),
    model, 
    SLOT(refresh()));
  connect(
    this,
    SIGNAL(activated(const QModelIndex&)),
    this,
    SLOT(setCurrentSong(const QModelIndex&)));
  connect(this, SIGNAL(customContextMenuRequested(const QPoint&)),
    this, SLOT(handleContextMenuRequest(const QPoint&)));
  connect(
    selectionModel(),
    SIGNAL(selectionChanged(const QItemSelection&, const QItemSelection&)),
    this,
    SLOT(handleSelectionChange(const QItemSelection&, const QItemSelection&)));
}

void ActivePlaylistView::configureHeaders(){
  QSqlRecord record = model->record();
  int idIndex = record.indexOf(DataStore::getActivePlaylistIdColName());
  int downVoteIndex = record.indexOf(DataStore::getDownVoteColName());
  int upVoteIndex = record.indexOf(DataStore::getUpVoteColName());
  int adderNameIndex = record.indexOf(DataStore::getAdderUsernameColName());
  int timeAddedIndex = record.indexOf(DataStore::getTimeAddedColName());
  setColumnHidden(idIndex, true);
  model->setHeaderData(
    downVoteIndex, Qt::Horizontal, tr("Down Votes"), Qt::DisplayRole);
  model->setHeaderData(
    upVoteIndex, Qt::Horizontal, tr("Up Votes"), Qt::DisplayRole);
  model->setHeaderData(
    adderNameIndex, Qt::Horizontal, tr("Adder"), Qt::DisplayRole);
  model->setHeaderData(
    timeAddedIndex, Qt::Horizontal, tr("Time Added"), Qt::DisplayRole);
}
  
void ActivePlaylistView::setCurrentSong(const QModelIndex& index){
  QSqlRecord songToPlayRecord = model->record(index.row());
  QVariant data = 
    songToPlayRecord.value(DataStore::getActivePlaylistIdColName());
  dataStore->setCurrentSong(data.value<playlist_song_id_t>());
}

void ActivePlaylistView::createActions(){
  removeSongAction = new QAction(tr("Remove Song"), this);
  connect(
    removeSongAction,
    SIGNAL(triggered()),
    this,
    SLOT(removeSongs()));
}

void ActivePlaylistView::handleContextMenuRequest(const QPoint& pos){
  QMenu contextMenu(this);
  contextMenu.addAction(removeSongAction);
  QAction *selected = contextMenu.exec(QCursor::pos());
  if(selected==NULL){
    selectionModel()->clear();
  }
  
}

void ActivePlaylistView::removeSongs(){
  dataStore->removeSongsFromActivePlaylist(
    Utils::getSelectedIds<playlist_song_id_t>(
      this,
      model,
      DataStore::getActivePlaylistIdColName()));
}

void ActivePlaylistView::handleSelectionChange(
  const QItemSelection& selected,
  const QItemSelection& deselected)
{
  if(selected.indexes().size() == 0){
    dataStore->resumePlaylistUpdates();
  }
  else{
    dataStore->pausePlaylistUpdates();
  }
}

} //end namespace

