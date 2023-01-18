import mido
import os
import time
import pyautogui as pag
pag.PAUSE = 0

def hp_delay(delay_sec: float) -> None:
    """ Delay function in high accuracy, using time.perf_counter(), which is more accurate than time.sleep() """
    _ = time.perf_counter() + delay_sec
    while time.perf_counter() < _:
        pass

mapping = {37: ',', 39: '.', 42: '/', 44: 'num0', 46: 'decimal',
36: 'z', 38: 'x', 40: 'c', 41: 'v', 43: 'b', 45: 'n', 47: 'm',

49: 'k', 51: 'l', 54: ';', 56: 'num2', 58: 'num3',
48: 'a', 50: 's', 52: 'd', 53: 'f', 55: 'g', 57: 'h', 59: 'j',

61: 'i', 63: 'o', 66: 'p', 68: 'num5', 70: 'num6',
60: 'q', 62: 'w', 64: 'e', 65: 'r', 67: 't', 69: 'y', 71: 'u',

73: '8', 75: '9', 78: '0', 80: 'num8', 82: 'num9',
72: '1', 74: '2', 76: '3', 77: '4', 79: '5', 81: '6', 83: '7',

85: 'F8', 87: 'F9', 90: 'F10', 92: 'divide', 94: 'multiply',
84: 'F1', 86: 'F2', 88: 'F3', 89: 'F4', 91: 'F5', 93: 'F6', 95: 'F7', }
note_range = list(mapping.keys())
note_range_min = min(note_range)
note_range_max = max(note_range)

# Choose a file in current directory
print("请选择要演奏的MIDI文件：")
for i, file in enumerate(os.listdir()):
    if file.endswith(".mid"):
        print("{}: {}".format(i, file))
while True:
    try:
        file = input("输入文件编号：")
        if file == "": raise ValueError
        file = int(file)
    except ValueError:
        print("请输入正确的编号。")
    else:
        break
file = os.listdir()[file]

mid = mido.MidiFile(file)
tpb = mid.ticks_per_beat
tempo = None
scores = []

ignored_timbres = [24] # Ignore Perc. and Sound Effects

# Read midi file
for i, track in enumerate(mid.tracks):
    current_track = []
    current_tick = 0
    print("Track {}: {}".format(i, track.name))
    for msg in track:
        print("[INFO]", msg)
        match msg.type:
            case "program_change":
                current_tick += msg.time
                if msg.program in ignored_timbres:
                    print("Ignored timbre:", msg.program)
                    break # Next Track
            case "set_tempo":
                current_tick += msg.time
                scores.append([current_tick, 0, msg.tempo])
                if tempo is None: tempo = msg.tempo
            case "note_on":
                current_tick += msg.time
                if msg.note not in note_range:
                    print("Change:", msg.note)
                    while msg.note > note_range_max:
                        msg.note -= 12
                    while msg.note < note_range_min:
                        msg.note += 12
                scores.append([current_tick, 1, [msg.note]])
            case _: # Other messages
                current_tick += msg.time
    else:
        continue # Next Track

if tempo is None: tempo = 6e7 / int(input("请输入默认速度（BPM）："))
scores = sorted(scores, key=lambda x: x[0])

for i in range(len(scores) - 1, 0, -1):
    # If two msgs are both notes, and they are in the same time
    if scores[i][0] == scores[i - 1][0] and scores[i][1] == 1 and scores[i - 1][1] == 1:
        # Merge them into one
        scores[i - 1][2].extend(scores[i][2])
        del scores[i]
    else: #Either one is note and another is tempo, or they are in different time
        # Calculate time difference
        scores[i][0] -= scores[i - 1][0]



# Countdown 3 seconds
for i in range(3, 0, -1):
    print("将会在{}秒后自动演奏。".format(i))
    hp_delay(1)

print("开始演奏。")
for score in scores:
    # For 0 delay, we don't need to use hp_delay()
    if score[0] != 0:
        hp_delay(score[0] * tempo / tpb / 1e6)

    if score[1] == 0: # Change tempo
        tempo = score[2]
    else: # Play note
        try:
            print("Pressing:", [mapping[note] for note in score[2]])
            pag.press([mapping[note] for note in score[2]])
        except KeyError:
            print("KeyError:", score[2])