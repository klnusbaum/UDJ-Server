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
import android.database.Cursor;

import java.util.List;
import java.util.HashMap;
import java.io.IOException;
import java.util.ArrayList;
import java.util.Date;
import java.net.URI;
import java.net.URISyntaxException;
import java.security.KeyStore;
import java.security.NoSuchAlgorithmException;
import java.security.KeyManagementException;
import java.security.KeyStoreException;
import java.security.UnrecoverableKeyException;
import java.security.cert.CertificateException;


import org.apache.http.params.BasicHttpParams;
import org.apache.http.HttpVersion;
import org.apache.http.Header;
import org.apache.http.conn.scheme.Scheme;
import org.apache.http.conn.scheme.SchemeRegistry;
import org.apache.http.conn.scheme.PlainSocketFactory;
import org.apache.http.params.HttpProtocolParams;
import org.apache.http.impl.conn.tsccm.ThreadSafeClientConnManager;
import org.apache.http.HttpEntity;
import org.apache.http.HttpResponse;
import org.apache.http.HttpStatus;
import org.apache.http.auth.AuthenticationException;
import org.apache.http.client.HttpClient;
import org.apache.http.client.entity.UrlEncodedFormEntity;
import org.apache.http.entity.StringEntity;
import org.apache.http.client.methods.HttpPost;
import org.apache.http.client.methods.HttpGet;
import org.apache.http.client.methods.HttpPut;
import org.apache.http.client.methods.HttpDelete;
import org.apache.http.NameValuePair;
import org.apache.http.ParseException;
import org.apache.http.client.HttpClient;
import org.apache.http.message.BasicNameValuePair;
import org.apache.http.conn.params.ConnManagerParams;
import org.apache.http.impl.client.DefaultHttpClient;
import org.apache.http.params.HttpConnectionParams;
import org.apache.http.params.HttpParams;
import org.apache.http.util.EntityUtils;
import org.apache.http.protocol.HTTP;
import org.apache.http.conn.ssl.SSLSocketFactory;

import org.json.JSONArray;
import org.json.JSONObject;
import org.json.JSONException;


import org.klnusbaum.udj.containers.LibraryEntry;
import org.klnusbaum.udj.containers.Event;
import org.klnusbaum.udj.UDJEventProvider;
import org.klnusbaum.udj.exceptions.EventOverException;
import org.klnusbaum.udj.exceptions.AlreadyInEventException;
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

  //private static final String NETWORK_PROTOCOL = "http";
  private static final String NETWORK_PROTOCOL = "https";
 
  //private static final String SERVER_HOST = "udjevents.com";
  private static final String SERVER_HOST = "10.0.2.2";

 
  private static final String TICKET_HASH_HEADER = "X-Udj-Ticket-Hash";
  private static final String USER_ID_HEADER = "X-Udj-User-Id";
 
  private static final int REGISTRATION_TIMEOUT = 30 * 1000; // ms
  
  private static final String AVAILABLE_QUERY_PARAM = "query";

  private static DefaultHttpClient httpClient;

  public static DefaultHttpClient getHttpClient() throws IOException{
    if(httpClient == null){
      try{
      KeyStore trustStore = KeyStore.getInstance(KeyStore.getDefaultType());
      trustStore.load(null,null);

      SSLSocketFactory sf = new CustomSSLSocketFactory(trustStore);
      sf.setHostnameVerifier(SSLSocketFactory.ALLOW_ALL_HOSTNAME_VERIFIER);
      Log.e(TAG, 
        "Need to change host verifier to only work with udjevents.com");

      SchemeRegistry schemeReg = new SchemeRegistry();
      /*schemeReg.register(
        new Scheme("http", PlainSocketFactory.getSocketFactory(), SERVER_PORT));*/
      schemeReg.register(new Scheme(  
        "https", sf, SERVER_PORT));
      BasicHttpParams params = new BasicHttpParams();
      ConnManagerParams.setMaxTotalConnections(params, 100);
      HttpProtocolParams.setVersion(params, HttpVersion.HTTP_1_1);
      HttpProtocolParams.setContentCharset(params, HTTP.UTF_8);
      HttpProtocolParams.setUseExpectContinue(params, true);

      ThreadSafeClientConnManager cm = new ThreadSafeClientConnManager(
        params, schemeReg);
      httpClient = new DefaultHttpClient(cm, params);
      }
      catch(NoSuchAlgorithmException e){
        //SHould never get here 
      }
      catch(KeyManagementException e){
        //SHould never get here 
      }
      catch(KeyStoreException e){
        //SHould never get here 
      }
      catch(CertificateException e){
        //SHould never get here 
      }
      catch(UnrecoverableKeyException e){
        //SHould never get here 
      }
    }
    return httpClient;
  }

  public static class AuthResult{
    public String ticketHash;
    public long userId;
    
    public AuthResult(String ticketHash, long userId){
      this.ticketHash = ticketHash;
      this.userId = userId;
    }
  }

  public static AuthResult authenticate(String username, String password)
    throws AuthenticationException, IOException
  {
    URI AUTH_URI = null;
    try{
      AUTH_URI = new URI(
        NETWORK_PROTOCOL, null,
        SERVER_HOST, SERVER_PORT, "/udj/auth", null, null);
    }
    catch(URISyntaxException e){
      //TODO should never get here but I should do something if it does.
    }
    final ArrayList<NameValuePair> params = new ArrayList<NameValuePair>();
    params.add(new BasicNameValuePair(PARAM_USERNAME, username));
    params.add(new BasicNameValuePair(PARAM_PASSWORD, password));
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
      for(Header h: resp.getAllHeaders()){
        Log.d(TAG, "Response had header " + h.getName());
      }
      throw new IOException("No ticket hash header was found in resposne");
    }
    else{
      return new AuthResult(
        resp.getHeaders(TICKET_HASH_HEADER)[0].getValue(),
        Long.valueOf(resp.getHeaders(USER_ID_HEADER)[0].getValue()));
    }
  }

  private static void basicResponseErrorCheck(
    HttpResponse resp, String response)
    throws AuthenticationException, IOException
  {
    basicResponseErrorCheck(resp, response, false);
  }

  private static void basicResponseErrorCheck(
    HttpResponse resp, 
    String response,
    boolean createdIsOk
  )
    throws AuthenticationException, IOException
  {
    if(resp.getStatusLine().getStatusCode() == HttpStatus.SC_FORBIDDEN){
      throw new AuthenticationException();
    }
    else if(
      resp.getStatusLine().getStatusCode() != HttpStatus.SC_OK && 
      !(
        createdIsOk && 
        resp.getStatusLine().getStatusCode() == HttpStatus.SC_CREATED)
      )
    {
      throw new IOException(response);
    }
  }

  private static void eventOverErrorCheck(HttpResponse resp)
    throws EventOverException
  {
    if(resp.getStatusLine().getStatusCode() == HttpStatus.SC_GONE){
      throw new EventOverException();
    }
  } 


  public static HttpResponse doGet(URI uri, String ticketHash)
    throws IOException
  {
    Log.d(TAG, "Doing get with uri: " + uri);
    final HttpGet get = new HttpGet(uri);
    get.addHeader(TICKET_HASH_HEADER, ticketHash);
    return getHttpClient().execute(get);
  }

  public static String doSimpleGet(URI uri, String ticketHash)
    throws AuthenticationException, IOException
  {
    final HttpResponse resp = doGet(uri, ticketHash);
    final String response = EntityUtils.toString(resp.getEntity());
    Log.d(TAG, "Simple get response: \"" + response +"\"");
    basicResponseErrorCheck(resp, response);
    return response;
  }

  public static String doEventRelatedGet(URI uri, String ticketHash)
    throws AuthenticationException, IOException, EventOverException
  {
    final HttpResponse resp = doGet(uri, ticketHash);
    final String response = EntityUtils.toString(resp.getEntity());
    Log.d(TAG, "Event related response: \"" + response +"\"");
    eventOverErrorCheck(resp);
    basicResponseErrorCheck(resp, response);
    return response;
  }

  public static HttpResponse doPut(URI uri, String ticketHash, String payload)
    throws IOException
  {
    Log.d(TAG, "Doing put to uri: " + uri);
    Log.d(TAG, "Put payload is: "+ (payload != null ? payload : "no payload"));
    String toReturn = null;
    final HttpPut put = new HttpPut(uri);
    put.addHeader(TICKET_HASH_HEADER, ticketHash);
    if(payload != null){
      StringEntity entity = new StringEntity(payload);
      entity.setContentType("text/json");
      put.addHeader(entity.getContentType());
      put.setEntity(entity);
    }
    return getHttpClient().execute(put);
  }

  public static String doSimplePut(URI uri, String ticketHash, String payload)
    throws AuthenticationException, IOException
  {
    final HttpResponse resp = doPut(uri, ticketHash, payload);
    final String response = EntityUtils.toString(resp.getEntity());
    Log.d(TAG, "Simple Put response: \"" + response +"\"");
    basicResponseErrorCheck(resp, response, true);
    return response;
  }

  public static String doEventRelatedPut( 
    URI uri, String ticketHash, String payload)
    throws AuthenticationException, IOException, EventOverException
  {
    final HttpResponse resp = doPut(uri, ticketHash, payload);
    final String response = EntityUtils.toString(resp.getEntity());
    Log.d(TAG, "Event related Put response: \"" + response +"\"");
    eventOverErrorCheck(resp);
    basicResponseErrorCheck(resp, response, true);
    return response;
  }

  public static HttpResponse doPost(URI uri, String authToken, String payload)
    throws AuthenticationException, IOException
  {
    Log.d(TAG, "Doing post to uri: " + uri);
    Log.d(TAG, "Post payload is: "+ (payload != null ? payload : "no payload"));
    String toReturn = null;
    final HttpPost post = new HttpPost(uri);
    if(payload != null){
      StringEntity entity = new StringEntity(payload);
      entity.setContentType("text/json");
      post.setEntity(entity);
    }
    post.addHeader(TICKET_HASH_HEADER, authToken);
    return getHttpClient().execute(post);
  }

  public static String doSimplePost(URI uri, String authToken, String payload)
    throws AuthenticationException, IOException
  {
    final HttpResponse resp = doPost(uri, authToken, payload);
    final String response = EntityUtils.toString(resp.getEntity());
    Log.d(TAG, "Simple Post response: \"" + response +"\"");
    basicResponseErrorCheck(resp, response, true);
    return response;
  }

  public static String doEventRelatedPost(
    URI uri, String authToken, String payload)
    throws AuthenticationException, IOException, EventOverException
  {
    final HttpResponse resp = doPost(uri, authToken, payload);
    final String response = EntityUtils.toString(resp.getEntity());
    Log.d(TAG, "Event related Post response: \"" + response +"\"");
    eventOverErrorCheck(resp);
    basicResponseErrorCheck(resp, response, true);
    return response;

  }
   
  public static HttpResponse doDelete(URI uri, String ticketHash)
    throws IOException, AuthenticationException
  {
    Log.d(TAG, "Doing delete to uri: " + uri);
    final HttpDelete delete = new HttpDelete(uri);
    delete.addHeader(TICKET_HASH_HEADER, ticketHash);
    return getHttpClient().execute(delete);
  }

  public static void doSimpleDelete(URI uri, String ticketHash)
    throws IOException, AuthenticationException
  {
    final HttpResponse resp = doDelete(uri, ticketHash);
    final String response = EntityUtils.toString(resp.getEntity());
    Log.d(TAG, "Delete response: \"" + response +"\"");
    basicResponseErrorCheck(resp, response);
  }

  public static void doEventRelatedDelete(URI uri, String ticketHash)
    throws IOException, AuthenticationException, EventOverException
  {
    final HttpResponse resp = doDelete(uri, ticketHash);
    final String response = EntityUtils.toString(resp.getEntity());
    Log.d(TAG, "Delete response: \"" + response +"\"");
    eventOverErrorCheck(resp);
    basicResponseErrorCheck(resp, response);
  }

  public static List<Event> getNearbyEvents(
    Location location, String ticketHash)
    throws
    JSONException, ParseException, IOException, AuthenticationException
  {
    if(location == null) return null;
    try{
      URI eventsQuery = new URI(
        NETWORK_PROTOCOL, null, SERVER_HOST, SERVER_PORT, 
        "/udj/events/" + location.getLatitude() + "/" + location.getLongitude(),
        null, null);
      JSONArray events = new JSONArray(doSimpleGet(eventsQuery, ticketHash));
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
        NETWORK_PROTOCOL, null, SERVER_HOST, SERVER_PORT, 
        "/udj/events",
        PARAME_EVENT_NAME+"="+query, null);
      JSONArray events = new JSONArray(doSimpleGet(eventsQuery, ticketHash));
      return Event.fromJSONArray(events);
    }
    catch(URISyntaxException e){
      return null;
      //TDOD inform caller that theire query is bad 
    }
  }

  private static void evenJoinConflictCheck(
    HttpResponse resp,
    String response,
    long userId)
    throws JSONException, ParseException, AlreadyInEventException
  {
    if(resp.getStatusLine().getStatusCode() == HttpStatus.SC_CONFLICT){
      JSONObject event = new JSONObject(response);
      if(userId == event.getLong("host_id")){
        //TODO throw already hosting exception
      }
      else{
        throw new AlreadyInEventException(
          event.getLong("id"), event.getString("name"));
      }
    }
  }

  public static void joinEvent(long eventId, long userId, String ticketHash)
    throws IOException, AuthenticationException, EventOverException, 
    AlreadyInEventException, JSONException, ParseException
  {
    try{
      URI uri  = new URI(
        NETWORK_PROTOCOL, null, SERVER_HOST, SERVER_PORT, 
        "/udj/events/" + eventId + "/users/"+userId,
        null, null);
      final HttpResponse resp = doPut(uri, ticketHash, "");
      final String response = EntityUtils.toString(resp.getEntity());
      Log.d(TAG, "Event join Put response: \"" + response +"\"");
      evenJoinConflictCheck(resp, response, userId);
      eventOverErrorCheck(resp);
      basicResponseErrorCheck(resp, response, true);
    }
    catch(URISyntaxException e){
      Log.e(TAG, "URI syntax error in join event");
    }
  }

  public static void leaveEvent(long eventId, long userId, String authToken)
    throws IOException, AuthenticationException
  {
    try{
      URI uri = new URI(
        NETWORK_PROTOCOL, null, SERVER_HOST, SERVER_PORT, 
        "/udj/events/"+eventId+"/users/"+userId,
        null, null);
      try{
        doEventRelatedDelete(uri, authToken);
      }
      catch(EventOverException e){
        //If we get here that's fine. no worries.
      }
    }
    catch(URISyntaxException e){
      //TODO inform caller that theire query is bad 
    }
  }

  public static JSONObject getActivePlaylist(long eventId, 
    String authToken)
    throws JSONException, ParseException, IOException, AuthenticationException,
    EventOverException
  {
    try{
      URI uri = new URI(
        NETWORK_PROTOCOL, null, SERVER_HOST, SERVER_PORT, 
        "/udj/events/"+eventId+"/active_playlist",
        null, null);
      return new JSONObject(doEventRelatedGet(uri, authToken));
    }
    catch(URISyntaxException e){
      return null;
      //TODO inform caller that theire query is bad 
    }
  }


  public static List<LibraryEntry> availableMusicQuery(
    String query, long eventId, String authToken)
    throws JSONException, ParseException, IOException, AuthenticationException,
    EventOverException
  {
    try{
      URI uri = new URI(
        NETWORK_PROTOCOL, null, SERVER_HOST, SERVER_PORT,
        "/udj/events/"+eventId+"/available_music",
        "query="+query, null);
      JSONArray libEntries = new JSONArray(doEventRelatedGet(uri, authToken));
      return LibraryEntry.fromJSONArray(libEntries);
    }
    catch(URISyntaxException e){
      //TODO inform caller that theire query is bad 
    }
    return null;
  }

  public static void addSongsToActivePlaylist(
    HashMap<Long, Long> requests, long eventId, String authToken)
    throws JSONException, ParseException, IOException, AuthenticationException,
    EventOverException
  {
    try{
      URI uri = new URI(
        NETWORK_PROTOCOL, null, SERVER_HOST, SERVER_PORT,
        "/udj/events/"+eventId+"/active_playlist/songs",
        null, null);
      String payload = getAddToActivePlaylistJSON(requests).toString();
      Log.d(TAG, "Add songs to active playlist payload");
      Log.d(TAG, payload);
      doEventRelatedPut(uri, authToken, payload); 
    }
    catch(URISyntaxException e){
      //TODO inform caller that theire query is bad 
    }
  }

  private static JSONArray getAddToActivePlaylistJSON(
    HashMap<Long, Long> requests) throws JSONException
  
  {
    JSONArray toReturn = new JSONArray();
    for(Long requestId : requests.keySet()){
      JSONObject requestObject = new JSONObject();
      requestObject.put("client_request_id", requestId);
      requestObject.put("lib_id", requests.get(requestId));
      toReturn.put(requestObject);
    }
    return toReturn;
  }

  public static HashMap<Long,Long> getAddRequests(
    long userId, long eventId, String authToken)
    throws JSONException, ParseException, IOException, AuthenticationException,
    EventOverException
  {
    try{
      URI uri = new URI(
        NETWORK_PROTOCOL, null, SERVER_HOST, SERVER_PORT,
        "/udj/events/"+eventId+"/active_playlist/users/"+
          userId + "/add_requests",
        null, null);
      return getRequestsHashMap(
        new JSONArray(doEventRelatedGet(uri, authToken)));
    }
    catch(URISyntaxException e){
      //TODO inform caller that theire query is bad 
    }
    return null;
  }

  private static HashMap<Long, Long> getRequestsHashMap(JSONArray requests)
    throws JSONException
  {
    HashMap<Long, Long> toReturn = new HashMap<Long, Long>();
    for(int i=0; i<requests.length(); ++i){
      JSONObject jObj = requests.getJSONObject(i);
      toReturn.put(jObj.getLong("client_request_id"), jObj.getLong("lib_id"));
    }
    return toReturn;
  }

  public static JSONObject getVoteRequests(
    long userId, long eventId, String authToken)
    throws JSONException, ParseException, IOException, AuthenticationException,
    EventOverException
  {
    try{
      URI uri = new URI(
        NETWORK_PROTOCOL, null, SERVER_HOST, SERVER_PORT,
        "/udj/events/"+eventId+"/active_playlist/users/"+
          userId + "/votes",
        null, null);
      return new JSONObject(doEventRelatedGet(uri, authToken));
    }
    catch(URISyntaxException e){
      //TODO inform caller that theire query is bad 
    }
    return null;
  }

  public static void doSongVotes(Cursor voteRequests, 
    long eventId, long userId, String authToken)
    throws IOException, AuthenticationException, EventOverException
  {
    if(voteRequests.moveToFirst()){
      int idColumnIndex = voteRequests.getColumnIndex(
        UDJEventProvider.VOTE_PLAYLIST_ENTRY_ID_COLUMN);
      int voteTypeIndex = voteRequests.getColumnIndex(
        UDJEventProvider.VOTE_TYPE_COLUMN);
      do{
        long playlistId = voteRequests.getLong(idColumnIndex);
        int voteType = voteRequests.getInt(voteTypeIndex);
        voteOnSong(eventId, playlistId, userId, voteType, authToken);
      }while(voteRequests.moveToNext());
    }
  }

  private static void voteOnSong(
    long eventId, long playlistId, long userId, int voteType, String authToken)
    throws IOException, AuthenticationException, EventOverException
  {
    String voteString = null;
    if(voteType == UDJEventProvider.UP_VOTE_TYPE){
      voteString = "upvote";
    }
    else if(voteType == UDJEventProvider.DOWN_VOTE_TYPE){
      voteString = "downvote";
    }
    try{
      URI uri = new URI(
        NETWORK_PROTOCOL, null, SERVER_HOST, SERVER_PORT,
        "/udj/events/"+eventId+"/active_playlist/" + playlistId + "/users/"+
          userId + "/" + voteString,
        null, null);
      doEventRelatedPost(uri, authToken, null);
    }
    catch(URISyntaxException e){
      //TODO inform caller that theire query is bad 
    }
  }
}
