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
