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
#ifndef MUSIC_FINDER_HPP
#define MUSIC_FINDER_HPP

#include <QDir>
#include "phonon/mediasource.h"


namespace UDJ{

/**
 * \brief A class used to find music on a Host's computer.
 */
class MusicFinder{
public:
  /** @name Finder Function(s) */
  //@{

  /**
   * \brief Finds all the music in a given directory.
   *
   * Recusrively searchs this directory and all subdirectories looking
   * for any music files to be added to the users music library. It then
   * returns a list of MediaSources representing all of the found songs.
   *
   * @param musicDir The directory in which to search for music.
   * @return A list of MediaSources corresponding to each found song.
   */
  static QList<Phonon::MediaSource> findMusicInDir(const QString& musicDir);

  static QList<Phonon::MediaSource> findMusicInDirWithMatcher(
      const QString& musicDir, const QRegExp& fileMatcher);
  static QString getMusicFileExtFilter();
  //@}
private:
  /** @name Private Function(s) */
  //@{

  /**
   * Retrieves the regular expression used to help determine if a file
   * constains music.
   *
   * @return The regular expression user to help determine if a file
   * constains music.
   */
  static QRegExp getMusicFileMatcher();

  static QStringList availableMusicTypes();

  //@}
}; 


} //end namespace
#endif //MUSIC_FINDER_HPP
