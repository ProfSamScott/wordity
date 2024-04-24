import re, random, json
import mysql.connector
from connect import connect
import os
dir_path = os.path.dirname(os.path.realpath(__file__)) + "/"

correct = ":green_square:"
incorrect = ":red_square:"
misplaced = ":yellow_square:"

filenames = {}
filenames["English"] = {}
filenames["English"]["common"] = {4:"words4_3.5.txt", 5:"words5_3.5.txt", 6:"words6_3.5.txt", 7:"words7_3.5.txt"}
filenames["English"]["uncommon"] = {5:"words5_2.8-3.5.txt"}
filenames["English"]["all"] = {4:"words4_1.txt", 5:"words5_1.txt", 6:"words6_1.txt", 7:"words7_1.txt"}

filenames["Spanish"] = {}
filenames["Spanish"]["common"] = {5:"spanish5_3.txt"}
filenames["Spanish"]["all"] = {4:"spanish4_0.txt", 5:"spanish5_0.txt", 6:"spanish6_0.txt", 7:"spanish7_0.txt"}

bigwordlists = {}
for language in filenames:
    bigwordlists[language] = {}
    for length in filenames[language]["all"]:
        bigwordlists[language][length] = set()
        with open(dir_path+filenames[language]["all"][length]) as file:
            for word in file:
                bigwordlists[language][length].add(word.lower().strip())

wordlists = {}
for language in filenames:
    wordlists[language]={}
    for rarity in filenames[language]:
        if rarity=="all":
            continue
        wordlists[language][rarity] = {}
        for length in filenames[language][rarity]:
            wordlists[language][rarity][length]=[]
            with open(dir_path+filenames[language][rarity][length]) as file:
                for word in file:
                    wordlists[language][rarity][length].append(word.lower().strip())

def check_word(word, language="English"):
    try:
        return word in bigwordlists[language][len(word)]
    except:
        return None

def score(word, guess, letters, language="English"):
    """ Both must be lowercase """
    if re.match(r"^[a-z]{"+str(len(word))+r"}$", guess) == None:
        return "**Oops!** Every guess must be of length "+str(len(word))+" and contain only letters.\nSay **/help** if you're having trouble.", letters, False

    global bigwordlists
    if guess not in bigwordlists[language][len(word)]:
        return "**Oops!** '"+guess.capitalize()+"' is not in my word list.\nSay **/help** if you're having trouble.", letters, False

    global correct, incorrect, misplaced

    word = [c for c in word]
    guess = [c for c in guess]
    feedback = [incorrect]*len(word)
    goodletters =[]
    # exact matches
    for i in range(len(guess)):
        if word[i] == guess[i]:
            word[i] = ""
            goodletters.append(guess[i])
            feedback[i] = correct
    # misplaced
    for i in range(len(guess)):
        if feedback[i] == incorrect:
            try:
                j = word.index(guess[i])
                word[j] = ""
                goodletters.append(guess[i])
                feedback[i] = misplaced
            except ValueError:
                pass
    # remove letters
    for i in range(len(guess)):
        if feedback[i] == incorrect and guess[i] not in goodletters:
            try:
                letters.remove(guess[i])
            except ValueError:
                pass

    return feedback, letters, len(goodletters) == len(word)

def make_report(record):
    """ record[0] = length, record[1] = puzzle number, record[2] = language, record[3] = rarity"""
    if record[3] != "custom":
        toprep  = "**"+record[2]+" Puzzle "+str(record[0])+"."+str(record[1])+" ("+str(record[0])+" letters, "+record[3]+")**\n"
        word = wordlists[record[2]][record[3]][record[0]][record[1]]
    else:
        toprep  = "**Custom "+record[2]+" Puzzle ("+str(record[0])+" letters)**\n"
        word = record[1]

    report = ""
    letters = True
    guesses = 0
    for i in range(5, len(record), 2):
        for j in range(len(record[i])):
            if j != 0:
                report += "   "
            report += "`"+record[i][j].upper()+"`"+record[i+1][j]
        report += "\n"
        guesses += 1
        if record[i+1] == [correct]*record[0]:
            report += "\n"+":balloon:"*(6 + 1 - guesses)
            letters = False
            break
        elif guesses == 6:
            report += "\n:boom: || ** "+word.upper()+" ** ||"
            letters = False
            break

    if letters:
        report += "\n` "
        for letter in "qwertyuiop":
            if letter in record[4]:
                report += letter.upper()+" "
            else:
                report += "  "
        report += "\n  "
        for letter in "asdfghjkl":
            if letter in record[4]:
                report += letter.upper()+" "
            else:
                report += "  "
        report += " \n   "
        for letter in "zxcvbnm":
            if letter in record[4]:
                report += letter.upper()+" "
            else:
                report += "  "
        report += "    `"

    return toprep+report

def make_sharable_report(record):
    if record[3] != "custom":
        toprep  = "**"+record[2]+" Puzzle "+str(record[0])+"."+str(record[1])+" ("+str(record[0])+" letters, "+record[3]+")**\n"
        word = wordlists[record[2]][record[3]][record[0]][record[1]]
    else:
        toprep  = "**Custom "+record[2]+" Puzzle ("+str(record[0])+" letters)**\n"
        word = record[1]

    report = ""
    letters = True
    guesses = 0
    for i in range(5, len(record), 2):
        for j in range(len(record[i])):
            report += record[i+1][j]+" "
        report += "\n"
        guesses += 1
        if record[i+1] == [correct]*record[0]:
            report += "\n"+":balloon:"*(6 + 1 - guesses)
            letters = False
            break
        elif guesses == 6:
            report += "\n:boom:"
            letters = False
            break

    if letters:
        report += "\n` "
        for letter in "qwertyuiop":
            if letter in record[4]:
                report += letter.upper()+" "
            else:
                report += "  "
        report += "\n  "
        for letter in "asdfghjkl":
            if letter in record[4]:
                report += letter.upper()+" "
            else:
                report += "  "
        report += " \n   "
        for letter in "zxcvbnm":
            if letter in record[4]:
                report += letter.upper()+" "
            else:
                report += "  "
        report += "    `"

    return toprep+report

def get_report(id, mydb):
    return make_report(get_state(id, mydb)[0])

def get_sharable_report(id, mydb):
    return make_sharable_report(get_state(id, mydb)[0])

def list2str(l):
    s=""
    for e in l:
        s += e
    return s

def get_new_state(id, mydb, size=5, puzzle=-1, word=None, language="English", rarity="common"):
    global wordlists
    mycursor = mydb.cursor()
    # out with the old
    sql = "DELETE FROM wordmeister WHERE id='"+str(id)+"'"
    mycursor.execute(sql)
    mydb.commit()
    # select a new word
    if word == None:
        try:
            if puzzle == -1:
                puzzle = random.randint(0, len(wordlists[language][rarity][size])-1)
            elif puzzle < 0 or puzzle >= len(wordlists[language][rarity][size]):
                return "Sorry, that puzzle id is invalid."
            word = wordlists[language][rarity][size][puzzle]
            record = [size, puzzle, language, rarity, "abcdefghijklmnopqrstuvwxyz"]
        except:
            return "Sorry, I do not have a word list for "+rarity+" "+language+" words of size "+str(size)+"."
    else:
        record = [len(word), word, language, "custom", "abcdefghijklmnopqrstuvwxyz"]
    # in with the new
    sql = "INSERT INTO wordmeister (id, puzzle) VALUES (%s, %s)"
    val = (id, json.dumps(record))
    mycursor.execute(sql, val)
    sql = "UPDATE wordity_counts SET count=count+1 WHERE size="+str(size)+" AND puzzle="+str(puzzle) +" AND language=%s AND rarity=%s"
    mycursor.execute(sql,[language, rarity])
    mydb.commit()
    # return
    return record

def get_state(id, mydb, size=5, puzzle=-1, language="English", rarity="common"):
    global wordlists
    mycursor = mydb.cursor()
    sql = "SELECT puzzle, contributors FROM wordmeister WHERE id='"+str(id)+"'"
    mycursor.execute(sql)
    result = mycursor.fetchone()
    if result == None:
        if puzzle == -1:
            puzzle = random.randint(0, len(wordlists[language][rarity][size])-1)
        elif puzzle < 0 or puzzle >= len(wordlists[language][rarity][size]):
            return "Sorry, that puzzle id is invalid."
        word = wordlists[language][rarity][size][puzzle]
        record = [size, puzzle, language, rarity, "abcdefghijklmnopqrstuvwxyz"]

        sql = "INSERT INTO wordmeister (id, puzzle) VALUES (%s, %s)"
        val = (id, json.dumps(record))
        mycursor.execute(sql, val)
        sql = "UPDATE wordity_counts SET count=count+1 WHERE size="+str(size)+" AND puzzle="+str(puzzle)
        mycursor.execute(sql)
        mydb.commit()
        return record, []

    return json.loads(result[0]), json.loads(result[1])


def one_move(id, guess, mydb, author):
    global wordlists
    record, contributors = get_state(id, mydb)
    if type(record[1]) == int:
        word = wordlists[record[2]][record[3]][record[0]][record[1]]
    else:
        word = record[1]
    feedback, letters, win = score(word, guess, [c for c in record[4]], record[2])
    if type(feedback) == str: #error
        return feedback
    else:
        record.extend([guess, feedback])
        record[4] = list2str(letters)
        if author not in contributors:
            contributors.append(author)
        mycursor = mydb.cursor()
        sql = "UPDATE wordmeister SET puzzle=%s, contributors=%s WHERE id=%s"
        val = (json.dumps(record), json.dumps(list(contributors)), id)
        mycursor.execute(sql, val)
        mydb.commit()

        score_report = ""
        if win:
            game_score = 6 + 2 - (record.index(guess)) // 2
            if type(record[1]) == str:
                score_report = "\n\nScore not recorded (custom puzzle)."
            elif len(contributors) == 1:
                score_report = set_score(author, game_score, record[0], record[1], mydb, record[2], record[3])
            else:
                score_report = "\n\nScore not recorded (cooperative)."
        elif len(record) >= 5 + 2 * 6:
            if type(record[1]) == str:
                score_report = "\n\nScore not recorded (custom puzzle)."
            elif len(contributors) == 1:
                score_report = set_score(author, 0, record[0], record[1], mydb, record[2], record[3])
            else:
                score_report = "\n\nScore not recorded (cooperative)."

    return make_report(record)+score_report

def set_score(author, score, size, puzzle, mydb, language="English", rarity="common"):
    mycursor = mydb.cursor()
    sql = "INSERT INTO wordity_scores (size, puzzle, id, score, language, rarity) VALUES ("+str(size)+","+str(puzzle)+",'"+str(author)+"',"+str(score)+",%s, %s)"
    try:
        mycursor.execute(sql,[language, rarity])
        mydb.commit()
        return "\n\nYour score has been recorded (**/rating**)."
    except:
        return "\n\nScore not recorded (repeat puzzle)."

def history(id, mydb, full = False, language="English", rarity="common"):
    mycursor = mydb.cursor()
    response = "\n**Ratings by Word Size for <@"+str(id)+"> ("+rarity.capitalize()+" "+language+" words)**\n"
    games = False
    dict = {4:":four:", 5:":five:", 6:":six:", 7:":seven:"}
    for size in range(4,8):
        sql="SELECT avg(score), count(score), sum(score) FROM `wordity_scores` WHERE size="+str(size)+" AND id='"+str(id)+"' AND language=%s AND rarity=%s"
        mycursor.execute(sql,[language, rarity])
        avg, count, sum = mycursor.fetchone()
        if avg != None:
            games = True
            avg = float(avg) / 5 * 10
            count = int(count)
            sum = int(sum)
            response += dict[size]
            if int(avg+0.5) == 0:
                response += ":red_square:"
            else:
                squares = 0
                for i in range(int(avg)):
                    response += ":green_square:"
                    squares += 1
                if avg - int(avg) >= 0.7:
                    response += ":yellow_square:"
                    squares += 1
                elif avg - int(avg) >= 0.3:
                    response += ":orange_square:"
            response += " **"+str(round(avg,1))+"**"
            if full:
                response += " ("+str(count)+" word" + ("s, " if count != 1 else ", ") + str(sum) + " balloon" + ("s" if sum != 1 else "") + ")"
            response += "\n"
    if not games:
        response += "Nothing to show! Use /new to start a puzzle."

    return response


def wordity_help():
    return """**Welcome to Wordity!**
I'm thinking of a word. Can you guess it?
I respond to Slash Commands, DMs, replies, and mentions.

DM me for a private game. Otherwise everyone in the channel or thread can guess.

**New Puzzles**
Say **/new** to start a puzzle of size 5.
Say **/new #** to start a puzzle of size #.
Say **/new #.##** to play a specific puzzle.
Say **/custom _____** to start a custom puzzle.

**Game Play**
Say any word to make a move.
Or use the **/guess** slash command
    :red_square: = letter does not appear in the puzzle
    :yellow_square: = letter is in wrong position
    :green_square: = letter is in correct position

**Other Commands**
Say **/progress** to see your progress.
Say **/share** to see sharable progress.
Say **/support** to give back to the bot.
Say **/help** to see this message.

Use this link to invite Wordity to your server: https://discord.com/oauth2/authorize?client_id=932675037767561296&permissions=277025392640&scope=applications.commands%20bot

Come to the support server to chat: https://discord.gg/VFMqPApRVR
"""

def support_message():
    return """**Do you like Wordity?**
Please consider voting, reviewing, or donating.
Vote: https://top.gg/bot/932675037767561296/vote
Review: https://top.gg/bot/932675037767561296
Donate: https://donatebot.io/checkout/932675037767561296
"""

def stats(mydb, language="English", rarity="common"):
    count = {}
    for size in range(4,8):
        mycursor = mydb.cursor()
        sql = "SELECT sum(count) FROM wordity_counts WHERE size="+str(size)+" AND language=%s AND rarity=%s"
        mycursor.execute(sql, [language, rarity])
        count[size] = int(mycursor.fetchone()[0])
    response = language + " "+rarity+" puzzles\n"
    for size in range(4,8):
        response +="Size "+str(size)+": "+str(count[size])+"\n"
    return response
