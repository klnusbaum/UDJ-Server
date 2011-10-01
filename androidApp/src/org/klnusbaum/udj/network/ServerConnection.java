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

import org.json.JSONArray;
import org.json.JSONObject;
import org.json.JSONException;


import org.klnusbaum.udj.auth.AuthActivity;
import org.klnusbaum.udj.containers.LibraryEntry;
import org.klnusbaum.udj.containers.PlaylistEntry;
import org.klnusbaum.udj.containers.Party;
import org.klnusbaum.udj.PartySelectorActivity;

/**
 * A connection to the UDJ server
 */
public class ServerConnection{
  
  public static final String PARAM_PARTYID = "partyId";
  public static final String PARAM_USERNAME = "username";
  public static final String PARAM_PASSWORD = "password";
  public static final String PARAM_LAST_UPDATE = "timestamp";
  public static final String PARAM_PLAYLIST_SYNC_INFO = "syncinfo";
  public static final String PARAM_PLAYLIST_ADDED= "added";
  public static final String PARAM_PLAYLIST_VOTED_UP= "votedUp";
  public static final String PARAM_PLAYLIST_VOTED_DOWN = "votedDown";
  public static final String PARAM_GET_PARTIES = "getParties";
  public static final String PARAM_LOCATION = "location";
  public static final String PARAM_LIB_QUERY = "search_query";
  public static final String SERVER_TIMESTAMP_FORMAT = "yyyy-mm-dd hh:mm:ss";
  /** 
   * This port number is a memorial to Keith Nusbaum, my father. I loved him
   * deeply and he was taken from this world far too soon. Never-the-less 
   * we all continue to benefit from his good deeds. Without him, I wouldn't 
   * be here, and there would be no UDJ. Please, don't change this port 
   * number. Keep the memory of my father alive.
   * K = 10 % 10 = 0
   * e = 4  % 10 = 4
   * i = 8  % 10 = 8
   * t = 19 % 10 = 9
   * h = 7  % 10 = 7
   * Port 4897, the Keith Nusbaum Memorial Port
   */
  public static final String SERVER_PORT_NUMBER = "4897"
  //public static final String SERVER_URL = "http://www.bazaarsolutions.org/udj";
  //THIS IS FOR TESTING AT THE MOMENT
  public static final String SERVER_URL = "http://10.0.2.2:"+SERVER_PORT_NUMBER;
  public static final String PLAYLIST_URI = 
    SERVER_URL + "/playlist";
  public static final String LIBRARY_URI = 
    SERVER_URL + "/library";
  public static final String PARTIES_URI =
    SERVER_URL + "/parties";
  public static final String AUTH_URI =
    SERVER_URL + "/auth";
  public static final String PARTY_LOGIN_URI =
    SERVER_URL + "/party_login";
  public static final String SYNC_PLAYLIST_URI =
    SERVER_URL + "/sync_playlist";
  public static final int REGISTRATION_TIMEOUT = 30 * 1000; // ms

  private static DefaultHttpClient httpClient;
  private static String mostRecentUsername;
  private static String mostRecentPassword;

  private static final String LOGIN_COOKIE_NAME = "loggedIn";
  private static final String PARTY_ID_COOKIE_NAME = "partyId";
  


  public static DefaultHttpClient getHttpClient(){
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

    if(!needCookieRefresh(username, password)){
      returnToActivityIfNecessary(true, handler, context);
      return true;
    }

    mostRecentUsername = username;
    mostRecentPassword = password;
    final ArrayList<NameValuePair> params = new ArrayList<NameValuePair>();
    params.add(new BasicNameValuePair(PARAM_USERNAME, mostRecentUsername));
    params.add(new BasicNameValuePair(PARAM_PASSWORD, mostRecentPassword));
    boolean authWorked = false;
    try{
      doSimplePost(params, AUTH_URI);
      authWorked = hasValidCookie();
    }
    catch(AuthenticationException e){
      Log.e("TAG", "Auth Auth exceptions");
      //TODO maybe do something?
    }
    catch(IOException e){
      Log.e("TAG", "Auth IOException exceptions");
      //TODO maybe do something?
    }

    returnToActivityIfNecessary(authWorked, handler, context);
    return authWorked;
  }

  private static void returnToActivityIfNecessary(
    final boolean authWorked, Handler handler, final Context context)
  {
    if(handler != null && context != null){
      handler.post(new Runnable(){
        public void run(){
          ((AuthActivity) context).onAuthResult(authWorked, mostRecentUsername, mostRecentPassword);
        }
      });
    }
  }

  public static List<LibraryEntry> libraryQuery(
    long partyId,
    String searchQuery)
    throws JSONException, ParseException, IOException, AuthenticationException
  {
    final ArrayList<NameValuePair> params = 
      getEssentialParameters(partyId, null);
      params.add(new BasicNameValuePair(PARAM_LIB_QUERY, searchQuery));
    JSONArray libraryEntries = new JSONArray(doGet(params, LIBRARY_URI));
    return LibraryEntry.fromJSONArray(libraryEntries);
  }

  public static List<PlaylistEntry> getPlaylistUpdate(  
    long partyId,
    List<PlaylistEntry> added, 
    List<PlaylistEntry> votedUp, 
    List<PlaylistEntry> votedDown, 
    GregorianCalendar lastUpdated) throws
    JSONException, ParseException, IOException, AuthenticationException
  {
    Log.i("TAG", "Doing playlist update");
    final ArrayList<NameValuePair> params = 
      getEssentialParameters(partyId, lastUpdated);
    JSONArray playlistEntries =null;
    if(nothingToUpdate(added, votedUp, votedDown)){
      Log.i("TAG", "Doing playlist get!");
      playlistEntries = new JSONArray(doGet(params, PLAYLIST_URI));
    }
    else{
      Log.i("TAG", "Doing playlist sync!");
      JSONObject syncInfo = new JSONObject();
      syncInfo.put(
        PARAM_PLAYLIST_ADDED, 
        PlaylistEntry.getJSONArray(added));
      syncInfo.put(
        PARAM_PLAYLIST_VOTED_UP,
        PlaylistEntry.getJSONArray(votedUp));
      syncInfo.put(
        PARAM_PLAYLIST_VOTED_DOWN,
        PlaylistEntry.getJSONArray(votedDown));
      params.add(new BasicNameValuePair(
        PARAM_PLAYLIST_SYNC_INFO, syncInfo.toString()));
      playlistEntries = doPost(params, SYNC_PLAYLIST_URI);
    }
    return PlaylistEntry.fromJSONArray(playlistEntries);
  }

  private static ArrayList<NameValuePair> getEssentialParameters(
    long partyId, GregorianCalendar lastUpdated)
  {
    ArrayList<NameValuePair> params = new ArrayList<NameValuePair>();
    ArrayList<PlaylistEntry> toReturn = new ArrayList<PlaylistEntry>();
    params.add(new BasicNameValuePair(PARAM_PARTYID, String.valueOf(partyId)));
    //TODO ACTUALLY GET THIS WORKING
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
    final HttpGet get = new HttpGet(uri + "?" + getParamString(params));
    final HttpResponse resp = getHttpClient().execute(get);
    final String response = EntityUtils.toString(resp.getEntity());
    if(resp.getStatusLine().getStatusCode() == HttpStatus.SC_OK){
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
    JSONArray parties = new JSONArray(doGet(params, PARTIES_URI));
    return Party.fromJSONArray(parties);
  }

  private static boolean needCookieRefresh(String username, String password){
    if(
      mostRecentUsername == null ||
      mostRecentPassword == null ||
      !mostRecentUsername.equals(username) ||
      !mostRecentPassword.equals(password)
    )
    {
      return true;
    }
    return !hasValidCookie();
  }

  private static boolean hasValidCookie(){
    for(Cookie cookie: getHttpClient().getCookieStore().getCookies()){
      if(cookie.getName().equals(LOGIN_COOKIE_NAME)){
        return true;
      }
    }
    return false;
  }

  public static Thread loginToParty(
    final long partyId,
    final Handler messageHandler, 
    final Context context)
  {
    final Thread t = new Thread(){
      public void run(){
        doPartyLogin(partyId, messageHandler, context);
      }
    };
    t.start();
    return t;
  }

  public static void doPartyLogin(
    final long partyId,
    final Handler handler, 
    final Context context)
  {
    final ArrayList<NameValuePair> params = new ArrayList<NameValuePair>();
    params.add(new BasicNameValuePair(PARAM_PARTYID, String.valueOf(partyId)));
    params.add(new BasicNameValuePair(PARAM_USERNAME, mostRecentUsername));
    try{
      doSimplePost(params,PARTY_LOGIN_URI);
      
    }
    catch(AuthenticationException e){
      Log.e("TAG", "Party login Auth exceptions");
      //TODO maybe do something?
    }
    catch(IOException e){
      Log.e("TAG", "Party login IOException exceptions");
      //TODO maybe do something?
    }
   
    handler.post(new Runnable(){
      public void run(){
        ((PartySelectorActivity)context).onPartySelection(
          isValidParty(), partyId);
      }
    });
  }

  private static boolean isValidParty(){
    for(Cookie cookie: getHttpClient().getCookieStore().getCookies()){
      if(cookie.getName().equals(PARTY_ID_COOKIE_NAME) &&
         !cookie.getValue().equals(String.valueOf(Party.INVALID_PARTY_ID)))
      {
        return true;
      }
    }
    return false;
  }

  private static boolean nothingToUpdate(
    List<PlaylistEntry> added,
    List<PlaylistEntry> votedUp,
    List<PlaylistEntry> votedDown)
  {
    return 
      (added == null || added.isEmpty()) &&
      (votedUp == null || votedUp.isEmpty()) &&
      (votedDown == null || votedDown.isEmpty());

  }

}
