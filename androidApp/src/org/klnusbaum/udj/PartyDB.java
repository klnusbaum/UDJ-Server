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


import android.database.sqlite.SQLiteDatabase;
import android.database.sqlite.SQLiteOpenHelper;
import android.content.Context;
import android.database.Cursor;
import android.content.ContentValues;
import android.util.Log;

import java.util.ArrayList;

/**
 * Class used for storing host information
 */
class HostsDB{
	/** Tag used for logging purposes. */
  private static final String TAG = "PartyDB";

	/** Name of the database */
  private static final String DATABASE_NAME = "partydb.db";
	/** Database version number */
  private static final int DATABASE_VERSION = 1;
	/** Name of the library table. */
  private static final String LIBRARY_TABLE_NAME = "library";
	/** Name of the playlist table. */
  private static final String PLAYLIST_TABLE_NAME = "playlist";
  /** Name of the partiers table. */
  private static final String PARTIERS_TABLE_NAME = "partiers";

  /** The various states a playlist record can be in */
  private static final String SYNCED_MARK="synced";
  private static final String UPDATEING_MARK ="updating"; 
  private static final String NEEDS_UPDATE_MARK ="needs update"; 
  
	/** Constants used for various column names */
  private static final String SONG_COLUMN = "song";
  private static final String ARTIST_COLUMN = "artist";
  private static final String ALBUM_COLUMN = "album";
  private static final String VOTES_COLUMN = "votes";
  private static final String PLAYLIST_ID_COLUMN = "pid";
  private static final String LIBRARY_ID_COLUMN = "lid";
  private static final String SYNC_STATE_COLUMN = "sync_state";


	/** SQL statement for creating the library table. */
  private static final String LIBRARY_TABLE_CREATE = 
    "CREATE TABLE " + LIBRARY_TABLE_NAME + "("+
		LIBRARY_ID_COLUMN + " INTEGER PRIMARY KEY, " +
		SONG_COLUMN + " TEXT NOT NULL, " +
    ARTIST_COLUMN + " TEXT NOT NULL, " + 
    ALBUM_COLUMN + " TEXT NOT NULL " + ");";

	/** SQL statement for creating the playlist table. */
  private static final String PLAYLIST_TABLE_CREATE = 
    "CREATE TABLE " + PLAYLIST_TABLE_NAME + "("+
		PLAYLIST_ID_COLUMN + " INTEGER PRIMARY KEY, " +
    VOTES_COLUMN + " INTEGER NOT NULL, " +
		SONG_COLUMN + " TEXT NOT NULL, " +
    ARTIST_COLUMN + " TEXT NOT NULL, " + 
    ALBUM_COLUMN + " TEXT NOT NULL, " +
    SYNC_STATE_COLUMN + " TEXT NOT NULL DEFAULT " + SYNCED_MARK + ");";


  /** Query for getting the playlist */
  private static final String PLAYLIST_QUERY = 
    "SELECT " + SONG_COLUMN + "," + ARTIST_COLUMN +
    "," + VOTES_COLUMN + " FROM " +PLAYLIST_TABLE_NAME;

  private static final String LIBRARY_QUERY = 
    "SELECT " + SONG_COLUMN + "," + ARTIST_COLUMN +
    " FROM " +LIBRARY_TABLE_NAME;

	/** Helper for opening up the actual database. */
  private final PartyDBHelper dbOpenHelper;

	/** A writable database instance. */
  private SQLiteDatabase writableDB;
	/** A readable database instance. */
  private SQLiteDatabase readableDB;

	/**
	 * Constructor for creating a HostsDB object.
   *
	 * @param context Context in which the database is being used.
	 */
  public HostsDB(Context context){
    dbOpenHelper = new PartyDBHelper(context);
    writableDB = dbOpenHelper.getWritableDatabase();
    readableDB = dbOpenHelper.getReadableDatabase();
  }

	/** Close the database. */
	public void close(){
		writableDB.close();
		readableDB.close();
	}

	public Cursor getPlaylist(){
		return readableDB.rawQuery(PLAYLIST_QUERY, null);
	}

	public Cursor getLibrary(){
		return readableDB.rawQuery(LIBRARY_QUERY, null);
	}

	/**
	 * A class for helping open a HostsDB.
	 */
  private class PartyDBHelper extends SQLiteOpenHelper{

		/** Actual database that is opened. */
    private SQLiteDatabase partydb;
		/** Context in which the database is opened. */
    private final Context helperContext;

		/**
		 * Constructs a new HostsDBOpenHelper object.
		 *
	 	 * @param context The context in which the HostsDBOpenHelper is used.
	 	 */
    PartyDBHelper(Context context){
      super(context, DATABASE_NAME, null, DATABASE_VERSION);
      helperContext = context;
    }

    @Override
    public void onCreate(SQLiteDatabase db){
      partydb = db;
      partydb.execSQL(LIBRARY_TABLE_CREATE);
      partydb.execSQL(PLAYLIST_TABLE_CREATE);
    }

    @Override
    public void onUpgrade(SQLiteDatabase db, int oldVersion, int newVersion){

    }
  }
}
