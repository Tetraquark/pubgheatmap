from pubg_python import PUBG, Shard
from heatmappy import Heatmapper
from PIL import Image

API_KEY = ''

ERANGEL_MAP_IMG_PATH = 'data/img/erangel_map.jpg'
MIRAMAR_MAP_IMG_PATH = 'data/img/miramar_map.jpg'

MAPS_IMGS_PATHS = {'Desert_Main' : MIRAMAR_MAP_IMG_PATH, 'Erangel_Main' : ERANGEL_MAP_IMG_PATH}

def buildHeatMap(pointsList, imgFile_path):
    mapimg = Image.open(imgFile_path)

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
    heatmapImg = buildHeatMap(playersCoords, mapImgPath)

    return heatmapImg

if __name__ == "__main__":
    player_name = 'tetraquark'
    match_number = 0
    out_heatmap_file_name = 'pubgheatmap11.jpg'
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
