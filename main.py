# ------------------------------------------------------------------------------------------------
# Copyright (c) 2016 Microsoft Corporation
# 
# Permission is hereby granted, free of charge, to any person obtaining a copy of this software and
# associated documentation files (the "Software"), to deal in the Software without restriction,
# including without limitation the rights to use, copy, modify, merge, publish, distribute,
# sublicense, and/or sell copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
# 
# The above copyright notice and this permission notice shall be included in all copies or
# substantial portions of the Software.
# 
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT
# NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND
# NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM,
# DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.
# ------------------------------------------------------------------------------------------------

# Tutorial sample #5: Observations

import MalmoPython
import os
import sys
import time
import json
import numpy as np
sys.stdout = os.fdopen(sys.stdout.fileno(), 'w', 0)  # flush print output immediately

def Menger(xorg, yorg, zorg, size, blocktype, variant, holetype):
    #draw solid chunk
    genstring = GenCuboidWithVariant(xorg,yorg,zorg,xorg+size-1,yorg+size-1,zorg+size-1,blocktype,variant) + "\n"
    #now remove holes
    unit = size
    while (unit >= 3):
        w=unit/3
        for i in xrange(0, size, unit):
            for j in xrange(0, size, unit):
                x=xorg+i
                y=yorg+j
                genstring += GenCuboid(x+w,y+w,zorg,(x+2*w)-1,(y+2*w)-1,zorg+size-1,holetype) + "\n"
                y=yorg+i
                z=zorg+j
                genstring += GenCuboid(xorg,y+w,z+w,xorg+size-1, (y+2*w)-1,(z+2*w)-1,holetype) + "\n"
                genstring += GenCuboid(x+w,yorg,z+w,(x+2*w)-1,yorg+size-1,(z+2*w)-1,holetype) + "\n"
        unit/=3
    return genstring

def GenCuboid(x1, y1, z1, x2, y2, z2, blocktype):
    return '<DrawCuboid x1="' + str(x1) + '" y1="' + str(y1) + '" z1="' + str(z1) + '" x2="' + str(x2) + '" y2="' + str(y2) + '" z2="' + str(z2) + '" type="' + blocktype + '"/>'

def GenCuboidWithVariant(x1, y1, z1, x2, y2, z2, blocktype, variant):
    return '<DrawCuboid x1="' + str(x1) + '" y1="' + str(y1) + '" z1="' + str(z1) + '" x2="' + str(x2) + '" y2="' + str(y2) + '" z2="' + str(z2) + '" type="' + blocktype + '" variant="' + variant + '"/>'
    
missionXML='''<?xml version="1.0" encoding="UTF-8" standalone="no" ?>
            <Mission xmlns="http://ProjectMalmo.microsoft.com" xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance">
            
              <About>
                <Summary>Hello world!</Summary>
              </About>
              
            <ServerSection>
              <ServerInitialConditions>
                <Time>
                    <StartTime>1000</StartTime>
                    <AllowPassageOfTime>false</AllowPassageOfTime>
                </Time>
                <Weather>clear</Weather>
              </ServerInitialConditions>
              <ServerHandlers>
                  <FlatWorldGenerator generatorString="3;7,44*49,73,35:1,159:4,95:13,35:13,159:11,95:10,159:14,159:6,35:6,95:6;12;"/>
                  <DrawingDecorator>
                    <DrawSphere x="-27" y="70" z="0" radius="30" type="air"/>''' + Menger(-40, 40, -13, 27, "stone", "smooth_granite", "air") + '''
                    <DrawCuboid x1="-25" y1="39" z1="-2" x2="-29" y2="39" z2="2" type="lava"/>
                    <DrawCuboid x1="-26" y1="39" z1="-1" x2="-28" y2="39" z2="1" type="obsidian"/>
                    <DrawBlock x="-27" y="39" z="0" type="diamond_block"/>
                  </DrawingDecorator>
                  <ServerQuitFromTimeUp timeLimitMs="30000"/>
                  <ServerQuitWhenAnyAgentFinishes/>
                </ServerHandlers>
              </ServerSection>
              
              <AgentSection mode="Survival">
                <Name>MalmoTutorialBot</Name>
                <AgentStart>
                    <Placement x="0.5" y="56.0" z="0.5" yaw="90"/>
                    <Inventory>
                        <InventoryItem slot="8" type="diamond_pickaxe"/>
                    </Inventory>
                </AgentStart>
                <AgentHandlers>
                  <ObservationFromFullStats/>
                  <ObservationFromGrid>
                      <Grid name="floor3x3">
                        <min x="-1" y="-1" z="-1"/>
                        <max x="1" y="-1" z="1"/>
                      </Grid>
                  </ObservationFromGrid>
                  <ContinuousMovementCommands turnSpeedDegs="180"/>
                  <InventoryCommands/>
                  <AgentQuitFromTouchingBlockType>
                      <Block type="diamond_block" />
                  </AgentQuitFromTouchingBlockType>
                </AgentHandlers>
              </AgentSection>
            </Mission>'''

# Create default Malmo objects:

agent_host = MalmoPython.AgentHost()
try:
    agent_host.parse( sys.argv )
except RuntimeError as e:
    print 'ERROR:',e
    print agent_host.getUsage()
    exit(1)
if agent_host.receivedArgument("help"):
    print agent_host.getUsage()
    exit(0)

my_mission = MalmoPython.MissionSpec(missionXML, True)
my_mission_record = MalmoPython.MissionRecordSpec()

# Attempt to start a mission:
max_retries = 3
for retry in range(max_retries):
    try:
        agent_host.startMission( my_mission, my_mission_record )
        break
    except RuntimeError as e:
        if retry == max_retries - 1:
            print "Error starting mission:",e
            exit(1)
        else:
            time.sleep(2)

# Loop until mission starts:

print "Waiting for the mission to start ",
world_state = agent_host.getWorldState()
while not world_state.has_mission_begun:
    sys.stdout.write(".")
    time.sleep(0.1)
    world_state = agent_host.getWorldState()
    for error in world_state.errors:
        print "Error:",error.text

print
print "Mission running ",

# Possible solution for challenge set in tutorial_4.py:

#agent_host.sendCommand("hotbar.9 1") #Press the hotbar key
#agent_host.sendCommand("hotbar.9 0") #Release hotbar key - agent should now be holding diamond_pickaxe

#agent_host.sendCommand("pitch 0.2") #Start looking downward slowly
#time.sleep(1)                        #Wait a second until we are looking in roughly the right direction
#agent_host.sendCommand("pitch 0")    #Stop tilting the camera
#agent_host.sendCommand("move 1")     #And start running...
#agent_host.sendCommand("attack 1")   #Whilst flailing our pickaxe!

def sigmoid(x):
    #don't need to have derivative capability, never going to backpropogate
    #use sigmoid to normalize calculations
    return(1/(1+np.exp(-x)))

actions = [] #list of all potential actions that the agent could take
#needs to be filled by default otherwise the model can't communicate to agent what to choose
#the actions list comes specific for a given environment.

class Capsule:
    def __init__(self, purpose, neurons):
        self.purpose = purpose
        self.neurons = neurons
        self.delta = 0.1
        np.random.seed(1)
    def think(neurons, state, actions):
        layer0 = state
        syn0 = np.random.random((neurons, len(layer0)))*2-1
        syn1 = np.random.random((len(plans), neurons))*2-1
        layer1 = sigmoid(np.dot(layer0, syn0))
        layer2 = sigmoid(np.dot(layer1, syn1))
        action_plan = actions[layer2.argmax]
        return(action_plan)
    def reward(x):
        delta *= 1/x
        syn0 *= delta
        syn1 *= delta
        #conscience rewards the capsules, this is how the individual modules of the model 
        #can learn, they are adjusted until finding synaptic weights

        #this function adjusts the synaptic weights, most rewards are negative
        #if the reward comes in positive, changes the delta coefficient

capsules = [Capsule('search', 20),Capsule('mine', 20),Capsule('fight', 20),Capsule('craft', 20)]

#list of capsules matches up to plan indices
class Conscience:
    def __init__(self, fit, plans, seed, neurons):
        self.fit = fit
        self.plans = plans
        self.delta = 0.1
        self.seed = seed
        self.neurons = neurons
        #seed argument to allow for genetic mutations
        np.random.seed(seed)
    def think(state):
        #vectorize world state
        #feed world_vector through model
        #output index of plans for the action to take
        #this new vector indicating what the player's goal is
        layer0 = np.array(state)
        syn0 = np.random.random((neurons, len(layer0)))*2-1
        syn1 = np.random.random((len(plans), neurons))*2-1
        layer1 = sigmoid(np.dot(layer0, syn0))
        layer2 = sigmoid(np.dot(layer1, syn1))

        plans[layer2.argmax()] = 1
        return(plans.argmax())
    def reward(x):
        #this function gets called whenever the agent does something objectively good
        #say they meet a goal, this rewards this conscience
        #if the agent gets hurt, lower this brain's fitness so that
        #the strong models are more able to survive in the implementation of
        #a genetic algorithm
        delta *= 1/x
        fit *= delta
# Loop until mission ends:
known_blocks = []
known_actions = ["move 1"]
empty_plan = [0] * len(capsules)
brain = Conscience(0, empty_plan, 1, 20)
while world_state.is_mission_running:
    sys.stdout.write(".")
    time.sleep(0.1)
    world_state = agent_host.getWorldState()
    for error in world_state.errors:
        print "Error:",error.text
    if world_state.number_of_observations_since_last_state > 0: # Have any observations come in?
        msg = world_state.observations[-1].text                 # Yes, so get the text
        observations = json.loads(msg)                          # and parse the JSON
        grid = observations.get(u'floor3x3', 0)                 # and get the grid we asked for
        print(observations)
        # ADD SOME CODE HERE TO SAVE YOUR AGENT
        hot_grid = [0] * len(grid)
        for i in range(len(grid)):
            if grid[i] not in known_blocks:
                known_blocks.append(grid[i])
            for j in range(len(known_blocks)):
                if grid[i] is known_blocks[j]:
                    hot_grid[i] = j
        params = np.random.random((1, 9))*2 - 1
        observation = [] #array that contains preprocessed information to think about
        observation.extend(hot_grid)
        for item in observations:
            if type(item) is int:
                observation.append(item)
        print(observation)
        #run through the conscience and capsules and do the action that comes out
        agent_host.sendCommand(capsules[brain.think(observation)].think())

              

print
print "Mission ended"
# Mission has ended.