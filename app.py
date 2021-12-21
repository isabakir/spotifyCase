from flask import Flask, render_template, request, url_for, redirect
# spotify http request
import requests
# base64 encode| decode
import base64
# path file
import os
# json parse
import json
# random number
import random
app = Flask(__name__)
# cliend_id =724bc87437c142589a1d03ae78082105
# url=https://accounts.spotify.com/en/authorize?
# secret=b411b254f8c44afeb4a4dbc25195ef16
# url=https://api.spotify.com/v1
# BQB_79qjo-Nz2g57qQ1nE01APS3oAqPE7grOGHAYcSO6vNqr27IUey7T3DoXYWVFn3Toc449o5JCTvAvjbc


def readGenres():
    filename = os.path.join(app.static_folder, 'genres.json')
    with open(filename) as genresFile:
        data = json.load(genresFile)
        return data


def authorize():
    # user secret
    client_id = "724bc87437c142589a1d03ae78082105"
    secret = "b411b254f8c44afeb4a4dbc25195ef16"

    # base64
    newSecret = client_id+":"+secret
    baseCode = base64.b64encode(bytes(newSecret, "utf-8"))
    decodeString = baseCode.decode("ascii")

    # post header
    headers = {}
    headers['Authorization'] = "Basic "+decodeString

    # post  data
    params = {}
    params['grant_type'] = "client_credentials"
    params['json'] = "true"

    datas = requests.post("https://accounts.spotify.com/api/token",
                          data=params, headers=headers)
    response = datas.json()

    token = response['access_token']

    return token


def search(token, query, queryType='artist', limit=50):

    uri = "https://api.spotify.com/v1/search"
    # reqest  args
    params = {}
    params["q"] = query
    params["type"] = queryType
    params["limit"] = limit

    # reqest header
    headers = {}
    headers["Authorization"] = "Bearer "+token+""

    res = requests.get(uri, params=params, headers=headers)

    response = res.json()

    return response
    # api req func


def getTracksList(token, artistId):

    # /v1/artists/id/top-tracks
    uri = "https://api.spotify.com/v1/artists/"+artistId+"/top-tracks"
    # req args
    params = {}
    params["country"] = "TR"

    # req header
    headers = {}
    headers["Authorization"] = "Bearer "+token+""

    res = requests.get(uri, params=params, headers=headers)

    response = res.json()
    # print(response)
    return response


def parseTrackListResponse(trackList):
    returnList = []
    for tracks in trackList['tracks']:

        data = {
            "name": tracks['artists'][0]['name'],
            "track": tracks["name"],
            "preview_url": tracks["preview_url"],
            "album_image": tracks["album"]['images'][0]['url']
        }
        returnList.append(data)
    return returnList


@app.route("/", methods=["GET"])
def main():

    print(request.args.get('genre'))
    if(request.args.get('genre')):
        return redirect(url_for("tracks", genre=request.args.get('genre')))
    else:
        if(request.args.get('error')):
            error = request.args.get('error')
            return render_template("index.html", error=error)
        else:
            return render_template("index.html")


@app.route("/tracks/<string:genre>")
def tracks(genre):
    staticData = readGenres()

    if genre in staticData:

        token = authorize()
        if token:
            api_res = search(token, staticData[genre][random.randint(
                0, len(staticData[genre]))], "artist", 10)
            artistId = api_res['artists']['items'][0]['id']
            trackList = getTracksList(token, artistId)
            data = parseTrackListResponse(trackList)
            print(data)
            return json.dumps(data)

    else:
        data = {"status": "success", "error": "Invalid genre. Please try again."}

        return json.dumps(data)
    return genre
