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
#include <QSqlQuery>

namespace UDJ{

PlaylistModel::PlaylistModel(
	QObject* parent,
	QSqlDatabase db):
	QSqlRelationalTableModel(parent, db)
{
  setTable("main_playlist_view");
  select();
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
	int plId = data(plIdIndex).toInt();
	QSqlQuery updateQuery(
		"UPDATE main_playlist_view "
		"SET voteCount = (voteCount + ?) "
		"WHERE plId = ? ", 
		database());
	updateQuery.addBindValue(difference);
	updateQuery.addBindValue(plId);
	bool worked = updateQuery.exec();
	PRINT_SQLERROR("Updating vote count didn't work!", updateQuery);
	if(worked){
		select();
	}		
	
}

} //end namespace
