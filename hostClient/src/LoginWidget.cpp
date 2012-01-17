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

#include "LoginWidget.hpp"
#include "UDJServerConnection.hpp"
#include "MetaWindow.hpp"
#include <QPushButton>
#include <QLineEdit>
#include <QLabel>
#include <QGridLayout>
#include <QMessageBox>
#include <QCheckBox>
#include <QKeyEvent>

class QKeyEvent;


namespace UDJ{


LoginWidget::LoginWidget():WidgetWithLoader(tr("Logging in...")){
  serverConnection = new UDJServerConnection(this);
  setupUi();
  connect(
    serverConnection, 
    SIGNAL(connectionEstablished()),
    this, 
    SLOT(startMainGUI()));
  connect(
    serverConnection, 
    SIGNAL(unableToConnect(const QString)),
    this, 
    SLOT(displayLoginFailedMessage(const QString)));
}

void LoginWidget::setupUi(){
  loginDisplay = new QWidget(this);

  logo = new QLabel("UDJ", this);

  usernameBox = new QLineEdit(this);
  usernameLabel = new QLabel(tr("Username"));
  usernameLabel->setBuddy(usernameBox);

  passwordBox = new QLineEdit(this);
  passwordBox->setEchoMode(QLineEdit::Password);
  passwordLabel = new QLabel(tr("Password"));
  passwordLabel->setBuddy(passwordBox);

  loginButton = new QPushButton(tr("Login"), this);

  QGridLayout *layout = new QGridLayout;
  layout->addWidget(logo,0,0,1,2, Qt::AlignCenter);
  layout->addWidget(usernameLabel,1,0);
  layout->addWidget(usernameBox,1,1);
  layout->addWidget(passwordLabel,2,0);
  layout->addWidget(passwordBox,2,1);
  layout->addWidget(loginButton,3,0,1,2, Qt::AlignCenter);
   
  
  connect(loginButton, SIGNAL(clicked(bool)), this, SLOT(doLogin()));
  loginDisplay->setLayout(layout);

  setMainWidget(loginDisplay);
  showMainWidget(); 
}

void LoginWidget::doLogin(){
  showLoadingText();
  serverConnection->startConnection(usernameBox->text(), passwordBox->text());
}

void LoginWidget::startMainGUI(){
  MetaWindow *metaWindow = new MetaWindow(serverConnection);
  metaWindow->show();
  serverConnection->setParent(metaWindow);
  close();
}

void LoginWidget::displayLoginFailedMessage(const QString errorMessage){
  showMainWidget();
  setCurrentWidget(loginDisplay);
  QMessageBox::critical(
    this,
    tr("Login Failed"),
    errorMessage);
}



}// end namespace UDJ


