from pathlib import Path
import PyPDF2
import re
import pandas as pd


def ReadPDFfileLineByLine(path):
    reader = PyPDF2.PdfReader(path + '/' + doc)
    # print the text of the first page
    texts = []
    lists =[]
    for i in  range(len(reader.pages)):
       texts.append(reader.pages[i].extract_text() )

    for text in texts:
       text = text.replace('\t', ' ')
       text = text.replace('\n', ' ')
       # Replace dots between numbers with slashes
       text = re.sub(r'(?<=\d)\.(?=\d)', '/', text)
       text = re.sub(r'\s+', ' ', text)
       text = re.sub(r'\t+', ' ', text)
       lines = text.split('.')
       # Process each line
       for line in lines:
          if(len(line) > 3):
              lists.append(line)

    df = pd.DataFrame({'text': lists})
    return df

def ReadPDF(path):
    
    # Open the PDF file
   with open(path, 'rb') as file:
       # Initialize PDF reader
       reader = PyPDF2.PdfReader(file)
    
       # Iterate through pages and extract text
       text = ""
       for page in reader.pages:
           text += page.extract_text()       
           text = text.replace('\t', ' ')
           text = text.replace('\n', ' ')
            # Replace dots between numbers with slashes
           text = re.sub(r'(?<=\d)\.(?=\d)', '/', text)
           text = re.sub(r'\s+', ' ', text)
           text = re.sub(r'\t+', ' ', text)

   return text

#---------------------------------------------------------------------------------------------------------------------------

# Step 1: Define a dictionary for number words to their numeric equivalents
number_words = {
    "one": 1, "a": 1, "two": 2, "three": 3, "four": 4, "five": 5, 
    "six": 6, "seven": 7, "eight": 8, "nine": 9, "ten": 10,
    "eleven": 11, "twelve": 12, "thirteen": 13, "fourteen": 14, 
    "fifteen": 15, "sixteen": 16, "seventeen": 17, "eighteen": 18, "nineteen": 19, 
    "twenty": 20, "thirty": 30, "forty": 40, "fifty": 50, 
    "sixty": 60, "seventy": 70, "eighty": 80, "ninety": 90, "hundred": 100
}

# Step 2: Define a dictionary for basic time units
time_units = {
    "second": 1,
    "minute": 60,          # 1 minute = 60 seconds
    "hour": 3600,          # 1 hour = 3600 seconds
    "day": 86400,          # 1 day = 86400 seconds
    "week": 604800,        # 1 week = 604800 seconds
    "month": 2592000,      # Approximation: 1 month = 30 days * 86400 seconds
    "year": 31536000,      # 1 year = 365 days * 86400 seconds
}

# Step 3: Define patterns for various time expressions including "from now"
time_patterns = {
    "past": r"(\d+|a|one|two|three|four|five|six|seven|eight|nine|ten|eleven|twelve|thirteen|fourteen|fifteen|sixteen|seventeen|eighteen|nineteen|twenty|thirty|forty|fifty|sixty|seventy|eighty|ninety|hundred)\s+(second|minute|hour|day|week|month|year)s?\s+ago",
    "future": r"in\s+(\d+|a|one|two|three|four|five|six|seven|eight|nine|ten|eleven|twelve|thirteen|fourteen|fifteen|sixteen|seventeen|eighteen|nineteen|twenty|thirty|forty|fifty|sixty|seventy|eighty|ninety|hundred)\s+(second|minute|hour|day|week|month|year)s?|(\d+|one|two|three|four|five|six|seven|eight|nine|ten|eleven|twelve|thirteen|fourteen|fifteen|sixteen|seventeen|eighteen|nineteen|twenty|thirty|forty|fifty|sixty|seventy|eighty|ninety|hundred)\s+(second|minute|hour|day|week|month|year)s?\s+later",
    "from_now": r"(\d+|one|two|three|four|five|six|seven|eight|nine|ten|eleven|twelve|thirteen|fourteen|fifteen|sixteen|seventeen|eighteen|nineteen|twenty|thirty|forty|fifty|sixty|seventy|eighty|ninety|hundred)\s+(second|minute|hour|day|week|month|year)s?\s+from\s+now",
    "last_next": r"(last|next)\s+(second|minute|hour|day|week|month|year)s?",
    "this": r"(this)\s+(second|minute|hour|day|week|month|year)s?",
    "more_than": r"more\s+than\s+(\d+|one|two|three|four|five|six|seven|eight|nine|ten|eleven|twelve|thirteen|fourteen|fifteen|sixteen|seventeen|eighteen|nineteen|twenty|thirty|forty|fifty|sixty|seventy|eighty|ninety|hundred)\s+(second|minute|hour|day|week|month|year)s?",
    "present": r"\b(now|currently|today|at the moment)\b",
    "basic_past": r"\b(yesterday|recently|earlier|lately)\b",
    "basic_future": r"\b(soon|tomorrow)\b",
}

# Basic time adverbs (manual coding, this needs to be manually extended)
time_adverbs = {
    "yesterday": -86400,
    "today": 0,
    "tomorrow": 86400,
    "soon": 10000,           # Arbitrary small positive value for 'soon'
    "now": 0,
    "recently": -604800,   # Assume "recently" refers to within the last week
    "earlier": -3600,      # Assume "earlier" refers to within the last hour
    "lately": -2592000,    # Assume "lately" refers to within the last month
}

# Step 4: Define a function to convert number words to digits
def word_to_num(word):
    if word.isdigit():  # If the word is already a digit, return it as an integer
        return int(word)
    
    # Convert the word to a number using the number_words dictionary
    if word in number_words:
        return number_words[word]
    
    # If the word represents a composite number (like "twenty-one"), handle it here
    if '-' in word:
        parts = word.split('-')
        return sum(number_words[part] for part in parts if part in number_words)
    
    return 0  # Default return 0 if not recognized

# Step 5: Define a function to calculate depth based on quantifiers
def calculate_depth(quantity, unit, is_past=True):
    quantity_num = word_to_num(quantity)
    seconds = quantity_num * time_units[unit]
    depth_code = -seconds if is_past else seconds
    return depth_code

# Step 6: Function to handle "last", "next", "this", "more than", and "from now" expressions
def handle_last_next_this_more_than_from_now(keyword, unit=None, is_from_now=False):
    if is_from_now:
        return time_units[unit] * keyword
    elif keyword == "last":
        return -time_units[unit]
    elif keyword == "next":
        return time_units[unit]
    elif keyword == "this":
        # Return the midpoint of the time unit
        if unit == "week":
            return time_units[unit] // 2  # Midpoint of a week
        elif unit == "year":
            return time_units[unit] // 2  # Midpoint of a year
        elif unit == "month":
            return time_units[unit] // 2  # Midpoint of a month
        return 0  # For other units, we keep it as 0
    elif keyword == "now":
        return 0  # "Now" means the current moment, so depth is 0
    elif keyword == "more than":
        # For "more than" we assume the expression refers to an unspecified duration greater than the given time
        return time_units[unit] * 1.5  # Arbitrary choice of 1.5x the time unit as the minimum bound
    return 0


# Step 7: Function to extract time expressions and map them to codes
def extract_time_expressions(text , fileName):
    text = text.lower()
    mapped_adverbs = []

    # Handle past expressions with quantifiers
    for match in re.finditer(time_patterns["past"], text):
        quantity, unit = match.groups()[:2]
        depth_code = calculate_depth(quantity, unit, is_past=True)
        mapped_adverbs.append((match.group(), depth_code))

    # Handle future expressions with quantifiers
    for match in re.finditer(time_patterns["future"], text):
        if match.group(1):  # Check if the match is "in X time"
            quantity, unit = match.groups()[:2]
        else:  # Match "X time later"
            quantity, unit = match.groups()[2:4]
        depth_code = calculate_depth(quantity, unit, is_past=False)
        mapped_adverbs.append((match.group(), depth_code))
    
    # Handle "last" and "next" expressions
    for match in re.finditer(time_patterns["last_next"], text):
        keyword, unit = match.groups()[:2]
        depth_code = handle_last_next_this_more_than_from_now(keyword, unit)
        mapped_adverbs.append((match.group(), depth_code))

    # Handle "this" expressions
    for match in re.finditer(time_patterns["this"], text):
        keyword, unit = match.groups()[:2]
        depth_code = handle_last_next_this_more_than_from_now(keyword, unit)
        mapped_adverbs.append((match.group(), depth_code))

    # Handle "from now" expressions
    for match in re.finditer(time_patterns["from_now"], text):
        quantity, unit = match.groups()[:2]
        depth_code = handle_last_next_this_more_than_from_now(word_to_num(quantity), unit, is_from_now=True)
        mapped_adverbs.append((match.group(), depth_code))

    # Handle "more than" expressions
    for match in re.finditer(time_patterns["more_than"], text):
        keyword, unit = match.groups()[:2]
        depth_code = handle_last_next_this_more_than_from_now("more than", unit)
        mapped_adverbs.append((match.group(), depth_code))

    # Handle basic present, past, and future adverbs
    for category, pattern in time_patterns.items():
        if category not in ["past", "future", "last_next", "this", "from_now"]:  # Skip complex patterns
            for match in re.finditer(pattern, text):
                if match.group() == "now":
                    code = 0  # "Now" is the current moment, so code is 0
                else:
                    code = time_adverbs.get(match.group(), 0)  # Use basic dictionary for these
                mapped_adverbs.append((match.group(), code))

    # Sort results by their depth code (past to future)
    mapped_adverbs.sort(key=lambda x: x[1])

    # Filter out duplicate entries
    unique_adverbs = {expr: code for expr, code in mapped_adverbs}
    
    # Convert to DataFrame
    df = pd.DataFrame(mapped_adverbs, columns=["Expression", "Code"])
    df["FileName"] = fileName
    return df

#-----------------------------------------------------------------------------------------------------------------------------
path = 'D:/CEO data/CEO_Answers/7'
folder_path = Path(path)
FileNames = []
# Iterate over all the files in the folder
for file_path in folder_path.iterdir():
    # Check if it's a file (and not a directory)
    if file_path.is_file():
        with open(file_path) as file:
           FileNames.append(file_path.name)


dataF = pd.DataFrame(columns=['FileName', 'Text'])

for doc in FileNames:
    str_path = path + '/' + doc
    text = ReadPDF(str_path)
    data = [{'FileName': doc, 'Text': text}]
    df = pd.DataFrame(data)
    dataF = pd.concat([dataF, df], ignore_index=True)

##print(dataF)
##dataF.to_csv('D:/DataFiles/output.csv', index=False)

Result = pd.DataFrame(columns=["Expression", "Code", "FileName"])
for index, row in dataF.iterrows():
    Text  = row['Text']
    ID = row['FileName']
    dfs = extract_time_expressions(Text , ID)
    dfs = dfs.drop_duplicates()
    Result = pd.concat([Result, dfs], ignore_index=True)

#print(Result)
Result.to_csv('D:/Result.csv', index=False)