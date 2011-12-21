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
#include "DataStore.hpp"
#include <QHeaderView>
#include <QSqlRelationalTableModel>
#include <QSqlRecord>
#include <QAction>
#include <QMenu>
#include <QContextMenuEvent>
#include <set>

namespace UDJ{

ActivePlaylistView::ActivePlaylistView(DataStore* dataStore, QWidget* parent):
  QTableView(parent),
  dataStore(dataStore)
{
  setContextMenuPolicy(Qt::CustomContextMenu);
  setEditTriggers(QAbstractItemView::NoEditTriggers);
  model = 
    new QSqlRelationalTableModel(this, dataStore->getDatabaseConnection());
  model->setTable(DataStore::getActivePlaylistViewName());
  model->select();
  verticalHeader()->hide();
  horizontalHeader()->setStretchLastSection(true);
  createActions();
  setModel(model);
  setSelectionBehavior(QAbstractItemView::SelectRows);
  connect(
    dataStore,
    SIGNAL(activePlaylistModified()),
    this, 
    SLOT(refreshDisplay()));
  connect(
    this,
    SIGNAL(activated(const QModelIndex&)),
    this,
    SLOT(setCurrentSong(const QModelIndex&)));
  connect(this, SIGNAL(customContextMenuRequested(const QPoint&)),
    this, SLOT(handleContextMenuRequest(const QPoint&)));
}
  
void ActivePlaylistView::refreshDisplay(){
  model->select();
}

void ActivePlaylistView::setCurrentSong(const QModelIndex& index){
  QSqlRecord songToPlayRecord = model->record(index.row());
  QVariant data = 
    songToPlayRecord.value(DataStore::getActivePlaylistIdColName());
  dataStore->setCurrentSong(data.value<playlist_song_id_t>());
}

std::vector<library_song_id_t> ActivePlaylistView::getSelectedSongs() const{
  QModelIndexList selected = selectedIndexes();
  std::vector<playlist_song_id_t> selectedIds;
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
    QSqlRecord playlistRecord = model->record(*it);
    selectedIds.push_back(playlistRecord.value(
      DataStore::getActivePlaylistIdColName()).value<playlist_song_id_t>());
  }
  return selectedIds;
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
  contextMenu.exec(QCursor::pos());
}

void ActivePlaylistView::removeSongs(){
  dataStore->removeSongsFromActivePlaylist(getSelectedSongs());
}

} //end namespace

