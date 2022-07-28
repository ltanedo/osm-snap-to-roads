# map-related
Implement Map Related stuff

## Content
1. **Map Matching**: Make [snap to roads](https://developers.google.com/maps/documentation/roads/snap) calls on files that contain gps data,  save the result to new files and show the result on Maps. Eventually, we want it to be able to accept a directory and deal with all `gps.txt` files within it and all its subfolders.
    * Pay attention to the restriction of calling the API
    * Keep async calls in mind
    * Assign correct timestamp for the snapped data
    * Assuming that the GPS file name is `gps.txt`, the file that contains the result returned from the api should be named to `gps_snapped.txt`, and be put in the same folder as the `gps` file.
    * How to use other methods instead of Google Maps for map Matching due to the call limitation of the Google Maps API? Not limited to JavaScript or Python, e.g. [map matching based on GraphHopper](https://github.com/graphhopper/map-matching).

1. **GPS Processing**: Remove outliers from the `gps_snapped.txt` file, interpolate data and save the result to `gps_filtered.txt`.
    * How to detect outliers?
    * How to interpolate?

## How to run:
1. Install dependencies
    ```
    npm install
    ```
1. Snap to road (**to be updated**)
    ```node.js
    node cli.js input_folder output.txt
    ```
1. Visualize GPS trace in a browser:
    ```HTML
    plot.html
    ```
1. to be continued


## Do NOT push your Google api key to the remote repository.
[How to hide API keys from github](https://gist.github.com/derzorngottes/3b57edc1f996dddcab25)


&nbsp;
&nbsp;
&nbsp;
&nbsp;
&nbsp;
&nbsp;
&nbsp;
&nbsp;
&nbsp;


# Map Mathing Steps

Java 8 and Maven >=3.3 are required. For the 'core' module Java 7 is sufficient.

Note: Instructions to build graph cache from scratch at end of readme

0. #### [OPTIONAL] Steps 0 - 2 (CONDENSED)

```bash
/usr/bin/ruby -e "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/master/install)"
```

```bash
python3 setup_mac.py
```
**Optional**: Graph Cache for New York State already included in files
- new-york-latest.osm.pbf from [here](http://download.geofabrik.de/north-america/us/new-york-latest.osm.pbf).
- place osm file in "map-data" folder
```bash
python3 setup_map_cache.py
```

3. #### convert 'gps.txt' to 'gps.gpx' (in subfolders of /data):
- script will remove outliers
- output will remove ".txt" adding ".gpx" to file path
```bash
python3 pre_snap.py
```

4. #### Run the map matching (in subfolders of /data):
- command will run map matching
- output will add ".res.gpx" to gpx file
```bash
python3 snap.py
```

5. #### Add speed + convert .txt (in subfolders of /data):
- will convert ".res.gpx" extention back to "_matched.txt" (for use with plot_advanced.html)
- output will have "_matched.txt" added ("gps_matched.txt" necessary to aviod conflicts with original "gps.txt")
```bash
python3 post_snap.py
```

6. #### OPTIONAL - matched.txt to matched.gpx (in subfolders of /data):
- changes "_matched.txt" extention to "_matched.gpx" (does not affect original gps.txt)
```bash
python3 post_to_gpx.py
```

7. #### OPTIONAL - Remove all files except original "gps.txt" (in subfolders of /data):
```bash
python3 post_clean.py
```

# Web app

Start via:
```bash
java -jar matching-web/target/graphhopper-map-matching-web-0.12-SNAPSHOT.jar server config.yml
```

Access the simple UI via `localhost:8989`.

You can post GPX files and get back snapped results as GPX or as compatible GraphHopper JSON. An example curl request is:
```bash
curl -XPOST -H "Content-Type: application/gpx+xml" -d @matching-core/src/test/resources/test1.gpx "localhost:8989/match?vehicle=car&type=json"
```

See the demo in action (black is GPS track, green is matched result):

![map-matching-example](https://cloud.githubusercontent.com/assets/129644/14740686/188a181e-0891-11e6-820c-3bd0a975f8a5.png)


# Original Steps to Rebuild "graph-cache"

0. Step 0 - Install Bash and Maven (Mac):
	
```bash
/usr/bin/ruby -e "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/master/install)"
```
	
```bash
brew cask install adoptopenjdk
```

```bash
brew install maven
```

1. #### Step 1 - Build Maven Package:

```bash
mvn package -DskipTests
```

2. #### Step 2 - Import an OSM map for the desire area for map-matching:
- download OpenStreetMap data in pbf or xml format are available from [here](http://download.geofabrik.de/).
- new-york-latest.osm.pbf from [here](http://download.geofabrik.de/north-america/us/new-york-latest.osm.pbf).
- place osm file in "map-data" folder

```bash
java -jar matching-web/target/graphhopper-map-matching-web-0.12-SNAPSHOT.jar import map-data/new-york-latest.osm.pbf
```

- The optional parameter `--vehicle` defines the routing profile like `car`, `bike`, `motorcycle` or `foot`.
You can also provide a comma separated list. For all supported values see the variables in the [FlagEncoderFactory](https://github.com/graphhopper/graphhopper/blob/0.7/core/src/main/java/com/graphhopper/routing/util/FlagEncoderFactory.java) of GraphHopper. 

- Before re-importing, you need to delete the `graph-cache` directory, which is created by the import.


