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
#include <QProgressDialog>
#include <QMessageBox>

namespace UDJ{


LoginWidget::LoginWidget():QWidget(){
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
    SLOT(loginFailed(const QString)));
}

void LoginWidget::setupUi(){

  loginProgress = NULL;
  logo = new QLabel("UDJ", this);

  usernameBox = new QLineEdit(getUsernameHint(), this);
  passwordBox = new QLineEdit(getPasswordHint(), this);
  passwordBox->setEchoMode(QLineEdit::Password);
  loginButton = new QPushButton(tr("Login"), this);
  QGridLayout *layout = new QGridLayout;
  layout->addWidget(logo,0,0,1,2, Qt::AlignCenter);
  layout->addWidget(usernameBox,1,0,1,2);
  layout->addWidget(passwordBox,2,0,1,2);
  layout->addWidget(loginButton,3,1,1,1);
  
  setLayout(layout);

  connect(loginButton, SIGNAL(clicked(bool)), this, SLOT(doLogin()));
}

bool LoginWidget::hasValidCredsFormat() const{
  return 
    usernameBox->text() != "" &&
    usernameBox->text() != getUsernameHint() &&
    passwordBox->text() != "" &&
    passwordBox->text() != getPasswordHint();
}

void LoginWidget::doLogin(){
  if(hasValidCredsFormat()){
    loginProgress = new QProgressDialog(
      tr("Logging in..."), 
      tr("Cancel"),
      0,
      1,
      this);
    serverConnection->startConnection(usernameBox->text(), passwordBox->text());
  }
  else{
    displayBadCredFormatMessage();
  }
}

void LoginWidget::startMainGUI(){
  loginProgress->setValue(1);
  MetaWindow *metaWindow = new MetaWindow(serverConnection);
  metaWindow->show();
  serverConnection->setParent(metaWindow);
  close();
}

void LoginWidget::loginFailed(const QString errorMessage){
  loginProgress->setValue(1);
  displayLoginFailedMessage(errorMessage);
}

void LoginWidget::displayBadCredFormatMessage(){
  QMessageBox::critical(
    this,
    tr("Bad creditials"),
    tr("Please type in your username and password"));
}

void LoginWidget::displayLoginFailedMessage(const QString errorMessage){
  QMessageBox::critical(
    this,
    tr("Login Failed"),
    errorMessage);
}



}// end namespace UDJ


