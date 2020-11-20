emoji = "<a:mc_clock:748835359991005215>d>"

emoji = emoji.split(":")

if len(emoji) != 3:
    print("here")
    print("not a valid emoji")

elif not emoji[2].endswith(">"):
    print("here 1")
    print("not a valid emoji")

emoji = emoji[2][:-1]

try:
    int(emoji)

except: 
    print("here 2")
    print("not a valid emoji")

else:
    print(emoji)