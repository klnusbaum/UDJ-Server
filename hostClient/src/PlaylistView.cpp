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
#include "LibraryModel.hpp"

namespace UDJ{

PlaylistView::PlaylistView(MusicLibrary* musicLibrary, LibraryModel *libraryModel, QWidget* parent):
  QTableView(parent),
  musicLibrary(musicLibrary),
  libraryModel(libraryModel)
{
  playlistModel = new PlaylistModel(musicLibrary, this);
  horizontalHeader()->setStretchLastSection(true);
  setItemDelegateForColumn(6, new PlaylistDelegate(this));
  setModel(playlistModel);
  setSelectionBehavior(QAbstractItemView::SelectRows);
}
  
QString PlaylistView::getFilePath(const QModelIndex& songIndex) const{
  return playlistModel->getFilePath(songIndex);
}

void PlaylistView::addSongToPlaylist(const QModelIndex& libraryIndex){
  libraryid_t libraryId = libraryModel->data(
    libraryIndex.sibling(libraryIndex.row(),0)).value<libraryid_t>();
	if(! playlistModel->addSongToPlaylist(libraryId)){
		//TODO display error message
	}
}

void PlaylistView::removeSong(const QModelIndex& index){
	if(! playlistModel->removeSongFromPlaylist(index)){
		//TODO display error message
	}
}

bool PlaylistView::isVotesColumn(int columnIndex){
  return columnIndex == 3; 
}


} //end namespace

