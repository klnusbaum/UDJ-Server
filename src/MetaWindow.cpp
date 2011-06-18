#include "MetaWindow.hpp"
#include <QAction>
#include <QGridLayout>
#include <QTabWidget>
#include <QPushButton>
#include <QToolBar>
#include <QStyle>

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
  
  connect(playAction, SIGNAL(triggered()), mediaObject, SLOT(play()));
  connect(pauseAction, SIGNAL(triggered()), mediaObject, SLOT(pause()));
  connect(stopAction, SIGNAL(triggered()), mediaObject, SLOT(stop()));

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
  
  QVBoxLayout *mainLayout = new QVBoxLayout;
  mainLayout->addLayout(seekerLayout);
  mainLayout->addLayout(playBackLayout);

  QWidget* widget = new QWidget;
  widget->setLayout(mainLayout);

  setCentralWidget(widget);
  setWindowTitle("Udj");



}
