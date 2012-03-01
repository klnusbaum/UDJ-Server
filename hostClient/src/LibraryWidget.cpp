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
#include "LibraryWidget.hpp"
#include "DataStore.hpp"
#include "LibraryView.hpp"
#include <QGridLayout>
#include <QLineEdit>
#include <QLabel>

namespace UDJ{

LibraryWidget::LibraryWidget(DataStore* dataStore, QWidget* parent):
  QWidget(parent),
  dataStore(dataStore)
{
  libraryView = new LibraryView(dataStore, this);
  searchEdit = new QLineEdit(this);
  QLabel *searchLabel = new QLabel(tr("Search:"),this);


  QGridLayout *layout = new QGridLayout(this);
  layout->addWidget(searchLabel,0,1,1,8, Qt::AlignRight);
  layout->addWidget(searchEdit,0,9,1,1);
  layout->addWidget(libraryView,1,0,1,10);
  layout->setRowStretch(1, 10);
  layout->setColumnStretch(0, 1);
  layout->setColumnStretch(1, 1);
  layout->setColumnStretch(2, 1);
  layout->setColumnStretch(3, 1);
  layout->setColumnStretch(4, 1);
  layout->setColumnStretch(5, 1);
  layout->setColumnStretch(6, 1);
  layout->setColumnStretch(7, 1);
  layout->setColumnStretch(8, 1);
  layout->setColumnStretch(9, 2);

  setLayout(layout);

  connect(
    searchEdit,
    SIGNAL(textChanged(const QString&)),
    libraryView,
    SLOT(filterContents(const QString&)));
}


} //end namespace


