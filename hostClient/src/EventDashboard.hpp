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
#ifndef EVENT_DASHBOARD_HPP
#define EVENT_DASHBOARD_HPP
#include "WidgetWithLoader.hpp"

class QLabel;
class QTabWidget;

namespace UDJ{

class DataStore;

/**
 * \brief Widget showing all the relevant data about an event.
 */
class EventDashboard : public WidgetWithLoader{
Q_OBJECT
public:
  /** @name Constructors */
  //@{

  /**
   * \brief Constructs an EventDashboard
   *
   * @param dataStore The DataStore backing this instance of UDJ.
   * @param parent The parent widget.
   */
  EventDashboard(DataStore *dataStore, QWidget *parent=0);

  //@}

signals:
  /** @name Signals */
  //@{

  /**
   * \brief Emitted when the event has endede.
   */
  void eventEnded();
 
  //@}

private:
 
  /** @name Private Functions */
  //@{

  
  /**
   * \brief Does UI initialization.
   */
  void setupUi();

  //@}

  /** @name Private Memeber */
  //@{

  /** \brief The data store backing this instance of UDJ*/
  DataStore *dataStore;

  /** \brief Label for displaying the event name */
  QLabel *eventName;

  /** \brief Label for displayling the events id */
  QLabel *eventId;

  /** \brief Widget which contains all of the content. */
  QWidget *mainContent;
 
  /** \brief the actual controlls for the event */
  QTabWidget *eventControls;

  //@}

private slots:

  /** @name Private Slots */
  //@{

  /** \brief Updates the info for the event */
  void updateEventInfo();

  /** \brief Ends the current event */
  void endEvent();
  
  /** 
   * \brief Handles certain tasks that need to be preformed once an event has 
   * ended.
   */
  void handleEventEnded();

  /**
   * \brief Handles when the ending of an event fails.
   */
  void handleEventEndingFailed(const QString errMessage);

  //@}
};


}//end namespace UDJ

#endif //EVENT_DASHBOARD_HPP
