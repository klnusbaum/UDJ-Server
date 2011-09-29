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
#ifndef MUSIC_LIBRARY_HPP
#define MUSIC_LIBRARY_HPP
#include <QSqlTableModel>
#include <QSqlDatabase>
#include <phonon/mediaobject.h>
#include <phonon/mediasource.h>
#include <QProgressDialog>
#include "ConfigDefs.hpp"
#include "UDJServerConnection.hpp"

namespace UDJ{

/** \brief A model representing the Hosts Music Library */
class MusicLibrary : public QSqlTableModel{
Q_OBJECT
public:

  /** @name Constructor(s) and Destructor */
  //@{

  /** \brief Constructs a MusicLibrary
   *
   * @param serverConnection Connection to the UDJ server.
   * @param parent The parent widget.
   */
  MusicLibrary(UDJServerConnection* serverConnection, QWidget* parent=0);

  /** \brief Does clean up when a Music Library is deallocated. */
  ~MusicLibrary();

  //@}

  /** @name Getters and Setters */
  //@{


  /**
   * \brief Sets the contents of the music library.
   *
   * Sets the hosts music library to a set of given songs. While doing this
   * a progress bar is updated in order to keep the user informed.
   *
   * @param songs Songs which the hosts library should contain.
   * @param progress A progress dialog to be updated as the music library
   * is updated.
   */
  void setMusicLibrary(QList<Phonon::MediaSource> songs, QProgressDialog& progress);

  /**
   * \brief Adds a single song to the music library.
   *
   * @param song Song to be added to the library.
   */
  void addSong(Phonon::MediaSource song);

  /**
   * \brief Given a media source, determines the song name from the current
   * model data.
   *
   * @param source Source whose song name is desired.
   * @return The name of the song contained in the given source according
   * to current model data. If the source could not be found in the model
   * and emptry string is returned.
   */
  QString getSongNameFromSource(const Phonon::MediaSource &source) const;

  //@}

  static const libraryid_t& getInvalidHostId(){
    static const libraryid_t invalidHostId = -1; 
    return invalidHostId;
  }

  static const libraryid_t& getInvalidServerId(){
    static const libraryid_t invalidServerId = -1; 
    return invalidServerId;
  }

private:
  
  /** @name Private Members */
  //@{

  /** \brief Object used to determine metadata of MediaSources. */
  Phonon::MediaObject* metaDataGetter;
  /** \brief The connection to the UDJ server. */
	UDJServerConnection* serverConnection;
  
  //@}

  /** @name Private Functions */
  //@{

  /**
   * \brief Determines the name of a song contained in a given MediaSource.
   *
   * Given a media source, this funciton uses a MediaObject to determine
   * the name of the song in the media source.
   *
   * @param song Song for which the name is desired.
   * @return Name of the given song.
   */
  QString getSongName(Phonon::MediaSource song) const;

  /**
   * \brief Determines the artist of a song contained in a given MediaSource.
   *
   * Given a media source, this funciton uses a MediaObject to determine
   * the artist of the song in the media source.
   *
   * @param song Song for which the artist is desired.
   * @return Artist of the given song.
   */
  QString getArtistName(Phonon::MediaSource song) const;

  /**
   * \brief Determines the album of a song contained in a given MediaSource.
   *
   * Given a media source, this funciton uses a MediaObject to determine
   * the album of the song in the media source.
   *
   * @param song Song for which the album is desired.
   * @return Album of the given song.
   */
  QString getAlbumName(Phonon::MediaSource song) const;

  //@}
};


} //end namespace
#endif //MUSIC_LIBRARY_HPP
