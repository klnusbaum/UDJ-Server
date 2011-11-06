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
#include "MusicLibrary.hpp"
#include "LibraryModel.hpp"
#include "UDJServerConnection.hpp"
#include "PlaybackWidget.hpp"

class QTabWidget;
class QPushButton;
class QAction;
class QLabel;
class QSplitter;
class QStackedWidget;

namespace UDJ{

class SettingsWidget;
class PlaylistView;
class LibraryView;
class ActivityList;
class PartyWidget;

/**
 * \brief A class that is the main point of interaction with the user. 
 * 
 * This is the main window with which the user will interact. It contains
 * all information about the current playlist, their music library, which
 * partiers are currently logged into their party, and any relevant 
 * settings.
 */
class MetaWindow : public QMainWindow{
  Q_OBJECT
public:
  /** @name Constructor(s) */
  //@{

  /** \brief Constructs a MetaWindow
   *
   * @param serverConnection A connection to a UDJ server.
   */
  MetaWindow(
    UDJServerConnection *serverConnection,
    QWidget *parent=0, 
    Qt::WindowFlags flags=0);

  //@}

private slots:

  /** @name Private Slots */
  //@{

  /**
   * \brief Set's the users music library to a user selected directory.
   */
  void setMusicDir();

  void displayLibrary();

  void displayPartyWidget();

  void displayPlaylist(playlistid_t playlist);

  
  //@}

private:
  /** @name Private Members */
  //@{
  
  /** \brief The main widget holding all the various tabs in the display. */
  QTabWidget *tabs;
  /** \brief Used to display the contents of the users media library */
  LibraryView* libraryView;
  /** \brief The users media library */
  MusicLibrary* musicLibrary;
  /** \brief A widget used for displaying and modifying settings */
  SettingsWidget* settingsWidget;
  /** \brief A connection with the UDJ server */
	UDJServerConnection* serverConnection;

  /** \brief Triggers selection of music directory. */
  QAction *setMusicDirAction;
 
  /** \brief Causes the application to quit. */
  QAction *quitAction;
 
//  QFileSystemWatcher* fileWatcher;

  LibraryModel *libraryModel;

  QWidget *mainWidget;
  
  ActivityList *activityList;

  PlaybackWidget *playbackWidget;

  PartyWidget *partyWidget;
  QStackedWidget *contentStack;



  //@}

  /** @name Private Functions */
  //@{

  /** \brief Sets up all the MetaWindow's UI components. */
  void setupUi();
  /** \brief Sets up the MetaWindow's menus. */
  void setupMenus();

  void createActions();
  
  //@}

};


} //end namespace 
#endif //METAWINDOW_HPP
