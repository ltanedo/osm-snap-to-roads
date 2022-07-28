import subprocess


'''
BUILD MAP CACHE COMMANDS
'''


#5 java -jar matching-web/target/graphhopper-map-matching-web-0.12-SNAPSHOT.jar import map-data/new-york-latest.osm.pbf>
subprocess.run(["java", "-jar", "matching-web/target/graphhopper-map-matching-web-0.12-SNAPSHOT.jar", "import" ,"map-data/new-york-latest.osm.pbf"])

