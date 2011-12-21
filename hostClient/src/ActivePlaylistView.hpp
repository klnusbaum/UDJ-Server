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
#ifndef ACTIVE_PLAYLIST_VIEW_HPP
#define ACTIVE_PLAYLIST_VIEW_HPP
#include "ConfigDefs.hpp"
#include <QTableView>
#include <vector>

class QSqlRelationalTableModel;
class QAction;

namespace UDJ{

class DataStore;

/**
 * \brief Used to view the items in a PlaylistModel
 */
class ActivePlaylistView : public QTableView{
Q_OBJECT
public:

  /** @name Constructors */
  //@{

  /**
   * \brief Constructs a ActivePlaylistView
   *
   * @param dataStore The music library containing music that might be
   * added to the playlist.
   * @param parent The parent widget.
   */
  ActivePlaylistView(DataStore* dataStore, QWidget* parent=0);

  //@}

private:

  std::vector<playlist_song_id_t> getSelectedSongs() const;

  void createActions();

  /** @name Private Members */
  //@{

  /**
   * \brief The data store containing music that could potentially be added
   * to the playlist.
   */
  DataStore* dataStore;


  QSqlRelationalTableModel *model;

  QAction *removeSongAction;
  //@}

private slots:

  void refreshDisplay(); 

  void setCurrentSong(const QModelIndex& index);

  void handleContextMenuRequest(const QPoint& pos);

  void removeSongs();

};


} //end namespace
#endif //ACTIVE_PLAYLIST_VIEW_HPP
