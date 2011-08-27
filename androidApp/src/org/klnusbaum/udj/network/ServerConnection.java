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

import android.content.Context;
import android.os.Handler;
import android.accounts.Account;
import android.util.Log;

import java.util.GregorianCalendar;
import java.util.List;
import java.io.IOException;
import java.text.SimpleDateFormat;
import java.util.TimeZone;
import java.util.ArrayList;

import org.apache.http.HttpEntity;
import org.apache.http.HttpResponse;
import org.apache.http.HttpStatus;
import org.apache.http.auth.AuthenticationException;
import org.apache.http.client.HttpClient;
import org.apache.http.client.entity.UrlEncodedFormEntity;
import org.apache.http.client.methods.HttpPost;
import org.apache.http.client.methods.HttpGet;
import org.apache.http.NameValuePair;
import org.apache.http.ParseException;
import org.apache.http.client.HttpClient;
import org.apache.http.client.methods.HttpPost;
import org.apache.http.message.BasicNameValuePair;
import org.apache.http.conn.params.ConnManagerParams;
import org.apache.http.impl.client.DefaultHttpClient;
import org.apache.http.params.HttpConnectionParams;
import org.apache.http.params.HttpParams;
import org.apache.http.util.EntityUtils;
import org.json.JSONArray;
import org.json.JSONException;


import org.klnusbaum.udj.auth.AuthActivity;
import org.klnusbaum.udj.containers.LibraryEntry;
import org.klnusbaum.udj.containers.PlaylistEntry;
import org.klnusbaum.udj.containers.Party;

/**
 * A connection to the UDJ server
 */
public class ServerConnection{
  
  public static final String PARAM_PARTYID = "partyId";
  public static final String PARAM_USERNAME = "username";
  public static final String PARAM_PASSWORD = "password";
  public static final String PARAM_LAST_UPDATE = "timestamp";
  public static final String PARAM_UPDATE_ARRAY = "updatearray";
  public static final String PARAM_GET_PARTIES = "getParties";
  public static final String PARAM_LOCATION = "location";
  public static final String SERVER_TIMESTAMP_FORMAT = "yyyy-mm-dd hh:mm:ss";
  //public static final String SERVER_URL = "http://www.bazaarsolutions.org/udj";
  //THIS IS FOR TESTING AT THE MOMENT
  public static final String SERVER_URL = "http://10.0.2.2:8081";
  public static final String PLAYLIST_URI = 
    SERVER_URL + "/playlist";
  public static final String LIBRARY_URI = 
    SERVER_URL + "/library";
  public static final String PARTIES_URI =
    SERVER_URL + "/parties";
  public static final int REGISTRATION_TIMEOUT = 30 * 1000; // ms
  private static HttpClient httpClient;
  


  public static HttpClient getHttpClient(){
    if(httpClient == null){
      httpClient = new DefaultHttpClient();
      final HttpParams params = httpClient.getParams();
      HttpConnectionParams.setConnectionTimeout(params, REGISTRATION_TIMEOUT);
      HttpConnectionParams.setSoTimeout(params, REGISTRATION_TIMEOUT);
      ConnManagerParams.setTimeout(params, REGISTRATION_TIMEOUT);
    }
    return httpClient;
  }
  /**
   * Attempts to authenticate with ther UDJ server. Should
   * be used by the AuthActivity.
   *
   * @param username The user name to be authenticated.
   * @param password The password to be authenticated.
   * @param messageHandler A handler used to send messages back to the
   * AuthActivity that called attemptAuth.
   * @param context The context from which the method was called, i.e. the
   * AuthActivity.
   * @return A thread that is running the authentication attempt.
   */
  public static Thread attemptAuth(final String username, final String password,
    final Handler messageHandler, final Context context)
  {
    final Thread t = new Thread(){
      public void run(){
        authenticate(username, password, messageHandler, context);
      }
    };
    t.start();
    return t;
  }


  /**
   * Actually handles authenticating the the user.
   *
   * @param username The user name to be authenticated.
   * @param password The password to be authenticated.
   * @param messageHandler A handler used to send messages back to the
   * AuthActivity that called attemptAuth.
   * @param context The context from which the method was called, i.e. the
   * AuthActivity.
   * @return True if the authentication was successful. False otherwise.
   */
  public static boolean authenticate(String username, String password,
    Handler handler, final Context context)
  {
/*    handler.post(new Runnable(){
      public void run(){
        ((AuthActivity) context).onAuthResult(true);
      }
    });*/
    return true;
  }

  public static List<LibraryEntry> getLibraryUpdate(
    Account account,
    String authtoken, 
    long partyId,
    GregorianCalendar lastUpdated)
    throws JSONException, ParseException, IOException, AuthenticationException
  {
    final ArrayList<NameValuePair> params = 
      getEssentialParameters(account.name, authtoken, partyId, lastUpdated);
    JSONArray libraryEntries = doPost(params, LIBRARY_URI);
    return LibraryEntry.fromJSONArray(libraryEntries);
  }

  public static List<PlaylistEntry> getPlaylistUpdate(  
   Account account,
    String authtoken, 
    long partyId,
    List<PlaylistEntry> toUpdate, 
    GregorianCalendar lastUpdated) throws
    JSONException, ParseException, IOException, AuthenticationException
  {
    final ArrayList<NameValuePair> params = 
      getEssentialParameters(account.name, authtoken, partyId, lastUpdated);
    JSONArray playlistEntries =null;
    if(toUpdate == null || toUpdate.isEmpty()){
      //TODO we should actually do a get here because we're not changing 
      //anything.
      playlistEntries = doGet(params, PLAYLIST_URI);
    }
    else{
      params.add(new BasicNameValuePair(
        PARAM_UPDATE_ARRAY, 
        PlaylistEntry.getJSONArray(toUpdate).toString()));
      playlistEntries = doPost(params, PLAYLIST_URI);
    }
    return PlaylistEntry.fromJSONArray(playlistEntries);
  }

  private static ArrayList<NameValuePair> getEssentialParameters(
    String name, String authtoken, long partyId, GregorianCalendar lastUpdated)
  {
    ArrayList<NameValuePair> params = new ArrayList<NameValuePair>();
    ArrayList<PlaylistEntry> toReturn = new ArrayList<PlaylistEntry>();
    params.add(new BasicNameValuePair(PARAM_PARTYID, String.valueOf(partyId)));
    params.add(new BasicNameValuePair(PARAM_USERNAME, name));
    params.add(new BasicNameValuePair(PARAM_PASSWORD, authtoken));
    if(lastUpdated != null){
      final SimpleDateFormat formatter =
        new SimpleDateFormat(SERVER_TIMESTAMP_FORMAT);
      formatter.setTimeZone(TimeZone.getTimeZone("UTC"));
      params.add(new BasicNameValuePair(
        PARAM_LAST_UPDATE, formatter.format(lastUpdated)));
    }
    return params;
  }

  public static JSONArray doPost(ArrayList<NameValuePair> params, String uri)
    throws AuthenticationException, IOException, JSONException
  {
    HttpEntity entity = null;
    entity = new UrlEncodedFormEntity(params);
    final HttpPost post = new HttpPost(uri);
    post.addHeader(entity.getContentType());
    post.setEntity(entity);
    final HttpResponse resp = getHttpClient().execute(post);
    final String response = EntityUtils.toString(resp.getEntity());
    JSONArray toReturn = null;
    if(resp.getStatusLine().getStatusCode() == HttpStatus.SC_OK){
      //Get stuff from response 
      toReturn = new JSONArray(response);
    } 
    else if(resp.getStatusLine().getStatusCode() == HttpStatus.SC_UNAUTHORIZED){
      throw new AuthenticationException();
    }
    else{
      throw new IOException();
    }
    return toReturn;
  }

  public static JSONArray doGet(ArrayList<NameValuePair> params, String uri)
    throws AuthenticationException, IOException, JSONException
  {
    final HttpGet get = new HttpGet(uri + "?" + getParamString(params));
    final HttpResponse resp = getHttpClient().execute(get);
    final String response = EntityUtils.toString(resp.getEntity());
    JSONArray toReturn = null;
    if(resp.getStatusLine().getStatusCode() == HttpStatus.SC_OK){
      //Get stuff from response 
      toReturn = new JSONArray(response);
    } 
    else if(resp.getStatusLine().getStatusCode() == HttpStatus.SC_UNAUTHORIZED){
      throw new AuthenticationException();
    }
    else{
      throw new IOException();
    }
    return toReturn;
  }

  private static String getParamString(ArrayList<NameValuePair> params){
    String toReturn = "";
    for(NameValuePair np: params){
      toReturn += np.getName() + "=" +np.getValue();
    }
    return toReturn;
  }

  public static List<Party> getNearbyParties(Account account, String authtoken)
    throws
    JSONException, ParseException, IOException, AuthenticationException
  {
    final ArrayList<NameValuePair> params = new ArrayList<NameValuePair>();
    params.add(new BasicNameValuePair(PARAM_USERNAME, account.name));
    params.add(new BasicNameValuePair(PARAM_PASSWORD, authtoken));
    //TODO Actually get location
    params.add(new BasicNameValuePair(PARAM_LOCATION, "unknown"));
    JSONArray parties = doGet(params, PARTIES_URI);
    return Party.fromJSONArray(parties);
  }

}
