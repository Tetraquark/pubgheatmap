# pubgheatmap

Create static heatmap image or timed heatmap of players activity of the match of PLAYERUNKNOWN'S BATTLEGROUNDS.

Timed heatmap example:

![PUBG activity timed-heatmap](/data/pubgheatmap_example_timedheatmap.gif)

Static heatmap example:

![PUBG activity static-heatmap](/data/pubgheatmap_example_staticheatmap.jpg)

# Requirements

Python 3

- heatmappy
- pubg-python
- tkinter

# How to use

First of all, set yours developer API key to API_KEY in pubgheatmap.py. You can get api key from [PUBG developers web-site](https://developer.playbattlegrounds.com).

Help message:
```
pubgheatmap.py -h
```

To get a static full players activity heatmap image of my last match on the EU server:
```
pubgheatmap.py -p tetraquark -s pc-eu -o my_static_heatmap.jpg
```

To get a timed heatmap frame of my last match on the EU server:
```
pubgheatmap.py -p tetraquark -s pc-eu -t
```