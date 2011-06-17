#include <QApplication>
#include "MetaWindow.hpp"

int main(int argc, char* argv[]){
  QApplication app(argc, argv);
  MetaWindow window;
  window.show();
  return app.exec();
}
