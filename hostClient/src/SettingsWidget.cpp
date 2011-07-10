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
#include "SettingsWidget.hpp"
#include <QCheckBox>
#include <QVBoxLayout>

namespace UDJ{


SettingsWidget::SettingsWidget(QWidget* parent):QWidget(parent){
  setupUi();
}

void SettingsWidget::setupUi(){
  allowFileUploads = new QCheckBox(tr("Allow song uploads"), this);
  allowFileUploads->setToolTip(tr("Allow users to upload songs. Could be dangerous!"));

  QVBoxLayout *mainLayout = new QVBoxLayout;
  mainLayout->addWidget(allowFileUploads);
  
  setLayout(mainLayout);
}


} //end namespace
