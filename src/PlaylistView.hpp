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
#ifndef PLAYLIST_WIDGET_HPP
#define PLAYLIST_WIDGET_HPP
#include <QTableView>
#include <QSqlDatabase>

class QSqlTableModel;

namespace UDJ{

class MusicLibrary;


class PlaylistView : public QTableView{
Q_OBJECT
public:
  PlaylistView(MusicLibrary* musicLibrary, QWidget* parent=0);
  QString getFilePath(const QModelIndex& songIndex) const;
public slots:
  void addSongToPlaylist(const QModelIndex& libraryIndex);
private slots:
void updateView(
  const QModelIndex& topLeft, 
  const QModelIndex& /*bottomRight*/);
private:
  MusicLibrary* musicLibrary;
  QSqlDatabase database;
  QSqlTableModel* playlistModel;
};


} //end namespace
#endif //PLAYLIST_WIDGET_HPP
