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
#ifndef WIDGET_WITH_LOADER_HPP
#define WIDGET_WITH_LOADER_HPP

#include <QStackedWidget>

class QLabel;

namespace UDJ{

/** \brief A widget which can be in a state of "loading" */
class WidgetWithLoader : public QStackedWidget{
Q_OBJECT
public:

  /** @name Constructors */
  //@{

  /**
   * \brief Constructs a WidgetWithLoader.
   *
   * @param dataStore The DataStore backing this instance of UDJ.
   * @param parent The parent widget.
   */
  WidgetWithLoader(QString loadingText, QWidget *parent=0);

  //@}

  /** @name Setters */
  //@{

  /**
   * \brief Sets the main widget that should be displayed when not in a loading 
   * state.
   * 
   * @param mainWidget The widget that should be displayed when not in a loading
   * state.
   */
  void setMainWidget(QWidget *mainWidget);

  //@}
public slots:

  /** @name Public Slots */
  //@{

  /** 
   * \brief Display the text indicating that the widget is in a "loading"
   * state.
   */
  void showLoadingText();

  /** \brief Display the main widget. */
  void showMainWidget();

  //@}

private:

  /** @name Private Memebers */
  //@{

  /** \brief Lable used to display the loading text. */
  QLabel *loadingLabel;

  /** \brief Main widget to be displayed when not in a loading state. */
  QWidget *mainWidget;

  //@}

};


}//end namespace udj

#endif //WIDGET_WITH_LOADER_HPP
