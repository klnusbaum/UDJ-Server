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
#include "PlaylistModel.hpp"

namespace UDJ{

PlaylistModel::PlaylistModel(
	MusicLibrary* library,
	QObject* parent):
	QSqlRelationalTableModel(parent, library->getDatabaseConnection()),
	musicLibrary(library)
{
  setTable(MusicLibrary::getPlaylistViewName());
  select();
	//Need to make this more dependent on the info from the Music Library, i.e. Music Library needs to say what
  //the valid columns are
  setHeaderData(0, Qt::Horizontal, "playlist id");
  setHeaderData(1, Qt::Horizontal, "library id");
  setHeaderData(2, Qt::Horizontal, "Song");
  setHeaderData(3, Qt::Horizontal, "Artist");
  setHeaderData(4, Qt::Horizontal, "Album");
  setHeaderData(5, Qt::Horizontal, "Filepath");
  setHeaderData(6, Qt::Horizontal, "Votes");
  setHeaderData(7, Qt::Horizontal, "Time Added");
  setEditStrategy(QSqlTableModel::OnFieldChange);
}

Qt::ItemFlags PlaylistModel::flags(const QModelIndex& index) const{
	Qt::ItemFlags fromParent = QSqlRelationalTableModel::flags(index);	
	if(index.column() != 6){
		int mask = ~Qt::ItemIsEditable;
		fromParent &= mask;
	}
	return fromParent;
}

bool PlaylistModel::updateVoteCount(const QModelIndex& index, int difference){
	if(index.column() != 6 || !index.isValid()){
		return false;
	}
	const QModelIndex plIdIndex = index.sibling(index.row(), 0);
	playlistid_t plId = data(plIdIndex).value<playlistid_t>();
	if(musicLibrary->alterVoteCount(plId, difference)){
		select();
	}
	else{
		//TODO should show error
	}
}

bool PlaylistModel::addSongToPlaylist(libraryid_t libraryId){
	bool success = musicLibrary->addSongToPlaylist(libraryId);
	if(success){
		select();
	}
	return success;
}

bool PlaylistModel::removeSongFromPlaylist(const QModelIndex& index){
	playlistid_t plId = data(index.sibling(index.row(), 0)).value<playlistid_t>();
	bool toReturn = musicLibrary->removeSongFromPlaylist(plId);
	if(toReturn){
		select();
	}
}

} //end namespace
