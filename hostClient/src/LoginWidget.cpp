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
#include <QCheckBox>
#include "DataStore.hpp"

class QKeyEvent;


namespace UDJ{


LoginWidget::LoginWidget(QWidget *parent)
  :WidgetWithLoader(tr("Logging in..."), parent)
{
  serverConnection = new UDJServerConnection(this);
  setupUi();
  connect(
    serverConnection, 
    SIGNAL(authenticated(const QByteArray&, const user_id_t&)),
    this, 
    SLOT(startMainGUI(const QByteArray&, const user_id_t&)));
  connect(
    serverConnection, 
    SIGNAL(authFailed(const QString)),
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


  saveCreds = new QCheckBox(tr("Remmember me"));
  connect(
    saveCreds,
    SIGNAL(toggled(bool)),
    this,
    SLOT(saveCredsChanged(bool)));


  QGridLayout *layout = new QGridLayout;
  layout->addWidget(logo,0,0,1,2, Qt::AlignCenter);
  layout->addWidget(usernameLabel,1,0);
  layout->addWidget(usernameBox,1,1);
  layout->addWidget(passwordLabel,2,0);
  layout->addWidget(passwordBox,2,1);
  layout->addWidget(saveCreds, 3, 1);
   
  
  loginDisplay->setLayout(layout);

  setMainWidget(loginDisplay);
  showMainWidget(); 

  if(DataStore::hasValidSavedCredentials()){
    QString username;
    QString password;
    DataStore::getSavedCredentials(&username, &password);
    usernameBox->setText(username);
    passwordBox->setText(password);
    saveCreds->setChecked(true); 
  }
}

void LoginWidget::doLogin(){
  showLoadingText();
  serverConnection->authenticate(usernameBox->text(), passwordBox->text());
}

void LoginWidget::startMainGUI(
  const QByteArray& ticketHash, const user_id_t& userId)
{
  if(saveCreds->isChecked()){
    DataStore::saveCredentials(usernameBox->text(), passwordBox->text());
  }

  MetaWindow *metaWindow = new MetaWindow(
    usernameBox->text(),
    passwordBox->text(),
    ticketHash, 
    userId);
  metaWindow->show();
  emit startedMainGUI();
}

void LoginWidget::displayLoginFailedMessage(const QString errorMessage){
  emit loginFailed();
  DataStore::setCredentialsDirty();
  showMainWidget();
  setCurrentWidget(loginDisplay);
  QMessageBox::critical(
    this,
    tr("Login Failed"),
    errorMessage);
}

void LoginWidget::saveCredsChanged(bool newCreds){
  if(!newCreds && DataStore::hasValidSavedCredentials()){
    DataStore::clearSavedCredentials();
    usernameBox->setText("");
    passwordBox->setText("");
  }
}


}// end namespace UDJ


