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

#include "PlaybackWidget.hpp"
#include "DataStore.hpp"
#include <QAction>
#include <QLabel>
#include <QTime>
#include <QHBoxLayout>
#include <QVBoxLayout>
#include <QToolBar>
#include <QStyle>

namespace UDJ{


PlaybackWidget::PlaybackWidget(DataStore *dataStore, QWidget *parent):
  QWidget(parent), dataStore(dataStore)
{
  audioOutput = new Phonon::AudioOutput(Phonon::MusicCategory, this);
  mediaObject = new Phonon::MediaObject(this);
  createActions();
  setupUi();

  mediaObject->setTickInterval(1000);
  connect(mediaObject, SIGNAL(tick(qint64)), this, SLOT(tick(qint64)));
  connect(mediaObject, SIGNAL(stateChanged(Phonon::State, Phonon::State)),
    this, SLOT(stateChanged(Phonon::State, Phonon::State)));
  connect(mediaObject, SIGNAL(currentSourceChanged(Phonon::MediaSource)),
    this, SLOT(sourceChanged(Phonon::MediaSource)));
  connect(mediaObject, SIGNAL(finished()), this, SLOT(finished()));
  connect(
    mediaObject,
    SIGNAL(metaDataChanged()),
    this,
    SLOT(metaDataChanged()));
  connect(
    dataStore,
    SIGNAL(manualSongChange(Phonon::MediaSource)),
    this,
    SLOT(setNewSource(Phonon::MediaSource)));

  connect(
    dataStore,
    SIGNAL(eventEnded()),
    this,
    SLOT(clearWidget()));
  Phonon::createPath(mediaObject, audioOutput);
}

void PlaybackWidget::tick(qint64 time){
  QTime tickTime(0, (time/60000)%60, (time/1000)%60);
  timeLabel->setText(tickTime.toString("mm:ss"));
}

void PlaybackWidget::sourceChanged(const Phonon::MediaSource &source){

}

void PlaybackWidget::metaDataChanged(){
  QStringList titleInfo = mediaObject->metaData(Phonon::TitleMetaData);
  if(titleInfo.size() > 0){
    songTitle->setText(titleInfo.at(0));
  }
  else{
    songTitle->setText("");
  }
}

void PlaybackWidget::stateChanged(
  Phonon::State newState, Phonon::State oldState)
{
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

void PlaybackWidget::play(){
  if(mediaObject->currentSource().type() == Phonon::MediaSource::Empty){
    Phonon::MediaSource nextSong = dataStore->takeNextSongToPlay();
    if(nextSong.type() == Phonon::MediaSource::Empty){
      return;
    }
    mediaObject->setCurrentSource(nextSong);
  }
  mediaObject->play();
}

void PlaybackWidget::aboutToFinish(){
  Phonon::MediaSource nextSong = dataStore->getNextSongToPlay();
  if(nextSong.type() == Phonon::MediaSource::Empty){
     return;
  }
  mediaObject->enqueue(dataStore->getNextSongToPlay());
}

void PlaybackWidget::finished(){
  Phonon::MediaSource nextSong = dataStore->takeNextSongToPlay();
  if(nextSong.type() != Phonon::MediaSource::Empty){
    mediaObject->setCurrentSource(nextSong);
    mediaObject->play();
  }
}

void PlaybackWidget::setupUi(){

  songTitle = new QLabel(this);
  timeLabel = new QLabel("--:--", this);

  QToolBar *bar = new QToolBar;
  bar->addAction(playAction);
  bar->addAction(pauseAction);
  bar->addAction(stopAction);

  seekSlider = new Phonon::SeekSlider(this);
  seekSlider->setMediaObject(mediaObject);

  volumeSlider = new Phonon::VolumeSlider(this);
  volumeSlider->setAudioOutput(audioOutput);
  volumeSlider->setSizePolicy(QSizePolicy::Maximum, QSizePolicy::Maximum);

  QHBoxLayout *infoLayout = new QHBoxLayout;
  infoLayout->addWidget(songTitle);
  infoLayout->addStretch();
  infoLayout->addWidget(timeLabel);

  QHBoxLayout *seekerLayout = new QHBoxLayout;
  seekerLayout->addWidget(seekSlider);

  QHBoxLayout *playBackLayout = new QHBoxLayout;
  playBackLayout->addWidget(bar);
  playBackLayout->addStretch();
  playBackLayout->addWidget(volumeSlider);

  QVBoxLayout *mainLayout = new QVBoxLayout;
  mainLayout->addLayout(infoLayout);
  mainLayout->addLayout(seekerLayout);
  mainLayout->addLayout(playBackLayout);
  setLayout(mainLayout);
}


void PlaybackWidget::createActions(){
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

  connect(playAction, SIGNAL(triggered()), this, SLOT(play()));
  connect(pauseAction, SIGNAL(triggered()), mediaObject, SLOT(pause()));
  connect(stopAction, SIGNAL(triggered()), mediaObject, SLOT(stop()));
}

void PlaybackWidget::setNewSource(Phonon::MediaSource newSong){
  mediaObject->setCurrentSource(newSong);
  mediaObject->play();
}

void PlaybackWidget::clearWidget(){
  mediaObject->stop();
  mediaObject->clear();
  songTitle->setText("");
  timeLabel->setText("--:--");
}


} //end namespace UDJ
