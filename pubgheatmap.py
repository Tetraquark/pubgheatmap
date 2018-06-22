from pubg_python import PUBG, Shard
from heatmappy import Heatmapper
from PIL import Image, ImageDraw, ImageTk
from collections import defaultdict
import sys, getopt
import math
import random

from slider_gallery_frame import SliderGalleryFrame
import tkinter as tk

API_KEY = ''

ERANGEL_MAP_IMG_PATH = 'data/img/erangel_map.jpg'
MIRAMAR_MAP_IMG_PATH = 'data/img/miramar_map.jpg'
SANHOK_MAP_IMG_PATH = 'data/img/sanhok_map.jpg'

MAPS_IMGS_PATHS = {'Desert_Main' : MIRAMAR_MAP_IMG_PATH, 'Erangel_Main' : ERANGEL_MAP_IMG_PATH, "Savage_Main" : SANHOK_MAP_IMG_PATH}

MAP_SCALE_COEFFS = {'Desert_Main' : 600, 'Erangel_Main' : 600, "Savage_Main" : 300}

PLANE_PATH_HEIGHT = 150080

def buildHeatMap(pointsList, circlesCoordsList, planePath, imgFile_path):
    mapimg = Image.open(imgFile_path)

    draw = ImageDraw.Draw(mapimg)

    # draw line of plane moving
    if len(planePath) == 2 and planePath[0] is not None and planePath[1] is not None:
        length = 2000
        starty = planePath[0][1] - length * math.sin(planePath[1])
        startx = planePath[0][0] - length * math.cos(planePath[1])
        endy = planePath[0][1] + length * math.sin(planePath[1])
        endx = planePath[0][0] + length * math.cos(planePath[1])
        draw.line(xy=[(startx, starty), (endx, endy)], width=3, fill=(0, 255, 255))

    for coordsAndRadius in circlesCoordsList:
        draw.ellipse([coordsAndRadius[0][0] - coordsAndRadius[1], coordsAndRadius[0][1] - coordsAndRadius[1],
                      coordsAndRadius[0][0] + coordsAndRadius[1], coordsAndRadius[0][1] + coordsAndRadius[1]],
                     outline='white')

    heatmapper = Heatmapper(point_diameter=25, point_strength=0.3, opacity=0.7)
    heatmapImg = heatmapper.heatmap_on_img(pointsList, mapimg)
    return heatmapImg

def getTelemetryPlayersCoords(telemetry, scale_coeff):
    player_positions_events = telemetry.events_from_type('LogPlayerPosition')
    coordinatesList = []

    for pke in player_positions_events:
        if pke.elapsed_time > 0:
            x = round(pke.character.location.x / scale_coeff)
            y = round(pke.character.location.y / scale_coeff)
            coordinatesList.append((x, y))

    return coordinatesList

def getTelemetryMapName(telemetry):
    events = telemetry.events_from_type('LogPlayerPosition')
    return events[random.randint(0, len(events))].common.map_name

def getTelemetrySafeZonesLocations(telemetry, scale_coeff):
    gameStatesEvents = telemetry.events_from_type('LogGameStatePeriodic')

    # need to select circles because api sends a lot of trash (intermediate circles)
    coordsDict = dict()
    for gs in gameStatesEvents:
        zoneCoords = [round(gs.game_state.safety_zone_position['x'] / scale_coeff),
                      round(gs.game_state.safety_zone_position['y'] / scale_coeff),
                      round(gs.game_state.safety_zone_position['z'])]

        if zoneCoords[0] in coordsDict:
            coordsDict[zoneCoords[0]][0] += 1
        else:
            coordsDict[zoneCoords[0]] = [1, zoneCoords, round(
                gs.game_state.safety_zone_radius / scale_coeff)]

    locationsAndRadii = []
    for key in coordsDict.keys():
        value = coordsDict[key]
        if value[0] > 4:
            locationsAndRadii.append((value[1], value[2]))

    return locationsAndRadii

def getTelemetryPlayersCoordsByTime(telemetry, scale_coeff):
    player_positions_events = telemetry.events_from_type('LogPlayerPosition')
    coordinatesDictByTime = defaultdict(list)

    for pke in player_positions_events:
        if pke.elapsed_time > 0:
            x = round(pke.character.location.x / scale_coeff)
            y = round(pke.character.location.y / scale_coeff)
            coordinatesDictByTime[pke.elapsed_time].append((x, y))

    return coordinatesDictByTime

def getTelemetrySafeZonesLocationsByTime(telemetry, scale_coeff):
    gameStatesEvents = telemetry.events_from_type('LogGameStatePeriodic')

    zonesDictByTime = dict()
    for gs in gameStatesEvents:
        zoneCoords = [round(gs.game_state.safety_zone_position['x'] / scale_coeff),
                      round(gs.game_state.safety_zone_position['y'] / scale_coeff),
                      round(gs.game_state.safety_zone_position['z'])]

        zonesDictByTime[gs.game_state.elapsed_time] = [zoneCoords, round(gs.game_state.safety_zone_radius / scale_coeff)]

    return zonesDictByTime

def getTelemetryRedZonesLocationsByTime(telemetry, scale_coeff):
    gameStatesEvents = telemetry.events_from_type('LogGameStatePeriodic')

    zonesDictByTime = dict()
    for gs in gameStatesEvents:
        zoneCoords = [round(gs.game_state.red_zone_position['x'] / scale_coeff),
                      round(gs.game_state.red_zone_position['y'] / scale_coeff)]

        zonesDictByTime[gs.game_state.elapsed_time] = [zoneCoords, round(gs.game_state.red_zone_radius / scale_coeff)]

    return zonesDictByTime

def getTelemetryPlanePath(telemetry, scale_coeff):
    player_positions_events = telemetry.events_from_type('LogPlayerPosition')

    positions_on_plane = [pos for pos in player_positions_events if
                          pos.character.location.z >= PLANE_PATH_HEIGHT and pos.character.location.z <= PLANE_PATH_HEIGHT + 15]

    x0 = positions_on_plane[0].character.location.x
    y0 = positions_on_plane[0].character.location.y
    x1 = positions_on_plane[-1].character.location.x
    y1 = positions_on_plane[-1].character.location.y

    angle = math.atan2(y1 - y0, x1 - x0)

    return [(round(x0 / scale_coeff), round(y0 / scale_coeff)), angle]

def buildTimedHeatMap(pointsList, circlesCoords, redCoords, planePath, imgFile_path):
    mapimg = Image.open(imgFile_path).convert('RGBA')

    game_events_image = Image.new('RGBA', mapimg.size, (255,255,255,0))
    draw = ImageDraw.Draw(game_events_image)

    if redCoords[1] > 0:
        draw.ellipse([redCoords[0][0] - redCoords[1], redCoords[0][1] - redCoords[1],
                      redCoords[0][0] + redCoords[1], redCoords[0][1] + redCoords[1]],
                     fill=(255, 0, 0, 50))

    # draw line of plane moving
    if len(planePath) == 2 and planePath[0] is not None and planePath[1] is not None:
        length = 2000
        starty = planePath[0][1] - length * math.sin(planePath[1])
        startx = planePath[0][0] - length * math.cos(planePath[1])
        endy = planePath[0][1] + length * math.sin(planePath[1])
        endx = planePath[0][0] + length * math.cos(planePath[1])
        draw.line(xy=[(startx, starty), (endx, endy)], width=3, fill=(0, 255, 255))

    draw.ellipse([circlesCoords[0][0] - circlesCoords[1], circlesCoords[0][1] - circlesCoords[1],
                  circlesCoords[0][0] + circlesCoords[1], circlesCoords[0][1] + circlesCoords[1]],
                 outline='white')

    mapimg = Image.alpha_composite(mapimg, game_events_image)

    heatmapper = Heatmapper(point_diameter=25, point_strength=0.5, opacity=0.7)
    heatmapImg = heatmapper.heatmap_on_img(pointsList, mapimg)
    return heatmapImg

def getMatchHeatmap(api, match):
    """
    Make a heatmap of players activity of the match.

    :param match: pubg_python.match object
    :return: PIL Image
    """
    asset = match.assets[0]
    telemetry = api.telemetry(asset.url)

    mapName = match.map
    while mapName == '':
        mapName = getTelemetryMapName(telemetry)

    mapImgPath = MAPS_IMGS_PATHS[mapName]
    mapScaleCoeff = MAP_SCALE_COEFFS[mapName]

    playersCoords = getTelemetryPlayersCoords(telemetry, mapScaleCoeff)
    circlesCoordsAndRadii = getTelemetrySafeZonesLocations(telemetry, mapScaleCoeff)
    planePath = getTelemetryPlanePath(telemetry, mapScaleCoeff)

    heatmapImg = buildHeatMap(playersCoords, circlesCoordsAndRadii, planePath, mapImgPath)

    return heatmapImg

def getMatchTimedHeatmap(api, match):
    """
    Make a heatmap of players activity of the match distributed by time.

    :param match: pubg_python.match object
    :return: list of tuples (int, PIL Image)
    """
    asset = match.assets[0]
    telemetry = api.telemetry(asset.url)

    mapName = match.map
    while mapName == '':
        mapName = getTelemetryMapName(telemetry)

    mapImgPath = MAPS_IMGS_PATHS[mapName]
    mapScaleCoeff = MAP_SCALE_COEFFS[mapName]

    playersCoords = getTelemetryPlayersCoordsByTime(telemetry, mapScaleCoeff)
    circlesCoordsAndRadii = getTelemetrySafeZonesLocationsByTime(telemetry, mapScaleCoeff)
    redCoordsAndRadii = getTelemetryRedZonesLocationsByTime(telemetry, mapScaleCoeff)
    planePath = getTelemetryPlanePath(telemetry, mapScaleCoeff)

    heatmapImgs = []
    prevTime = 1
    # generate map for every game periodic tick
    for time, _ in sorted(circlesCoordsAndRadii.items()):
        repackedPlayerCoords = []
        # adjust frequent player coords updates to game periodic ticks
        for t in range(prevTime, time):
            if t in playersCoords:
                for coordinates in playersCoords[t]:
                    repackedPlayerCoords.append(coordinates)
        heatmapImg = buildTimedHeatMap(repackedPlayerCoords, circlesCoordsAndRadii[time], redCoordsAndRadii[time], planePath, mapImgPath)
        heatmapImgs.append((time, heatmapImg))
        prevTime = time

    return heatmapImgs

def main(argv):
    player_name = ''
    server = None
    out_heatmap_file_name = ''
    timed = False

    match_number = 0

    try:
        opts, args = getopt.getopt(argv,"hp:s:o:m:t",["playername=","server=","outputfile=","match=","timed"])
    except getopt.GetoptError:
        print('pubgheatmap.py -p <playername> -s <server> [-t] [-o <outputfile>]')
        sys.exit(2)
    for opt, arg in opts:
        if opt == '-h':
            print('pubgheatmap.py -p <playername> -s <server> [-t/--timed] [-o <outputfile>]')
            print('Allowed servers: pc-as, pc-eu, pc-krjp, pc-na, pc-oc, pc-sa, pc-sea')
            print('Example of a static match heatmap: pubgheatmap.py -p tetraquark -s pc-eu -o heatmap.jpg')
            print('Example of a temporal heatmap: pubgheatmap.py -p tetraquark -s pc-eu -t')
            print('In temporal heatmap frame, you can use the left or right arrow keys to rewind.')
            print('')
            sys.exit()
        elif opt in ("-p", "--playername"):
            player_name = arg
        elif opt in ("-s", "--server"):
            server = Shard(arg)
        elif opt in ("-o", "--outputfile"):
            out_heatmap_file_name = arg
        elif opt in ("-m", "--match"):
            match_number = int(arg)
        elif opt in ("-t", "--timed"):
            timed = True


    if not player_name or server is None:
        print('Forgot to enter the player name or server.')
        print('pubgheatmap.py -p <playername> -s <server> -o <outputfile>')
        sys.exit(2)

    print('Trying to get data from PUBG servers.')

    api = PUBG(API_KEY, server)

    # get required player
    players = api.players().filter(player_names=[player_name])
    myPlayer = players[0]

    # get the last player matches
    mathcesIdList = [match.id for match in myPlayer.matches]
    # get required match object
    match = api.matches().get(mathcesIdList[match_number])

    print('Done.')

    if not timed:
        print('Trying to build the match heatmap.')
        # get match heatmap (PIL image file)
        heatmapImg = getMatchHeatmap(api=api, match=match)

        # save image to the file
        if not out_heatmap_file_name:
            out_heatmap_file_name = mathcesIdList[match_number] + '_heatmap.jpg'

        print('Heatmap built. Saving to file', out_heatmap_file_name)

        heatmapImg.save(out_heatmap_file_name)

        print('Done.')
    else:
        print('Trying to build the match heatmaps.')
        # get match heatmaps
        heatmapImgs = getMatchTimedHeatmap(api=api, match=match)

        root = tk.Tk()
        root.title("pubgheatmap - temporal hitmap")

        heatmapsPhotoImgsList = []

        final_img_size = root.winfo_screenheight() - 20  # 20px for slider
        if heatmapImgs[0][1].size[0] > final_img_size or heatmapImgs[0][1].size[1] > final_img_size:
            for time, heatmapImg in heatmapImgs:
                heatmapsPhotoImgsList.append(ImageTk.PhotoImage(
                    heatmapImg.resize((final_img_size, final_img_size), Image.ANTIALIAS)))
        else:
            for time, heatmapImg in heatmapImgs:
                heatmapsPhotoImgsList.append(ImageTk.PhotoImage(heatmapImg))
        # Launching an image gallery with a slider
        sliderGalleryFrame = SliderGalleryFrame(root, heatmapsPhotoImgsList, final_img_size)
        sliderGalleryFrame.mainloop()

        print('Done.')

if __name__ == "__main__":
    main(sys.argv[1:])
