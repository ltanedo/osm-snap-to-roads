const config = require('./constants.js');
const apiKey = config.APIKEY;
// console.log(apiKey);

const jsdom = require("jsdom");
const { JSDOM } = jsdom;
const { window } = new JSDOM(`<!DOCTYPE html>`);
const $ = require('jquery')(window);

var fs = require('fs');
var opn = require('opn');
var http = require('http');
var express = require('express');
var app = express();
var bodyParser = require('body-parser');
var geodist = require('geodist');
var find = require('find');
var googleMapsClient = require('@google/maps').createClient({
    key: apiKey
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

function drawSnapRoad(latlngArray, timeStamps, outputFilename) {
    distance = 0;  // reset the distance for each trip
    var counter = 0;
    var tempLatLng = [];
    var count = 0;

    // delete the content of outputFile if it already exists
    if (fs.existsSync(outputFilename)) {
        fs.unlinkSync(outputFilename);
    }

    for (var i = 0; i < latlngArray.length; i++) {
        counter++;
        if (counter === 90 || i === latlngArray.length - 1) {
            tempLatLng.push(latlngArray[i]);
            tempTimeStamps.push(timeStamps[i]);
            counter = 0;
            runSnapToRoad(tempLatLng, outputFilename);
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

function snapRoad(response, outputFilename) {

    var data = response.json.snappedPoints;
    // console.log(data)
    var distanceArray = [];
    for (var i = 0; i < data.length; i++) {
        var tempdist = [];
        var originalI = parseInt(JSON.stringify(data[i].originalIndex));
        var time = tempTimeStamps[originalI];
        tempdist.push(JSON.stringify(data[i].location.latitude) + ',' + JSON.stringify(data[i].location.longitude));
        distanceArray.push(tempdist);

        var tempString = time + ',' + JSON.stringify(data[i].location.latitude) + ',' + JSON.stringify(data[i].location.longitude);
        // console.log(tempString)

        fs.appendFileSync(outputFilename, tempString + "\n");
    }
    distance = distance + geodist(distanceArray.join(','));
    fs.writeFileSync('distance.txt', distance + " meters", function (err) {
        if (err) throw err;
    });
}

function runSnapToRoad(p, outputFilename) {
    // console.log(p);
    googleMapsClient.snapToRoads({
        interpolate: false,
        path: p.join('|')
    }, function (err, response) {
        // console.log(err)
        if (!err) {
            snapRoad(response, outputFilename);
        }
    });
}

//parse the input txt file
function processFile(filename, outputFilename) {
    var lines = fs.readFileSync(filename).toString().split('\n');
    var networkCount = 0;
    for (var line = 1; line < lines.length - 1; line++) {
        var _content = $.trim(lines[line].replace(/"/g, ''));
        var parsedString = _content.split(',');

        if (parsedString[parsedString.length - 1].toLowerCase() === "network") {
            networkCount++;
            continue;
        }
        var time = parsedString[0];
        timeStamps.push(time);
        var lat = parsedString[2];
        var long = parsedString[3];

        var latlng = lat + ',' + long;
        latlngArray.push(latlng);
    }
    drawSnapRoad(latlngArray, timeStamps, outputFilename);
    console.log('network lines #: ' + networkCount);
}

function invokeMap(fileDir) {
    inputfile = fs.readFileSync(fileDir);

    app.get('/', function (request, response) {
        response.sendfile('map2.html');
    });
    app.listen(8080);

    opn('http://localhost:8080');
}


find.file(/gps.*(?<!snap)(\.txt$)/, input, function (files) {  // match all files: starts with gps, and end with .txt
    console.log("number of gps files: " + files.length);
    // https://blog.lavrton.com/javascript-loops-how-to-handle-async-await-6252dd3c795
    // deal with each file syncronized
    files.forEach(absGPSFilename => {
        filePaths = absGPSFilename.split('/');
        folder = filePaths.slice(0, filePaths.length - 1);
        filename = filePaths[filePaths.length - 1];
        outputFilename = filename.split('.')[0] + '_snap.txt';
        output = folder + '/' + outputFilename;

        processFile(absGPSFilename, output);
        // invokeMap(files[inputs]);
    });
});
//fs.unlinkSync(output); //clear and delete the output txt file | can comment this line out if you want the txt file append
