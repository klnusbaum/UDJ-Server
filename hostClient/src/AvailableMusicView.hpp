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
#ifndef AVAILABLE_MUSIC_VIEW_HPP
#define AVAILABLE_MUSIC_VIEW_HPP
#include <QTableView>
#include <vector>
#include "ConfigDefs.hpp"

class QSqlRelationalTableModel;
class QAction;

namespace UDJ{

class DataStore;

class AvailableMusicView : public QTableView{
Q_OBJECT
public:
  AvailableMusicView(DataStore *dataStore, QWidget *parent=0);
private:
  DataStore *dataStore;
  QSqlRelationalTableModel *availableMusicModel;  
  QAction *removeFromAvailableMusic;
  QAction *addToActivePlaylist;
  std::vector<library_song_id_t> getSelectedSongs() const;

  void createActions();

  static const QString& getRemoveMenuItemName(){
    static const QString removeMenuItemName = tr("Remove");
    return removeMenuItemName;
  }

  static const QString& getAdd2ActivePlaylistMenuItemName(){
    static const QString add2ActivePlaylistMenuItemName = 
      tr("Add To Active Playlist");
    return add2ActivePlaylistMenuItemName;
  }

private slots:
  void updateView();
  void handleContextMenuRequest(const QPoint &pos);
  void addSongsToActivePlaylist();
  void removeSongsFromAvailableMusic();
  void addSongToActivePlaylist(const QModelIndex& index);
};


} //end namespace
#endif //AVAILABLE_MUSIC_VIEW_HPP
