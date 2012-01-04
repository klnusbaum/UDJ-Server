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
package org.klnusbaum.udj;

import android.content.ContentProvider;
import android.net.Uri;
import android.content.ContentValues;
import android.database.Cursor;
import android.database.sqlite.SQLiteDatabase;
import android.database.sqlite.SQLiteOpenHelper;
import android.database.sqlite.SQLiteQueryBuilder;
import android.content.Context;
import android.util.Log;
import android.database.SQLException;
import android.content.ContentUris;
import android.content.ContentResolver;
import android.content.ContentProviderOperation;
import android.content.OperationApplicationException;
import android.os.RemoteException;

import java.util.ArrayList;
import java.util.HashMap;

import org.json.JSONArray;
import org.json.JSONObject;
import org.json.JSONException;

/**
 * Content provider used to maintain the content asociated
 * with the current event the user is logged into.
 */
public class UDJEventProvider extends ContentProvider{
  
	/** Name of the database */
  private static final String DATABASE_NAME = "event.db";
	/** Database version number */
  private static final int DATABASE_VERSION = 1;

  /** URI for the playlist */
  public static final Uri PLAYLIST_URI = 
    Uri.parse("content://org.klnusbaum.udj/playlist");

  public static final Uri PLAYLIST_ADD_REQUEST_URI = 
    Uri.parse("content://org.klnusbaum.udj/playlist/add_request");

  public static final Uri VOTES_URI = 
    Uri.parse("content://org.klnusbaum.udj/playlist/votes");

  public static final Uri CURRENT_SONG_URI =
    Uri.parse("content://org.klnusbaum.udj/current_song");


  /** PLAYLIST TABLE */

	/** Name of the playlist table. */
  private static final String PLAYLIST_TABLE_NAME = "playlist";

	/** Constants used for various Playlist column names */
  public static final String PLAYLIST_ID_COLUMN = "_id";
  public static final String UP_VOTES_COLUMN = "up_votes";
  public static final String DOWN_VOTES_COLUMN = "down_votes";
  public static final String PRIORITY_COLUMN = "priority";
  public static final String TIME_ADDED_COLUMN ="time_added";
  public static final String TITLE_COLUMN = "title";
  public static final String ARTIST_COLUMN = "artist";
  public static final String ALBUM_COLUMN = "album";
  public static final String DURATION_COLUMN = "duration";
  public static final String ADDER_ID_COLUMN = "adder_id";
  public static final String ADDER_USERNAME_COLUMN = "adder_username";

	/** SQL statement for creating the playlist table. */
  private static final String PLAYLIST_TABLE_CREATE = 
    "CREATE TABLE " + PLAYLIST_TABLE_NAME + "("+
		PLAYLIST_ID_COLUMN + " INTEGER PRIMARY KEY , " +
    UP_VOTES_COLUMN + " INTEGER NOT NULL, " +
    DOWN_VOTES_COLUMN + " INTEGER NOT NULL, " +
    PRIORITY_COLUMN + " INTEGER NOT NULL, "  +
    TIME_ADDED_COLUMN + " TEXT NOT NULL, " +
    DURATION_COLUMN + " INTEGER NOT NULL, " +
		TITLE_COLUMN + " TEXT NOT NULL, " +
    ARTIST_COLUMN + " TEXT NOT NULL, " + 
    ALBUM_COLUMN + " TEXT NOT NULL, " +
    ADDER_ID_COLUMN + " INTEGER NOT NULL, " +
    ADDER_USERNAME_COLUMN + " STRING NOT NULL);";

  /** SONG ADD REQUESTS TABLE */

  /** Name of add request table. */
  private static final String ADD_REQUESTS_TABLE_NAME = "add_requests";
  
  /** Constants used for various column names in the song add request table. */
  public static final String ADD_REQUEST_ID_COLUMN = "_id";
  public static final String ADD_REQUEST_LIB_ID_COLUMN = "lib_id";
  public static final String ADD_REQUEST_SYNC_STATUS_COLUMN = "sync_status";

  /** Constants used for the sync status of an add request */
  public static final int ADD_REQUEST_NEEDS_SYNC = 1;
  public static final int ADD_REQUEST_SYNCED = 0;

  /** SQL statement for creating the song add requests table. */
  private static final String ADD_REQUEST_TABLE_CREATE = 
    "CREATE TABLE " + ADD_REQUESTS_TABLE_NAME + "(" +
    ADD_REQUEST_ID_COLUMN + " INTEGER PRIMARY KEY AUTOINCREMENT, " + 
    ADD_REQUEST_LIB_ID_COLUMN + " INTEGER NOT NULL, " +
    ADD_REQUEST_SYNC_STATUS_COLUMN + " INTEGER DEFAULT "+ 
      ADD_REQUEST_NEEDS_SYNC + ", " +
    "CHECK (" + ADD_REQUEST_SYNC_STATUS_COLUMN + "=" + ADD_REQUEST_NEEDS_SYNC +
    " OR " + ADD_REQUEST_SYNC_STATUS_COLUMN + "=" + ADD_REQUEST_SYNCED +
    "));";


   /** VOTES TABLE */
   
   /** Name of votes table */
   private static final String VOTES_TABLE_NAME = "votes";

   /** Constants used for various column names in the votes table */
   public static final String VOTE_ID_COLUMN = "_id";
   public static final String VOTE_PLAYLIST_ENTRY_ID_COLUMN = "playlist_id";
   public static final String VOTE_TYPE_COLUMN = "vote_type";
   public static final String VOTE_SYNC_STATUS_COLUMN = "sync_status";

   /** Constants used for the sync status of an up vote */
   public static final int VOTE_NEEDS_SYNC = 1;
   public static final int VOTE_SYNCED = 0;

   /** Constants use for vote types */
   public static final int UP_VOTE_TYPE = 1;
   public static final int DOWN_VOTE_TYPE = 2;

   /** SQL statement for creating the up votes table */
  private static final String VOTES_TABLE_CREATE = 
    "CREATE TABLE " + VOTES_TABLE_NAME + " (" +
    VOTE_ID_COLUMN + " INTEGER PRIMARY KEY AUTOINCREMENT, " + 
    VOTE_PLAYLIST_ENTRY_ID_COLUMN + " INTEGER UNIQUE REFERENCES " +
      PLAYLIST_TABLE_NAME + "(" + PLAYLIST_ID_COLUMN + ") ON DELETE CASCADE, " +
    VOTE_TYPE_COLUMN + " INTEGER NOT NULL CHECK(" +
      VOTE_TYPE_COLUMN +"=" + UP_VOTE_TYPE + " OR " + VOTE_TYPE_COLUMN + "=" + 
      DOWN_VOTE_TYPE + "), " + 
    VOTE_SYNC_STATUS_COLUMN + " INTEGER DEFAULT "+ VOTE_NEEDS_SYNC + " " +
    "CHECK (" + VOTE_SYNC_STATUS_COLUMN + "=" + VOTE_NEEDS_SYNC +
    " OR " + VOTE_SYNC_STATUS_COLUMN + "=" + VOTE_SYNCED + "));";

  /** Playlist View */

  /** Name of view */
  private static final String PLAYLIST_VIEW_NAME = "playlist_view";
 
  /** SQL statement for creating the playlist view */
  private static final String PLAYLIST_VIEW_CREATE =
    "CREATE VIEW " + PLAYLIST_VIEW_NAME + " AS SELECT * FROM " +
    PLAYLIST_TABLE_NAME + " LEFT JOIN " + VOTES_TABLE_NAME + " ON " +
    PLAYLIST_TABLE_NAME + "." + PLAYLIST_ID_COLUMN + "=" +
    VOTES_TABLE_NAME + "." + VOTE_PLAYLIST_ENTRY_ID_COLUMN + ";";

  /** Current Song Table */

  /** Name of table */
  private static final String CURRENT_SONG_TABLE_NAME = "current_song";

  /** Constants for the column names in the current song table.
      Note that we're going to reuse all of the other constants for column
      names that were used in the playlist table as well.  */
  public static final String TIME_PLAYED_COLUMN = "time_played";

  /** SQL statement for creating the current song table */
  private static final String CURRENT_SONG_TABLE_CREATE = 
    "CREATE TABLE " + CURRENT_SONG_TABLE_NAME + "("+
		PLAYLIST_ID_COLUMN + " INTEGER PRIMARY KEY , " +
    UP_VOTES_COLUMN + " INTEGER NOT NULL, " +
    DOWN_VOTES_COLUMN + " INTEGER NOT NULL, " +
    TIME_ADDED_COLUMN + " TEXT NOT NULL, " +
    TIME_PLAYED_COLUMN + " TEXT NOT NULL, " +
    DURATION_COLUMN + " INTEGER NOT NULL, " +
		TITLE_COLUMN + " TEXT NOT NULL, " +
    ARTIST_COLUMN + " TEXT NOT NULL, " + 
    ALBUM_COLUMN + " TEXT NOT NULL, " +
    ADDER_ID_COLUMN + " INTEGER NOT NULL, " +
    ADDER_USERNAME_COLUMN + " STRING NOT NULL);";



	/** Helper for opening up the actual database. */
  private EventDBHelper dbOpenHelper;

	/**
	 * A class for helping open a PartDB.
	 */
  private class EventDBHelper extends SQLiteOpenHelper{

		/**
		 * Constructs a new EventDBHelper object.
		 *
	 	 * @param context The context in which the HostsDBOpenHelper is used.
	 	 */
    EventDBHelper(Context context){
      super(context, DATABASE_NAME, null, DATABASE_VERSION);
    }

    @Override
    public void onCreate(SQLiteDatabase db){
      db.execSQL(PLAYLIST_TABLE_CREATE);
      db.execSQL(ADD_REQUEST_TABLE_CREATE);
      db.execSQL(VOTES_TABLE_CREATE);
      db.execSQL(PLAYLIST_VIEW_CREATE);
      db.execSQL(CURRENT_SONG_TABLE_CREATE);
    }

    @Override
    public void onUpgrade(SQLiteDatabase db, int oldVersion, int newVersion){

    }
  }

  @Override
  public boolean onCreate(){
    dbOpenHelper = new EventDBHelper(getContext());
    return true;
  }

  @Override
  public String getType(Uri uri){
    return "none";
  }

  @Override
  public int delete(Uri uri, String where, String[] whereArgs){
    if(uri.equals(PLAYLIST_URI)){
      SQLiteDatabase db = dbOpenHelper.getWritableDatabase();
      return db.delete(PLAYLIST_TABLE_NAME, where, whereArgs);
    }
    else if(uri.equals(PLAYLIST_ADD_REQUEST_URI)){
      SQLiteDatabase db = dbOpenHelper.getWritableDatabase();
      return db.delete(ADD_REQUESTS_TABLE_NAME, where, whereArgs);
    } 
    else if(uri.equals(VOTES_URI)){
      SQLiteDatabase db = dbOpenHelper.getWritableDatabase();
      return db.delete(VOTES_TABLE_NAME, where, whereArgs);
    }
    else if(uri.equals(CURRENT_SONG_URI)){
      SQLiteDatabase db = dbOpenHelper.getWritableDatabase();
      return db.delete(CURRENT_SONG_TABLE_NAME, where, whereArgs);
    }
    throw new IllegalArgumentException("Unknown URI " + uri);
  }

  @Override
  public Uri insert(Uri uri, ContentValues initialValues){
    Uri toReturn = null;
    if(uri.equals(PLAYLIST_URI)){
      SQLiteDatabase db = dbOpenHelper.getWritableDatabase();
      long rowId = db.insert(PLAYLIST_TABLE_NAME, null, initialValues);    
      if(rowId >=0){
        toReturn = Uri.withAppendedPath(
          PLAYLIST_URI, String.valueOf(rowId));
      }
    }
    else if(uri.equals(PLAYLIST_ADD_REQUEST_URI)){
      SQLiteDatabase db = dbOpenHelper.getWritableDatabase();
      long rowId = db.insert(ADD_REQUESTS_TABLE_NAME, null, initialValues);    
      if(rowId >=0){
        toReturn = Uri.withAppendedPath(
          PLAYLIST_ADD_REQUEST_URI, String.valueOf(rowId));
      }
    }
    else if(uri.equals(VOTES_URI)){
      SQLiteDatabase db = dbOpenHelper.getWritableDatabase();
      long rowId = db.insert(VOTES_TABLE_NAME, null, initialValues);    
      if(rowId >=0){
        toReturn = Uri.withAppendedPath(
          VOTES_URI, String.valueOf(rowId));
      }
    }
    else if(uri.equals(CURRENT_SONG_URI)){
      SQLiteDatabase db = dbOpenHelper.getWritableDatabase();
      long rowId = db.insert(CURRENT_SONG_TABLE_NAME, null, initialValues);    
      if(rowId >=0){
        toReturn = CURRENT_SONG_URI;
      }
    }
    else{
      throw new IllegalArgumentException("Unknown URI " + uri);
    }
    return toReturn;
  }
  
  @Override
  public Cursor query(Uri uri, String[] projection, 
    String selection, String[] selectionArgs, String sortOrder)
  {
    SQLiteQueryBuilder qb = new SQLiteQueryBuilder();
    if(uri.equals(PLAYLIST_URI)){
      qb.setTables(PLAYLIST_VIEW_NAME);
    }
    else if(uri.equals(PLAYLIST_ADD_REQUEST_URI)){
      qb.setTables(ADD_REQUESTS_TABLE_NAME);
    }
    else if(uri.equals(CURRENT_SONG_URI)){
      qb.setTables(CURRENT_SONG_TABLE_NAME);
    }
    else if(uri.equals(VOTES_URI)){
      qb.setTables(VOTES_TABLE_NAME);
    }
    else{
      throw new IllegalArgumentException("Unknown URI " + uri);
    }

    SQLiteDatabase db = dbOpenHelper.getReadableDatabase();
    Cursor toReturn = qb.query(
      db, projection, selection, selectionArgs, null,
      null, sortOrder);

    toReturn.setNotificationUri(getContext().getContentResolver(), uri);
    return toReturn;
  }

  @Override
  public int update(Uri uri, ContentValues values, String where, 
    String[] whereArgs)
  {
    if(uri.equals(PLAYLIST_URI)){
      SQLiteDatabase db = dbOpenHelper.getWritableDatabase();
      int numRowsChanged = 
        db.update(PLAYLIST_TABLE_NAME, values, where, whereArgs);
      return numRowsChanged;
    }
    else if(uri.equals(PLAYLIST_ADD_REQUEST_URI)){
      SQLiteDatabase db = dbOpenHelper.getWritableDatabase();
      int numRowsChanged = 
        db.update(ADD_REQUESTS_TABLE_NAME, values, where, whereArgs);
      return numRowsChanged;
    } 
    else if(uri.equals(VOTES_URI)){
      SQLiteDatabase db = dbOpenHelper.getWritableDatabase();
      int numRowsChanged = 
        db.update(VOTES_TABLE_NAME, values, where, whereArgs);
      return numRowsChanged;
    } 
    throw new IllegalArgumentException("Unknown URI " + uri);
     //TODO implement this
  }

  public static void eventCleanup(ContentResolver cr){
    cr.delete(PLAYLIST_ADD_REQUEST_URI, null, null);
    cr.delete(PLAYLIST_URI, null, null);
    cr.delete(VOTES_URI, null, null);
    cr.delete(CURRENT_SONG_URI, null, null);
  }

  public static void setPreviousAddRequests(
    ContentResolver cr, 
    HashMap<Long, Long> previousRequests)
  {
    try{
      ArrayList<ContentProviderOperation> batchOps = 
        new ArrayList<ContentProviderOperation>();
      for(Long requestId: previousRequests.keySet()){
        batchOps.add(
          getAddRequestInsertOp(requestId, previousRequests.get(requestId)));
        if(batchOps.size() >= 50){
          cr.applyBatch(Constants.AUTHORITY, batchOps);
          batchOps.clear();
        }
      }
      if(batchOps.size() > 0){
        cr.applyBatch(Constants.AUTHORITY, batchOps);
        batchOps.clear();
      }
    }
    catch(RemoteException e){

    }
    catch(OperationApplicationException e){
    
    }
  }

  private static ContentProviderOperation getAddRequestInsertOp(
    long requestId, long libId)
  {
    final ContentProviderOperation.Builder insertOp = 
      ContentProviderOperation.newInsert(
        UDJEventProvider.PLAYLIST_ADD_REQUEST_URI)
      .withValue(UDJEventProvider.ADD_REQUEST_ID_COLUMN, requestId)
      .withValue(UDJEventProvider.ADD_REQUEST_LIB_ID_COLUMN, libId)
      .withValue(UDJEventProvider.ADD_REQUEST_SYNC_STATUS_COLUMN, 
        UDJEventProvider.ADD_REQUEST_SYNCED);
    return insertOp.build();

  }

  public static void setPreviousVoteRequests(
    ContentResolver cr, 
    JSONObject votes)
    throws JSONException
  {
    ArrayList<ContentProviderOperation> batchOps = 
      new ArrayList<ContentProviderOperation>();
    JSONArray upVotes = votes.getJSONArray("up_vote_ids");
    JSONArray downVotes = votes.getJSONArray("down_vote_ids");
    try{
      for(int i=0; i<upVotes.length(); i++){
        batchOps.add(getVoteRequestInsertOp(upVotes.getLong(i), UP_VOTE_TYPE)); 
        if(batchOps.size() > 0){
          cr.applyBatch(Constants.AUTHORITY, batchOps);
          batchOps.clear();
        }
      }
      for(int i=0; i<downVotes.length(); i++){
        batchOps.add(
          getVoteRequestInsertOp(downVotes.getLong(i), DOWN_VOTE_TYPE)); 
        if(batchOps.size() > 0){
          cr.applyBatch(Constants.AUTHORITY, batchOps);
          batchOps.clear();
        }
      }
      if(batchOps.size() > 0){
        cr.applyBatch(Constants.AUTHORITY, batchOps);
        batchOps.clear();
      }
    }
    catch(RemoteException e){

    }
    catch(OperationApplicationException e){
    
    }
  }

  private static ContentProviderOperation getVoteRequestInsertOp(
    long playlistId, int voteType)
  {
    final ContentProviderOperation.Builder insertOp = 
      ContentProviderOperation.newInsert(VOTES_URI)
      .withValue(VOTE_PLAYLIST_ENTRY_ID_COLUMN, playlistId)
      .withValue(VOTE_TYPE_COLUMN, voteType)
      .withValue(VOTE_SYNC_STATUS_COLUMN, VOTE_SYNCED);
    return insertOp.build();
  }
}
