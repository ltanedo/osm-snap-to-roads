import {APIKEY} from "./constants.js"

var fs = require('fs');
var opn = require('opn');
var http = require('http');
var express = require('express');
var app = express();
var geodist = require('geodist');
var find = require('find');
var googleMapsClient = require('@google/maps').createClient({
    key: APIKEY
});
if (process.argv.length !== 4) {
    console.error('format: node cli.js input.txt output.txt');
    process.exit(1);
}

var input = process.argv[2];
var output = process.argv[3];
var timeStamps = [];  //collection of time stamps
var latlngArray = [];  //collection of lat and lng from the txt
var tempTimeStamps = [];
var distance = 0;

function drawSnapRoad(latlngArray, timeStamps) {
    var counter = 0;
    var tempLatLng = [];
    var count = 0;
    for (var i = 0; i < latlngArray.length; i++) {
        counter++;
        if (counter == 90 || i == latlngArray.length - 1) {
            tempLatLng.push(latlngArray[i]);
            tempTimeStamps.push(timeStamps[i]);
            counter = 0;
            runSnapToRoad(tempLatLng);
            count = count + tempLatLng.length;

            tempLatLng = [];
            timeStamps = [];
        }
        else {
            tempLatLng.push(latlngArray[i]);
            tempTimeStamps.push(timeStamps[i]);
        }
    }
}

function snapRoad(response) {
    var data = response.json.snappedPoints;
    var distanceArray = [];
    for (var i = 0; i < data.length; i++) {
        var tempdist = [];
        var originalI = parseInt(JSON.stringify(data[i].originalIndex));
        var time = tempTimeStamps[originalI];
        tempdist.push(JSON.stringify(data[i].location.latitude) + ',' + JSON.stringify(data[i].location.longitude));
        distanceArray.push(tempdist);

        var tempString = time + ',' + JSON.stringify(data[i].location.latitude) + ',' + JSON.stringify(data[i].location.longitude);

        fs.appendFileSync(output, tempString + "\n");
    }
    distance = distance + geodist(distanceArray.join(','));
    fs.writeFileSync('distance.txt', distance + " meters", function (err) {
        if (err) throw err;
    });
}

function runSnapToRoad(p) {
    googleMapsClient.snapToRoads({
        interpolate: false,
        path: p.join('|')
    }, function (err, response) {
        if (!err) {
            snapRoad(response);
        }
    });
}

//parse the input txt file
function processFile(fileDir) {
    var lines = fs.readFileSync(fileDir).toString().split('\n');
    for (var line = 1; line < lines.length - 1; line++) {

        var parsedString = lines[line].replace(/"/g, '').split(',');

        var time = parsedString[0];
        timeStamps.push(time);
        var lat = parsedString[2];
        var long = parsedString[3]

        var latlng = lat + ',' + long;
        latlngArray.push(latlng);
    }
    drawSnapRoad(latlngArray, timeStamps);
}

function invokeMap(fileDir) {
    const PORT = 8080;

    fs.readFile('map2.html', function (err, html) {

        if (err) throw err;

        http.createServer(function (request, response) {
            response.writeHeader(200, { "Content-Type": "text/html" });
            response.write(html);

            response.end();
        }).listen(PORT);
    });
    opn('http://localhost:8080');
}

find.file(/\gps1.txt$/, input, function (files) {
    for (var inputs = 0; inputs < files.length; inputs++) {
        processFile(files[inputs]);
        invokeMap(files[inputs]);
    }
});
//fs.unlinkSync(output); //clear and delete the output txt file | can comment this line out if you want the txt file append
