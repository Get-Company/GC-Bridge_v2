from gtts import gTTS

import os


def speak():
    mytext = "1 Name oder Begriff auf dem Orgareiter, kennzeichnen klar und eindeutig die Akte und somit gleichzeitig den Inhalt. 2 Position der Reiter, welche systematisch gestaffelt sind, A (hinten) Z (vorne). Somit haben Sie alle Begriffe mit dem gleichen Anfangsbuchstaben immer hintereinander. 3 Farben bieten eine zusätzliche Strukturmöglichkeit um Bereiche, Sachgebiete, Regionen, Abteilungen oder  Wirtschaftsjahre optisch besser zu untergliedern. 4 Leitbereiche oder Untergruppen unterteilt mit Leitkarten ermöglichen eine weitere feine Gliederung innerhalb eines Bereiches, Fach- oder Sachgebietes."

    language = "de"

    myobj = gTTS(text=mytext, lang=language, slow=False)

    myobj.save("text.mp3")

    os.system("start text.mp3")
