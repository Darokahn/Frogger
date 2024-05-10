import game
import pygame
import froggerlib
import random
import json
import log
from thesaurus import Thesaurus

print = log.log

def createWinLane(laneHeight):
    return (
    ["Home", [0, 0, 140, laneHeight]],
    ["Grass", [140, 0, 80, laneHeight]],
    ["Home", [220, 0, 140, laneHeight]],
    ["Grass", [360, 0, 80, laneHeight]],
    ["Home", [440, 0, 140, laneHeight]],
    ["Grass", [580, 0, 80, laneHeight]],
    ["Home", [660, 0, 140, laneHeight]]
    )

def makeLanes(laneCount, screenWidth, screenHeight):
    objects = []
    laneY = screenHeight / laneCount
    currentY = screenHeight
    for _ in range(laneCount):
        currentY -= laneY
        laneTypes = ["Water", "Road"]
        laneType = random.choice(laneTypes)
        laneX = screenWidth
        args = [0, currentY, laneX, laneY]
        if _ + 1 == laneCount:
            for obj in createWinLane(laneY):
                objects.append(obj)
            frogHeight = (3/4) * laneY
            frogOffset = (1/8) * laneY
            frogWidth = frogHeight
            frogX = (laneX / 2) - (frogWidth / 2)
            frogY = screenHeight - frogHeight - frogOffset
            frogSpeed = 50
            frogDX = laneY
            frogDY = laneY
            objects.append(["Frog", [frogX, frogY, frogWidth, frogHeight, frogX, frogY, frogSpeed, frogDX, frogDY]])
            break
        elif _ == 0:
            objects.append(["Stage", [0, currentY, laneX, laneY]])
            continue
        objects.append([laneType, args])
        newObstacles = generateObstacles(laneType, laneX, laneY, currentY)
        print(json.dumps(newObstacles), prints = False)
        for obstacle in newObstacles:
            objects.append(obstacle)
    return objects

def generateObstacles(laneType, laneWidth, laneHeight, yPosition):
    genericArgs = genericObstacleArgs(laneWidth, laneHeight, yPosition, random.randint(1, 4))
    if laneType == "Water":
        return generateWaterObstacles(genericArgs)
    if laneType == "Road":
        return generateRoadObstacles(genericArgs)
    
def generateWaterObstacles(genericArgs):
    obstacles = []
    waterTypes = ["Alligator", "Turtle", "Log"]
    for obstacleArgs in genericArgs:
        typ = random.choice(waterTypes)
        obstacles.append([typ, obstacleArgs])
    return obstacles
        

def generateRoadObstacles(genericArgs):
    obstacles = []
    laneTypes = ["Car", "RaceCar"]
    carTypes = ["Car", "Dozer", "Truck"]
    laneType = random.choice(laneTypes)
    if laneType == "Car":
        for obstacleArgs in genericArgs:
            typ = random.choice(carTypes)
            obstacles.append([typ, obstacleArgs])
        return obstacles
    obstacleArgs = random.choice(genericArgs)
    del obstacleArgs[-1]
    obstacleArgs += [1, 20]
    obstacles.append([laneType, obstacleArgs])
    return obstacles
    
def genericObstacleArgs(laneWidth, laneHeight, yPosition, numObstacles):
    obstacles = []
    obstacleHeight = (3/4) * laneHeight
    obstacleOffset = 1/8 * laneHeight
    obstacleDirection = random.choice((-1, 1))
    obstacleSpeed = random.randint(3, 10)
    obstacleWidth = random.randint(60, 100)
    occupiedSpace = obstacleWidth * numObstacles
    unoccupied = laneWidth - occupiedSpace
    spacerWidth = unoccupied / numObstacles
    for point in range(numObstacles):
        x = (point * obstacleWidth) + (point * spacerWidth)
        y = yPosition + obstacleOffset
        dx = 1000 * obstacleDirection
        dy = y
        genericArgs = [x, y, obstacleWidth, obstacleHeight, dx, dy, obstacleSpeed]
        obstacles.append(genericArgs)
    return obstacles
        
        

def getTypeTable():
    """Populates the value {types} with key-value pairs that link a string (I.E. "Frog") to a corresponding froggerlib type (froggerlib.frog.Frog).
    This way, a simple list of text entries or JSON code can be used to create a stage filled with objects."""
    types = Thesaurus()
    
    filterDataMembers = lambda cls: cls.lower() != cls  # returns False for the data members of froggerlib that are not game objects (game objects are capitalized)
    names = filter(filterDataMembers, dir(froggerlib) + list(globals()))
    
    for key in names:
        try:
            value = eval(f"froggerlib.{key}")
        except AttributeError:
            value = eval(key)
        types.update({key: value})
    return types

def colorObject(obj, types):
    colors = {
                "Frog": "light green",
                "Road": "#444444",
                "Log": "#996633",
                "Water": "#66ccff",
                "Grass": "green",
                "Alligator": "dark green",
                "Stage": "#009933",
                "Turtle": "red",
                "Home": "yellow"
              }
    objType = types[type(obj)]
    
    if objType in colors:
        obj.color = colors[objType]
        return
    obj.color = [random.randint(0, 255) for i in range(3)]
    return

def addObjToScene(obj, objType, scene, types):
    objTypes = objType.__mro__
    
    if "color" not in vars(obj):
        colorObject(obj, types)
    
    inTypes = lambda x : x in types  # returns False for the parent and grandparent types of obj that aren't in the types thesaurus.
    
    objTypes = list(filter(inTypes, objTypes + tuple(dir())))
    
    for typ in objTypes:
        typ = types[typ]
        if typ in scene:
            scene[typ].append(obj)
    return scene

def initiateObjects(loads):
    if type(loads) == str:
        with open(loads, "r") as loadStr:
            loads = loadStr.read()
            loads = json.loads(loads)
    scene = {"Locatable": [],
            "Movable": [],
            "Touchable": [],
            "Untouchable": [],
            "Dodgeable": [],
            "Rideable": [],
            "PlayerControllable": []}
    
    types = getTypeTable()
    
    for item in loads:
        classArgs = item[1]
        item = item[0]
        objType = types[item]
        obj = objType(*classArgs)
        addObjToScene(obj, objType, scene, types)
    return scene

def addParticle(obstacle, scene, objSpeed, color):
    deltay = obstacle.getY()
    deltay += (obstacle.getHeight()/2)
    if obstacle.getX() > obstacle.getDesiredX():
        deltax = obstacle.getX() + obstacle.getWidth()
        particleDirection = 1
    else:
        deltax = obstacle.getX()
        particleDirection = -1
        
    size = (random.randint(5, 20) * objSpeed)/5
    if particleDirection == -1:
        deltax -= size
    deltay += random.randint(-10, 10)
    deltay -= size/2
    
    xMag = (random.randint(0, 1) * particleDirection * objSpeed) + deltax
    yMag = ((random.randint(-10, 10)/10) *objSpeed) + deltay
    
    speed = random.randint(1, 3) * objSpeed
    
    p = Particle(deltax, deltay, size, size, xMag, yMag, speed, color)
    
    addObjToScene(p, Particle, scene, Game.types)
    

class Particle(froggerlib.Movable):
    def __init__(self, x, y, w, h, dx, dy, s, color):
        super().__init__(x, y, w, h, dx, dy, s)
        self.color = color
    def move(self):
        froggerlib.Movable.move(self)
        if self.atDesiredLocation():
            del self
        
class Game(game.Game):
    
    types = getTypeTable()
    
    def __init__(self, name, width, height, fps, loads):
        super().__init__(name, width, height, fps)
        self.scene = initiateObjects(loads)
        self.loads = loads
        
    def lose(self):
        print("lose")
        self.reset()
    
    def win(self):
        print("win")
        self.loads = makeLanes(10, SCREEN_WIDTH, SCREEN_HEIGHT)
        self.reset()
        
    def reset(self):
        self.scene = initiateObjects(self.loads)
        
    def game_logic(self, keys, newKeys, buttons, newbuttons, mouse_position, dt):
        arrows = {
                    1073741904: froggerlib.PlayerControllable.left,
                    1073741903: froggerlib.PlayerControllable.right,
                    1073741906: froggerlib.PlayerControllable.up,
                    1073741905: froggerlib.PlayerControllable.down
                  }
        for key in newKeys:
            for player in self.scene["PlayerControllable"]:
                if key in arrows:
                    arrows[key](player)
                if player.outOfBounds(SCREEN_WIDTH, SCREEN_HEIGHT):
                    self.lose()
        for mover in self.scene["Movable"]:
            if mover.getX() + mover.getWidth() < 0 and type(mover) not in (Particle, froggerlib.Frog):
                mover.setX(800)
            elif mover.getX() > SCREEN_WIDTH and type(mover) not in (Particle, froggerlib.Frog):
                mover.setX(0 - mover.getWidth())
            if type(mover) == Particle:
                if mover.atDesiredLocation():
                    for typ in self.scene:
                        if mover in self.scene[typ]:
                            self.scene[typ].remove(mover)
            mover.move()
        for toucher in self.scene["Untouchable"]:
            for player in self.scene["PlayerControllable"]:
                if toucher.hits(player):
                    self.lose()
        for obstacle in self.scene["Dodgeable"]:
            for player in self.scene["PlayerControllable"]:
                if obstacle.hits(player):
                    self.lose()
            for particle in range(round(obstacle.getSpeed()/3)):
                addParticle(obstacle, self.scene, obstacle.getSpeed(), "grey")
        for ride in self.scene["Rideable"]:
            for player in self.scene["PlayerControllable"]:
                ride.supports(player)
        for touched in self.scene["Touchable"]:
            for player in self.scene["PlayerControllable"]:
                if touched.hits(player):
                    self.win()
        
    def paint(self, screen):
        screen.fill("white")
        for item in self.scene["Locatable"]:
            x, y = item.getX(), item.getY()
            width, height = item.getWidth(), item.getHeight()
            itemSurface = pygame.Surface((width, height))
            itemSurface.fill(item.color)
            screen.blit(itemSurface, (x, y))
        pygame.display.flip()
    
    def __str__(self):
        types = getTypeTable()
        scene = ""
        for typ in self.scene:
            objects = ""
            for obj in self.scene[typ]:
                formatting = ", "
                if obj is self.scene[typ][-1]:
                    formatting = ""
                objText = types[type(obj)]
                objects += objText + formatting
            scene += f"{typ}: {objects}\n"
        return scene

SCREEN_WIDTH, SCREEN_HEIGHT = (800, 720)

load = "" # put a template here

if not load.strip():
    load = "loads/load1.json"

g = Game("frogger", SCREEN_WIDTH, SCREEN_HEIGHT, 30, load)

g.main_loop()

log.Log.final()