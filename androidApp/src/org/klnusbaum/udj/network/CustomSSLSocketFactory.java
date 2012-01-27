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
package org.klnusbaum.udj.network;

import org.apache.http.conn.ssl.SSLSocketFactory;

import javax.net.ssl.SSLContext;
import javax.net.ssl.TrustManager;

import java.security.SecureRandom;
import java.security.KeyStore;
import java.security.NoSuchAlgorithmException;
import java.security.KeyManagementException;
import java.security.KeyStoreException;
import java.security.UnrecoverableKeyException;
import java.net.UnknownHostException;
import java.io.IOException;
import java.net.Socket;

public class CustomSSLSocketFactory extends SSLSocketFactory{
  private SSLContext sslContext = SSLContext.getInstance("TLS");

  public CustomSSLSocketFactory(KeyStore truststore)
    throws NoSuchAlgorithmException, KeyManagementException, KeyStoreException,
    UnrecoverableKeyException
  {
    super(truststore);
    TrustManager[] tm = new TrustManager[] { new FullX509TrustManager() };
    sslContext.init(null, tm, new SecureRandom());
  }

  @Override
  public Socket createSocket() throws IOException{
    return sslContext.getSocketFactory().createSocket();
  }

  @Override
  public Socket createSocket(
    Socket socket, String host, int port, boolean autoClose) 
    throws IOException, UnknownHostException
  {
    return sslContext.getSocketFactory().createSocket(
      socket, host, port, autoClose);
  }

}
