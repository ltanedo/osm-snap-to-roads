import subprocess
import os

def main():
    list_gpx_files = []
    list_txt_files = []

    path = os.getcwd() + '/data'

    for r, d, f in os.walk(path):
        for file in f:
            if '.gpx' in file:
                list_gpx_files.append(os.path.join(r, file))

    for r, d, f in os.walk(path):
        for file in f:
            if '.txt' in file:
                list_txt_files.append(os.path.join(r, file))

    run(list_gpx_files)

def run(list_gpx_files):

	for gpx_file in list_gpx_files:
		if '.res.gpx' not in gpx_file:
			subprocess.run(["java", "-jar", "matching-web/target/graphhopper-map-matching-web-0.12-SNAPSHOT.jar", "match", gpx_file])
			

if __name__ == '__main__':
    main()