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
#ifndef PLAYBACK_WIDGET_HPP
#define PLAYBACK_WIDGET_HPP
#include <QWidget>
#include <phonon/audiooutput.h>
#include <phonon/seekslider.h>
#include <phonon/mediaobject.h>
#include <phonon/volumeslider.h>


class QAction;
class QLabel;


namespace UDJ{

class DataStore;

/** \brief Widget used for controlling music playback. */
class PlaybackWidget : public QWidget{

Q_OBJECT

public:
  /** @name Constructors */
  //@{

  /**
   * \brief Constructs a Playback widget.
   *
   * @param dataStore The DataStore backing this instance of UDJ.
   * @param parent The parent widget.
   */
  PlaybackWidget(DataStore *dataStore, QWidget *parent=0);

  //@}

private slots:
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
   * \brief Called whenever the current song being played is about to finish.
   */
  void aboutToFinish();

  /**
   * \brief Called when the primary media object has finished playing it's
   * current song.
   */
   void finished();

   /** \brief Start playback. */
   void play();

   /** \brief Handles when meta data is changed. */
   void metaDataChanged();

   /**
    * \brief Sets the currently playing song to the given new song.
    *
    * @param newSong The new song that should be playing.
    */
   void setNewSource(Phonon::MediaSource newSong);

  //@}

private:
  
  /** @name Private Functions */
  //@{

  /** \brief Sets up all the actions used by the MetaWindow. */
  void createActions();

  /** \brief Initializes UI. */
  void setupUi();

  //@}

  /** @name Private Memeber */
  //@{

  /** \brief Causes playback to start */
  QAction *playAction;

  /** \brief Pauses playback */
  QAction *pauseAction;

  /** \brief Stops playback */
  QAction *stopAction;

  /** \brief Used to display the name of the currently playing song. */
	QLabel *songTitle;

  /** \bried Used to display the time played of the current song. */
  QLabel *timeLabel;

  /** \brief The main seeker to change the songs current playback position. */
  Phonon::SeekSlider *seekSlider;

  /** \brief The primary media object used for song playback. */
  Phonon::MediaObject *mediaObject;

  /** \brief The primary audioOutput device used for song playback. */
  Phonon::AudioOutput *audioOutput;

  /** \brief The volume slider used to control playback volume. */
  Phonon::VolumeSlider *volumeSlider;

  /**
   * \brief The data store backing this instance of UDJ.
   */
  DataStore *dataStore;

  //@}

};

} //end namespace UDJ
#endif 
