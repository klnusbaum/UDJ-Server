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
#ifndef LIBRARY_VIEW_HPP
#define LIBRARY_VIEW_HPP
#include "ConfigDefs.hpp"
#include "DataStore.hpp"
#include <QTableView>

class QContextMenuEvent;

namespace UDJ{

class MusicModel;

/** 
 *\brief A class for viewing the current contents of the users music library.
 */
class LibraryView : public QTableView{
Q_OBJECT
public:
	/** @name Constructors */
  //@{

  /** \brief Constructs a LibraryView
   *
   * @param dataStore The data store being used by the applicaiton.
   * @param parent The parent widget
   */
  LibraryView(DataStore *dataStore, QWidget* parent=0);

  //@}
private slots:
  /** @name Private Slots */
  //@{

  /**
   * \brief Displays a context menu at the given position.
   *
   * @param pos The position where the context menu should be displayed.
   */
  void handleContextMenuRequest(const QPoint &pos);

private:

  /** @name Private Memeber */
  //@{

  /**
   * \brief The data store backing this instance of UDJ.
   */
  DataStore *dataStore;

  /** \brief The model backing LibraryView.  */
  MusicModel *libraryModel;

  /** \brief Action used for deleting songs from the library. */
  QAction *deleteSongAction;
 
  /** \brief Actions used for adding songs to the list of available songs. */
  QAction *addToAvailableMusicAction;

  //@}

  /** @name Private Functions */
  //@{

  /** \brief Initilaizes actions.  */
  void createActions();

  void configureColumns();

  /**
   * \brief Gets the name used for the delete context menu item.
   *
   * @return The name for the deleted context menu item.
   */
  static const QString& getDeleteContextMenuItemName(){
    static const QString deleteContextMenuItemName = tr("Delete");
    return deleteContextMenuItemName;
  }

  /**
   * \brief Gets the name used for the add to available music
   *  context menu item.
   *
   * @return The name for the add to available music  context menu item.
   */
  static const QString& getAddToAvailableContextMenuItemName(){
    static const QString addToAvailableContextMenuItemName = 
      tr("Add to Available Music");
    return addToAvailableContextMenuItemName;
  }

  //@}

private slots:
  /** @name Private Slots */
  //@{

  /** 
   * \brief Adds the currently selected songs to the list of available music.
   */
  void addSongToAvailableMusic();

  /** 
   * \brief Deletes the currently selected songs from the library.
   */
  void deleteSongs();

  void addSongsToSongList(song_list_id_t songListId);

  static const QString& getDataQuery(){
    static const QString dataQuery = 
      "SELECT " +
      DataStore::getLibIdColName() + ", " +
      DataStore::getLibSongColName() + ", " +
      DataStore::getLibArtistColName() + ", " +
      DataStore::getLibAlbumColName() + ", " +
      DataStore::getLibDurationColName() + ", " +
      DataStore::getLibFileColName() + " " +
      "FROM " + DataStore::getLibraryTableName() + " WHERE " +
      DataStore::getLibIsDeletedColName() + "=0 AND " +
      DataStore::getLibSyncStatusColName() + " != " +
      QString::number(DataStore::getLibNeedsAddSyncStatus()) + ";";
    return dataQuery;
  }

  //@}
};


}//end namespace
#endif //LIBRARY_VIEW_HPP
