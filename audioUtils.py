import re
import subprocess
import time
from enum import Enum

import audioMapping

VOLUME_LEVEL_REGEX = r"(^\s{4}Prop:\skey\sSpa:Pod:Object:Param:Props:channelVolumes.*(\r\n|\r|\n))(^\s{6}Array:\schild.*(\r\n|\r|\n))(\s{8}Float\s.*(\r\n|\r|\n))"
MUTE_STATUS_REGEX = r"(^\s{4}Prop:\skey\sSpa:Pod:Object:Param:Props:mute.*(\r\n|\r|\n))(\s{6}Bool\s.*(\r\n|\r|\n))"

# pw-cli set-param <clientID> Props '{ mute: false, channelVolumes: [ 0.98, 0.98 ] }'
# id=$(pw-dump | jq '.[] | select(.type == "PipeWire:Interface:Node") | select(.info.props["application.name"] == "Scream") | .id')
# pw-cli e <clientID> Props
# pw-cli list-objects Port
#
# pw-cli
# wpctl
# pw-dump
# pw-link
#


class Direction(Enum):
    OUT = "out"
    IN = "in"


class Channel(Enum):
    FRONT_LEFT = "FL"
    FRONT_RIGHT = "FR"


def GetNodeID(name: str) -> list[int]:
    try:
        output = subprocess.run(
            [
                f'echo -n $(pw-dump | jq \'.[] | select(.type == "PipeWire:Interface:Node") | select(.info.props["application.name"] == "{name}") | .id\')'
            ],
            shell=True,
            capture_output=True,
        )
        nodes = output.stdout.decode("UTF-8")

        # if application name lookup fails try node name lookup
        if len(nodes.strip()) < 1:
            output = subprocess.run(
                [
                    f'echo -n $(pw-dump | jq \'.[] | select(.type == "PipeWire:Interface:Node") | select(.info.props["node.name"] == "{name}") | .id\')'
                ],
                shell=True,
                capture_output=True,
            )
            nodes = output.stdout.decode("UTF-8")

        # if node name lookup fails try PID lookup
        if len(nodes.strip()) < 1:
            output = subprocess.run(
                [
                    f'echo -n $(pw-dump | jq \'.[] | select(.type == "PipeWire:Interface:Node" or "PipeWire:Interface:Client") | select(.info.props["application.process.id"] == {name}) | .id\')'
                ],
                shell=True,
                capture_output=True,
            )
            nodes = output.stdout.decode("UTF-8")

        if nodes.find(" ") > -1:
            nodesArray = nodes.split(" ")
        else:
            return [int(nodes)]

        # only return the first audio device (audio out) if its discord because the second one is the mic
        if name == "WEBRTC VoiceEngine":
            return [int(nodesArray[0])]

        return list(map(int, nodesArray))
    except:
        return [-1]


def GetNodeFromPID(pid: int) -> list[int]:
    try:
        output = subprocess.run(
            [
                f'echo -n $(pw-dump | jq \'.[] | select(.type == "PipeWire:Interface:Client") | select(.info.props["application.process.id"] == {pid}) | .id\')'
            ],
            shell=True,
            capture_output=True,
        )
        clients = output.stdout.decode("UTF-8")

        if clients.find(" ") > -1:
            clientsArray = clients.split(" ")
        else:
            clientsArray = [int(clients)]

        clientsArray = list(map(int, clientsArray))

        output = subprocess.run(
            [f"pw-cli list-objects Node"],
            shell=True,
            capture_output=True,
        )
        for client in clientsArray:
            regexPattern = _createClientToNodeRegex(client)
            regex = re.compile(regexPattern, re.MULTILINE)
            regexResult = re.findall(regex, output.stdout.decode("UTF-8"))
            if len(regexResult) > 0:
                return [int(regexResult[0][0].split(",")[0][4:])]
    except:
        return [-1]
    return [-1]


def _SetVolume(nodeId: int, volume: int):
    internalVolume = audioMapping.GetFloatValue(volume)
    output = subprocess.run(
        [
            "pw-cli set-param "
            + str(nodeId)
            + " Props '{ mute: false, channelVolumes: ["
            + str(internalVolume)
            + ", "
            + str(internalVolume)
            + "] }'"
        ],
        shell=True,
        capture_output=True,
    )
    # print(output.stdout.decode('UTF-8'))


def SetVolume(nodeId: list[int], volume: int):
    for node in nodeId:
        _SetVolume(node, volume)


def _GetVolume(nodeId: int) -> int:
    output = subprocess.run(
        ["pw-cli e " + str(nodeId) + " Props"], shell=True, capture_output=True
    )
    regex = re.compile(VOLUME_LEVEL_REGEX, re.MULTILINE)
    result = re.findall(regex, output.stdout.decode("UTF-8"))
    audioLevel = result[0][4].strip()
    return audioMapping.GetIntVlaue(float(audioLevel[6:]))


def GetVolume(nodeId: list[int]) -> int:
    return _GetVolume(nodeId[0])


def _GetMuteStatus(nodeId: int) -> bool:
    output = subprocess.run(
        ["pw-cli e " + str(nodeId) + " Props"], shell=True, capture_output=True
    )
    regex = re.compile(MUTE_STATUS_REGEX, re.MULTILINE)
    result = re.findall(regex, output.stdout.decode("UTF-8"))
    muteStatus = result[0][2].strip()
    return muteStatus[5:].lower() == "true"


def GetMuteStatus(nodeId: list[int]) -> bool:
    return _GetMuteStatus(nodeId[0])


def _ToggleMute(nodeId: int):
    output = subprocess.run(
        [
            "pw-cli set-param "
            + str(nodeId)
            + " Props '{ mute: "
            + ("true" if not _GetMuteStatus(nodeId) else "false")
            + "}'"
        ],
        shell=True,
        capture_output=True,
    )
    # print(output.stdout.decode('UTF-8'))


def ToggleMute(nodeId: list[int]):
    for node in nodeId:
        _ToggleMute(node)


def GetDefaultSinkVolume() -> int:
    output = subprocess.run(
        ["pactl get-sink-volume @DEFAULT_SINK@"], shell=True, capture_output=True
    )
    return int(output.stdout.decode("UTF-8").split(" / ")[1][:-1])


def SetDefaultSinkVolume(volume: int):
    output = subprocess.run(
        ["pactl set-sink-volume @DEFAULT_SINK@ " + str(volume) + "%"],
        shell=True,
        capture_output=True,
    )
    # print(output.stdout.decode('UTF-8'))


def ToggleDefaultSinkMute():
    output = subprocess.run(
        ["pactl set-sink-mute @DEFAULT_SINK@ toggle"], shell=True, capture_output=True
    )
    # print(output.stdout.decode('UTF-8'))


def _createChannelRegex(nodeId: int, direction: Direction, channel: Channel) -> str:
    requiredProps = (
        r'((\s{3,}node.id\s=\s"'
        + str(nodeId)
        + r'"$)|(\s{3,}port.direction\s=\s"'
        + direction.value
        + r'"$)|(\s{3,}audio.channel\s=\s"'
        + channel.value
        + r'"$))'
    )
    return (
        r"(^\sid.*$)"
        + r'(\s{3,}(.*")$)*?'
        + requiredProps
        + r'(\s{3,}(.*")$)*?'
        + requiredProps
        + r'(\s{3,}(.*")$)*?'
        + requiredProps
        + r'(\s{3,}(.*")$)+'
    )


def _createClientToNodeRegex(clientId: int) -> str:
    requiredProps = r'((\s{3,}client.id\s=\s"' + str(clientId) + r'"$))'
    return r"(^\sid.*$)" + r'(\s{3,}(.*")$)*?' + requiredProps


def GetChannel(nodeId: int, direction: Direction, channel: Channel) -> int:
    output = subprocess.run(
        ["pw-cli list-objects Port"], shell=True, capture_output=True
    )
    regexPattern = _createChannelRegex(nodeId, direction, channel)
    regex = re.compile(regexPattern, re.MULTILINE)
    regexResult = re.findall(regex, output.stdout.decode("UTF-8"))
    # print(regexResult)
    return regexResult[0][0].split(",")[0][4:]


def RemoveLink(outChannelId: int, inChannelId: int):
    output = subprocess.run(
        [f"pw-link -d {str(outChannelId)} {str(inChannelId)}"],
        shell=True,
        capture_output=True,
    )
    # print(output.stdout.decode('UTF-8'))
    return output.returncode == 0


def CreateLink(outChannelId: int, inChannelId: int):
    output = subprocess.run(
        [f"pw-link {str(outChannelId)} {str(inChannelId)}"],
        shell=True,
        capture_output=True,
    )
    # print(output.stdout.decode('UTF-8'))
    return output.returncode == 0


def createMapping():
    id = GetNodeID("Scream")
    volumeLevel = 100
    oldVolume = 0.001
    volume = 0.0
    while oldVolume > 0:
        volume = GetVolume(id)
        if oldVolume != volume:
            oldVolume = volume
            # print(str(volumeLevel) + ", " + str(volume))
            volumeLevel -= 1
        time.sleep(0.1)


if __name__ == "__main__":
    # GetDefaultSinkVolume()
    # execute only if run as the entry point into the program
    # id = GetNodeID("Scream")
    # ToggleMute(id)
    # ToggleMute(id)
    # GetMuteStatus(id)
    # print(GetVolume(id))
    # SetVolume(id, 50)
    # print(GetVolume(id))
    # SetVolume(id, 26)
    # print(GetVolume(id))
    # createMapping()
    # print(GetNodeID("alsa_output.usb-SteelSeries_Arctis_Nova_Pro_Wireless-00.analog-stereo"))
    # GetChannel(33, Direction.IN, Channel.FRONT_LEFT)
    # CreateLink(46, 45)
    # RemoveLink(46, 45)
    nodeid = GetNodeID("jellyfin-desktop")
    node = GetNodeFromPID(1313553)
    CreateLink(
        GetChannel(nodeid[0], Direction.OUT, Channel.FRONT_LEFT),
        GetChannel(33, Direction.IN, Channel.FRONT_LEFT),
    )
    CreateLink(
        GetChannel(nodeid[0], Direction.OUT, Channel.FRONT_RIGHT),
        GetChannel(33, Direction.IN, Channel.FRONT_RIGHT),
    )

    RemoveLink(
        GetChannel(33, Direction.OUT, Channel.FRONT_LEFT),
        GetChannel(33, Direction.IN, Channel.FRONT_LEFT),
    )
    RemoveLink(
        GetChannel(33, Direction.OUT, Channel.FRONT_RIGHT),
        GetChannel(33, Direction.IN, Channel.FRONT_RIGHT),
    )
