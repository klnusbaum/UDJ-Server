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
#include "ActivePlaylistModel.hpp"

namespace UDJ{

ActivePlaylistModel::ActivePlaylistModel(
	MusicLibrary* library,
	QObject* parent):
	QSqlRelationalTableModel(parent, library->getDatabaseConnection()),
	musicLibrary(library)
{
  setTable(MusicLibrary::getActivePlaylistViewName());
  select();
  setEditStrategy(QSqlTableModel::OnFieldChange);
}

Qt::ItemFlags ActivePlaylistModel::flags(const QModelIndex& index) const{
	Qt::ItemFlags fromParent = QSqlRelationalTableModel::flags(index);	
	if(index.column() != 6){
		int mask = ~Qt::ItemIsEditable;
		fromParent &= mask;
	}
	return fromParent;
}

bool ActivePlaylistModel::updateVoteCount(const QModelIndex& index, int difference){
	if(index.column() != 6 || !index.isValid()){
		return false;
	}
	const QModelIndex plIdIndex = index.sibling(index.row(), 0);
	playlist_song_id_t plId = data(plIdIndex).value<playlist_song_id_t>();
	if(musicLibrary->alterVoteCount(plId, difference)){
		select();
	}
	else{
		//TODO should show error
	}
}

bool ActivePlaylistModel::addSongToPlaylist(library_song_id_t libraryId){
	bool success = musicLibrary->addSongToActivePlaylist(libraryId);
	if(success){
		select();
	}
	return success;
}

bool ActivePlaylistModel::removeSongFromPlaylist(const QModelIndex& index){
	playlist_song_id_t plId = data(index.sibling(index.row(), 0)).value<playlist_song_id_t>();
	bool toReturn = musicLibrary->removeSongFromActivePlaylist(plId);
	if(toReturn){
		select();
	}
}

QString ActivePlaylistModel::getFilePath(const QModelIndex& songIndex) const{
  QModelIndex filePathIndex = 
    songIndex.sibling(songIndex.row(), getFilePathColIndex());
  return data(filePathIndex).toString();
}

} //end namespace
