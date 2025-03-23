import os

DB = 'hack_ai_thon'
MONGO_URI = os.environ.get('MONGO_URI', '')
 
USER_COLLECTION = 'Employees'
SESSION_COLLECTION = 'Sessions'
QUERY_COLLECTION = 'Queries'
FAQ_COLLECTION = 'FAQ'
EMAIL_ADDRESS = "lintosaji.1990@gmail.com"
SUPABASE_URL = "postgresql://postgres.chduybdjpvedaveezdbf:Lintomon2003*@aws-0-ap-southeast-1.pooler.supabase.com:6543/postgres"

MISTRAL_SMALL = 'mistral-small-2402'
MISTRAL_LARGE = 'mistral-large-latest'

PROMPT_USER_INTENT = 'prompt_user_intent.txt'
if os.path.abspath('.').split('\\')[1] == 'AI_61_Byte-Benders_02':
    PROMPT_USER_INTENT = os.path.join('src', 'prompts', PROMPT_USER_INTENT)

CODE_CONDUCT = "Code-of-Conduct.pdf"
if os.path.abspath('.').split('\\')[1] == 'AI_61_Byte-Benders_02':
    CODE_CONDUCT = os.path.join('db', CODE_CONDUCT)