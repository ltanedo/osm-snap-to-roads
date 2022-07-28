package com.graphhopper.matching.http;

import com.fasterxml.jackson.databind.JsonNode;
import com.graphhopper.matching.EdgeMatch;
import com.graphhopper.matching.GPXExtension;
import com.graphhopper.matching.MatchResult;
import com.graphhopper.routing.VirtualEdgeIteratorState;
import com.graphhopper.storage.IntsRef;
import com.graphhopper.storage.index.QueryResult;
import com.graphhopper.util.EdgeIteratorState;
import com.graphhopper.util.GPXEntry;
import com.graphhopper.util.PointList;
import com.graphhopper.util.shapes.GHPoint3D;
import org.junit.Test;

import java.util.ArrayList;
import java.util.List;

import static org.junit.Assert.assertEquals;

public class ExtendedJsonResponseTest {

    @Test
    public void shouldCreateBasicStructure() {
        JsonNode jsonObject = MapMatchingResource.convertToTree(new MatchResult(getEdgeMatch()), false, false);
        JsonNode route = jsonObject.get("diary").get("entries").get(0);
        JsonNode link = route.get("links").get(0);
        JsonNode geometry = link.get("geometry");
        assertEquals("geometry should have type", "LineString", geometry.get("type").asText());
        assertEquals("geometry should have coordinates", "LINESTRING (-38.999 -3.4445, -38.799 -3.555)", geometry.get("coordinates").asText());

        assertEquals("wpts[0].timestamp should exists", 100000l, link.get("wpts").get(0).get("timestamp").asLong());
        assertEquals("wpts[0].y should exists", "-3.4446", link.get("wpts").get(0).get("y").asText());
        assertEquals("wpts[0].x should exists", "-38.9996", link.get("wpts").get(0).get("x").asText());

        assertEquals("wpts[1].timestamp should exists", 100001l, link.get("wpts").get(1).get("timestamp").asLong());
        assertEquals("wpts[1].y should exists", "-3.4449", link.get("wpts").get(1).get("y").asText());
        assertEquals("wpts[1].x should exists", "-38.9999", link.get("wpts").get(1).get("x").asText());
    }

    private List<EdgeMatch> getEdgeMatch() {
        List<EdgeMatch> list = new ArrayList<>();
        list.add(new EdgeMatch(getEdgeIterator(), getGpxExtension()));
        return list;
    }

    private List<GPXExtension> getGpxExtension() {
        List<GPXExtension> list = new ArrayList<>();
        QueryResult queryResult1 = new QueryResult(-3.4445, -38.9990) {
            @Override
            public GHPoint3D getSnappedPoint() {
                return new GHPoint3D(-3.4446, -38.9996, 0);
            }
        };
        QueryResult queryResult2 = new QueryResult(-3.4445, -38.9990) {
            @Override
            public GHPoint3D getSnappedPoint() {
                return new GHPoint3D(-3.4449, -38.9999, 0);
            }
        };

        list.add(new GPXExtension(new GPXEntry(-3.4446, -38.9996, 100000), queryResult1));
        list.add(new GPXExtension(new GPXEntry(-3.4448, -38.9999, 100001), queryResult2));
        return list;
    }

    private EdgeIteratorState getEdgeIterator() {
        PointList pointList = new PointList();
        pointList.add(-3.4445, -38.9990);
        pointList.add(-3.5550, -38.7990);
        return new VirtualEdgeIteratorState(0, 0, 0, 1, 10,  new IntsRef(1), "test of iterator", pointList, false);
    }

}
