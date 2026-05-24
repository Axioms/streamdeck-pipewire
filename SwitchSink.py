import subprocess
import sys

import audioUtils

GAME_SINK_NAME = "game_sink"
DEFAULT_SINK_NAME = (
    "easyeffects_sink"
)


def GetWindowPid() -> int:
    # hyprctl activewindow -j | jq ".pid"

    output = subprocess.run(
        ['hyprctl activewindow -j | jq ".pid"'], shell=True, capture_output=True
    )

    return int(output.stdout.decode("UTF-8"))


if __name__ == "__main__":
    option = sys.argv[1]
    gameNode = audioUtils.GetNodeID(GAME_SINK_NAME)
    defaultNode = audioUtils.GetNodeID(DEFAULT_SINK_NAME)

    match option:
        case "SinkToSink":
            Game_FL = audioUtils.GetChannel(gameNode[0], audioUtils.Direction.OUT, audioUtils.Channel.FRONT_LEFT)
            Game_FR = audioUtils.GetChannel(gameNode[0], audioUtils.Direction.OUT, audioUtils.Channel.FRONT_RIGHT)

            Default_FL = audioUtils.GetChannel(defaultNode[0], audioUtils.Direction.IN, audioUtils.Channel.FRONT_LEFT)
            Default_FR = audioUtils.GetChannel(defaultNode[0], audioUtils.Direction.IN, audioUtils.Channel.FRONT_RIGHT)

            audioUtils.CreateLink(Game_FL, Default_FL)
            audioUtils.CreateLink(Game_FR, Default_FR)
        case "AppToSink":
                gameAppNode = audioUtils.GetNodeFromPID(GetWindowPid())

                defaultNode = audioUtils.GetNodeID(DEFAULT_SINK_NAME)
                Default_FL = audioUtils.GetChannel(defaultNode[0], audioUtils.Direction.IN, audioUtils.Channel.FRONT_LEFT)
                Default_FR = audioUtils.GetChannel(defaultNode[0], audioUtils.Direction.IN, audioUtils.Channel.FRONT_RIGHT)

                GameApp_FL = audioUtils.GetChannel(gameAppNode[0], audioUtils.Direction.OUT, audioUtils.Channel.FRONT_LEFT)
                GameApp_FR = audioUtils.GetChannel(gameAppNode[0], audioUtils.Direction.OUT, audioUtils.Channel.FRONT_RIGHT)

                Default_FL = audioUtils.GetChannel(defaultNode[0], audioUtils.Direction.IN, audioUtils.Channel.FRONT_LEFT)
                Default_FR = audioUtils.GetChannel(defaultNode[0], audioUtils.Direction.IN, audioUtils.Channel.FRONT_RIGHT)

                Game_FL = audioUtils.GetChannel(gameNode[0], audioUtils.Direction.IN, audioUtils.Channel.FRONT_LEFT)
                Game_FR = audioUtils.GetChannel(gameNode[0], audioUtils.Direction.IN, audioUtils.Channel.FRONT_RIGHT)

                audioUtils.RemoveLink(GameApp_FL, Default_FL)
                audioUtils.RemoveLink(GameApp_FR, Default_FR)

                audioUtils.CreateLink(GameApp_FL, Game_FL)
                audioUtils.CreateLink(GameApp_FR, Game_FR)
        case _:
            sys.exit(-1)
