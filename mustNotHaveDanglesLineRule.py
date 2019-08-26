from gvsig import uselib

uselib.use_plugin("org.gvsig.topology.app.mainplugin")

import sys


from org.gvsig.topology.lib.spi import AbstractTopologyRule


from gvsig import logger
from gvsig import LOGGER_WARN,LOGGER_INFO,LOGGER_ERROR

from org.gvsig.topology.lib.api import TopologyLocator

from org.gvsig.expressionevaluator import ExpressionEvaluatorLocator

from ExtendAction import ExtendAction
from TrimAction import TrimAction
#from SnapAction import SnapAction


class MustNotHaveDanglesLineRule(AbstractTopologyRule):
  
  geomName = None
  expression = None
  expressionBuilder = None
  
  def __init__(self, plan, factory, tolerance, dataSet1):
    #        TopologyPlan plan,
    #        TopologyRuleFactory factory,
    #        double tolerance,
    #        String dataSet1
    
    AbstractTopologyRule.__init__(self, plan, factory, tolerance, dataSet1)
    self.addAction(ExtendAction())
    self.addAction(TrimAction())
    #self.addAction(SnapAction())
  
  def check(self, taskStatus, report, feature1):
    #SimpleTaskStatus taskStatus, 
    #TopologyReport report, 
    #Feature feature1

    try:
      print "Starts with: ", feature1.Name
      logger("si", LOGGER_INFO)

      if (self.expression == None):
        manager = ExpressionEvaluatorLocator.getManager()
        self.expression = manager.createExpression()
        self.expressionBuilder = manager.createExpressionBuilder()
        self.geomName = feature1.getType().getDefaultGeometryAttributeName()

      line = feature1.getDefaultGeometry()

      if line == None:
        return

      tolerance = self.getTolerance()
      numVertexLine = line.getNumVertices()
      lista = [line.getVertex(0), line.getVertex(numVertexLine-1)]
      
      for vertex in lista:
        noError = False
        print "One end of the line ", feature1.get("Name"), "is: ", vertex

        if tolerance != 0:
          vertexTolerance = vertex.buffer(tolerance)
        else:
          vertexTolerance = vertex

        theDataSet = self.getDataSet1()
        if theDataSet.getSpatialIndex() != None:
          for reference in theDataSet.query(vertexTolerance):
            #FeatureReference reference

            feature = reference.getFeature()
            otherLine = feature.getDefaultGeometry()

            print "Analyzing vertex of ", feature1.Name, " with line ", feature.Name

            if (reference.equals(feature1.getReference())):
              print "Same entity"
              print numVertexLine
              if numVertexLine > 2:
                endVertex = line.getVertex(0)
                print type(endVertex)
                cloneLine = line.cloneGeometry()
                if lista.index(vertex) == 0:
                  cloneLine.removeVertex(0)
                  if cloneLine.intersects(vertexTolerance):
                    print "Intersects with itself"
                    noError = True
                    
                  else:
                    print "No intersects with itself"
                else:
                  cloneLine.removeVertex(numVertexLine-1)
                  if cloneLine.intersects(vertexTolerance):
                    print "Intersects with itself"
                    noError = True
                    
                  else:
                    print "No intersects with itself"

            if (vertexTolerance.intersects(otherLine) and not line.equals(otherLine)):
              print "Intersects vertex", feature1.Name, " with line ", feature.Name
              noError = True
              break

          logger("previous report", LOGGER_INFO)
          if noError == False:
            error = vertex
            ver = vertex.convertToWKT()
            logger("report", LOGGER_INFO)
            print "The mistake is: ", error
            report.addLine(self,
              theDataSet,
              None,
              line,
              error,
              feature1.getReference(),
              None,
              0,
              0,
              False,
              "The point is dangling",
              ver
            )

          else:
            print "Intersects"
            
      else:
        logger("else", LOGGER_INFO)
        self.expression.setPhrase(
          self.expressionBuilder.ifnull(
            self.expressionBuilder.column(self.geomName),
            self.expressionBuilder.constant(False),
            self.expressionBuilder.ST_Overlaps(
              self.expressionBuilder.column(self.geomName),
              self.expressionBuilder.geometry(line)
            )
          ).toString()
        )
        feature = theDataSet.findFirst(self.expression)
        if feature != None:
            otherPoint = feature.getDefaultGeometry()
            error = None
            if otherPoint!=None :
              error = point.difference(otherPoint)
            
            report.addLine(self,
              theDataSet,
              None,
              point,
              error,
              feature1.getReference(),
              None,
              False,
              "The point is dangling"
            )
        logger("end", LOGGER_INFO)
    except:
      #logger("2 Can't check feature."+str(ex), LOGGER_WARN)
      ex = sys.exc_info()[1]
      logger("Can't execute rule. Class Name:" + ex.__class__.__name__ + " Except:" + str(ex))
    finally:
      pass
def main(*args):
  # testing class m = MustNotHaveDanglesLineRule(None, None, 3, None)
  print "* Executing MustNotHaveDanglesLine RULE main."
  tm = TopologyLocator.getTopologyManager()
  
  from mustNotHaveDanglesLineRuleFactory import MustNotHaveDanglesLineRuleFactory
  a = MustNotHaveDanglesLineRuleFactory()
  tm.addRuleFactories(a)