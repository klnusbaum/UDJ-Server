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
#include <QToolBar>
#include <QStyle>
#include <QFileDialog>
#include <QProgressDialog>
#include "MusicFinder.hpp"
#include <QMenuBar>
#include <QDesktopServices>
#include "SettingsWidget.hpp"
#include "MusicLibrary.hpp"
#include "PlaylistView.hpp"
#include "LibraryView.hpp"


namespace UDJ{


MetaWindow::MetaWindow(){
  audioOutput = new Phonon::AudioOutput(Phonon::MusicCategory, this);
  mediaObject = new Phonon::MediaObject(this);
  makeDBConnection();

  mediaObject->setTickInterval(1000);
  connect(mediaObject, SIGNAL(tick(qint64)), this, SLOT(tick(qint64)));
  connect(mediaObject, SIGNAL(stateChanged(Phonon::State, Phonon::State)),
    this, SLOT(stateChanged(Phonon::State, Phonon::State)));
  connect(mediaObject, SIGNAL(currentSourceChanged(Phonon::MediaSource)),
    this, SLOT(sourceChanged(Phonon::MediaSource)));
  //connect(mediaObject, SIGNAL(aboutToFinish()), this, SLOT(aboutToFinish()));
  //connect(mediaObject, SIGNAL(finished()), this, SLOT(finished()));

  Phonon::createPath(mediaObject, audioOutput);

  createActions();
  setupUi();
  setupMenus();


}

void MetaWindow::makeDBConnection(){
  QDir dbDir(QDesktopServices::storageLocation(QDesktopServices::DataLocation));  
  if(!dbDir.exists()){
    //TODO handle if this fails
    dbDir.mkpath(dbDir.absolutePath());
  }
  musicdb = QSqlDatabase::addDatabase("QSQLITE", getMusicDBConnectionName());
  musicdb.setDatabaseName(dbDir.absoluteFilePath(getMusicDBName()));
  musicdb.open(); 
  QSqlQuery setupQuery(musicdb);
	bool worked = true;
  worked = setupQuery.exec("CREATE TABLE IF NOT EXISTS library "
    "(id INTEGER PRIMARY KEY AUTOINCREMENT, "
   "song TEXT NOT NULL, artist TEXT, album TEXT, filePath TEXT)");  
	PRINT_SQLERROR("Error creating library table", setupQuery)	
  worked = setupQuery.exec("CREATE TABLE IF NOT EXISTS mainplaylist"
   "(id INTEGER PRIMARY KEY AUTOINCREMENT, "
   "libraryId INTEGER REFERENCES library (id) ON DELETE CASCADE, "
   "voteCount INTEGER DEFAULT 1, "
   "timeAdded INTEGER DEFAULT CURRENT_TIMESTAMP);");
	PRINT_SQLERROR("Error creating mainplaylist table.", setupQuery)	
  worked = setupQuery.exec("CREATE VIEW IF NOT EXISTS main_playlist_view "
    "AS SELECT "
    "mainplaylist.id AS plId, "
    "mainplaylist.libraryId AS libraryId, "
    "library.song AS song, "
    "library.artist AS artist, "
    "library.album AS album, "
    "library.filePath AS filePath, "
    "mainplaylist.voteCount AS voteCount, "
    "mainplaylist.timeAdded AS timeAdded "
    "FROM mainplaylist INNER JOIN library ON "
    "mainplaylist.libraryId = library.id ORDER BY mainplaylist.voteCount DESC, mainplaylist.timeAdded;");
	PRINT_SQLERROR("Error creating main_playlist_view view.", setupQuery)	
  worked = setupQuery.exec("CREATE TRIGGER IF NOT EXISTS updateVotes INSTEAD OF "
    "UPDATE ON main_playlist_view BEGIN "
    "UPDATE mainplaylist SET voteCount=new.voteCount "
    "WHERE  mainplaylist.id = old.plId;"
    "END;");
	PRINT_SQLERROR("Error creating update trigger for main_playlist_view.", setupQuery)	
	worked = setupQuery.exec("CREATE TRIGGER IF NOT EXISTS deleteSongFromPlaylist "
	"INSTEAD OF DELETE ON main_playlist_view "
	"BEGIN "
	"DELETE FROM mainplaylist "
	"where mainplaylist.id = old.plId; "
	"END;");
	PRINT_SQLERROR("Error creating delete trigger for main_playlist_view.", setupQuery)	
  worked = setupQuery.exec("CREATE TRIGGER IF NOT EXISTS insertOnPlaylist INSTEAD OF "
    "INSERT ON main_playlist_view BEGIN "
    "INSERT INTO mainplaylist "
    "(libraryId) VALUES (new.libraryId);"
    "END;");
	PRINT_SQLERROR("Error creating insert trigger for main_playlist_view.", setupQuery)	
}

void MetaWindow::tick(qint64 time){

}

void MetaWindow::sourceChanged(const Phonon::MediaSource &source){

}

void MetaWindow::stateChanged(Phonon::State newState, Phonon::State oldState){
  switch(newState){
  case Phonon::PlayingState:
    playAction->setEnabled(false);   
    pauseAction->setEnabled(true);   
    stopAction->setEnabled(true);   
    break;
  case Phonon::StoppedState:
    playAction->setEnabled(true);   
    pauseAction->setEnabled(false);   
    stopAction->setEnabled(false);   
    break;
  case Phonon::PausedState:
    playAction->setEnabled(true);   
    pauseAction->setEnabled(false);   
    stopAction->setEnabled(true);   
    break;
  default:
    break;
  }
}

void MetaWindow::setMusicDir(){
  //TODO: Check to see if musicDir is different than then current music dir
  QDir musicDir = QFileDialog::getExistingDirectory(this,
    tr("Pick you music folder"),
    QDir::homePath(),
    QFileDialog::ShowDirsOnly);
  QList<Phonon::MediaSource> newMusic = MusicFinder::findMusicInDir(musicDir.absolutePath());   
  if(newMusic.isEmpty()){
    return;
  }
  int numNewFiles = newMusic.size();
  QProgressDialog progress("Loading Library...", "Cancel", 0, numNewFiles, this); 
  progress.setWindowModality(Qt::WindowModal);
  musicLibrary->setMusicLibrary(newMusic, progress);
  musicLibrary->select();
  progress.setValue(numNewFiles);
}

void MetaWindow::tableClicked(const QModelIndex& index){
  if(index.column() == 6){
    return;
  }
  mediaObject->stop();
  mediaObject->setCurrentSource(mainPlaylist->getFilePath(index));
  mediaObject->play();
	mainPlaylist->removeSong(index);
}

void MetaWindow::aboutToFinish(){
  QModelIndex nextIndex = mainPlaylist->model()->index(0,0);
  if(nextIndex.isValid()){
    mediaObject->enqueue(
      Phonon::MediaSource(mainPlaylist->getFilePath(nextIndex)));
  }
}

void MetaWindow::createActions(){
  playAction = new QAction(style()->standardIcon(QStyle::SP_MediaPlay),
    tr("Play"), this);
  playAction->setShortcut(tr("Ctrl+P"));
  pauseAction = new QAction(style()->standardIcon(QStyle::SP_MediaPause),
    tr("Pause"), this);
  pauseAction->setShortcut(tr("Ctrl+A"));
  pauseAction->setEnabled(false);
  stopAction = new QAction(style()->standardIcon(QStyle::SP_MediaStop),
    tr("Stop"), this);
  stopAction->setShortcut(tr("Ctrl+S"));
  stopAction->setEnabled(false);

  setMusicDirAction = new QAction(tr("S&et Music Directory"), this);
  setMusicDirAction->setShortcut(tr("Ctrl+E"));

  quitAction = new QAction(tr("&Quit"), this);
  quitAction->setShortcuts(QKeySequence::Quit);
  
  connect(playAction, SIGNAL(triggered()), mediaObject, SLOT(play()));
  connect(pauseAction, SIGNAL(triggered()), mediaObject, SLOT(pause()));
  connect(stopAction, SIGNAL(triggered()), mediaObject, SLOT(stop()));
  connect(quitAction, SIGNAL(triggered()), this, SLOT(close()));
  connect(setMusicDirAction, SIGNAL(triggered()), this, SLOT(setMusicDir()));
}

void MetaWindow::setupUi(){
  QToolBar *bar = new QToolBar;

  bar->addAction(playAction);  
  bar->addAction(pauseAction);  
  bar->addAction(stopAction);  

  seekSlider = new Phonon::SeekSlider(this);
  seekSlider->setMediaObject(mediaObject);
  
  volumeSlider = new Phonon::VolumeSlider(this);
  volumeSlider->setAudioOutput(audioOutput);
  volumeSlider->setSizePolicy(QSizePolicy::Maximum, QSizePolicy::Maximum);

  QHBoxLayout *seekerLayout = new QHBoxLayout;
  seekerLayout->addWidget(seekSlider);
  
  QHBoxLayout *playBackLayout = new QHBoxLayout;
  playBackLayout->addWidget(bar);
  playBackLayout->addStretch();
  playBackLayout->addWidget(volumeSlider);

  musicLibrary = new MusicLibrary(musicdb, this);
  libraryView = new LibraryView(musicLibrary, this);

  mainPlaylist = new PlaylistView(musicLibrary, this);

  partiersView = new QTableView(this);

  settingsWidget = new SettingsWidget(this);
  
  QTabWidget* tabWidget = new QTabWidget(this);
  tabWidget->addTab(mainPlaylist, tr("Playlist"));
  tabWidget->addTab(libraryView, tr("Music Library"));
  tabWidget->addTab(partiersView, tr("Partiers"));
  tabWidget->addTab(settingsWidget, tr("Settings"));
  
  
  QVBoxLayout *mainLayout = new QVBoxLayout;
  mainLayout->addLayout(seekerLayout);
  mainLayout->addLayout(playBackLayout);
  mainLayout->addWidget(tabWidget);

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
    SLOT(tableClicked(const QModelIndex&)));
}

void MetaWindow::setupMenus(){
  QMenu *musicMenu = menuBar()->addMenu(tr("&Music"));
  musicMenu->addAction(setMusicDirAction);
  musicMenu->addSeparator();
  musicMenu->addAction(quitAction);
}



} //end namespace
