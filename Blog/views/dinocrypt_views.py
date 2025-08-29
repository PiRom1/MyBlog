import json
from django.shortcuts import render, redirect

from Blog.models import *
from django.http import HttpResponse, HttpResponseBadRequest, HttpResponseRedirect, JsonResponse

from django.contrib.auth.decorators import login_required
from django.utils import timezone
from django.template.loader import render_to_string




import numpy as np
import math as m
import random as rd
# import pygame



class DungeonGenerator:


    def __init__(self):
        pass


    def distance(self, a, b):
        '''
        Compute distance between two coordinates in a 2D plan

        a: list, list of x and y coordinates of point A
        b: list, list of x and y coordinates of point B
        '''

        return m.sqrt( (b[0] - a[0])**2 + (b[1] - a[1])**2)



    def generate_room(self, size, stability = 1):
        '''
        Generate a room, in a circular random shape
        We start with a full open squared room.
        Then, the more the cells are far from the center, the higher is the probability of this cell to become a wall.
        This probability is ponderated with the stability factor.

        size: list, list of width and height of the base squared room
        stability: int, ponderates the probability of the cell to turn into a wall. The higher it is, the more square the room is going to be
        '''

        # Base squared open room
        t = np.ones(shape = size)

        # Find center
        center = (int(size[0]/2), int(size[1]/2))


        distance_max = self.distance((0,0), center)
        for i in range(size[0]):
            for j in range(size[1]):
                d = self.distance((i,j), center)
                proba = d / (distance_max * (stability + 0.1))

                if rd.random() <= proba:
                    t[i,j] = 0


        ## Remplir les trous
        # get space table
        size_t = np.zeros_like(t)
        for i in range(size[0]):
            for j in range(size[1]):
                cases_size = self.get_nb_free_adjacent_cells(t, (i,j))
                size_t[i,j] = cases_size

        for i in range(size[0]):
            for j in range(size[1]):
                if size_t[i,j] < np.max(size_t):
                    t[i,j] = 0

        ## Crop table
        x_min = 0
        x_max = size[0]
        y_min = 0
        y_min = size[1]

        # get x_min
        for i in range(size[0] - 1):
            slice = t[i, 0:]
            if np.sum(slice) > 0:
                x_min = i
                break

        # get x_max
        for i in range(size[0] - 1):
            slice = t[size[0] - 1 - i, 0:]
            if np.sum(slice) > 0:
                x_max = size[0] - i
                break

        # get y_min
        for i in range(size[1] - 1):
            slice = t[0:, i]
            if np.sum(slice) > 0:
                y_min = i
                break

        # get y_max
        for i in range(size[1] - 1):
            slice = t[0:, size[1] - 1 - i]
            if np.sum(slice) > 0:
                y_max = size[1] - i
                break



        cropped_t = t[x_min:x_max, y_min:y_max]

        return t, cropped_t


    def add_rooms(self, dungeon, room_size, nb_rooms, stability):
        '''
        Add nb_rooms of size room_size and stability to the dungeon.
        '''

        dungeon_width, dungeon_height = dungeon.shape
        rooms_coords = []

        for i in range(nb_rooms):
            print(f"Génération salle n° {i+1} ...")
            room, cropped_room = self.generate_room(size = room_size, stability = stability)

            x = rd.randint(0, dungeon_width - 1 - cropped_room.shape[1])
            y = rd.randint(0, dungeon_height - 1 - cropped_room.shape[0])

            while np.sum(dungeon[y:(y + cropped_room.shape[0]), x:(x + cropped_room.shape[1])]) > 0:
                x = rd.randint(0, dungeon_width - 1 - cropped_room.shape[1])
                y = rd.randint(0, dungeon_height - 1 - cropped_room.shape[0])

            dungeon[y:(y + cropped_room.shape[0]), x:(x + cropped_room.shape[1])] = cropped_room

            room_coord = (np.where(cropped_room == 1)[0][0], np.where(cropped_room == 1)[1][0])
            dungeon_coord = [y + room_coord[0], x + room_coord[1]]
            rooms_coords.append(dungeon_coord)


        return dungeon, rooms_coords





    def get_nb_free_adjacent_cells(self, t, pos):
        '''
        Function to get the number of free adjacent cases in a table from a certain position

        t : numpy array, table in which you are calculating the free adjacent cells number
        pos : list, list of x and y coordinates
        '''

        def get_cells_to_explore(pos):
            movement = [[1, 0], [-1, 0], [0, 1], [0, -1]]
            positions = []
            for move in movement:
                new_pos = (pos[0] + move[0], pos[1] + move[1])
                if 0 <= new_pos[0] < t.shape[0] and 0 <= new_pos[1] < t.shape[1]:
                    positions.append(new_pos)

            return positions

        # If we are in a wall
        if t[pos] == 0:
            return 0

        # Else : sum initiates at 1
        s = 1

        # Get base cells
        cases_to_explore = get_cells_to_explore(pos)
        explored_cases = [pos]

        # While there remain cells to be explored
        while cases_to_explore:

            case = cases_to_explore.pop()

            if t[case] == 1: # Si sol
                s += 1
                explored_cases.append(case)  # Case explorée

                adjacent_cases = get_cells_to_explore(case)  # Récupérer les cases adjacentes

                for adjacent_case in adjacent_cases:
                    if adjacent_case not in explored_cases and adjacent_case not in cases_to_explore:
                        cases_to_explore.append(adjacent_case)


        return s




    def generate_corridor(self, t, first_coord, second_coord):
        '''
        Add a random corridor in a table t between 2 coordinates

        t: numpy array, the tablme in which you add a corridor
        first_coord: list, list of coordinates where the corridor begins
        second_coord: list, list of coordinates where the corridor ends
        '''

        # While we're not arrived to final position
        while first_coord != second_coord:
            t[*first_coord] = 1

            if rd.random() > 0.5: # x side (horizontal)
                if first_coord[1] < second_coord[1]: # Go toward the destination cell
                    first_coord[1] += 1
                else:
                    first_coord[1] -= 1
            else: # y side (vertical)
                if first_coord[0] < second_coord[0]: # Go toward the destination cell
                    first_coord[0] += 1
                else:
                    first_coord[0] -= 1

        return t


    def add_corridors(self, t, rooms_coords):
        '''
        Add corridors to a table t, from different coords

        t: numpy array, table in which you add corridors
        rooms_coords: list, list of the coordinates of the different rooms
        '''

        first_coord = rooms_coords.pop(0)

        while rooms_coords:
            distances = [self.distance(first_coord, coord) for coord in rooms_coords]

            coord = first_coord.copy()
            t = self.generate_corridor(t, coord, rooms_coords[np.argmin(distances)])   # Add corridor between the two proximal coordinates
            t = self.generate_corridor(t, coord, rooms_coords[np.argmax(distances)])   # Add corridor between the two farest coordinates


            # change coords
            first_coord = rooms_coords[np.argmin(distances)].copy()
            rooms_coords.remove(first_coord)


        return t



    def is_cell_free_for_chest(self, t, coord):
        '''
        Computes if a cell is free for a chest. The cell is free if the chest would not entrave user's movement.
        The algorithm computes whether the cell is free or not by checking the walls all around.
        If there are two sets of walls separated by free cells, then the cell is not free for welcoming a chest.

        t: numpy array, table in which you want to add a chest
        coord: list, list of coordinates where you want to check if a chest is possible here

        returns: bool, True or False, Can this cell accept a chest or not
        '''

        # If current cell is a wall
        if t[*coord] == 0:
            return False


        # The coordinates around coord, arranged in order
        around_coords = [[0, -1], [1, -1], [1, 0], [1, 1], [0, 1], [-1, 1], [-1, 0], [-1, -1]]

        # String that will contain the walls around the cell
        around_walls = ''

        for around_coord in around_coords:
            new_coord = [coord[0] + around_coord[0], coord[1] + around_coord[1]]
            if new_coord[0] < 0 or new_coord[0] >= t.shape[0] or new_coord[1] < 0 or new_coord[1] >= t.shape[1]:
                around_walls += '0'
            else:
                around_walls += str(int(t[*new_coord]))

        # If only free space around the chest
        if '0' not in around_walls:
            return True
        # If only walls around the chest
        if '1' not in around_walls:
            return False

        # Check if the cell is free
        splitted = around_walls.split('1')
        size = len([i for i in splitted if i])
        if size <= 1:
            return True

        return False


    def generate_chests(self, t, nb_chests):
        '''
        Add nb_chests to a table t

        t: numpy array, table in which you add chest
        nb_chests: int, number of chests to add
        '''


        for i in range(nb_chests):
            print(f"Génération du coffre n°{i+1} ...")

            index = rd.randint(0, len(np.where(t == 1)[0]))  # Chose a random cell in the table
            is_case_free = self.is_cell_free_for_chest(t, [np.where(t==1)[0][index], np.where(t==1)[1][index]])
            while not is_case_free:  # Run until we found a free cell
                index = rd.randint(0, len(np.where(t == 1)[0]))
                is_case_free = self.is_cell_free_for_chest(t, [np.where(t==1)[0][index], np.where(t==1)[1][index]])


            t[*[np.where(t==1)[0][index], np.where(t==1)[1][index]]] = 2


        return t






    def generate_dungeon(self, dungeon_size, room_size, nb_rooms, stability, nb_chests):
        '''
        Generate a random dungeon with all the functions up above

        dungeon_size: list, list of width and height of the dungeon
        nb_rooms: int, number of rooms in the dungeon
        stability: float, stability of the rooms
        nb_chests: int, number of chests in the dungeon
        '''

        # Dungeon initialization
        dungeon = np.zeros(dungeon_size)

        ## Build rooms
        rooms_coords = [] # Stock des coordonnées pour construire les couloirs

        dungeon, rooms_coords = self.add_rooms(dungeon, room_size, nb_rooms, stability)
        corridorless_dungeon = dungeon.copy()

        ## Add corridors
        dungeon = self.add_corridors(dungeon, rooms_coords.copy())


        ## Add chests
        chestless_dungeon = dungeon.copy()
        dungeon = self.generate_chests(dungeon, nb_chests)


        return Dungeon(dungeon = dungeon,
                       dungeon_size = dungeon_size,
                       corridorless_dungeon = corridorless_dungeon,
                       chestless_dungeon = chestless_dungeon,
                       room_size = room_size,
                       nb_rooms = nb_rooms,
                       stability = stability,
                       nb_chests = nb_chests,
                       room_coordinates = rooms_coords)





class Dungeon:

    def __init__(self, dungeon, dungeon_size, corridorless_dungeon, chestless_dungeon, room_size, nb_rooms, stability, nb_chests, room_coordinates):

        self.dungeon = dungeon
        self.dungeon_size = dungeon_size
        self.corridorless_dungeon = corridorless_dungeon
        self.chestless_dungeon = chestless_dungeon
        self.room_size = room_size
        self.nb_rooms = nb_rooms
        self.stability = stability
        self.nb_chests = nb_chests
        self.room_coordinates = room_coordinates


    def __str__(self):
        return str(self.dungeon)



    # def show(self, which = None):

    #     # Paramètres du tableau
    #     ROWS, COLS = self.dungeon_size  # dimensions du tableau
    #     CELL_SIZE = 10                  # taille d'une cellule en pixels

    #     # Couleurs
    #     BLACK = (0, 0, 0)
    #     TOMATO = (255, 99, 71)


    #     # Initialisation de Pygame
    #     pygame.init()
    #     screen = pygame.display.set_mode((COLS * CELL_SIZE, ROWS * CELL_SIZE))
    #     pygame.display.set_caption("Affichage Numpy 2D avec Pygame")

    #     running = True
    #     clock = pygame.time.Clock()

    #     if which == 'corridorless':
    #         t = self.corridorless_dungeon
    #     elif which == 'chestless':
    #         t = self.chestless_dungeon
    #     else:
    #         t = self.dungeon

    #     while running:
    #         for event in pygame.event.get():
    #             if event.type == pygame.QUIT:
    #                 running = False

    #         # Affichage du tableau
    #         for row in range(ROWS):
    #             for col in range(COLS):
    #                 if t[row, col] == 1:
    #                     color = TOMATO
    #                 elif t[row, col] == 0:
    #                     color = BLACK
    #                 elif t[row, col] == 2:
    #                     color = '#fe45cc'

    #                 pygame.draw.rect(screen, color,
    #                                 (col * CELL_SIZE, row * CELL_SIZE, CELL_SIZE, CELL_SIZE))

    #         pygame.display.flip()
    #         clock.tick(30)

    #     pygame.quit()




@login_required
def dungeon(request):

        

    dungeon_generator = DungeonGenerator()
    while True:
        try:
            dungeon = dungeon_generator.generate_dungeon(dungeon_size = (100, 100), room_size = (15, 15), nb_rooms = 10, stability = 1, nb_chests = 10)
            print("Donjon géneré avec succès !")
            break
        except:
            print("Erreur lors de la génération du donjon... Tentative de re-géneration en cours.")
    
    start_coord = np.where(dungeon.dungeon == 1)
        
    context = {"dungeon" : json.dumps(dungeon.dungeon.tolist()),
               "start_coord" : [int(start_coord[0][0]), int(start_coord[1][0])]}
    print(context)

    url = "Blog/dinocrypt/dungeon.html"

    return render(request, url, context)
