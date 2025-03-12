import mido
import utils
import copy

# Mido objects, but with extra capibility added for OpenMusenet things
class MIDI(mido.MidiFile):
    def __init__(self, filePath=""):
        if(filePath != ""):
            super().__init__(filePath)
        else:
            super().__init__()
            track = mido.MidiTrack()
            self.tracks.append(track)
        self._changeToTicksPerBeat(480)

    def _changeToTicksPerBeat(self, newTPB):
        for i, track in enumerate(self.tracks):
            for msg in track:
                msg.time = round(msg.time * (float(newTPB) / float(self.ticks_per_beat)))
        self.ticks_per_beat = newTPB

    """
    Get the MIDI in the format that the AI (OpenMusenet3) can understand
    """
    def _getAIFormat(self):
        class _Note:
            def __init__(self, msgOn, msgOff):
                self.note = msgOn.note
                self.length = msgOff.time - msgOn.time
                self.start = msgOn.time
                self.velocity = msgOn.velocity
                self.channel = msgOn.channel
                self.markedDuplicate = False

            def getChannelStrChar(self):
                return utils.toAIChannel(self.channel)

            def getDynamicsStrChar(self):
                return utils.toAIVelocity(self.velocity)

        class Notes:
            def __init__(self):
                self.notes = []

            def add(self, note):
                self.notes.append(note)
            """
            Convert to the AI's format,
            Also removes duplicate notes here (Notes with same channel that happen at the same time)
            """
            def toAIformat(self):
                aiStr = ""
                self.sort_notes()
                previousNoteStart = 0
                currentTimeNotes = []
                previousStartTimeGreaterThan0 = 0
                notesLen = len(self.notes)
                for noteIndex in range(notesLen):
                    note = self.notes[noteIndex]
                    for otherNote in currentTimeNotes:
                        if otherNote.note == note.note and round(otherNote.start) == round(note.start) and (
                                otherNote.channel == note.channel or (note.channel > 13 and otherNote.channel > 13)):  #
                            if (not otherNote.markedDuplicate):
                                if (otherNote.length > note.length):
                                    note.markedDuplicate = True
                                else:
                                    otherNote.markedDuplicate = True

                    if note.start == previousNoteStart:
                        currentTimeNotes.append(note)
                    if note.start != previousNoteStart or noteIndex == notesLen - 1:
                        currentTimeNoteTimeKeeper = previousStartTimeGreaterThan0
                        for currentTimeNote in currentTimeNotes:
                            if (not currentTimeNote.markedDuplicate):
                                noteStr = \
                                    (str(round(currentTimeNote.start - currentTimeNoteTimeKeeper)) + str(
                                        currentTimeNote.getDynamicsStrChar()) + str(
                                        round(currentTimeNote.length)) + str(currentTimeNote.getChannelStrChar()) + str(
                                        currentTimeNote.note))
                                currentTimeNoteTimeKeeper = currentTimeNote.start
                                aiStr += noteStr + "|"
                        currentTimeNotes = [note]
                        # When the time increases from the previous note more than 0, like 240, it will reset the currentTimeNotes to just the current note since it is the start
                        previousStartTimeGreaterThan0 = previousNoteStart
                    previousNoteStart = note.start
                return aiStr

            def sort_notes(self):
                self.notes = sorted(self.notes, key=lambda note: note.start)

        tracksCopy = copy.deepcopy(self.tracks)
        notesOnCount = 0
        tempo = 0
        tickMultiplier = 480 / self.ticks_per_beat
        absoluteTime = 0
        notesOn = []
        notesIntermediateFormat = Notes()



        for i, track in enumerate(self.tracks):
            for msg in track:
                if str(type(msg)) == "<class 'mido.messages.messages.Message'>":
                    if msg.type == "note_off" or getattr(msg, "velocity", None) == 0:
                        msg.time = msg.time * tickMultiplier
                        absoluteTime += msg.time
                        msg.time = absoluteTime
                        for noteOn in range(len(notesOn) - 1, -1, -1):
                            if notesOn[noteOn].channel == msg.channel:
                                if notesOn[noteOn].note == msg.note:
                                    note = _Note(notesOn[noteOn], msg)
                                    notesIntermediateFormat.add(note)
                                    notesOn.pop(noteOn)
                                    break
                        notesOnCount -= 1
                    elif msg.type == "note_on":
                        msg.time = msg.time * tickMultiplier
                        absoluteTime += msg.time
                        msg.time = absoluteTime
                        notesOn.append(msg)
                        notesOnCount += 1
                    elif msg.type == "program_change":
                        absoluteTime += msg.time * tickMultiplier
                    else:
                        try:
                            absoluteTime += msg.time * tickMultiplier
                        except:
                            pass
                else:
                    if msg.type == "track_name":
                        absoluteTime = msg.time * tickMultiplier
                    elif msg.type == "end_of_track":
                        absoluteTime = 0
                    else:
                        try:
                            absoluteTime += msg.time * tickMultiplier
                        except:
                            pass
        self.tracks = tracksCopy
        return notesIntermediateFormat.toAIformat()
    """
    Convert string of notes by AI into MIDO messages
    """

    def _getMostRecentNoteOnEventTick(self):
        mostRecentTick = 0
        for i, track in enumerate(self.tracks):
            for msg in track:
                if(msg.type == "note_on"):
                    if msg.time > mostRecentTick:
                        mostRecentTick = msg.time
        return mostRecentTick

    def createTrackIfNotExist(self, index):
        if len(self.tracks) <= index:
            for i in range(index - len(self.tracks) + 1):
                track = mido.MidiTrack()
                track.append(mido.MetaMessage('track_name', name='Test', time=0))
                #track.append(mido.MetaMessage('end_of_track', time=0))
                self.tracks.append(track)

    """
    Pretends all events are absolute
    """
    def _convertAllToAbsoluteTicks(self):
        absoluteTime = 0
        for i, track in enumerate(self.tracks):
            for msg in track:
                if msg.type == "track_name":
                    absoluteTime = msg.time
                    msg.time = absoluteTime
                elif msg.type == "end_of_track":
                    absoluteTime = 0
                else:
                    absoluteTime += msg.time
                    msg.time = absoluteTime

    """
        Assuming events are all absolute, convert them to the normal mido delta time
    """

    def _convertAllToDeltaTicks(self):
        relativeTime = 0
        previousTime = 0
        for i, track in enumerate(self.tracks):
            for msg in track:
                if msg.type == "track_name":
                    relativeTime = msg.time
                elif msg.type == "end_of_track":
                    relativeTime = msg.time
                else:
                    relativeTime = msg.time - previousTime
                previousTime = msg.time
                msg.time = relativeTime

    def _castTimesToInts(self):
        for track in self.tracks:
            for msg in track:
                msg.time = int(msg.time)

    def _appendAIToSelf(self, aiNotes):
        def _AIToMessage(aiNote: str):
            delimited = utils.parseNote(aiNote)
            return [
                mido.Message('note_on', note=delimited["note"], channel=delimited["track"],
                             velocity=delimited["velocity"], time=0),
                mido.Message('note_off', note=delimited["note"], channel=delimited["track"], velocity=0,
                             time=delimited["length"])
            ]

        self._convertAllToAbsoluteTicks()

        splitAINotes = aiNotes.split("|")
        events = []
        current_time = self._getMostRecentNoteOnEventTick()

        for aiNote in splitAINotes:
            if aiNote != "":
                note_events = _AIToMessage(aiNote)
                delimited = utils.parseNote(aiNote)

                # Adjust timing for note_on
                note_events[0].time = delimited["start"] + current_time
                note_events[1].time = delimited["start"] + delimited["length"] + current_time
                current_time += delimited["start"]

                # Add note_on event
                events.append(note_events[0])

                # Add note_off event
                events.append(note_events[1])

        # Sort events by time
        events.sort(key=lambda x: x.time)

        # Add events to the MIDI file
        for event in events:
            self.createTrackIfNotExist(event.channel)

            i = -1
            if(len(self.tracks[event.channel]) != 0):
                while self.tracks[event.channel][i].time > event.time or self.tracks[event.channel][i].type == "end_of_track":
                    i-=1
            if(i == -1):
                self.tracks[event.channel].append(event)
            else:
                self.tracks[event.channel].insert(i+1, event)

        self._convertAllToDeltaTicks()
