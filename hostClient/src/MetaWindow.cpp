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
#include "MetaWindow.hpp"
#include <QSqlQuery>
#include <QHBoxLayout>
#include <QVBoxLayout>
#include <QAction>
#include <QTabWidget>
#include <QPushButton>
#include <QFileDialog>
#include <QProgressDialog>
#include <QMenuBar>
#include <QLabel>
#include <QInputDialog>
#include <QSplitter>
#include <QGridLayout>
#include "SettingsWidget.hpp"
#include "MusicFinder.hpp"
#include "MusicLibrary.hpp"
#include "PlaylistView.hpp"
#include "LibraryView.hpp"
#include "PartiersView.hpp"
#include "LibraryModel.hpp"
#include "ActivityList.hpp"


namespace UDJ{


MetaWindow::MetaWindow(
  UDJServerConnection *serverConnection, 
  QWidget *parent, 
  Qt::WindowFlags flags)
  :QMainWindow(parent,flags),
  serverConnection(serverConnection)
{
  serverConnection->setParent(this);

  createActions();
  setupUi();
  setupMenus();
}

void MetaWindow::setMusicDir(){
  //TODO: Check to see if musicDir is different than then current music dir
  QDir musicDir = QFileDialog::getExistingDirectory(this,
    tr("Pick you music folder"),
    QDir::homePath(),
    QFileDialog::ShowDirsOnly);
  QList<Phonon::MediaSource> newMusic = 
    MusicFinder::findMusicInDir(musicDir.absolutePath());   
  if(newMusic.isEmpty()){
    return;
  }
  int numNewFiles = newMusic.size();
  QProgressDialog progress(
    "Loading Library...", "Cancel", 0, numNewFiles, this); 
  progress.setWindowModality(Qt::WindowModal);
  musicLibrary->setMusicLibrary(newMusic, progress);
  progress.setValue(numNewFiles);
}

void MetaWindow::playlistClicked(const QModelIndex& index){
  if(PlaylistView::isVotesColumn(index.column())){
    return;
  }
  playbackWidget->changeSong(mainPlaylist->getFilePath(index));
	mainPlaylist->removeSong(index);
}

void MetaWindow::setupUi(){

  playbackWidget = new PlaybackWidget(musicLibrary, this);

  musicLibrary = new MusicLibrary(serverConnection, this);
  libraryModel = new LibraryModel(this, musicLibrary);
  libraryView = new LibraryView(libraryModel, this);

  mainPlaylist = new PlaylistView(musicLibrary, libraryModel, this);

 // partiersView = new PartiersView(serverConnection,this);

  settingsWidget = new SettingsWidget(this);
  
  QTabWidget* tabWidget = new QTabWidget(this);
  tabWidget->addTab(mainPlaylist, tr("Playlist"));
  tabWidget->addTab(libraryView, tr("Music Library"));
//  tabWidget->addTab(partiersView, tr("Partiers"));
  tabWidget->addTab(settingsWidget, tr("Settings"));
  
  activityList = new ActivityList(musicLibrary);
 
  QHBoxLayout *contentLayout = new QHBoxLayout;
  contentLayout->addWidget(activityList);
  contentLayout->addWidget(tabWidget,6);
  
  QVBoxLayout *mainLayout = new QVBoxLayout;
  mainLayout->addLayout(contentLayout,6);
  mainLayout->addWidget(playbackWidget);

  QWidget* widget = new QWidget;
  widget->setLayout(mainLayout);

  setCentralWidget(widget);
  setWindowTitle("UDJ");

  connect(
    libraryView, 
    SIGNAL(activated(const QModelIndex&)), 
    mainPlaylist, 
    SLOT(addSongToPlaylist(const QModelIndex&)));
  connect(
    libraryView, 
    SIGNAL(songAddRequest(const QModelIndex&)), 
    mainPlaylist, 
    SLOT(addSongToPlaylist(const QModelIndex&)));
  connect(
    mainPlaylist,
    SIGNAL(activated(const QModelIndex&)),
    this,
    SLOT(playlistClicked(const QModelIndex&)));

  resize(800,600);
}

void MetaWindow::createActions(){
  quitAction = new QAction(tr("&Quit"), this);
  quitAction->setShortcuts(QKeySequence::Quit);
  setMusicDirAction = new QAction(tr("S&et Music Directory"), this);
  setMusicDirAction->setShortcut(tr("Ctrl+E"));
  connect(setMusicDirAction, SIGNAL(triggered()), this, SLOT(setMusicDir()));
  connect(quitAction, SIGNAL(triggered()), this, SLOT(close()));
}

void MetaWindow::setupMenus(){
  QMenu *musicMenu = menuBar()->addMenu(tr("&Music"));
  musicMenu->addAction(setMusicDirAction);
  musicMenu->addSeparator();
  musicMenu->addAction(quitAction);
}


} //end namespace
