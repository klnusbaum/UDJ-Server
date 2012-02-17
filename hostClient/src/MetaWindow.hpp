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
#ifndef METAWINDOW_HPP
#define MEATWINDOW_HPP
#include <QMainWindow>
#include <QTableView>
#include <QSqlDatabase>
//#include <QFileSystemWatcher>
#include <QSqlTableModel>
#include "UDJServerConnection.hpp"
#include "PlaybackWidget.hpp"

class QTabWidget;
class QPushButton;
class QAction;
class QLabel;
class QSplitter;
class QStackedWidget;
class QCloseEvent;

namespace UDJ{

class SettingsWidget;
class PlaylistView;
class LibraryView;
class ActivityList;
class EventWidget;
class DataStore;
class SongListView;

/**
 * \brief A class that is the main point of interaction with the user. 
 * 
 * This is the main window with which the user will interact. It contains
 * all information about the current playlist, their music library, which
 * event goers are currently logged into their event, and any relevant 
 * settings.
 */
class MetaWindow : public QMainWindow{
  Q_OBJECT
public:
  /** @name Constructor(s) */
  //@{

  /** \brief Constructs a MetaWindow
   *
   * @param ticketHash Ticket hash that should be used by the data store.
   * @param userId UserId that should be used by the data store.
   */
  MetaWindow(
    const QString& username,
    const QString& password,
    const QByteArray& ticketHash,
    const user_id_t& userId,
    QWidget *parent=0, 
    Qt::WindowFlags flags=0);

  //@}

protected:
  virtual void closeEvent(QCloseEvent *event);

private slots:

  /** @name Private Slots */
  //@{

  /**
   * \brief Displays stuff for adding songs to a library.
   */
  void addMusicToLibrary();

  void addSongToLibrary();

  /**
   * \brief Displays the library view in the main content panel.
   */
  void displayLibrary();

  /**
   * \brief Displays the event widget in the main content panel.
   */
  void displayEventWidget();

  void displaySongList(song_list_id_t songListId);
  
  //@}

private:
  /** @name Private Members */
  //@{
  
  /** \brief The main widget holding all the various tabs in the display. */
  QTabWidget *tabs;
  /** \brief Used to display the contents of the users media library */
  LibraryView* libraryView;
  /** \brief The users media library */
  DataStore* dataStore;
  /** \brief A widget used for displaying and modifying settings */
  SettingsWidget* settingsWidget;

  /** \brief Triggers selection of music directory. */
  QAction *addMusicAction;

  /** \brief Causes the application to quit. */
  QAction *quitAction;

  QAction *addSongAction;

//  QFileSystemWatcher* fileWatcher;


  /** \brief The main display widget. */
  QWidget *mainWidget;
  
  /** \brief The list of potential activites that can be done in UDJ. */
  ActivityList *activityList;

  /** \brief Widget used for controlling music playback. */
  PlaybackWidget *playbackWidget;

  /** \brief Widget used for displaying event related UI components. */
  EventWidget *eventWidget;

  SongListView *songListView;

  /** \brief Stack used to display various UI components. */
  QStackedWidget *contentStack;

  //@}

  /** @name Private Functions */
  //@{

  /** \brief Sets up all the MetaWindow's UI components. */
  void setupUi();
  /** \brief Sets up the MetaWindow's menus. */
  void setupMenus();

  /** \brief Creates the actions used in the MetaWindow */
  void createActions();

  //@}

};


} //end namespace 
#endif //METAWINDOW_HPP
