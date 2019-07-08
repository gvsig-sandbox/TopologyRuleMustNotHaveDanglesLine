from gvsig import uselib

uselib.use_plugin("org.gvsig.topology.app.mainplugin")

import sys


from org.gvsig.topology.lib.spi import AbstractTopologyRule


from gvsig import logger
from gvsig import LOGGER_WARN,LOGGER_INFO,LOGGER_ERROR

from org.gvsig.topology.lib.api import TopologyLocator

from org.gvsig.expressionevaluator import ExpressionEvaluatorLocator

#from DeletePointAction import DeletePointAction


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
    #self.addAction(DeletePointAction())
  
  def check(self, taskStatus, report, feature1):
    #SimpleTaskStatus taskStatus, 
    #TopologyReport report, 
    #Feature feature1

    try:
      print "Starts with: ", feature1.Name
      logger("si", LOGGER_INFO)
      #store2 = self.getDataSet2().getFeatureStore()
      #tolerance = self.getTolerance()
      #logger("1", LOGGER_INFO)
      
      if (self.expression == None):
        manager = ExpressionEvaluatorLocator.getManager()
        self.expression = manager.createExpression()
        self.expressionBuilder = manager.createExpressionBuilder()
        self.geomName = feature1.getType().getDefaultGeometryAttributeName()
      
      line = feature1.getDefaultGeometry()
      #lineTolerance = line.buffer(tolerance) #polygon
      numVertexLine = line.getNumVertices()
      lista = [line.getVertex(0), line.getVertex(numVertexLine-1)]
      
      for vertex in lista:
        noError = False
        print "One end of the line ", feature1.get("Name"), "is: ", vertex
        print type(vertex)
        #if( point==None ):
         # return
        #logger("1", LOGGER_INFO)
        
        theDataSet = self.getDataSet1()
        #logger("2", LOGGER_INFO)
        if theDataSet.getSpatialIndex() != None:
          #logger("if", LOGGER_INFO)
          for reference in theDataSet.query(vertex):
            #FeatureReference reference
            # Misma feature
            #logger("ref"+str(reference), LOGGER_INFO)
            
            
            feature = reference.getFeature()
            otherLine = feature.getDefaultGeometry()
            #numVertexOtherLine = otherLine.getNumVertices()
            
            print "Analyzing vertex of ", feature1.Name, " with line ", feature.Name
            #if line.touches(otherLine):
            

            if (reference.equals(feature1.getReference())):
              print "Same entity"
              print numVertexLine
              #continue;
              if numVertexLine > 2:
                endVertex = line.getVertex(0)
                print type(endVertex)
                cloneLine = line.cloneGeometry()
                if lista.index(vertex) == 0:
                  cloneLine.removeVertex(0)
                  if cloneLine.intersects(vertex):
                    print "Intersects with itself"
                    noError = True
                    
                  else:
                    print "No intersects with itself"
                else:
                  cloneLine.removeVertex(numVertexLine-1)
                  if cloneLine.intersects(vertex):
                    print "Intersects with itself"
                    noError = True
                    
                  else:
                    print "No intersects with itself"
                    
              
            if (vertex.intersects(otherLine) and not line.equals(otherLine)):
              print "Intersects vertex", feature1.Name, " with line ", feature.Name
              noError = True
              break

                
          logger("previous report", LOGGER_INFO)
          if noError == False:
            error = vertex
            logger("report", LOGGER_INFO)
            print "The mistake is: ", error
            report.addLine(self,
              theDataSet,
              None,
              line,
              error,
              feature1.getReference(),
              None,
              False,
              "The point is dangling"
            )

          else:
            print "Intersecta"
            
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
    except: # Exception as ex:
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