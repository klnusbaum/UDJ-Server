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
#include <phonon/audiooutput.h>
#include <phonon/seekslider.h>
#include <phonon/mediaobject.h>
#include <phonon/volumeslider.h>
#include <phonon/audiooutput.h>
#include <QSqlTableModel>
#include "MusicLibrary.hpp"
#include "LibraryModel.hpp"
#include "UDJServerConnection.hpp"

class QTabWidget;
class QPushButton;
class QAction;
class QLabel;

namespace UDJ{

class SettingsWidget;
class PlaylistView;
class LibraryView;
class PartiersView;

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
  MetaWindow(QWidget *parent=0, Qt::WindowFlags flags=0);

  //@}

private slots:

  /** @name Private Slots */
  //@{

  /**
   * \brief Handles whenever the state of the primary
   * MediaObject is changed. 
   *
   * @param newState The new state of the primary MediaObject.
   * @parma oldState The old state of the primary MediaObject.
   */
  void stateChanged(Phonon::State newState, Phonon::State oldState);
  
  /** \brief Called when ever the primary MediaObject "ticks" 
   *
   * @param time The current time of the primary MediaObject.
   */
  void tick(qint64 time);

  /**
   * \brief Called whenever media source of the primary MediaObject is changed.
   *
   * @param source The new source of the primary MediaObject.
   */
  void sourceChanged(const Phonon::MediaSource &source);

  /**
   * \brief Set's the users music library to a user selected directory.
   */
  void setMusicDir();
  
  /**
   * \brief Called whenever the playlist is clicked.
   *
   * @param index The index of the item in the playlist that was clicked.
   */
  void playlistClicked(const QModelIndex& index);

  /**
   * \brief Called whenever the current song being played is about to finish.
   */
  void aboutToFinish();

  /**
   * \brief Called when the primary media object has finished playing it's
   * current song.
   */
   void finished();

   void doLogin();
  
  //@}

private:
  /** @name Private Members */
  //@{
  
  /** \brief Used to display the name of the currently playing song. */
	QLabel *songTitle;
  /** \bried Used to display the time played of the current song. */
  QLabel *timeLabel;
  /** \brief The main widget holding all the various tabs in the display. */
  QTabWidget *tabs;
  /** \brief The main seeker to change the songs current playback position. */
  Phonon::SeekSlider *seekSlider;
  /** \brief The primary media object used for song playback. */
  Phonon::MediaObject *mediaObject;
  /** \brief The primary audioOutput device used for song playback. */
  Phonon::AudioOutput *audioOutput;
  /** \brief The volume slider used to control playback volume. */
  Phonon::VolumeSlider *volumeSlider;
  /** \brief Used to display the contents of the users media library */
  LibraryView* libraryView;
  /** \brief Used to display the current song playlist. */
  PlaylistView* mainPlaylist;
  /** \brief Used to display the list of partiers currently logged into 
  the party.*/
  PartiersView* partiersView;
  /** \brief The users media library */
  MusicLibrary* musicLibrary;
  /** \brief A widget used for displaying and modifying settings */
  SettingsWidget* settingsWidget;
  /** \brief A connection with the UDJ server */
	UDJServerConnection* serverConnection;

  /** \brief Causes playback to start */
  QAction *playAction;
  /** \brief Pauses playback */
  QAction *pauseAction;
  /** \brief Stops playback */
  QAction *stopAction;
  /** \brief Triggers selection of music directory. */
  QAction *setMusicDirAction;
  /** \brief Causes the application to quit. */
  QAction *quitAction;
//  QFileSystemWatcher* fileWatcher;

  LibraryModel *libraryModel;


  QPushButton *loginButton;
  //@}

  /** @name Private Functions */
  //@{

  /** \brief Sets up all the actions used by the MetaWindow. */
  void createActions();
  /** \brief Sets up all the MetaWindow's UI components. */
  void setupUi();
  /** \brief Sets up the MetaWindow's menus. */
  void setupMenus();
  
  //@}

};


} //end namespace 
#endif //METAWINDOW_HPP
