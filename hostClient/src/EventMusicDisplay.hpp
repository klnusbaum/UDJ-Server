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
#ifndef EVENT_MUSIC_DISPLAY_HPP
#define EVENT_MUSIC_DISPLAY_HPP
#include <QWidget>

namespace UDJ{


class DataStore;

/** \brief Displays all the music related content for an Event */
class EventMusicDisplay : public QWidget{
Q_OBJECT
public:
  /** @name Constructors */
  //@{

  /**
   * \brief Constructs an Event Music Display.
   *
   * @param dataStore The DataStore backing this instance of UDJ.
   * @param parent The parent widget.
   */
  EventMusicDisplay(DataStore *dataStore, QWidget *parent=0);

  //@}
private:
  /** @name Private Memeber */
  //@{

  /**
   * \brief The data store backing this instance of UDJ.
   */
  DataStore *dataStore;
  
  //@}
};


} //end namespace
#endif //EVENT_MUSIC_DISPLAY_HPP
