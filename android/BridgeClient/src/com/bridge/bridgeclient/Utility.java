//probably several good reasons why I shouldn't do this, but retriving
//urls is so tedious in java
package com.bridge.bridgeclient;

import org.apache.http.HttpEntity;
import org.apache.http.HttpResponse;
import org.apache.http.StatusLine;
import org.apache.http.client.ClientProtocolException;
import org.apache.http.client.HttpClient;
import org.apache.http.client.methods.HttpGet;
import org.apache.http.client.methods.HttpPost;
import org.apache.http.impl.client.DefaultHttpClient;

import java.io.BufferedReader;
import java.io.IOException;
import java.io.InputStream;
import java.io.InputStreamReader;

class Utility
{
    private static HttpClient client = new DefaultHttpClient();

    public static String getURL(String url) throws ClientProtocolException, IOException
    {
        StringBuilder builder = new StringBuilder();
        HttpGet get = new HttpGet(url);

        HttpResponse response = client.execute(get);
        StatusLine status = response.getStatusLine();
        HttpEntity entity = response.getEntity();
        InputStream content = entity.getContent();
        BufferedReader reader = new BufferedReader(new InputStreamReader(content));

        String line;
        while ((line = reader.readLine()) != null)
        {
            builder.append(line);
        }

        return builder.toString();
    }

    public static void postURL(String url) throws IOException
    {
        HttpPost post = new HttpPost(url);
        HttpResponse response = client.execute(post);
    }
}
