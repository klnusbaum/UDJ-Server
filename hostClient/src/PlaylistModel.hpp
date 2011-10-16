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
#include "MusicLibrary.hpp"

namespace UDJ{

/** 
 * \brief A model representing the data in the Playlist.
 */
class PlaylistModel : public QSqlRelationalTableModel{
Q_OBJECT
public:
  /** @name Constructor(s) */
  //@{

  /**
   * \brief Constructs a playlist model.
   *
   * @param serverConnection The connection the the UDJ server.
   * @param parent The parent QObject.
   */
	PlaylistModel(MusicLibrary *library, QObject* parent=0);

  //@}

  /** @name Overriden from QSqlRelationalTableModel */
  //@{

  /** \brief . */
	virtual Qt::ItemFlags flags(const QModelIndex& index) const;

  //@}

  /** @name Getters and Setters */
  //@{

  /**
   * \brief Changes the vote count at of the playlist item located at index.
   *
   * Depending on the value of difference, this function either increments
   * or decrements the vote count of the playlist item located at index.
   *
   * @param index The index of the playlist item whose vote count is to be
   * changed.
   * @param difference The change in number that should be applied to the 
   * playlist item's vote count.
   * @return True if changing the vote count was sucessful, false otherwise.
   */
	bool updateVoteCount(const QModelIndex& index, int difference);
  
  /**
   * \brief Adds a song to the playlist.
   *
   * @param libraryId The library id of the song to be added to the playlist.
   * @return True if the song was sucessfully added to the playlist,
   * false otherwise.
   */
	bool addSongToPlaylist(library_song_id_t libraryId);
  
  /**
   * \brief Removes a song from the playlist.
   *
   * @param index Index of the song to be removed.
   * @return True if the song was sucessfully removed, false otherwise.
   */
	bool removeSongFromPlaylist(const QModelIndex& index);

  QString getFilePath(const QModelIndex& songIndex) const;

  //@}
private:

  static const int& getFilePathColIndex(){
    static const int filePathColIndex = 9;
    return filePathColIndex;
  }
  /** @name Private Members */
  //@{

  /** \brief The music library. */
	MusicLibrary* musicLibrary;

  //@}
};


} //end namespace
#endif //PLAYLIST_MODEL_HPP

