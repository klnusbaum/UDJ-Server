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
#ifndef PLAYLIST_MODEL_HPP
#define PLAYLIST_MODEL_HPP

#include <QSqlRelationalTableModel>
#include "ConfigDefs.hpp"

namespace UDJ{


class PlaylistModel : public QSqlRelationalTableModel{
Q_OBJECT
public:
	PlaylistModel(QObject* parent=0, QSqlDatabase db=QSqlDatabase());
	virtual Qt::ItemFlags flags(const QModelIndex& index) const;
};


} //end namespace
#endif //PLAYLIST_MODEL_HPP

