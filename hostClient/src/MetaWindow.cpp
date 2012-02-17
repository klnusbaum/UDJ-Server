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
#include "SongListView.hpp"
#include "SettingsWidget.hpp"
#include "MusicFinder.hpp"
#include "DataStore.hpp"
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
#include <QSplitter>


namespace UDJ{


MetaWindow::MetaWindow(
  const QString& username,
  const QString& password,
  const QByteArray& ticketHash,
  const user_id_t& userId,
  QWidget *parent,
  Qt::WindowFlags flags)
  :QMainWindow(parent,flags)
{
  dataStore = new DataStore(username, password, ticketHash, userId, this);
  createActions();
  setupUi();
  setupMenus();
  QSettings settings(
    QSettings::UserScope,
    DataStore::getSettingsOrg(),
    DataStore::getSettingsApp());
  restoreGeometry(settings.value("metaWindowGeometry").toByteArray());
  restoreState(settings.value("metaWindowState").toByteArray());
}

void MetaWindow::closeEvent(QCloseEvent *event){
  QSettings settings(
    QSettings::UserScope,
    DataStore::getSettingsOrg(),
    DataStore::getSettingsApp());
  settings.setValue("metaWindowGeometry", saveGeometry());
  settings.setValue("metaWindowState", saveState());
  QMainWindow::closeEvent(event);
}



void MetaWindow::addMusicToLibrary(){
  //TODO: Check to see if musicDir is different than then current music dir
  QDir musicDir = QFileDialog::getExistingDirectory(this,
    tr("Pick folder to add"),
    QDir::homePath(),
    QFileDialog::ShowDirsOnly);
  QList<Phonon::MediaSource> musicToAdd = 
    MusicFinder::findMusicInDir(musicDir.absolutePath());   
  if(musicToAdd.isEmpty()){
    return;
  }
  int numNewFiles = musicToAdd.size();
  QProgressDialog progress(
    "Loading Library...", "Cancel", 0, numNewFiles, this); 
  progress.setWindowModality(Qt::WindowModal);
  dataStore->addMusicToLibrary(musicToAdd, progress);
  progress.setValue(numNewFiles);
}

void MetaWindow::addSongToLibrary(){
  QString fileName = QFileDialog::getOpenFileName(
      this,
      tr("Pick song to add"),
      QDir::homePath(),
      tr("Audio Files (*.mp3 *.ogg)"));
  dataStore->addSongToLibrary(Phonon::MediaSource(fileName));
}

void MetaWindow::setupUi(){

  playbackWidget = new PlaybackWidget(dataStore, this);

  libraryView = new LibraryView(dataStore, this);

  eventWidget = new EventWidget(dataStore, this);

  songListView = new SongListView(dataStore, this);

  activityList = new ActivityList(dataStore);

  QWidget* contentStackContainer = new QWidget(this);
  contentStack = new QStackedWidget(this);
  contentStack->addWidget(libraryView);
  contentStack->addWidget(eventWidget);
  contentStack->addWidget(songListView);
  contentStack->setCurrentWidget(libraryView);
  QVBoxLayout *contentStackLayout = new QVBoxLayout;
  contentStackLayout->addWidget(contentStack, Qt::AlignCenter);
  contentStackContainer->setLayout(contentStackLayout);

  QSplitter *content = new QSplitter(Qt::Horizontal, this);
  content->addWidget(activityList);
  content->addWidget(contentStackContainer);
  content->setStretchFactor(1, 10);

  QVBoxLayout *mainLayout = new QVBoxLayout;
  mainLayout->addWidget(content,6);
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
    SIGNAL(songListClicked(song_list_id_t)),
    this,
    SLOT(displaySongList(song_list_id_t)));

  connect(
    songListView,
    SIGNAL(canNoLongerDisplay()),
    activityList,
    SLOT(switchToLibrary()));

  if(dataStore->isCurrentlyHosting()){
    displayEventWidget();
  }

}

void MetaWindow::createActions(){
  quitAction = new QAction(tr("&Quit"), this);
  quitAction->setShortcuts(QKeySequence::Quit);
  addMusicAction = new QAction(tr("Add &Music"), this);
  addMusicAction->setShortcut(tr("Ctrl+M"));
  addSongAction = new QAction(tr("A&dd Song"), this);
  addSongAction->setShortcut(tr("Ctrl+D"));
  connect(addMusicAction, SIGNAL(triggered()), this, SLOT(addMusicToLibrary()));
  connect(quitAction, SIGNAL(triggered()), this, SLOT(close()));
  connect(addSongAction, SIGNAL(triggered()), this, SLOT(addSongToLibrary()));
}

void MetaWindow::setupMenus(){
  QMenu *musicMenu = menuBar()->addMenu(tr("&Music"));
  musicMenu->addAction(addMusicAction);
  musicMenu->addAction(addSongAction);
  musicMenu->addSeparator();
  musicMenu->addAction(quitAction);
}


void MetaWindow::displayLibrary(){
  contentStack->setCurrentWidget(libraryView);
}

void MetaWindow::displayEventWidget(){
  contentStack->setCurrentWidget(eventWidget);
}


void MetaWindow::displaySongList(song_list_id_t songListId){
  std::cout << "About to display song list:  " << songListId << std::endl;
  songListView->setSongListId(songListId);
  contentStack->setCurrentWidget(songListView);
}



} //end namespace
