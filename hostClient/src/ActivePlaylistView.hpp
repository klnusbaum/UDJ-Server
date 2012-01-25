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
#include "DataStore.hpp"

class QAction;

namespace UDJ{

class MusicModel;

/**
 * \brief Used to dislay the active playlist.
 */
class ActivePlaylistView : public QTableView{
Q_OBJECT
public:

  /** @name Constructors */
  //@{

  /**
   * \brief Constructs an ActivePlaylistView
   *
   * @param dataStore The DataStore backing this instance of UDJ.
   * @param parent The parent widget.
   */
  ActivePlaylistView(DataStore* dataStore, QWidget* parent=0);

  //@}

private:

  /** @name Private Functions */
  //@{

  /**
   * \brief Initializes actions used in the ActivePlaylistView
   */
  void createActions();

  /** @name Private Members */
  //@{

  /**
   * \brief The data store containing music that could potentially be added
   * to the playlist.
   */
  DataStore* dataStore;

  /**
   * \brief The model backing the view
   */
  MusicModel *model;

  /**
   * \brief Action used to remove songs from the active playlist.
   */
  QAction *removeSongAction;

  //@}

   /** @name Private Slots */
   //@{
private slots:

  /**
   * \brief Takes the given index, identifies the song it corresponds to,
   * and sets that as the current song being played.
   *
   * @param index The model index of the playlist entry that should be set
   *  as the currenty song.
   */
  void setCurrentSong(const QModelIndex& index);

  /**
   * \brief .
   */
  void handleContextMenuRequest(const QPoint& pos);

  /**
   * \brief .
   */
  void handleSelectionChange(
    const QItemSelection &selected, const QItemSelection &deselected);

  /**
   * \brief Removes all the currently selected songs from the active playlist.
   */
  void removeSongs();
  
  void configureHeaders();

  static const QString& getDataQuery(){
    static const QString dataQuery = 
      "SELECT " +
      DataStore::getActivePlaylistViewName() 
        + "." + DataStore::getActivePlaylistIdColName() + ", " +
      DataStore::getLibSongColName() + ", " +
      DataStore::getLibArtistColName() + ", " +
      DataStore::getLibAlbumColName() + ", " +
      DataStore::getUpVoteColName() + ", " +
      DataStore::getDownVoteColName() + ", " +
      DataStore::getLibDurationColName() + ", " +
      DataStore::getAdderUsernameColName() + ", " +
      DataStore::getTimeAddedColName() + 
      " FROM " + DataStore::getActivePlaylistViewName() + 
      " LEFT JOIN " + DataStore::getPlaylistRemoveRequestsTableName() + 
      " ON " + DataStore::getActivePlaylistViewName() + "." + 
        DataStore::getActivePlaylistIdColName() +
      "=" + DataStore::getPlaylistRemoveRequestsTableName() + "." +
        DataStore::getPlaylistRemoveEntryIdColName() + ";";
      " WHERE " + DataStore::getPlaylistRemoveRequestsTableName() + "." +
        DataStore::getPlaylistRemoveEntryIdColName() + 
      " is null;";
    return dataQuery;
  }

  //@}

};


} //end namespace
#endif //ACTIVE_PLAYLIST_VIEW_HPP
