#ifndef METAWINDOW_HPP
#define MEATWINDOW_HPP
#include <QMainWindow>
#include <phonon/audiooutput.h>
#include <phonon/seekslider.h>
#include <phonon/mediaobject.h>
#include <phonon/volumeslider.h>
#include <phonon/audiooutput.h>

class QTabWidget;
class QPushButton;
class QAction;

class MetaWindow : public QMainWindow{
  Q_OBJECT
public:
  MetaWindow();
private slots:
  void stateChanged(Phonon::State newState, Phonon::State oldState);
  void tick(qint64 time);
  void sourceChanged(const Phonon::MediaSource &source);
  
private:
  QTabWidget *tabs;
  Phonon::SeekSlider *seekSlider;
  Phonon::MediaObject *mediaObject;
  Phonon::AudioOutput *audioOutput;
  Phonon::VolumeSlider *volumeSlider;
  QList<Phonon::MediaSource> sources;

  QAction *playAction;
  QAction *pauseAction;
  QAction *stopAction;

  void createActions();
  void setupUi();
};

#endif
