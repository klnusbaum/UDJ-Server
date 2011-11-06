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
#include "SettingsWidget.hpp"
#include "MusicFinder.hpp"
#include "MusicLibrary.hpp"
#include "LibraryModel.hpp"
#include "LibraryView.hpp"
#include "ActivityList.hpp"
#include "EventWidget.hpp"
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
#include <QStackedWidget>


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

void MetaWindow::setupUi(){

  playbackWidget = new PlaybackWidget(musicLibrary, this);

  musicLibrary = new MusicLibrary(serverConnection, this);
  libraryModel = new LibraryModel(this, musicLibrary);
  libraryView = new LibraryView(libraryModel, this);

  eventWidget = new EventWidget(musicLibrary, this);
 
  activityList = new ActivityList(musicLibrary);

  contentStack = new QStackedWidget(this);
  contentStack->addWidget(libraryView);
  contentStack->addWidget(eventWidget);
  contentStack->setCurrentWidget(libraryView);
 
  QHBoxLayout *contentLayout = new QHBoxLayout;
  contentLayout->addWidget(activityList);
  contentLayout->addWidget(contentStack,6);
  
  QVBoxLayout *mainLayout = new QVBoxLayout;
  mainLayout->addLayout(contentLayout,6);
  mainLayout->addWidget(playbackWidget);

  QWidget* widget = new QWidget;
  widget->setLayout(mainLayout);

  setCentralWidget(widget);
  setWindowTitle("UDJ");

  connect(
    activityList,
    SIGNAL(libraryClicked()),
    this,
    SLOT(displayLibrary()));

  connect(
    activityList,
    SIGNAL(eventClicked()),
    this,
    SLOT(displayEventWidget()));

  connect(
    activityList,
    SIGNAL(playlistClicked(playlist_id_t)),
    this,
    SLOT(displayPlaylist(playlist_id_t)));

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


void MetaWindow::displayLibrary(){
  contentStack->setCurrentWidget(libraryView);
}

void MetaWindow::displayEventWidget(){
  contentStack->setCurrentWidget(eventWidget);
}

void MetaWindow::displayPlaylist(playlist_id_t playlist){

}



} //end namespace
