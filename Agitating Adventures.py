##########################################################################
## Program Author:  George Zhang (Original by Greg Anthony)             ##
## Revision Date:   Dec 31, 2018                                        ##
## Program Name:    Christmas Adventure                                 ##
## Description:     This program just does a Christmas themed game.     ##
##########################################################################

"""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""
Credit To: Greg Anthony

WELCOME! 

List of pre-made functions:

printInventory() - prints out the current inventory (both the items, and how many of each)
alreadyHaveIt(item) - checks if an item is already in the inventory and returns True or False. Disregards how many of each item there is
inventory(item) - Adds whatever item has been passed to the inventory. It will check if the item is already in the inventory. If it is, it adds 1 to the total for that item. If not, it makes a new entry for this item and sets its starting number to 1.
actionMenu() - prints a basic menu to the user with four choices: see the inventory, aggressive action, defensive action, or quit game. This menu is intended for scenes of action. It is up to you to decide what results from each choice! 
movementMenu() - Prints a basic menu of movements (left, right, forward), as well as allowing the player to see the menu or quit. It is up to you what happens if they choose a given movement!
removeStudent() - Removes the first student from the list of students (studentList) and returns their name as a string
removeItem(item) - Removes one unit of the given item from the inventory. It checks if that was the last unit. If so, it removes the item from the inventory completely.
gameOver() - checks if there are any students left in studentList. If not, tells the user the game is over and exits the program
main() - Holds the linear story (all the print statements). 

Sound documentation at: http://docs.python.org/3/library/winsound.html
"""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""

#Import libraries
import sys
import time as t
import math as m
import winsound as w
import pygame as p
from pygame.locals import *
from subprocess import call

def main(*args, **kwargs):
    """Run the program :D"""
    #Change the text colour to green
    call('color ' + 'a', shell = True)

    #make global variable Lists
    inventory = []
    students = []
    students.extend([
        'George', 'Yucen', 'Jeff', 'Kevin', 'Aarush', 'Daniel',
        'Colin', 'Andrew', 'David', 'Ian', 'Daniel', 'Shaun', 'Bryan',
    ])

    # start up pygame window
    p.init()

    # pygame constants
    SCREEN_WIDTH = 800 # width of window
    SCREEN_HEIGHT = 600 # height of window
    WHITE = (255, 255, 255)
    RED = (255, 0, 0)
    BLACK = (0, 0, 0)

    # make window
    screen = p.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT)) # size
    p.display.set_caption('Christmas Adventure') # title

    # get image with background removed
    def remove_background(image, background=None):
        """Return image with transparent background."""
        image = image.copy()
        if background is None:
            background = image.get_at((0, 0))
        image.set_colorkey(background)
        return image.convert()
    # end remove_background

    # draw player
    def draw_image(screen, image, x, y, angle=0):
        """Draw image on the screen at specified coordinates."""
        image = image.copy()
        if angle != 0:
            image = p.transform.rotate(image, m.degrees(angle))
        screen.blit(
            image,
            (
                x - image.get_width()/2,
                y - image.get_height()/2
            )
        )
    # end draw_player

    def draw_text(
        screen, x, y, text,
        name='freesansbold.ttf',
        size=35,
        colour=(0, 0, 0),
        angle=0,
    ):
        """Draw text on the screen at specified coordinates."""
        font = p.font.Font(name, size)
        text_obj = font.render(text, True, colour)
        draw_image(screen, text_obj, x, y, angle)
    # end draw_text

    def position(player_x, player_y, x, y):
        """Get coordinates of object relative to player."""
        return (
            SCREEN_WIDTH/2 - player_x + x*64,
            SCREEN_HEIGHT/2 + player_y + y*64
        )
    # end position

    # make pygame constants / variables
    clock = p.time.Clock() # make screen clock

    def main_loop(screen, *args, **kwargs):
        # game variables
        game_exit = False
        game_end = False
        direction_x = 0
        direction_y = 0
        player_bg = True
        background = []
        collideable = []
        breakable = []
        hoverable = []
        texture = {}
        with open('Christmas Adventure Map.txt', mode = 'r') as l:
            land_key = {}
            while True: # get land key
                line = l.readline()
                if line.strip() != '':
                    line = line.split()
                    if len(line) == 1:
                        land_key[line[0]] = 'blank'
                    elif len(line) == 2:
                        land_key[line[0]] = line[1]
                    else:
                        land_key[line[0]] = [line[1]]
                        for rect in line[2:]:
                            try:
                                hitbox = p.Rect(tuple(map(
                                    int, rect.split(sep = '-')
                                )))
                            except:
                                continue
                            bounds = p.Rect(0, 0, 64, 64)
                            if bounds.contains(hitbox):
                                land_key[line[0]].append(hitbox)
                                continue
                            hitbox = hitbox.clip(bounds)
                            if hitbox.area > 0:
                                land_key[line[0]].append(hitbox)
                        # end for
                else:
                    break
            # end while
            for land in (background, collideable, breakable, hoverable):
                while True: # get land
                    line = l.readline().strip()
                    if line != '':
                        land.append([])
                        for item, tile in enumerate(line):
                            key = land_key[tile]
                            if isinstance(key, list):
                                key = key[0]
                            if (
                                land is collideable
                                and key in ('start', 'start-nbg')
                            ):
                                if key[-4:] == '-nbg':
                                    player_bg = False
                                player_x = item*64
                                player_y = len(land[:-1])*-64
                                key = 'blank'
                            land[-1].append(key)
                        # end for
                    else:
                        break
                # end while
            # end for
        # end with
        PLAYER = p.image.load('player.png').convert() # take image
        PLAYER_WIDTH = PLAYER.get_width() # get image width
        PLAYER_HEIGHT = PLAYER.get_height() # get image height
        if player_bg: # remove background if specified
            PLAYER = remove_background(PLAYER)
        for t in land_key.values():
            try:
                key = t
                if isinstance(key, list):
                    key = t[0]
                if key == 'blank':
                    texture[key] = p.Surface((0, 0))
                elif key[-4:] == '-nbg':
                    texture[key] = \
                        p.image.load(key[:-4] + '.png').convert()
                    texture[key] = \
                        remove_background(texture[key])
                else:
                    texture[key] = p.image.load(key + '.png').convert()
                if isinstance(t, list):
                    texture[key] = [texture[key]]
                    texture[key].extend(t[1:])
            except Exception as e:
                print(e)
                try:
                    texture[key] = p.image.load('debug.png').convert()
                    print('Using debug.png as backup')
                except:
                    print('unavailiable texture')
                    sys.exit('unavailiable texture')
        # end for

        # actual loop
        while game_exit is not True:
            # screen colour
            screen.fill(WHITE)

            # event checking
            for event in p.event.get():
                etype = event.type
                if etype == QUIT:
                    # exit program if red x button closed
                    p.quit()
                    return None
                elif etype == KEYDOWN:
                    ekey = event.key
                    if ekey == K_w:
                        direction_y += 1
                    elif ekey == K_a:
                        direction_x -= 1
                    elif ekey == K_s:
                        direction_y -= 1
                    elif ekey == K_d:
                        direction_x += 1
                    elif ekey == K_BACKSLASH:
                        print(
                            background,
                            collideable,
                            breakable,
                            hoverable,
                            land_key,
                            texture,
                            sep = '\n',
                        )
                elif etype == KEYUP:
                    ekey = event.key
                    if ekey == K_w:
                        direction_y += -1
                    elif ekey == K_a:
                        direction_x -= -1
                    elif ekey == K_s:
                        direction_y -= -1
                    elif ekey == K_d:
                        direction_x += -1
            # end for

            # update player
            if direction_x or direction_y:
                land_x = (
                    round((player_x - 32)/64),
                    round((player_x - 32)/64) + 1,
                )
                land_y = (
                    round((-player_y - 32)/64),
                    round((-player_y - 32)/64) + 1,
                )
                if direction_x and direction_y:
                    player_x += direction_x# * (m.sqrt(2)/2)
                else:
                    player_x += direction_x
                for x, y in ((i, j) for i in land_x for j in land_y):
                    px1, py1, px2, py2 = \
                         PLAYER.get_rect()
                    px1 = player_x - 24
                    py1 = -player_y - 24
                    p_rect = p.Rect(px1, py1, px2, py2)
                    try:
                        if isinstance(texture[collideable[y][x]], list):
                            for rect in texture[collideable[y][x]][1:]:
                                t_rect = rect.move(x*64 - 32, y*64 - 32)
                                if p_rect.colliderect(t_rect):
                                    player_x -= direction_x
                                    break
                            # end for
                        else:
                            tx1, ty1, tx2, ty2 = \
                                 texture[collideable[y][x]].get_rect()
                            if tx2 == 0 and ty2 == 0:
                                continue
                            tx1 = x*64 - 33
                            ty1 = y*64 - 33
                            t_rect = p.Rect(tx1, ty1, tx2, ty2)
                            if p_rect.colliderect(t_rect):
                                player_x -= direction_x
                                break
                    except IndexError:
                        pass
                    try:
                        if isinstance(texture[breakable[y][x]], list):
                            for rect in texture[breakable[y][x]][1:]:
                                t_rect = rect.move(x*64 - 32, y*64 - 32)
                                if p_rect.colliderect(t_rect):
                                    player_x -= direction_x
                                    break

                            # end for
                        else:
                            tx1, ty1, tx2, ty2 = \
                                 texture[breakable[y][x]].get_rect()
                            if tx2 == 0 and ty2 == 0:
                                continue
                            tx1 = x*64 - 33
                            ty1 = y*64 - 33
                            t_rect = p.Rect(tx1, ty1, tx2, ty2)
                            if p_rect.colliderect(t_rect):
                                player_x -= direction_x
                                break
                    except IndexError:
                        pass
                # end for
                if direction_x and direction_y:
                    player_y += direction_y# * (m.sqrt(2)/2)
                else:
                    player_y += direction_y
                for x, y in ((i, j) for i in land_x for j in land_y):
                    px1, py1, px2, py2 = \
                         PLAYER.get_rect()
                    px1 = player_x - 24
                    py1 = -player_y - 24
                    p_rect = p.Rect(px1, py1, px2, py2)
                    try:
                        if isinstance(texture[collideable[y][x]], list):
                            for rect in texture[collideable[y][x]][1:]:
                                t_rect = rect.move(x*64 - 32, y*64 - 32)
                            # end for
                        else:
                            tx1, ty1, tx2, ty2 = \
                                 texture[collideable[y][x]].get_rect()
                            if tx2 == 0 and ty2 == 0:
                                continue
                            tx1 = x*64 - 33
                            ty1 = y*64 - 33
                            t_rect = p.Rect(tx1, ty1, tx2, ty2)
                        if p_rect.colliderect(t_rect):
                            player_y -= direction_y
                            break
                    except IndexError:
                        pass
                    try:
                        if isinstance(texture[breakable[y][x]], list):
                            for rect in texture[breakable[y][x]][1:]:
                                t_rect = rect.move(x*64 - 32, y*64 - 32)
                            # end for
                        else:
                            tx1, ty1, tx2, ty2 = \
                                 texture[breakable[y][x]].get_rect()
                            if tx2 == 0 and ty2 == 0:
                                continue
                            tx1 = x*64 - 33
                            ty1 = y*64 - 33
                            t_rect = p.Rect(tx1, ty1, tx2, ty2)
                        if p_rect.colliderect(t_rect):
                            player_y -= direction_y
                            break
                    except IndexError:
                        pass
                # end for

            # draw tiles
            for i, row in (
                *enumerate(background),
                *enumerate(collideable),
                *enumerate(breakable),
            ):
                for j, item in enumerate(row):
                    if item in ('blank', 'start'):
                        continue
                    t = texture[item]
                    if isinstance(t, list):
                        t = t[0]
                    draw_image(
                        screen,
                        t,
                        *position(player_x, player_y, j, i),
                    )
                # end for
            # end for

            # draw player
            draw_image(screen, PLAYER, SCREEN_WIDTH/2, SCREEN_HEIGHT/2)
            try:
                draw_text(
                    screen,
                    *position(player_x, player_y, player_sx, player_sy),
                    'Happy New Year!',
                )
            except:
                player_sx, player_sy = player_x//64, -player_y//64
                draw_text(
                    screen,
                    *position(player_x, player_y, player_sx, player_sy),
                    'Happy New Year!',
                )

            # update screen and wait
            p.display.update()
            clock.tick(60) # 60 fps
        # end while
    # end main_loop

    # run main loop
    main_loop(screen)
# end main

#Prints the current inventory. If the inventory is empty, tells the user. 
def printInventory():
    if len(inventoryList) == 0:
        print("Your pockets are empty!")
    for i in range(0, len(inventoryList)):
        print(inventoryList[i][0] + " : " + str(inventoryList[i][1]))
#End function
    
#Checks if the item is already in the inventory
def alreadyHaveIt(item):
    for i in range(0, len(inventoryList)):
        if inventoryList[i][0] == item:
            return True
    return False
#End function

#Adds the passed item to the inventory
def inventory(item):
    global inventoryList
    if alreadyHaveIt(item) == True:
        for i in range(0, len(inventoryList)):
            if inventoryList[i][0] == item:
                inventoryList[i][1] += 1
    else:
        newItem = []
        newItem.append(item)
        newItem.append(1)
        inventoryList.append(newItem)
#End function

#Print menu of choices, force a valid input, and return their choice as int
def actionMenu():
    print("What will you do?")
    time.sleep(3)
    cont = True
    #Print menu, and force valid input
    while cont:
        try:
            choice = int(input("1 - Check inventory\n2 - Be aggressive\n3 - Be defensive\n4 - Quit"))
            if choice == 4:
                exit()
            elif choice == 1:
                printInventory()
            else:
                return choice
        except ValueError:
            print("That wasn't a smart choice! Try again!")
#End function

#Print menu of choices, force a valid input, and return their choice as int
def movementMenu():
    print("What will you do?")
    cont = True
    #Print menu, and force valid input
    while cont:
        time.sleep(3)
        try:
            choice = int(input("1 - Check inventory\n2 - Turn left\n3 - Turn right\n4 - Go Straight\n5 - Quit"))
            if choice == 5:
                exit()
            elif choice == 1:
                printInventory()
            else:
                return choice
        except ValueError:
            print("That wasn't a smart choice! Try again!")
#End function

#Removes the student from the front of studentList and returns their name as a string
def removeStudent():
    global studentList
    return studentList.pop(0)
#End function

#Removes one unit of the given item from inventory
def removeItem(item):
    global inventoryList
    for i in range(0, len(inventoryList)):
        if inventoryList[i][0] == item:
            if inventoryList[i][1] > 1:
                inventoryList[i][1] -= 1
            else:
                inventoryList.pop(i)

#Check if game is over, and inform player if yes. End program
def gameOver():
    if len(studentList) < 1:
        print("Oh NOOOO! That was your last classmate! You let them ALL DOWN!\nGAME OVER.")
        exit()
#End function
        
'''
def main():
    cont = True #boolean for loops
    global studentList #List of students

    print("It's nearly Christmas! We've been invited to the North Pole by Santa "
          "Himself! Here he comes!")
    time.sleep(2)

##    winsound.PlaySound("Santa Laugh.wav", winsound.SND_FILENAME)

    #Force correct name entry
    while cont:
    
        name = input("Ho Ho Ho! What's your name?")

        #On multiple lines for spacing reasons
        if name == "Giny" or name == "Kamile" or name == "Leah" or name == "Leyla":
            print("Oh. I had asked for the other class... I guess you'll do.")
            cont = False
        elif name == "Harriet" or name == "Saijal" or name == "Noye" or name == "Sharon":
            print("Oh. I had asked for the other class... I guess you'll do.")
            cont = False
        elif name == "Ria" or name == "Sarah" or name == "Maria" or name == "Annie":
            print("Oh. I had asked for the other class... I guess you'll do.")
            cont = False
        elif name == "Katrina" or name == "Vivien" or name == "Blessing":
            print("Oh. I had asked for the other class... I guess you'll do.")
            cont = False

        elif name == "Who laughs like that?":
            print("GAME OVER. Way to make Santa feel awkward.")
            exit()

        else:
            print("Listen, I'm Santa. I'm kind of a big deal. That's not your name.")
    
    #End while

    #Generate list of students
    studentList = ["Giny", "Kamile", "Leah", "Leyla", "Harriet", "Saijal", "Noye", "Sharon", "Ria", "Sarah", "Maria", "Annie", "Blessing", "Vivien", "Katrina"]

    #Remove current player from list
    studentList.remove(name)
    
    #Flavor text
    print("Now, if you'll come this way, Mr. Anthony has prepared a special feast for "
          "us!")

    #more flavor text
    for i in range(0, 2):
        time.sleep(2)
        print("...")
        time.sleep(1)
    #End for

    #Even more flavor text
    print("Almost there! Mind the ga-")
    time.sleep(3)
    print("What on Earth? What are the elves up to? Ow! That one just threw a candy "
          "cane at me! That hurt!")
    time.sleep(4)
    print("The elves are rebelling! Not the face! RUN FOR IT!!!")
    time.sleep(3)
    print("There are dozens of them! They're throwing so many candy canes at us! "
          "We're not going to make it.... EVERY SANTA FOR HIMSELF!")
    time.sleep(3)
    print("With candy canes falling left, right, and center, maybe I could...")

    choice = input("Should I pick up a handful of the candy? (Y/N)")

    #If the user takes the candy it is added to the inventory. If they do not the game ends
    if choice == "N":
        print("You quickly ignore the candy and get back up to run away. As you stand up "
              "a candy cane hits you right in the spleen. Death by candy cane.")
        print("GAME OVER.")
        time.sleep(10)
        exit()
    elif choice == "Y":
        print("Good choice! You place the candy in your pocket.")
        inventory("candy cane")

    cont = True
    while cont:
        choice = actionMenu()
        if choice == 2:
            print("Wow! You sure are angry! In your Hulk-rage you grab your candy cane and throw it at an "
                  "elf. It hits him square on his little elf head and knocks him out! Now run for it!")
            removeItem("candy cane")
            cont = False
            time.sleep(3)
        if(choice == 3):
             print("Being the coward that you are, you try to save yourself. As you run past " + removeStudent()
                   + ", an elf gets a direct hit with one of his evil candy canes. She's blacked out!")
             time.sleep(3)
             gameOver()
             cont = False


    print("Exiting the toy factory, you find yourself in the middle of elf town: The most evil place that ever evil'd!")
    time.sleep(3)

    cont = True
    while cont:
        choice = movementMenu()
        if choice == 2:
            print("Turning left, you walk in to a brick wall. " + removeStudent() + " begins to laugh at you. In the process, she\n"
                  "slips on the ice, begins to slide down a hill, and falls off a cliff out of sight. Well that's unfortunate.")
            cont = False
            time.sleep(3)
            gameOver()
        if(choice == 3):
             print("Turning right, you see the elf horde quickly approaching. You'd best not go that way.")
             time.sleep(3)
        if(choice == 4):
             print("Going straight, you run in to a dead-end. The street is lined with elf huts. Elf huts are like houses, but\n"
                   "with really tiny doors.")
             time.sleep(3)
             cont = False

    cont = True
    while cont:
        choice = actionMenu()
        if choice == 2:
            print("Being the aggressive person that you are, you make your stand and face the elvish horde as they charge upon you!\n"
                  "The elves run straight past, apparently noticing your rather scrawny stature and deciding that " + removeStudent() +
                  " made a more appealing target. That was the last you saw of them before deciding to run away.")
            time.sleep(3)
            gameOver()
            cont = False
        if(choice == 3):
             print("Deciding that facing an army of angry elves isn't what you studied in school, you quickly run in to the nearby\n"
                   " elf hut and close the door behind you. Oh, look at that - you've found some gift-wrapping paper!")
             time.sleep(3)
             inventory("gift wrapping paper")
             cont = False
        
    
    #Time to take over!
    print("Our adventure has only just begun! It's time for you to make this game your own!\n"
          "I have set up this code so that you can do all sorts of things. You can give the player more "
          "choices, add in more scenarios, create new items to use, add new sounds, more menu choices, "
          "and so much more!\nI have put in place a system whereby if all your classmates die, the game is "
          "over. Think of them as 'lives.' There is a header comment in the code to explain the functions\n"
          "Have fun - and Merry Christmas!")
    time.sleep(10000)
#End function
        
'''
if __name__ == '__main__':
    main()
