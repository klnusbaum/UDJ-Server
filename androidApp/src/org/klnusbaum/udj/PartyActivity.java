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

import android.app.Activity;
import android.os.Bundle;
import android.content.Intent;
import android.widget.TabHost;
import android.view.View;
import android.content.Context;
import android.accounts.AccountManager;
import android.accounts.Account;
import android.content.DialogInterface;
import android.app.AlertDialog;
import android.app.Dialog;
import android.content.ContentResolver;

import android.support.v4.app.Fragment;
import android.support.v4.app.FragmentActivity;
import android.support.v4.app.FragmentTransaction;
import android.support.v4.app.DialogFragment;

import java.util.HashMap;

import org.klnusbaum.udj.auth.AuthActivity;
import org.klnusbaum.udj.containers.Party;
import org.klnusbaum.udj.sync.SyncAdapter;

/**
 * The main activity display class.
 */
public class PartyActivity extends FragmentActivity{
  
  private TabHost tabHost;
  private TabManager tabManager;
  private long partyId;
  private Account account;
  private String authtoken;

  private static final String TAB_EXTRA = "org.klnusbaum.udj.tab";
  public static final String ACCOUNT_EXTRA = "org.klnusbaum.udj.account";

  private static final String DIALOG_FRAG_TAG = "dialog";

  @Override
  protected void onCreate(Bundle savedInstanceState){
    super.onCreate(savedInstanceState);
    
    setContentView(R.layout.tablayout);
    if(savedInstanceState != null){
      tabHost.setCurrentTabByTag(savedInstanceState.getString(TAB_EXTRA));
      partyId = savedInstanceState.getLong(Party.PARTY_ID_EXTRA);
      account = (Account)savedInstanceState.getParcelable(ACCOUNT_EXTRA);
    }
    else{
      Intent intent = getIntent();
      partyId = 
        intent.getLongExtra(Party.PARTY_ID_EXTRA, Party.INVALID_PARTY_ID);
      if(partyId == Party.INVALID_PARTY_ID){
        setResult(Activity.RESULT_CANCELED);
        finish();
      }
      account = intent.getParcelableExtra(ACCOUNT_EXTRA);
    }
    tabHost = (TabHost)findViewById(android.R.id.tabhost);
    tabHost.setup();

    tabManager = new TabManager(this, tabHost, R.id.realtabcontent);
    
    Bundle partyBundle = new Bundle();
    partyBundle.putLong(Party.PARTY_ID_EXTRA, partyId);
    tabManager.addTab(tabHost.newTabSpec("playlist").setIndicator("Playlist"),
      PlaylistActivity.PlaylistFragment.class, partyBundle);
    tabManager.addTab(tabHost.newTabSpec("library").setIndicator("Library"),
      LibraryActivity.LibraryFragment.class, partyBundle);

    Bundle syncParams = new Bundle();
    syncParams.putLong(Party.PARTY_ID_EXTRA, partyId);
    syncParams.putBoolean(SyncAdapter.LIBRARY_SYNC_EXTRA, true);
    syncParams.putBoolean(SyncAdapter.PLAYLIST_SYNC_EXTRA, true);
    ContentResolver.requestSync(account, getString(R.string.authority), syncParams);
  }


  @Override
  protected void onSaveInstanceState(Bundle outState){
    super.onSaveInstanceState(outState);
    outState.putString(TAB_EXTRA, tabHost.getCurrentTabTag());
    outState.putLong(Party.PARTY_ID_EXTRA, partyId);
  }

  @Override 
  public void onBackPressed(){
    DialogFragment newFrag = new QuitDialogFragment();
    newFrag.show(getSupportFragmentManager(), DIALOG_FRAG_TAG);
  }

  private void doQuit(){
    dismissQuitDialog();
    setResult(Activity.RESULT_OK);
    finish();
  }

  private void dismissQuitDialog(){
    QuitDialogFragment qd = 
      (QuitDialogFragment)getSupportFragmentManager().findFragmentByTag(DIALOG_FRAG_TAG);
    qd.dismiss();
  }

  public static class QuitDialogFragment extends DialogFragment{
    
    @Override
    public Dialog onCreateDialog(Bundle savedInstanceState){
      return new AlertDialog.Builder(getActivity())
        .setTitle(R.string.quit_title)
        .setMessage(R.string.quit_message)
        .setPositiveButton(android.R.string.ok,
          new DialogInterface.OnClickListener(){
            public void onClick(DialogInterface dialog, int whichButton){
              ((PartyActivity)getActivity()).doQuit();
            }
          })
        .setNegativeButton(android.R.string.cancel,
          new DialogInterface.OnClickListener(){
            public void onClick(DialogInterface dialog, int whichButton){
              ((PartyActivity)getActivity()).dismissQuitDialog();
            }
          })
        .create();
    }
  }


  /** The following is taken from the android Support Demos */

    /**
     * This is a helper class that implements a generic mechanism for
     * associating fragments with the tabs in a tab host.  It relies on a
     * trick.  Normally a tab host has a simple API for supplying a View or
     * Intent that each tab will show.  This is not sufficient for switching
     * between fragments.  So instead we make the content part of the tab host
     * 0dp high (it is not shown) and the TabManager supplies its own dummy
     * view to show as the tab content.  It listens to changes in tabs, and takes
     * care of switch to the correct fragment shown in a separate content area
     * whenever the selected tab changes.
     */
    public static class TabManager implements TabHost.OnTabChangeListener {
        private final FragmentActivity mActivity;
        private final TabHost mTabHost;
        private final int mContainerId;
        private final HashMap<String, TabInfo> mTabs = new HashMap<String, TabInfo>();
        TabInfo mLastTab;

        static final class TabInfo {
            private final String tag;
            private final Class<?> clss;
            private final Bundle args;
            private Fragment fragment;

            TabInfo(String _tag, Class<?> _class, Bundle _args) {
                tag = _tag;
                clss = _class;
                args = _args;
            }
        }

        static class DummyTabFactory implements TabHost.TabContentFactory {
            private final Context mContext;

            public DummyTabFactory(Context context) {
                mContext = context;
            }

            @Override
            public View createTabContent(String tag) {
                View v = new View(mContext);
                v.setMinimumWidth(0);
                v.setMinimumHeight(0);
                return v;
            }
        }

        public TabManager(FragmentActivity activity, TabHost tabHost, int containerId) {
            mActivity = activity;
            mTabHost = tabHost;
            mContainerId = containerId;
            mTabHost.setOnTabChangedListener(this);
        }

        public void addTab(TabHost.TabSpec tabSpec, Class<?> clss, Bundle args) {
            tabSpec.setContent(new DummyTabFactory(mActivity));
            String tag = tabSpec.getTag();

            TabInfo info = new TabInfo(tag, clss, args);

            // Check to see if we already have a fragment for this tab, probably
            // from a previously saved state.  If so, deactivate it, because our
            // initial state is that a tab isn't shown.
            info.fragment = mActivity.getSupportFragmentManager().findFragmentByTag(tag);
            if (info.fragment != null && !info.fragment.isDetached()) {
                FragmentTransaction ft = mActivity.getSupportFragmentManager().beginTransaction();
                ft.detach(info.fragment);
                ft.commit();
            }

            mTabs.put(tag, info);
            mTabHost.addTab(tabSpec);
        }

        @Override
        public void onTabChanged(String tabId) {
            TabInfo newTab = mTabs.get(tabId);
            if (mLastTab != newTab) {
                FragmentTransaction ft = mActivity.getSupportFragmentManager().beginTransaction();
                if (mLastTab != null) {
                    if (mLastTab.fragment != null) {
                        ft.detach(mLastTab.fragment);
                    }
                }
                if (newTab != null) {
                    if (newTab.fragment == null) {
                        newTab.fragment = Fragment.instantiate(mActivity,
                                newTab.clss.getName(), newTab.args);
                        ft.add(mContainerId, newTab.fragment, newTab.tag);
                    } else {
                        ft.attach(newTab.fragment);
                    }
                }

                mLastTab = newTab;
                ft.commit();
                mActivity.getSupportFragmentManager().executePendingTransactions();
            }
        }
    }
}

