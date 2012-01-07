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
#ifndef ACTIVITY_LIST_HPP
#define ACTIVITY_LIST_HPP
#include <QTreeView>
#include "ConfigDefs.hpp"

class QStandardItemModel;
class QStandardItem;

namespace UDJ{


class DataStore;


/**
 * \brief Displays the various activities that can be done in UDJ.
 */
class ActivityList : public QTreeView{
Q_OBJECT
public:
  /** @name Constructors */
  //@{

  /**
   * \brief Constructs an ActivityList
   *
   * @param dataStore The DataStore backing this instance of UDJ.
   * @param parent The parent widget.
   */
  ActivityList(DataStore *dataStore, QWidget *parent=0);

  //@}

signals:
  /** @name Signals */
  //@{

  /** 
   * \brief Emitted when the library activity is clicked.
   */
  void libraryClicked();

  /** 
   * \brief emited when the event activity is clicked.
   */
  void eventClicked();
//  void playlistClicked(playlist_id_t playlistId);

  //@}

private:
  
  /** @name Private Functions */
  //@{

  /** 
   * \brief Does UI initialization.
   */
  void setupUi();
  
  /** 
   * \brief Gets the name of the library activity.
   *
   * @return The name of the library activity.
   */
  static const QString& getLibraryTitle(){
    static const QString libraryTitle(tr("Library"));
    return libraryTitle;
  }

  /** 
   * \brief Gets the name of the event activity.
   *
   * @return The name of the event activity.
   */
  static const QString& getEventTitle(){
    static const QString eventTitle(tr("Event"));
    return eventTitle;
  }

  static const QString& getSongListTitle(){
    static const QString songListTitle(tr("Song Lists"));
    return songListTitle;
  }

  static const QString& getNewSongListTitle(){
    static const QString newSongListTitle(tr("New Song List"));
    return newSongListTitle;
  }

  

  //@}

  /** @name Private Memeber */
  //@{

  /** \brief Pointer to the DataStore backing this instance of UDJ */
  DataStore *dataStore;

  /** \brief Model used to list the activities. */
  QStandardItemModel *model;

  QStandardItem *songListRoot;

  //@}

private slots:

  /** @name Private Slots */
  //@{

  /**
   * \brief Makes appropriate ui changes when the activity at the given index
   * is clicked.
   *
   * @param index The index of the activity that was clicked.
   */
  void itemClicked(const QModelIndex& index);


  //@}
};


}//end namespace UDJ
#endif //ACTIVITY_LIST_HPP
