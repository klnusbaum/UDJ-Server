#include "MetaWindow.hpp"
#include <QAction>
#include <QGridLayout>
#include <QTabWidget>
#include <QPushButton>
#include <QToolBar>
#include <QStyle>
#include "QFileDialog"
#include "MusicFinder.hpp"
#include <QMenuBar>
#include "SettingsWidget.hpp"

namespace UDJ{


MetaWindow::MetaWindow(){
  audioOutput = new Phonon::AudioOutput(Phonon::MusicCategory, this);
  mediaObject = new Phonon::MediaObject(this);

  mediaObject->setTickInterval(1000);
  connect(mediaObject, SIGNAL(tick(qint64)), this, SLOT(tick(qint64)));
  connect(mediaObject, SIGNAL(stateChanged(Phonon::State, Phonon::State)),
    this, SLOT(stateChanged(Phonon::State, Phonon::State)));
  connect(mediaObject, SIGNAL(currentSourceChanged(Phonon::MediaSource)),
    this, SLOT(sourceChanged(Phonon::MediaSource)));

  Phonon::createPath(mediaObject, audioOutput);

  createActions();
  setupUi();
  setupMenus();

  mediaObject->setCurrentSource(Phonon::MediaSource("waterlanding.mp3"));
  

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
  QString musicDir = QFileDialog::getExistingDirectory(this,
    tr("Pick you music folder"),
    QDir::homePath(),
    QFileDialog::ShowDirsOnly);
  QList<Phonon::MediaSource> newMusic = MusicFinder::findMusicInDir(QDir(musicDir));   
  if(newMusic.isEmpty()){
    return;
  }
  for(int i=0; i<newMusic.size(); ++i){
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

  libraryView = new QTableView(this);
  playlistView = new QTableView(this);
  partiersView = new QTableView(this);
  settingsWidget = new SettingsWidget(this);
  
  QTabWidget* tabWidget = new QTabWidget(this);
  tabWidget->addTab(playlistView, tr("Playlist"));
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
}

void MetaWindow::setupMenus(){
  QMenu *musicMenu = menuBar()->addMenu(tr("&Music"));
  musicMenu->addAction(setMusicDirAction);
  musicMenu->addSeparator();
  musicMenu->addAction(quitAction);
}


} //end namespace
