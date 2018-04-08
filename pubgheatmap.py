from pubg_python import PUBG, Shard
from heatmappy import Heatmapper
from PIL import Image, ImageDraw

API_KEY = ''

ERANGEL_MAP_IMG_PATH = 'data/img/erangel_map.jpg'
MIRAMAR_MAP_IMG_PATH = 'data/img/miramar_map.jpg'

MAPS_IMGS_PATHS = {'Desert_Main' : MIRAMAR_MAP_IMG_PATH, 'Erangel_Main' : ERANGEL_MAP_IMG_PATH}

def buildHeatMap(pointsList, circlesCoordsList, imgFile_path):
    mapimg = Image.open(imgFile_path)

    draw = ImageDraw.Draw(mapimg)
    for coordsAndRadius in circlesCoordsList:
        draw.ellipse([coordsAndRadius[0][0] - coordsAndRadius[1], coordsAndRadius[0][1] - coordsAndRadius[1],
                      coordsAndRadius[0][0] + coordsAndRadius[1], coordsAndRadius[0][1] + coordsAndRadius[1]],
                     outline='white')

    heatmapper = Heatmapper(point_diameter=25, point_strength=0.2, opacity=0.7)
    heatmapImg = heatmapper.heatmap_on_img(pointsList, mapimg)
    return heatmapImg

def getTelemetryPlayersCoords(telemetry):
    player_positions_events = telemetry.events_from_type('LogPlayerPosition')
    coordinatesList = []

    for pke in player_positions_events:
        if pke.elapsed_time > 0:
            x = round(pke.character.location.x / 600)
            y = round(pke.character.location.y / 600)
            coordinatesList.append((x, y))

    return coordinatesList

def getTelemetryMapName(telemetry):
    events = telemetry.events_from_type('LogPlayerPosition')
    return events[0].common.map_name

def getTelemetrySafeZonesLocations(telemetry):
    gameStatesEvents = telemetry.events_from_type('LogGameStatePeriodic')

    # need to select circles because api sends a lot of trash (intermediate circles)
    coordsDict = dict()
    for gs in gameStatesEvents:
        zoneCoords = [round(gs.game_state.safety_zone_position['x']/600), round(gs.game_state.safety_zone_position['y']/600),
                      round(gs.game_state.safety_zone_position['z'])]

        if zoneCoords[0] in coordsDict:
            coordsDict[zoneCoords[0]][0] += 1
        else:
            coordsDict[zoneCoords[0]] = [1, zoneCoords, round(gs.game_state.safety_zone_radius/600)]

    locationsAndRadii = []
    for key in coordsDict.keys():
        value = coordsDict[key]
        if value[0] > 3:
            locationsAndRadii.append((value[1], value[2]))

    return locationsAndRadii

def getMatchHeatmap(match):
    """
    Make a heatmap of players activity of the match.

    :param match: pubg_python.match object
    :return: PIL Image
    """
    asset = match.assets[0]
    telemetry = api.telemetry(asset.url)

    mapName = getTelemetryMapName(telemetry)
    mapImgPath = MAPS_IMGS_PATHS[mapName]

    playersCoords = getTelemetryPlayersCoords(telemetry)
    circlesCoordsAndRadii = getTelemetrySafeZonesLocations(telemetry)

    heatmapImg = buildHeatMap(playersCoords, circlesCoordsAndRadii, mapImgPath)

    return heatmapImg

if __name__ == "__main__":
    player_name = 'tetraquark'
    match_number = 2
    out_heatmap_file_name = 'pubgheatmap58.jpg'
    server = Shard.PC_EU

    api = PUBG(API_KEY, server)

    # get required player
    players = api.players().filter(player_names=[player_name])
    myPlayer = players[0]

    # get the last player matches
    mathcesIdList = [match.id for match in myPlayer.matches]
    # get required match object
    match = api.matches().get(mathcesIdList[match_number])

    # get match heatmap (PIL image file)
    heatmapImg = getMatchHeatmap(match=match)

    # save image to the file
    heatmapImg.save(out_heatmap_file_name)
