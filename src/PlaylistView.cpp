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
#include "PlaylistView.hpp"
#include "MusicLibrary.hpp"
#include <QHeaderView>
#include <QSqlRecord>
#include <QSqlField>
#include "PlaylistDelegate.hpp"
#include "PlaylistModel.hpp"

namespace UDJ{

PlaylistView::PlaylistView(MusicLibrary* musicLibrary, QWidget* parent):
  QTableView(parent),
  musicLibrary(musicLibrary),
  database(musicLibrary->database())
{
  playlistModel = new PlaylistModel(this, database);
  horizontalHeader()->setStretchLastSection(true);
  setItemDelegateForColumn(6, new PlaylistDelegate(this));
  setModel(playlistModel);
  setColumnHidden(0,true);
  setColumnHidden(1,true);
  setColumnHidden(5,true);
  setSelectionBehavior(QAbstractItemView::SelectRows);
}
  
void PlaylistView::addSongToPlaylist(const QModelIndex& libraryIndex){
  QString libraryId = musicLibrary->data(
    libraryIndex.sibling(libraryIndex.row(),0)).toString();
	QSqlRecord toInsert;
	toInsert.append(QSqlField("libraryId", QVariant::Int));
	toInsert.setValue(0, libraryId);
	EXEC_SQL(
		"Adding to playlist failed", 
		playlistModel->insertRecord(-1, toInsert), 
		(*playlistModel))
}

QString PlaylistView::getFilePath(const QModelIndex& songIndex) const{
  QModelIndex filePathIndex = songIndex.sibling(songIndex.row(), 5);
  return playlistModel->data(filePathIndex).toString();
}

void PlaylistView::removeSong(const QModelIndex& index){
	EXEC_SQL(
		"Error deleting song", 
		playlistModel->removeRow(index.row()), 
		(*playlistModel) ) 
}


} //end namespace

