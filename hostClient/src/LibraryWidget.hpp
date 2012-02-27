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
#ifndef LIBRARY_WIDGET_HPP
#define LIBRARY_WIDGET_HPP
#include "ConfigDefs.hpp"
#include <QWidget>

class QLineEdit;

namespace UDJ{

class DataStore;
class LibraryView;



/**
 * \brief Displays the various activities that can be done in UDJ.
 */
class LibraryWidget : public QWidget{
Q_OBJECT
public:
  /** @name Constructors */
  //@{

  /**
   * \brief Constructs a LibraryWidget
   *
   * @param dataStore The DataStore backing this instance of UDJ.
   * @param parent The parent widget.
   */
  LibraryWidget(DataStore *dataStore, QWidget *parent=0);

  //@}

private:
  DataStore *dataStore;
  LibraryView *libraryView;
  QLineEdit *searchEdit;

};


}//end namespace UDJ
#endif //LIBRARY_WIDGET_HPP

