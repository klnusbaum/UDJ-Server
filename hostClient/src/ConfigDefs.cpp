#include "ConfigDefs.hpp"
namespace UDJ{


const QString& getServerUrlPath(){
  static const QString SERVER_URL_PATH= "http://0.0.0.0:8081";
  return SERVER_URL_PATH;
}

const QUrl& getServerUrl(){
  static const QUrl SERVER_URL(getServerUrlPath());
  return SERVER_URL;
}

const QUrl& getAuthUrl(){
  static const QUrl AUTH_URL(getServerUrlPath() + "/auth");
  return AUTH_URL;
}


} //end UDJ namespace
