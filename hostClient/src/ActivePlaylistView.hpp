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
#include <QTableView>
#include <QSqlDatabase>
#include <phonon/mediasource.h>


namespace UDJ{

class MusicLibrary;
class ActivePlaylistModel;
class LibraryModel;

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
   * @param musicLibrary The music library containing music that might be
   * added to the playlist.
   * @param parent The parent widget.
   */
  ActivePlaylistView(MusicLibrary* musicLibrary, LibraryModel *libraryModel, QWidget* parent=0);

  //@}

  QString getFilePath(const QModelIndex& songIndex) const;

  static bool isVotesColumn(int columnIndex);


public slots:

  /** @name Public slots */
  //@{

  /** 
   * \brief Adds song to the playlist.
   * 
   * @param libraryIndex Index in the library model corresponding to the
   * song that should be added.
   */
  void addSongToPlaylist(const QModelIndex& libraryIndex);
  
  /**
   * \brief Removes the given song from the playlist.
   * 
   * @param index The index in the playlist model that corresponds to the song
   * which should be removed.
   */
	void removeSong(const QModelIndex& index);

  //@}

private:

  /** @name Private Members */
  //@{

  /**
   * \brief The music library containing music that could potentially be added
   * to the playlist.
   */
  MusicLibrary* musicLibrary;

  LibraryModel* libraryModel;

  /** \brief The model containing the playlist data */
  ActivePlaylistModel* playlistModel;


  //@}

};


} //end namespace
#endif //PLAYLIST_VIEW_HPP
