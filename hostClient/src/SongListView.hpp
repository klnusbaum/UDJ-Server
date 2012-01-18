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
#ifndef SONG_LIST_VIEW_HPP
#define SONG_LIST_VIEW_HPP
#include "ConfigDefs.hpp"
#include <QTableView>
#include "DataStore.hpp"

class QAction;


namespace UDJ{

class DataStore;
class MusicModel;

/**
 * \brief Used to dislay the song list.
 */
class SongListView : public QTableView{
Q_OBJECT
public:
  /** @name Constructors */
  //@{

  /**
   * \brief Constructs an SongListView.
   *
   * @param dataStore The DataStore backing this instance of UDJ.
   * @param parent The parent widget.
   */
  SongListView(DataStore *dataStore, QWidget *parent=0);

  //@}

signals:
  void canNoLongerDisplay();

public slots:
  void setSongListId(song_list_id_t songListId);

private:
  /** @name Private Memeber */
  //@{

  void createActions();

  /**
   * \brief The data store containing music that could potentially be added
   * to the playlist.
   */
  DataStore *dataStore;

  QAction *removeFromSongList;

  song_list_id_t currentSongListId;
 
  /** \brief The model backing this view. */
  MusicModel *songListEntryModel;  


  //@}

  /** @name Private Functions */
  //@{
 
private slots:
  /** @name Private Slots */
  //@{

  /** 
   * \brief Updates the data being displayed in the view.
   */
  void onSongListEntriesChanged(song_list_id_t updatedSongList);

  /**
   * \brief Displays context menus when requested.
   *
   * @param pos The position where the context menu should be displayed.
   */ 
  void handleContextMenuRequest(const QPoint &pos);

  void onSongListDelete(song_list_id_t deletedId);

  void removeSelectedSongsFromList();

  static QString getQuery(song_list_id_t songList){
    return 
      "SELECT "+
      DataStore::getLibraryTableName() + "." + 
        DataStore::getLibIdColName() + " AS " +
        DataStore::getLibIdAlias() +", " +
      DataStore::getLibraryTableName() + "." + 
        DataStore::getLibSongColName() + ", " +
      DataStore::getLibraryTableName() + "." + 
        DataStore::getLibArtistColName() + ", " +
      DataStore::getLibraryTableName() + "." + 
        DataStore::getLibAlbumColName() + ", " +
      DataStore::getLibraryTableName() + "." + 
        DataStore::getLibDurationColName() + ", " +
      DataStore::getSongListEntryTableName() + "." + 
        DataStore::getSongListEntryIdColName() + " " +
      "FROM " + DataStore::getSongListEntryTableName() + 
      " INNER JOIN " + DataStore::getLibraryTableName() + 
      " ON " + 
      DataStore::getSongListEntryTableName() + "." + 
         DataStore::getSongListEntrySongIdColName() + "=" +
      DataStore::getLibraryTableName() + "." + DataStore::getLibIdColName() + 
      " WHERE " + 
      DataStore::getSongListEntryTableName() + "." + 
        DataStore::getSongListEntrySongListIdColName() + 
      "=" + QString::number(songList) + ";";
  }

  void configHeaders();
  //@}
};


} //end namespace
#endif //SONG_LIST_VIEW_HPP
