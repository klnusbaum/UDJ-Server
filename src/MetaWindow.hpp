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
//#include <QFileSystemWatcher>
#include <phonon/audiooutput.h>
#include <phonon/seekslider.h>
#include <phonon/mediaobject.h>
#include <phonon/volumeslider.h>
#include <phonon/audiooutput.h>
#include <QSqlTableModel>
#include "MusicLibrary.hpp"

class QTabWidget;
class QPushButton;
class QAction;

namespace UDJ{

class SettingsWidget;
class PlaylistWidget;
class LibraryView;

class MetaWindow : public QMainWindow{
  Q_OBJECT
public:
  MetaWindow();
private slots:
  void stateChanged(Phonon::State newState, Phonon::State oldState);
  void tick(qint64 time);
  void sourceChanged(const Phonon::MediaSource &source);
  void setMusicDir();
  void tableClicked(const QModelIndex& index);
  void addSongToPlaylist(const QModelIndex& index);
  
private:
  QTabWidget *tabs;
  Phonon::SeekSlider *seekSlider;
  Phonon::MediaObject *mediaObject;
  Phonon::AudioOutput *audioOutput;
  Phonon::VolumeSlider *volumeSlider;
  LibraryView* libraryView;
  PlaylistWidget* mainPlaylist;
  QTableView* partiersView;
  MusicLibrary* musicLibrary;
  SettingsWidget* settingsWidget;

  QAction *playAction;
  QAction *pauseAction;
  QAction *stopAction;
  QAction *setMusicDirAction;
  QAction *quitAction;

//  QFileSystemWatcher* fileWatcher;

  void createActions();
  void setupUi();
  void setupMenus();
  static QModelIndex getFilePathIndex(const QModelIndex& songIndex);
};


} //end namespace 
#endif //METAWINDOW_HPP
