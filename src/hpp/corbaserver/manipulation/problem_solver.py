#!/usr/bin/env python
#
# Copyright (c) 2014 CNRS
# Author: Florent Lamiraux
#

# Redistribution and use in source and binary forms, with or without
# modification, are permitted provided that the following conditions are
# met:
#
# 1. Redistributions of source code must retain the above copyright
#    notice, this list of conditions and the following disclaimer.
#
# 2. Redistributions in binary form must reproduce the above copyright
# notice, this list of conditions and the following disclaimer in the
# documentation and/or other materials provided with the distribution.
#
# THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS
# "AS IS" AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT
# LIMITED TO, THE IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR
# A PARTICULAR PURPOSE ARE DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT
# HOLDER OR CONTRIBUTORS BE LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL,
# SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT
# LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES; LOSS OF USE,
# DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND ON ANY
# THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT
# (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE
# OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH
# DAMAGE.

def newProblem (client = None, name = None):
    from hpp.corbaserver.problem_solver import newProblem
    if client is None:
        from hpp.corbaserver.manipulation import Client
        client = Client()
    newProblem (client = client, name = name)

from hpp.corbaserver.problem_solver import _convertToCorbaAny, ProblemSolver as Parent

## Definition of a manipulation planning problem
#
#  This class wraps the Corba client to the server implemented by
#  libhpp-manipulation-corba.so
#
#  Some method implemented by the server can be considered as private. The
#  goal of this class is to hide them and to expose those that can be
#  considered as public.
class ProblemSolver (Parent):
    def __init__ (self, robot):
        super (ProblemSolver, self).__init__ (robot, hppcorbaClient = robot.client.basic)

    ## Select a problem by its name.
    #  If no problem with this name exists, a new
    #  hpp::manipulation::ProblemSolver is created and selected.
    #  \param name the problem name.
    #  \return true if a new problem was created.
    def selectProblem (self, name):
        return self.client.manipulation.problem.selectProblem (name)

    ## Return a list of available elements of type type
    #  \param type enter "type" to know what types I know of.
    #              This is case insensitive.
    def getAvailable (self, type):
        if type.lower () == "type":
            res = self.client.basic.problem.getAvailable (type) + \
                  self.client.manipulation.problem.getAvailable (type)
            return res
        try:
            return self.client.basic.problem.getAvailable (type)
        except:
            return self.client.manipulation.problem.getAvailable (type)

    ## Return a list of selected elements of type type
    #  \param type enter "type" to know what types I know of.
    #              This is case insensitive.
    #  \note For most of the types, the list will contain only one element.
    def getSelected (self, type):
        try:
            return self.client.basic.problem.getSelected (type)
        except:
            return self.client.manipulation.problem.getSelected (type)

    ## \name Contact surfaces
    #
    #  In placement states, objects are in contact with other objects or with
    #  the environment through contact surfaces.
    #  \{

    ##  \copydoc hpp::corbaserver::manipulation::Problem::getEnvironmentContactNames
    def getEnvironmentContactNames(self):
        return self.client.manipulation.problem.getEnvironmentContactNames()

    ##  \copydoc hpp::corbaserver::manipulation::Problem::getRobotContactNames
    def getRobotContactNames(self):
        return self.client.manipulation.problem.getRobotContactNames()

    ##  \copydoc hpp::corbaserver::manipulation::Problem::getEnvironmentContact
    def getEnvironmentContact(self, name):
        return self.client.manipulation.problem.getEnvironmentContact(name)

    ##  \copydoc hpp::corbaserver::manipulation::Problem::getRobotContact
    def getRobotContact(self, name):
        return self.client.manipulation.problem.getRobotContact(name)

    ## \}

    ## \name Constraints
    #  \{

    ## Create placement and pre-placement constraints
    #
    # \param width set to None to skip creation of pre-placement constraint
    #
    # See hpp::corbaserver::manipulation::Problem::createPlacementConstraint
    # and hpp::corbaserver::manipulation::Problem::createPrePlacementConstraint
    def createPlacementConstraints (self, placementName, shapeName, envContactName, width = 0.05):
        name = placementName
        self.client.manipulation.problem.createPlacementConstraint (name, shapeName, envContactName)
        if width is not None:
            prename = "pre_" + name
            self.client.manipulation.problem.createPrePlacementConstraint (prename, shapeName, envContactName, width)
            return name, prename
        return name

    ## Create QP Static stability constraint
    #
    #  \copydoc hpp::corbaserver::manipulation::Problem::createQPStabilityConstraint
    def createQPStabilityConstraint(self, *args):
        self.client.manipulation.problem.createQPStabilityConstraint(*args)

    ## \copydoc hpp::corbaserver::manipulation::Problem::registerConstraints
    def registerConstraints(self, *args):
        self.client.manipulation.problem.registerConstraints(*args)

    ## Return balance constraints created by method
    #  ProblemSolver.createStaticStabilityConstraints
    def balanceConstraints (self):
        return self.balanceConstraints_

    ## Get whether right hand side of a numerical constraint is constant
    #  \param constraintName Name of the numerical constraint,
    #  \return whether right hand side is constant
    def getConstantRightHandSide (self, constraintName) :
        return self.client.basic.problem.getConstantRightHandSide \
            (constraintName)

    ## Lock degree of freedom of a FreeFlyer joint
    # \param freeflyerBname base name of the joint
    #        (It will be completed by '_xyz' and '_SO3'),
    # \param lockJointBname base name of the LockedJoint constraints
    #        (It will be completed by '_xyz' and '_SO3'),
    # \param values config of the locked joints (7 float)
    def lockFreeFlyerJoint (self, freeflyerBname, lockJointBname,
                            values = (0,0,0,0,0,0,1)):
        lockedJoints = list ()
        self.createLockedJoint (lockJointBname, freeflyerBname, values)
        lockedJoints.append (lockJointBname)
        return lockedJoints

    ## Lock degree of freedom of a planar joint
    # \param jointName name of the joint
    #        (It will be completed by '_xy' and '_rz'),
    # \param lockJointName name of the LockedJoint constraint
    # \param values config of the locked joints (4 float)
    def lockPlanarJoint (self, jointName, lockJointName, values = (0,0,1,0)):
        lockedJoints = list ()
        self.createLockedJoint (lockJointName, jointName, values)
        lockedJoints.append (lockJointName)
        return lockedJoints

    ## \}

    ## \name Solve problem and get paths
    #  \{

    ## Set the problem target to stateId
    # The planner will look for a path from the init configuration to a configuration in
    # state stateId
    def setTargetState (self, stateId):
        self.client.manipulation.problem.setTargetState(stateId)
    ## \}
