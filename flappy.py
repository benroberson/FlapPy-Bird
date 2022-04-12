#python3
#cmdline args: Use an integer 1-4 to demo different levels of training.
#cmdline args: Or no arguments for a random initialization.
import pygame, sys, time
from pygame.locals import *
import random
import math
import numpy as np
import sys
pygame.init()

#constants
#board size
xmax=900
ymax=600
DISPLAYSURF = pygame.display.set_mode((xmax, ymax))
pygame.display.set_caption('FlapPy')
birdImg = pygame.image.load('ybird-big.png')

BLACK = (  0,   0,   0)
WHITE = (255, 255, 255)
RED = (255,   0,   0)
GREEN = (  0, 255,   0)
BLUE = (  0,   0, 255)
YELLOW = (255, 255, 0)
fpsClock=pygame.time.Clock()

#constants
FPS=60
pipeWidth=80
gapHeight=150
bird_x=80
bird_y=ymax*.6
bird_w=43
bird_h=30
spdup=2
#variables
score = 0
y_spd=0
frameCount=(-1)
pipes=[]
next_pipe=[]
bird = pygame.Rect(bird_x, bird_y, bird_w, bird_h)	 #bird
looping=True

#network
progress=0
if len(sys.argv)>1:
	progress=int(sys.argv[1])

#PRE-DETERMINED WEIGHTS FROM PREVIOUS RUNS
#quality: meh
if(progress==1):
	weightsL1=np.array([[ 0.31431067, 0.084785  , 0.30064062],[-0.8738743 ,-0.46813362,-0.07853632],[-0.23529337, 0.07492885,-0.63322539]])
	weightsL2=np.array([ 0.45328671,-0.95900646, 0.15162343])
#quality: decent
elif(progress==2):
	weightsL1=np.array([[-0.83336703,0.43988739,-0.48190723],[-0.30973067,0.110059,0.6963024],[0.83280786,-0.00118471,-0.47811464]])
	weightsL2=np.array([-0.77319211,-0.14416796,0.77024503])
#quality: awesome
elif(progress==3):
	weightsL1=np.array([[-0.49794471473342033, 0.7397473901212568, -0.21048167346064167], [-0.09625933558177077, 0.05053663360433471, 0.11833361672567057], [0.25044866219333145, -0.0011133613847348048, -0.2766796191275747]])
	weightsL2=np.array([-0.67621998,-0.14416796,0.77024503])
#quality: perfect
elif(progress==4):
	print("HI")
	weightsL1=np.array([[-1.        ,-0.83916195, 0.85129423], [-1.        , 0.99068001, 0.92442616], [ 0.99652072,-0.72392455, 0.71504415]])
	weightsL2=np.array([ 0.0360545 ,-1.        , 0.84286559])
#quality: RANDOM INIT
else:
	print("HI")
	weightsL1=(np.random.rand(3,3)*2-1)
	weightsL2=(np.random.rand(3)*2-1)

last_weightsL1=[]
last_weightsL2=[]
last_frames=0
history_flag=0
file = open("best_scores.txt","w+")

def sigmoid(x):
	return 1 / (1 + math.exp(-x))

#def restart():
#	global score,y_spd,frameCount
	#last_frames=frames
#	return 0
def quitgame():
	global file
	file.close()
	print("score:",score)
	pygame.quit()
	sys.exit()

while True:
	while looping: # main game loop
		#pipes[]: [pipe xpos, gap ypos]
		#all pipes have same width, height(max), ypos(edge)
		#Rect=(x,y,w,h)
		frameCount+=1
		#gravity
		y_spd-=.35
		if y_spd < -10:
			y_spd=-10
		
		#erase objects
		pygame.draw.rect(DISPLAYSURF, BLACK, bird) #(bird.x,bird.y,bird.w+4,bird.h))	 #bird
		for p in pipes:
			pygame.draw.rect(DISPLAYSURF, BLACK, (p[0], 0, pipeWidth, ymax))	 #pipe
			
		#mainipulate objects:
		#add new pipe
		if frameCount % math.floor(200/spdup) == 0:
			pipes.append([xmax,random.randint(bird_h/2,ymax-gapHeight-bird_h/2)])
		#if frameCount % 50 == 0:
		#	print(fpsClock.get_fps())		
		if pipes[0][0]+pipeWidth > bird.left:
			next_pipe=pipes[0]
		else:
			next_pipe=pipes[1]
		#pipe scrolling
		for p in pipes:
			p[0]-=2*spdup
			
		#flap pressed
		if pygame.key.get_pressed()[K_SPACE] == True:
			y_spd = 5
		if pygame.key.get_pressed()[K_p] == True:
			time.sleep(2)
		if pygame.key.get_pressed()[K_h] == True:
			history_flag=1
		if pygame.key.get_pressed()[K_r] == True:
			weightsL1=np.random.rand(3,3)*2-1
			weightsL2=np.random.rand(3)*2-1
		#Flap Decision
		#parameter ideas:
		#gap (x-bird_x), y, spd? for gap of leftmost pipe bird hasn't passed
		#bird y pos, spd?
		params = np.array([bird.y/ymax, next_pipe[1]/ymax, next_pipe[0]/xmax])
		output = weightsL2[0]*sigmoid((weightsL1[0]*params).sum()) + \
		weightsL2[1]*sigmoid((weightsL1[1]*params).sum()) + \
		weightsL2[2]*sigmoid((weightsL1[2]*params).sum())
		if output>0:
			y_spd = 5
		#if frameCount % 50 == 0:
		#print("output:",output)		
		
		#update bird position
		bird.y -= y_spd
		
		#collisions
		for p in pipes[:2]:
			if p[0] < -pipeWidth:
				pipes.pop(0)
				score +=1
			#inside a pipe
			if bird.right > p[0] and bird.right < p[0]+pipeWidth+bird_w:
				#collision with top/bottom surfaces
				if bird.top < p[1] or bird.bottom > p[1]+gapHeight:
					looping=False
					#print(frameCount, "COLLISION")
		#hit upper/lower		
		if bird.top < 0 or bird.bottom > ymax:
			looping=False
		
		#draw objects	
		for p in pipes:
			pygame.draw.rect(DISPLAYSURF, GREEN, (p[0], 0, pipeWidth, ymax))		 #pipe
			pygame.draw.rect(DISPLAYSURF, BLACK, (p[0], p[1], pipeWidth, gapHeight))  #gap
		#pygame.draw.rect(DISPLAYSURF, YELLOW, bird)		 #bird
		DISPLAYSURF.blit(birdImg,(bird.x,bird.y))
		#quit by [x]
		for event in pygame.event.get():
			if event.type == QUIT:
				quitgame()
		pygame.display.update()
		fpsClock.tick(FPS)
	
	print("score:",score)
	print("frameCount:",frameCount)
	#if this round did better than last, keep this round, otherwise go back to last
	if frameCount > last_frames:
		last_weightsL1 = weightsL1.copy()
		last_weightsL2 = weightsL2.copy()
		last_frames=frameCount
		print("BETTER")
		#record new best to file
		file.write("score: "+str(score)+"\n")
		file.write("frameCount: "+str(frameCount)+"\n")
		file.write(np.array2string(weightsL1,separator=',')+"\n")
		file.write(np.array2string(weightsL2,separator=',')+"\n")
	else:
		weightsL1 = last_weightsL1.copy()
		weightsL2 = last_weightsL2.copy()
		print("WORSE")
		
	#randomly change network
	#relate score to change chance
	if history_flag==0:
		if frameCount<100:
			percent_change=1 #4
			change_chance=0.3
		elif frameCount<500 and last_frames<700:
			percent_change=0.3 #1
			change_chance=0.2
		else:
			percent_change=0.1 #0.5
			change_chance=0.12
		changes=[random.randint(0,1) for i in range(12)]
		for i in range(12):
			#index each elem in mtx, change if %chance is met
			if np.random.rand()<change_chance:
				if i<9:
					weightsL1[i//3][i%3] += ((np.random.rand()-.5)*2*percent_change)
					if abs(weightsL1[i//3][i%3])>1:
						weightsL1[i//3][i%3] = np.sign(weightsL1[i//3][i%3])
				else:
					weightsL2[i-9] += ((np.random.rand()-.5)*2*percent_change)
					if abs(weightsL2[i-9])>1:
						weightsL2[i-9] = np.sign(weightsL2[i-9])
		
					#weightsL2[i-9] *= ((np.random.rand()-.5)*2*percent_change+1)
	print("last_frames:",last_frames)
	#print("last weights:")
	#print(last_weightsL1)
	print("current weights:")
	print(weightsL1)
	print(weightsL2)
	#reset board
	score=0
	y_spd=0
	pipes=[]
	next_pipe=[]
	bird = pygame.Rect(bird_x, bird_y, bird_w, bird_h)	 #bird
	pygame.draw.rect(DISPLAYSURF, BLACK, (0,0,xmax,ymax))	 #bird
	pygame.display.update()
	frameCount=(-1)
	looping=True
	history_flag=0
	
		