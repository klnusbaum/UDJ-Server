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
#include "UDJServerConnection.hpp"

namespace UDJ{

PlaylistView::PlaylistView(UDJServerConnection* serverConnection, MusicLibrary* musicLibrary, QWidget* parent):
  QTableView(parent),
  musicLibrary(musicLibrary),
  serverConnection(serverConnection)
{
  playlistModel = new PlaylistModel(serverConnection, this);
  horizontalHeader()->setStretchLastSection(true);
  setItemDelegateForColumn(6, new PlaylistDelegate(this));
  setModel(playlistModel);
  setColumnHidden(0,true);
  setColumnHidden(1,true);
  setColumnHidden(5,true);
  setSelectionBehavior(QAbstractItemView::SelectRows);
}
  
void PlaylistView::addSongToPlaylist(const QModelIndex& libraryIndex){
  int libraryId = musicLibrary->data(
    libraryIndex.sibling(libraryIndex.row(),0)).toInt();
	if(! playlistModel->addSongToPlaylist(libraryId)){
		//TODO display error message
	}
}

QString PlaylistView::getFilePath(const QModelIndex& songIndex) const{
  QModelIndex filePathIndex = songIndex.sibling(songIndex.row(), 5);
  return playlistModel->data(filePathIndex).toString();
}

void PlaylistView::removeSong(const QModelIndex& index){
	if(! playlistModel->removeSongFromPlaylist(index)){
		//TODO display error message
	}
}


} //end namespace

