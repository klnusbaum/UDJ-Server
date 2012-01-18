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
#include "SongListView.hpp"
#include "DataStore.hpp"
#include "Utils.hpp"
#include "MusicModel.hpp"
#include <QSqlQuery>
#include <QAction>
#include <QMenu>
#include <QModelIndex>
#include <QSqlRecord>
#include <QHeaderView>


namespace UDJ{


SongListView::SongListView(DataStore *dataStore, QWidget *parent):
  QTableView(parent),
  dataStore(dataStore),
  currentSongListId(-1)
{
  setEditTriggers(QAbstractItemView::NoEditTriggers);
  createActions();
  songListEntryModel = 
    new MusicModel(getQuery(currentSongListId), dataStore, this);
  setModel(songListEntryModel);
  horizontalHeader()->setStretchLastSection(true);
  setSelectionBehavior(QAbstractItemView::SelectRows);
  setContextMenuPolicy(Qt::CustomContextMenu);
  connect(this, SIGNAL(customContextMenuRequested(const QPoint&)),
    this, SLOT(handleContextMenuRequest(const QPoint&)));
  connect(dataStore, SIGNAL(songListModified(song_list_id_t)),
    this, SLOT(onSongListEntriesChanged(song_list_id_t)));
  connect(dataStore, SIGNAL(songListDeleted(song_list_id_t)),
    this, SLOT(onSongListDelete(song_list_id_t)));
  songListEntryModel->refresh();
  configHeaders();
}

void SongListView::configHeaders(){
  QSqlRecord record = songListEntryModel->record();
  int libIdIndex = record.indexOf(DataStore::getLibIdAlias());
  int idIndex = record.indexOf(DataStore::getSongListEntryIdColName());
  int durationIndex = record.indexOf(DataStore::getLibDurationColName());
  setColumnHidden(libIdIndex, true);
  setColumnHidden(idIndex, true);
  resizeColumnToContents(durationIndex);

}

void SongListView::handleContextMenuRequest(const QPoint &pos){
  QMenu contextMenu(this);
  contextMenu.addAction(removeFromSongList);
  contextMenu.exec(QCursor::pos());
}

void SongListView::createActions(){
  removeFromSongList = new QAction(tr("Remove From Song List"), this);
  connect(
    removeFromSongList,
    SIGNAL(triggered()),
    this,
    SLOT(removeSelectedSongsFromList()));
}

void SongListView::onSongListEntriesChanged(
  song_list_id_t updatedSongList)
{
  if(updatedSongList==currentSongListId){ 
    /*QSqlQuery query("SELECT * FROM " +
    DataStore::getSongListEntryTableName() + " where " + 
    DataStore::getSongListEntrySongListIdColName() + "=?;",
    dataStore->getDatabaseConnection());
    query.addBindValue(QVariant::fromValue(currentSongListId));
    query.exec();
    songListEntryModel->setQuery(query);*/
    songListEntryModel->refresh();
  }
}

void SongListView::setSongListId(song_list_id_t songListId){
  currentSongListId = songListId;
  //onSongListEntriesChanged(currentSongListId);
  songListEntryModel->refresh(getQuery(currentSongListId));
}

void SongListView::onSongListDelete(song_list_id_t deletedId){
  if(deletedId == currentSongListId){
    emit canNoLongerDisplay();
  }
}

void SongListView::removeSelectedSongsFromList(){
  dataStore->removeSongsFromSongList(
    currentSongListId,
    Utils::getSelectedIds<song_list_entry_id_t>(
      this,
      songListEntryModel,
      DataStore::getSongListEntryIdColName()));
}


} //end namespace
