package com.bridge.bridgeclient;

import com.actionbarsherlock.app.SherlockFragment;

import android.os.Bundle;
import android.view.View;
import android.view.ViewGroup;
import android.view.LayoutInflater;
import android.widget.ExpandableListView;

import android.widget.Toast;

import java.net.URI;
import java.net.URISyntaxException;

public class AssetsFragment extends SherlockFragment
{
    String serverURL;
    AssetList assetList;

    public AssetsFragment()
    {
        super();
        this.serverURL = null;
        this.assetList = new AssetList();
    }

    @Override
    public void onCreate(Bundle savedInstanceState)
    {
        super.onCreate(savedInstanceState);
    }

    @Override
    public View onCreateView (LayoutInflater inflater, ViewGroup container, Bundle savedInstanceState)
    {
        View view = inflater.inflate(R.layout.assetsfragment, container);
        final ExpandableListView devices = (ExpandableListView) view.findViewById(R.id.expandassetlist);
        final AssetExpandableListAdapter deviceAdapter = new AssetExpandableListAdapter(getActivity(), assetList);
        devices.setAdapter(deviceAdapter);

        return view;
    }

    public void displayError(String message)
    {
    }
}
