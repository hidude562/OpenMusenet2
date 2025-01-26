def toMIDIChannel(inputStr: str):
    channelMap = {
        "%": 0,
        "^": 1,
        "&": 2,
        "*": 3,
        ";": 4,
        ":": 5,
        "'": 6,
        '"': 7,
        ")": 9,
        "{": 10,
        "}": 11,
        "[": 12,
        "]": 13,
        "(": 14
    }

    return channelMap.get(inputStr)

def toAIChannel(inputNum: int):
    channelMap = {
        0: "%",
        1: "^",
        2: "&",
        3: "*",
        4: ";",
        5: ":",
        6: "'",
        7: '"',
        9: ")",
        10: "{",
        11: "}",
        12: "[",
        13: "]",
        14: "(",
    }
    return channelMap.get(inputNum, "(")

def toAIVelocity(inputNum: int):
    velocityMap = {
        48: "!",
        60: "@",
        100: "#",
    }
    for i in velocityMap.keys():
        if inputNum <= i:
            return velocityMap[i]
    return "$"

def toMidiVelocity(inputNum: str):
    velocityMap = {
        "!": 48,
        "@": 60,
        "#": 100,
        "$": 127
    }
    return velocityMap[inputNum]

    return 127

def parseNote(note: str):
    # Numbers are used to delimit symbols
    delimitedNote = []
    strBuilder = ""

    # Add a space to force adding if last token is number
    note += " "

    for token in note:
        if(token.isnumeric()):
            strBuilder += token
        else:
            if(strBuilder != ""):
                delimitedNote.append(strBuilder)
                strBuilder = ""
            if(token != " "):
                delimitedNote.append(token)
    print(delimitedNote)
    return {"start": int(delimitedNote[0]), "velocity": toMidiVelocity(delimitedNote[1]), "length": int(delimitedNote[2]), "track": toMIDIChannel(delimitedNote[3]), "note": int(delimitedNote[4])}
