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

import android.util.Log;
import android.location.Location;

import java.util.List;
import java.io.IOException;
import java.util.ArrayList;
import java.util.Date;
import java.net.URI;
import java.net.URISyntaxException;

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
import org.json.JSONObject;
import org.json.JSONException;


import org.klnusbaum.udj.containers.LibraryEntry;
import org.klnusbaum.udj.containers.PlaylistEntry;
import org.klnusbaum.udj.containers.Event;

/**
 * A connection to the UDJ server
 */
public class ServerConnection{
  
  private static final String TAG = "ServerConnection";
  private static final String PARAM_USERNAME = "username";

  private static final String PARAM_PASSWORD = "password";

  private static final String PARAME_EVENT_NAME = "name";
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
  private static final int SERVER_PORT = 4897;

  private static final String NETWORK_PROTOCOL = "http";
 
  private static final String SERVER_HOST = "10.0.2.2";

 
  private static final String TICKET_HASH_HEADER = "X-Udj-Ticket-Hash";
 
  private static final int REGISTRATION_TIMEOUT = 30 * 1000; // ms
  
  private static final String AVAILABLE_QUERY_PARAM = "query";

  private static DefaultHttpClient httpClient;

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


  public static String authenticate(String username, String password)
    throws AuthenticationException, IOException
  {
    URI AUTH_URI = null;
    try{
      AUTH_URI = new URI(
        NETWORK_PROTOCOL,"",  SERVER_HOST, SERVER_PORT, "/udj/auth", "", "");
    }
    catch(URISyntaxException e){
      //TODO should never get here but I should do something if it does.
    }
    final ArrayList<NameValuePair> params = new ArrayList<NameValuePair>();
    params.add(new BasicNameValuePair(PARAM_USERNAME, username));
    params.add(new BasicNameValuePair(PARAM_PASSWORD, password));
    boolean authWorked = false;
    HttpEntity entity = null;
    entity = new UrlEncodedFormEntity(params);
    final HttpPost post = new HttpPost(AUTH_URI);
    post.addHeader(entity.getContentType());
    post.setEntity(entity);
    final HttpResponse resp = getHttpClient().execute(post);
    if(resp.getStatusLine().getStatusCode() == HttpStatus.SC_UNAUTHORIZED){
      throw new AuthenticationException();
    }
    else if(!resp.containsHeader(TICKET_HASH_HEADER)){
      throw new IOException("No ticket hash header was found in resposne");
    }
    else{
      return resp.getHeaders(TICKET_HASH_HEADER)[0].getValue();
    }
  }

  public static List<LibraryEntry> availableMusicQuery(
    String query,
    int eventId,
    String ticketHash)
    throws JSONException, ParseException, IOException, AuthenticationException
  {
    try{
      URI queryUri = new URI(
        NETWORK_PROTOCOL, "", SERVER_HOST, SERVER_PORT, 
        "/udj/events/" + eventId + "/available_music", 
        AVAILABLE_QUERY_PARAM + "=" +query, "");
      JSONArray searchResults = new JSONArray(doGet(queryUri, ticketHash));
      return LibraryEntry.fromJSONArray(searchResults);
    }
    catch(URISyntaxException e){
      return null;
      //TDOD inform caller that theire query is bad 
    }
  }
    
  public static List<PlaylistEntry> addSongToPlaylist(
    PlaylistEntry toAdd, int eventId, String ticketHash) 
    throws JSONException, ParseException, IOException, AuthenticationException
  {
    ArrayList<PlaylistEntry> toAddList = new ArrayList<PlaylistEntry>();
    toAddList.add(toAdd);
    return addSongsToPlaylist(toAddList, eventId, ticketHash);
  }

  public static List<PlaylistEntry> addSongsToPlaylist(  
    List<PlaylistEntry> added, int eventId, String ticketHash) throws
    JSONException, ParseException, IOException, AuthenticationException
  {
    //TODO implement
    return null;
    /*JSONArray toAddArray = PlaylistEntry.getJSONArray(added);
    params.add(new BasicNameValuePair(
      PARAM_PLAYLIST_TO_ADD, toAddArray.toString()));
    JSONArray returnedEntries = new JSONArray(doPost(params, PLAYLIST_URI));
    return PlaylistEntry.fromJSONArray(returnedEntries);*/
  }


  public static List<PlaylistEntry> getPlaylist(int eventId, String ticketHash) /*throws
    JSONException, ParseException, IOException, AuthenticationException*/
  {
    return null;
    /*Log.i("TAG", "Getting playlist.");
    JSONArray returnedEntries = new JSONArray(doGet(PLAYLIST_URI));
    return PlaylistEntry.fromJSONArray(returnedEntries);*/
  }

  /*public static String doPost(ArrayList<NameValuePair> params, String uri)
    throws AuthenticationException, IOException
  {
    String toReturn = null;
    HttpEntity entity = null;
    entity = new UrlEncodedFormEntity(params);
    final HttpPost post = new HttpPost(uri);
    post.addHeader(entity.getContentType());
    post.setEntity(entity);
    final HttpResponse resp = getHttpClient().execute(post);
    final String response = EntityUtils.toString(resp.getEntity());
    if(resp.getStatusLine().getStatusCode() == HttpStatus.SC_OK){
      toReturn = response;
    } 
    else if(resp.getStatusLine().getStatusCode() == HttpStatus.SC_UNAUTHORIZED){
      throw new AuthenticationException();
    }
    else{
      throw new IOException();
    }
    return toReturn;
  }*/

  public static String doGet(URI uri, String ticketHash)
    throws AuthenticationException, IOException
  {
    final HttpGet get = new HttpGet(uri);
    get.addHeader(TICKET_HASH_HEADER, ticketHash);
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

  public static List<Event> getNearbyEvents(
    Location location, String ticketHash)
    throws
    JSONException, ParseException, IOException, AuthenticationException
  {
    if(location == null) return null;
    try{
      URI eventsQuery = new URI(
        NETWORK_PROTOCOL, "", SERVER_HOST, SERVER_PORT, 
        "/udj/events/" + location.getLatitude() + "/" + location.getLongitude(),
        "", "");
      JSONArray events = new JSONArray(doGet(eventsQuery, ticketHash));
      return Event.fromJSONArray(events);
    }
    catch(URISyntaxException e){
      return null;
      //TDOD inform caller that theire query is bad 
    }
  }

  public static List<Event> searchForEvents(
    String query, String ticketHash)
    throws
    JSONException, ParseException, IOException, AuthenticationException
  {
    try{
      URI eventsQuery = new URI(
        NETWORK_PROTOCOL, "", SERVER_HOST, SERVER_PORT, 
        "/udj/events/",
        PARAME_EVENT_NAME+"="+query, "");
      JSONArray events = new JSONArray(doGet(eventsQuery, ticketHash));
      return Event.fromJSONArray(events);
    }
    catch(URISyntaxException e){
      return null;
      //TDOD inform caller that theire query is bad 
    }
  }

  public static void doPartyLogin(final long partyId){
    /*final ArrayList<NameValuePair> params = new ArrayList<NameValuePair>();
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
    });*/
  }

}
