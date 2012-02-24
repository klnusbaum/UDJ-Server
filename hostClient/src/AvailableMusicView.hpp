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
#include "DataStore.hpp"
#include "ConfigDefs.hpp"

class QAction;
class QSortFilterProxyModel;

namespace UDJ{

class MusicModel;

/**
 * \brief Used to dislay the active playlist.
 */
class AvailableMusicView : public QTableView{
Q_OBJECT
public:
  /** @name Constructors */
  //@{

  /**
   * \brief Constructs an AvailableMusicView.
   *
   * @param dataStore The DataStore backing this instance of UDJ.
   * @param parent The parent widget.
   */
  AvailableMusicView(DataStore *dataStore, QWidget *parent=0);

  //@}

private:
  /** @name Private Memeber */
  //@{

  /**
   * \brief The data store containing music that could potentially be added
   * to the playlist.
   */
  DataStore *dataStore;

  /** \brief The model backing this view. */
  MusicModel *availableMusicModel;

  QSortFilterProxyModel *proxyModel;

  /** \brief Action for removing songs from the available music */
  QAction *removeFromAvailableMusic;

  /** \brief Action for adding songs to the active playlist. */
  QAction *addToActivePlaylist;

  //@}

  /** @name Private Functions */
  //@{
 
  /** 
   * \brief Initializes all the actions for this view.
   */
  void createActions();

  /** 
   * \brief Gets the text for the remove menu item.
   *
   * @return The text for the remove menu item.
   */
  static const QString& getRemoveMenuItemName(){
    static const QString removeMenuItemName = tr("Remove");
    return removeMenuItemName;
  }

  /** 
   * \brief Gets the text for the Add To Active Playlist menu item.
   *
   * @return The text for the Add To Active Playlist menu item. 
   */
  static const QString& getAdd2ActivePlaylistMenuItemName(){
    static const QString add2ActivePlaylistMenuItemName = 
      tr("Add To Active Playlist");
    return add2ActivePlaylistMenuItemName;
  }

private slots:
  /** @name Private Slots */
  //@{

  /**
   * \brief Displays context menus when requested.
   *
   * @param pos The position where the context menu should be displayed.
   */ 
  void handleContextMenuRequest(const QPoint &pos);

  /**
   * \brief Adds all the currently selected songs to the active playlist.
   */
  void addSongsToActivePlaylist();

  /** 
   * \brief Removes all the currently selected songs from the available music.
   */
  void removeSongsFromAvailableMusic();

  /** 
   * \brief Adds the song located at the given index to the active playlist.
   *
   * @param index Index of the song to be added to the active playlist.
   */
  void addSongToActivePlaylist(const QModelIndex& index);

  static const QString& getDataQuery(){
    static const QString dataQuery = 
      "SELECT " +
      DataStore::getLibraryTableName() + "." + 
        DataStore::getLibSongColName() + ", " +
      DataStore::getLibraryTableName() + "." + 
        DataStore::getLibArtistColName() + ", " +
      DataStore::getLibraryTableName() + "." + 
        DataStore::getLibAlbumColName() + ", " +
      DataStore::getLibraryTableName() + "." + 
        DataStore::getLibDurationColName() + ", " +
      DataStore::getAvailableMusicTableName() + "." + 
        DataStore::getAvailableEntryLibIdColName() + ", " +
      DataStore::getAvailableMusicTableName() + "." + 
        DataStore::getAvailableEntrySyncStatusColName() + " " +

      " FROM " + DataStore::getAvailableMusicTableName() + 
      " INNER JOIN " + DataStore::getLibraryTableName() +
      " ON " + DataStore::getAvailableMusicTableName() + "." +
      DataStore::getAvailableEntryLibIdColName() + "=" + 
      DataStore::getLibraryTableName() + "." + DataStore::getLibIdColName() +
      " AND " + DataStore::getAvailableMusicTableName() + "." + 
      DataStore::getAvailableEntryIsDeletedColName() + "=0;";
    return dataQuery;
  }

  void configHeaders();

  //@}
};


} //end namespace
#endif //AVAILABLE_MUSIC_VIEW_HPP
