package com.bridge.bridgeclient;

import android.content.Context;

import android.view.View;
import android.view.ViewGroup;
import android.widget.BaseExpandableListAdapter;
import android.widget.TextView;
import android.widget.Toast;

import org.json.JSONObject;
import org.json.JSONArray;
import org.json.JSONException;
import java.io.IOException;
import org.apache.http.client.ClientProtocolException;

class AssetExpandableListAdapter extends BaseExpandableListAdapter
{
    private Context context;

    private AssetList assets;

    public AssetExpandableListAdapter(Context context) {
        super();
        this.context = context;
        this.assets = new AssetList("http://192.168.0.198:8080");
    }


    public boolean isChildSelectable(int groupPosition, int childPosition)
    {
        return true;
    }

    public Object getChild (int groupPosition, int childPosition)
    {
        return assets.get(groupPosition);
    }

    public long getChildId(int groupPosition, int childPosition)
    {
        return 0;
    }

    public View getChildView(int groupPosition, int childPosition, boolean isLastChild, View convertView, ViewGroup parent)
    {
        return new AssetView(context, assets.get(groupPosition));
    }

    public int getChildrenCount(int groupPosition)
    {
        return 1;
    }

    public long getGroupId(int groupPosition)
    {
        return groupPosition;
    }

    public Object getGroup(int groupPosition)
    {
        return assets.get(groupPosition).getName();
    }

    public View getGroupView(int groupPosition, boolean isExpanded, View convertView, ViewGroup parent)
    {
        TextView view = new TextView(context);
        view.setText((String) getGroup(groupPosition));

        return view;
    }

    public int getGroupCount()
    {
        return assets.length() ;
    }

    public boolean hasStableIds()
    {
        return false;
    }

    public void refresh()
    {
        try {

            assets.refresh();
        }
            catch (JSONException e)
        {
            Toast.makeText(context, e.getMessage(), Toast.LENGTH_SHORT).show();
        } 
            catch (ClientProtocolException e)
        {
            Toast.makeText(context, e.getMessage(), Toast.LENGTH_SHORT).show();
        }
            catch (IOException e)
        {
            Toast.makeText(context, e.getMessage(), Toast.LENGTH_SHORT).show();
        }

        notifyDataSetChanged();
    }
}
