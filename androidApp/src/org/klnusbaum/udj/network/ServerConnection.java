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
import java.util.Date;

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
import org.apache.http.cookie.Cookie;
import org.apache.http.auth.AuthScope;
import org.apache.http.auth.UsernamePasswordCredentials;

import org.json.JSONArray;
import org.json.JSONObject;
import org.json.JSONException;


import org.klnusbaum.udj.auth.AuthActivity;
import org.klnusbaum.udj.containers.LibraryEntry;
import org.klnusbaum.udj.containers.PlaylistEntry;
import org.klnusbaum.udj.containers.Party;
import org.klnusbaum.udj.containers.AcousticsInfo;

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
  public static final String SERVER_URL = "https://www-s.acm.uiuc.edu/acoustics";
  public static final String PLAYLIST_URI = 
    SERVER_URL + "/playlist";
  public static final String LIBRARY_URI = 
    SERVER_URL + "/library";
  /*public static final String PARTIES_URI =
    SERVER_URL + "/parties";*/
  public static final String QUERY_URI =
    SERVER_URL + "/json.pl";
  public static final String AUTH_URI =
    SERVER_URL + "/www-data/auth";
  public static final String CHANGE_PARTY_BASE_URI = 
    QUERY_URI + "?mode=change_player;player_id=";
  public static final int REGISTRATION_TIMEOUT = 30 * 1000; // ms

  private static DefaultHttpClient httpClient;

  private static final String LOGIN_COOKIE_NAME = "CGISESSID";
  
  private static final AuthScope SERVER_AUTH_SCOPE = 
    new AuthScope("www-s.acm.uiuc.edu", AuthScope.ANY_PORT);


  public static DefaultHttpClient getHttpClient(){
    if(httpClient == null){
      httpClient = new DefaultHttpClient();
      final HttpParams params = httpClient.getParams();
      HttpConnectionParams.setConnectionTimeout(params, REGISTRATION_TIMEOUT);
      HttpConnectionParams.setSoTimeout(params, REGISTRATION_TIMEOUT);
      ConnManagerParams.setTimeout(params, REGISTRATION_TIMEOUT);
      /*httpClient.getAuthSchemes().register(
        AuthPolicy.SPNEGO, new NegotiateSchemeFactory());*/
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

    if(!needCookieRefresh(username, password)){
      returnToActivityIfNecessary(true, handler, context);
      return true;
    }
    UsernamePasswordCredentials creds = 
      new UsernamePasswordCredentials(username, password);
    DefaultHttpClient client = getHttpClient();
    client.getCredentialsProvider().setCredentials(SERVER_AUTH_SCOPE, creds);

    boolean authWorked = false;
    try{
      HttpGet get = new HttpGet(AUTH_URI);
      HttpResponse resp = client.execute(get);
      authWorked = hasValidCookie();
    }
    /*catch(AuthenticationException e){
      Log.e("TAG", "Auth exceptions");
      //TODO maybe do something?
    }*/
    catch(IOException e){
      Log.e("TAG", "IOException exceptions");
      //TODO maybe do something?
    }

    returnToActivityIfNecessary(authWorked, handler, context);
    return authWorked;
  }

  private static void returnToActivityIfNecessary(
    final boolean authWorked, Handler handler, final Context context)
  {
    UsernamePasswordCredentials creds = 
      (UsernamePasswordCredentials)getHttpClient()
      .getCredentialsProvider()
      .getCredentials(SERVER_AUTH_SCOPE);
    final String username = creds.getUserName();
    final String password = creds.getPassword();
    if(handler != null && context != null){
      handler.post(new Runnable(){
        public void run(){
          ((AuthActivity) context).onAuthResult(authWorked, username, password);
        }
      });
    }
  }

  public static List<PlaylistEntry> getPlaylistUpdate(  
    long partyId,
    List<PlaylistEntry> toUpdate, 
    GregorianCalendar lastUpdated) throws
    JSONException, ParseException, IOException, AuthenticationException
  {
    final ArrayList<NameValuePair> params = 
      getEssentialParameters(partyId, lastUpdated);
    JSONObject acousticsInfo =null;
    if(toUpdate == null || toUpdate.isEmpty()){
      //TODO we should actually do a get here because we're not changing 
      //anything.
      playlistEntries = new JSONObject(doGet(params, QUERY_URI));
    }
    else{
      params.add(new BasicNameValuePair(
        PARAM_UPDATE_ARRAY, 
        PlaylistEntry.getJSONArray(toUpdate).toString()));
      playlistEntries = doPost(params, PLAYLIST_URI);
    }
    //return PlaylistEntry.fromJSONArray(playlistEntries);
    return AcousticsInfo.getPlaylistEntries(acousticsInfo);
  }

  private static ArrayList<NameValuePair> getEssentialParameters(
     long partyId, GregorianCalendar lastUpdated)
  {
    ArrayList<NameValuePair> params = new ArrayList<NameValuePair>();
    params.add(new BasicNameValuePair(PARAM_PARTYID, String.valueOf(partyId)));
    //TODO Needs to be changed for acoustics
    /*if(lastUpdated != null){
      final SimpleDateFormat formatter =
        new SimpleDateFormat(SERVER_TIMESTAMP_FORMAT);
      formatter.setTimeZone(TimeZone.getTimeZone("UTC"));
      params.add(new BasicNameValuePair(
        PARAM_LAST_UPDATE, formatter.format(lastUpdated)));
    }*/
    return params;
  }

  public static void doSimplePost(ArrayList<NameValuePair> params, String uri)
    throws AuthenticationException, IOException
  {
    HttpEntity entity = null;
    entity = new UrlEncodedFormEntity(params);
    final HttpPost post = new HttpPost(uri);
    post.addHeader(entity.getContentType());
    post.setEntity(entity);
    final HttpResponse resp = getHttpClient().execute(post);
    if(resp.getStatusLine().getStatusCode() == HttpStatus.SC_UNAUTHORIZED){
      throw new AuthenticationException();
    }
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

  public static String doGet(ArrayList<NameValuePair> params, String uri)
    throws AuthenticationException, IOException
  {
    final HttpGet get = new HttpGet(uri + getParamString(params));
    final HttpResponse resp = getHttpClient().execute(get);
    String response = EntityUtils.toString(resp.getEntity());
    if(resp.getStatusLine().getStatusCode() != HttpStatus.SC_UNAUTHORIZED){
      return response;
    }
    else if(resp.getStatusLine().getStatusCode() == HttpStatus.SC_UNAUTHORIZED){
      throw new AuthenticationException();
    }
    else{
      throw new IOException();
    }
  }

  private static String getParamString(ArrayList<NameValuePair> params){
    if(params == null){
      return "";
    }
    String toReturn = "?";
    boolean isFirst = true;
    for(NameValuePair np: params){
      if(isFirst){
        toReturn += np.getName() + "=" +np.getValue();
        isFirst=false;
      }
      else{
        toReturn += "&" + np.getName() + "=" +np.getValue();
      }
    }
    return toReturn;
  }

  public static List<Party> getNearbyParties(Account account, String authtoken)
    throws
    JSONException, ParseException, IOException, AuthenticationException
  {
    final ArrayList<NameValuePair> params = new ArrayList<NameValuePair>();
    //TODO Actually get location
    params.add(new BasicNameValuePair(PARAM_LOCATION, "unknown"));
    JSONObject acousticsInfo = new JSONObject(doGet(params, QUERY_URI));
    return AcousticsInfo.getParties(acousticsInfo);
  }

  private static boolean needCookieRefresh(String username, String password){
    UsernamePasswordCredentials creds = 
      (UsernamePasswordCredentials)getHttpClient()
      .getCredentialsProvider()
      .getCredentials(SERVER_AUTH_SCOPE);
    if(
      creds == null ||
      creds.getUserName() == null ||
      !creds.getUserName().equals(username) ||
      creds.getPassword() == null ||
      !creds.getPassword().equals(username)
    )
    {
      return true;
    }
    return !hasValidCookie();
  }

  private static boolean hasValidCookie(){
    for(Cookie cookie: getHttpClient().getCookieStore().getCookies()){
      if(cookie.getName().equals(LOGIN_COOKIE_NAME))
      {
        return true;
      }
    }
    return false;
  }

  public static void loginToParty(
    int position, 
    String partyName, 
    Handler handler)
  {
    final boolean success = true;
    try{
      doGet(CHANGE_PARTY_BASE_URI+partyName, null); 
    }
    catch(AuthenticationException e){
      success = false;
    }
    catch(IOException e){
      success = false;
    }
    handler.post(new Runnable(){
      public void run(){
        ((PartySelectorActivity) context).onPartyLogin(
          success, position, partyName);
      }
    });
  }
}
