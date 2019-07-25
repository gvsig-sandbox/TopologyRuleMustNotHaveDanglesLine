# encoding: utf-8

import gvsig
from gvsig import geom
from gvsig.geom import *
from java.lang import Throwable
from gvsig import commonsdialog
from gvsig.commonsdialog import *
import math
from org.gvsig.fmap.geom import GeometryLocator
from org.gvsig.fmap.geom import GeometryManager
from org.gvsig.fmap.geom import GeometryUtils
from org.gvsig.topology.lib.spi import AbstractTopologyRuleAction
import sys

from gvsig import logger
from gvsig import LOGGER_WARN,LOGGER_INFO,LOGGER_ERROR

#from addons.TopologyRuleMustHaveDanglesLine.mustNotHaveLineFactory import MustNotHaveDanglesLineRuleFactory
#from mustNotHaveDanglesLineFactory import MustNotHaveDanglesLineRuleFactory
from org.gvsig.topology.lib.api import ExecuteTopologyRuleActionException

#from mustNotHaveDanglesLineRuleFactory import MustNotHaveDanglesLineRuleFactory

class SnapAction(AbstractTopologyRuleAction):

  def __init__(self):
    AbstractTopologyRuleAction.__init__(
      self,
      "MustNotHaveDanglesLine", #MustNotHaveDanglesLineRuleFactory.NAME,
      "SnapAction",
      "Snap Action",
      ""#CAMBIAR
    )
  
  logger("1", LOGGER_INFO)
  def execute(self, rule, line, parameters):
    #TopologyRule rule, TopologyReportLine line, DynObject parameters
    try:
    
      #logger("2", LOGGER_INFO)
      dataSet = rule.getDataSet1()
      
      while True:
        try:
          d = float(commonsdialog.inputbox("Enter a distance", title = "", messageType = IDEA, initialValue = "", root = None))
          print "Dialog box: ", d
          if d == 0:
            print "entra en d=0"
            envelope = dataSet.getFeatureStore().getEnvelope()

            if envelope is not None or not envelope.isEmpty():
              print "entra en if del envelope"
              d = envelope.getLowerCorner().distance(envelope.getUpperCorner())
              print d
            else:
              print "entra al else del raise"
              raise Throwable("Not valid envelope")
          break
        except ValueError:
          print("The entered values are not correct. Try again")

      vertexError = geom.createGeometryFromWKT(line.getData())
      print vertexError
      
      reference = line.getFeature1()
      feature1 = reference.getFeature()
      lineToSnap = feature1.getDefaultGeometry()

      geoManager = GeometryLocator.getGeometryManager()
      subtype = lineToSnap.getGeometryType().getSubType()
      snappedLine = geoManager.createLine(subtype)

      numVertex = lineToSnap.getNumVertices()

      store = dataSet.getFeatureStore()
      features = store.getFeatureSet()

      distance = float('inf')
      for feature in features:
        otherLine = feature.getDefaultGeometry()
        print feature.Name

        if not vertexError.intersects(otherLine):
          dist = vertexError.distance(otherLine)

          if dist<distance:
            distance = dist
            geoNearest = otherLine
            print distance
            geoName = feature.Name

      print "nearest geometry ", geoName

      numVertexOtherLine = geoNearest.getNumVertices()
      print numVertexOtherLine
      
      disToSegment = float('inf')
      if GeometryUtils.isSubtype(geom.MULTICURVE, geoNearest.getGeomtryType()):
        for x in range(0, geoNearest.getNumPrimitives()):
          geox = geoNearest.getPrimitiveAt(x)
          numVertexMulti = geox.getNumVertices()
          for i in range(0, numVertexMulti-1):
            print "index ", i
            vertex1 = geox.getVertex(i)
            vertex2 = geox.getVertex(i+1)
            segment = geoManager.createLine(subtype)
            segment.addVertex(vertex1)
            segment.addVertex(vertex2)
            print segment.getNumVertices()
    
            dToSegment = vertexError.distance(segment)
    
            if dToSegment < disToSegment:
              disToSegment = dToSegment
              segmentNearest = segment
              numSegment = i + 1
              print disToSegment
      else:
        for i in range(0, numVertexOtherLine-1):
          print "index ", i
          vertex1 = geoNearest.getVertex(i)
          vertex2 = geoNearest.getVertex(i+1)
          segment = geoManager.createLine(subtype)
          segment.addVertex(vertex1)
          segment.addVertex(vertex2)
          print segment.getNumVertices()
  
          dToSegment = vertexError.distance(segment)
  
          if dToSegment < disToSegment:
            disToSegment = dToSegment
            segmentNearest = segment
            numSegment = i + 1
            print disToSegment

      print "Segment nearest is ", numSegment
      print "Distance nearest to segment is ", disToSegment

      dToVertex1 = vertexError.distance(segmentNearest.getVertex(0))
      print "dToVertex1 ", dToVertex1
      dToVertex2 = vertexError.distance(segmentNearest.getVertex(1))
      print "dToVertex2 ", dToVertex2

      if dToVertex1<d or dToVertex2<d:
        if dToVertex1<dToVertex2:
          vertex = segmentNearest.getVertex(0)
          print "vertex 1"
        elif dToVertex1>dToVertex2:
          vertex = segmentNearest.getVertex(1)
          print "vertex 2"
        elif dToVertex1 == dToVertex2:
          vertex = segmentNearest.getVertex(0)
          print "vertex 1"
      elif disToSegment < d:
        print "perpendicular"
        try:
          slope1 = (segmentNearest.getVertex(1).getY()-segmentNearest.getVertex(0).getY())/(segmentNearest.getVertex(1).getX()-segmentNearest.getVertex(0).getX())
        except ZeroDivisionError:
          slope1 = float('inf')
        b1 = segmentNearest.getVertex(0).getY() - slope1 * segmentNearest.getVertex(0).getX()
        print "straight line 1"
        print slope1, b1

        try:
          slope2 = -(1/slope1)
        except ZeroDivisionError:
          slope2 = float('-inf')
        b2 = vertexError.getY() - slope2 * vertexError.getX()

        print "straight line 2"
        print slope2, b2

        x = (b2-b1)/(slope1-slope2)
        if math.isnan(x):
          if slope1 == 0:
            x = vertexError.getX()
          elif slope1 == float('inf'):
            x = segmentNearest.getVertex(0).getX()
        print "x", x
        y = slope1*x + b1
        if math.isnan(y):
          y = vertexError.getY()
        print "y", y

        vertex = createPoint(subtype, x, y)
        print vertex

      else:
        vertex = None

      if vertex != None:
        if lineToSnap.getVertex(0) == vertexError:
          print "start"
  #      if typeLine == "start":
          snappedLine.addVertex(vertex)
  
        for i in range(0, numVertex):
          print i
          if lineToSnap.getVertex(i) == vertexError:
            print "continue"
            continue
          else:
            print "else"
            snappedLine.addVertex(lineToSnap.getVertex(i))
            print snappedLine.getNumVertices()
  
        if lineToSnap.getVertex(numVertex-1) == vertexError:
          print "end"
  #      if typeLine == "end":
          snappedLine.addVertex(vertex)

        print "update"
        feature1 = feature1.getEditable()
        feature1.set("GEOMETRY", snappedLine)
        dataSet.update(feature1)

      else:
        print "It can't snap"
      
    except:
      ex = sys.exc_info()[1]
      print "Error", ex.__class__.__name__, str(ex)
      #throw new ExecuteTopologyRuleActionException(ex);
      #raise ExecuteTopologyRuleActionException(ex)

def main(*args):

    c = SnapAction()
    pass