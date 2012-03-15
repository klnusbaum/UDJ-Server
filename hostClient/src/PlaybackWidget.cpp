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
  QWidget(parent), dataStore(dataStore), currentPlaybackState(PLAYING)
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
  connect(mediaObject, SIGNAL(finished()), this, SLOT(playNextSong()));
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

  connect(
    dataStore,
    SIGNAL(eventCreated()),
    this,
    SLOT(enablePlayback()));

  connect(
    dataStore,
    SIGNAL(eventEnded()),
    this,
    SLOT(disablePlayback()));

  connect(
    dataStore,
    SIGNAL(activePlaylistModified()),
    this,
    SLOT(handlePlaylistChange()));

  Phonon::createPath(mediaObject, audioOutput);
  dataStore->isCurrentlyHosting() ? setEnabled(true) : setEnabled(false);
  playNextSong();
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

}

void PlaybackWidget::playNextSong(){
  Phonon::MediaSource nextSong = dataStore->takeNextSongToPlay();
  mediaObject->setCurrentSource(nextSong);
  if(nextSong.type() != Phonon::MediaSource::Empty){
    mediaObject->play();
  }
}

void PlaybackWidget::handlePlaylistChange(){
  if((mediaObject->currentSource().type() == Phonon::MediaSource::Empty ||
      mediaObject->currentSource().type() == Phonon::MediaSource::Invalid) &&
      currentPlaybackState != PAUSED)
  {
    playNextSong();
  }
}

void PlaybackWidget::setupUi(){

  songTitle = new QLabel(this);
  timeLabel = new QLabel("--:--", this);

  QToolBar *bar = new QToolBar;
  bar->addAction(playAction);
  bar->addAction(pauseAction);

  volumeSlider = new Phonon::VolumeSlider(this);
  volumeSlider->setAudioOutput(audioOutput);
  volumeSlider->setSizePolicy(QSizePolicy::Maximum, QSizePolicy::Maximum);

  seekSlider = new Phonon::SeekSlider(this);
  seekSlider->setMediaObject(mediaObject);

  QHBoxLayout *infoLayout = new QHBoxLayout;
  infoLayout->addWidget(songTitle);
  infoLayout->addStretch();
  infoLayout->addWidget(timeLabel);

  QHBoxLayout *playBackLayout = new QHBoxLayout;
  playBackLayout->addWidget(bar);
  playBackLayout->addStretch();
  playBackLayout->addWidget(volumeSlider);

  QHBoxLayout *seekerLayout = new QHBoxLayout;
  seekerLayout->addWidget(seekSlider);

  QVBoxLayout *mainLayout = new QVBoxLayout;
  mainLayout->addLayout(infoLayout);
  mainLayout->addLayout(seekerLayout);
  mainLayout->addLayout(playBackLayout);
  setLayout(mainLayout);
}

void PlaybackWidget::play(){
  currentPlaybackState = PLAYING;
  mediaObject->play();
  playAction->setEnabled(false);
  pauseAction->setEnabled(true);
}

void PlaybackWidget::pause(){
  currentPlaybackState = PAUSED;
  mediaObject->pause();
  playAction->setEnabled(true);
  pauseAction->setEnabled(false);
}


void PlaybackWidget::createActions(){
  playAction = new QAction(style()->standardIcon(QStyle::SP_MediaPlay),
    tr("Play"), this);
  playAction->setShortcut(tr("Ctrl+P"));
  playAction->setEnabled(false);
  pauseAction = new QAction(style()->standardIcon(QStyle::SP_MediaPause),
    tr("Pause"), this);
  pauseAction->setShortcut(tr("Ctrl+A"));

  connect(playAction, SIGNAL(triggered()), this, SLOT(play()));
  connect(pauseAction, SIGNAL(triggered()), this, SLOT(pause()));
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

void PlaybackWidget::enablePlayback(){
  setEnabled(true);
}

void PlaybackWidget::disablePlayback(){
  setEnabled(false);
}


} //end namespace UDJ
