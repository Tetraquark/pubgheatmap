# pubgheatmap

Create heatmap image of players activity of the match of PLAYERUNKNOWN'S BATTLEGROUNDS.

Heatmap example:

![PUBG activity heatmap](/data/example_heatmap.jpg)

# Requirements

Python 3

- heatmappy
- pubg-python

# How to use

First of all, set yours developer API key to API_KEY in pubgheatmap.py. You can get api key from [PUBG developers web-site](https://developer.playbattlegrounds.com).

Help message:
```
pubgheatmap.py -h
```

Gets heatmap of my last match on the EU server:
```
pubgheatmap.py -p tetraquark -s pc-eu
```