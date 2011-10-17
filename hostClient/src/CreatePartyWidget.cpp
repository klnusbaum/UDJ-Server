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
#include "CreatePartyWidget.hpp"
#include "MusicLibrary.hpp"
#include <QLineEdit>
#include <QPushButton>
#include <QLabel>
#include <QVBoxLayout>
#include <QProgressDialog>
#include <QMessageBox>


namespace UDJ{


CreatePartyWidget::CreatePartyWidget(
  MusicLibrary *musicLibrary, 
  QWidget *parent):
  QWidget(parent),
  musicLibrary(musicLibrary)
{
  setupUi();
  connect(
    createPartyButton,
    SIGNAL(clicked(bool)),
    this,
    SLOT(doLogin()));
  connect(
    musicLibrary,
    SIGNAL(partyCreated()),
    this,
    SLOT(partyCreateSuccess()));
  connect(
    musicLibrary,
    SIGNAL(partyCreationFailed()),
    this,
    SLOT(partyCreateFail()));
}


void CreatePartyWidget::setupUi(){
  nameEdit = new QLineEdit(tr("Name of party"));
  passwordEdit = new QLineEdit(tr("Password (optional)"));
  locationEdit = new QLineEdit(tr("Location (optional)"));
  createPartyButton = new QPushButton(tr("Create Party"));
  createPartyButton->setSizePolicy(QSizePolicy::Minimum, QSizePolicy::Minimum);
  createLabel = new QLabel(tr("Create a New Party"));

  QVBoxLayout *mainLayout = new QVBoxLayout;
  mainLayout->addWidget(createLabel, Qt::AlignCenter);
  mainLayout->addWidget(nameEdit);
  mainLayout->addWidget(passwordEdit);
  mainLayout->addWidget(locationEdit);
  mainLayout->addWidget(createPartyButton);

  setLayout(mainLayout);
}

void CreatePartyWidget::doLogin(){
  musicLibrary->createNewParty(
    nameEdit->text(),
    passwordEdit->text(),
    locationEdit->text());
  createProgress = new QProgressDialog(
    tr("Creating party..."),
    tr("Cancel"),
    0,
    1,
    this);
}

void CreatePartyWidget::partyCreateSuccess(){
  createProgress->setValue(1);
  emit partyCreated();
}

void CreatePartyWidget::partyCreateFail(){
  createProgress->setValue(1);
  QMessageBox::critical(
    this,
    tr("Party Creation Failed"),
    tr("Failed to create party"));
}


}//end namespace UDJ
