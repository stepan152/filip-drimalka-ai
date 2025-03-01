import streamlit as st
from sentence_transformers import SentenceTransformer
import numpy as np
import re
import os
from PIL import Image
import base64
import anthropic  # pro Claude API
import json
from io import BytesIO
import requests
from sklearn.metrics.pairwise import cosine_similarity

# Konfigurace stránky
st.set_page_config(
    page_title="AI Průvodce myšlenkami Filipa Dřímalky",
    page_icon="🧠",
    layout="wide",
    initial_sidebar_state="expanded"
)

# CSS pro lepší vzhled
st.markdown("""
<style>
    .main-header {
        font-size: 2.2rem;
        font-weight: 600;
        color: #1E6FD9;
        margin-bottom: 1rem;
    }
    .sub-header {
        font-size: 1.5rem;
        font-weight: 500;
        color: #333;
        margin-bottom: 0.8rem;
    }
    .st-emotion-cache-16txtl3 h1, h2, h3, h4 {
        font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
    }
    .stButton > button {
        background-color: #1E6FD9;
        color: white;
        border-radius: 5px;
        font-weight: 500;
        padding: 0.5rem 1rem;
        border: none;
        transition: all 0.3s;
    }
    .stButton > button:hover {
        background-color: #1550a0;
        box-shadow: 0 2px 5px rgba(0,0,0,0.2);
    }
    .message-container {
        padding: 1rem;
        margin-bottom: 1rem;
        border-radius: 5px;
    }
    .user-message {
        background-color: #f0f0f0;
        border-left: 4px solid #1E6FD9;
    }
    .assistant-message {
        background-color: #f7f9fd;
        border-left: 4px solid #6c757d;
    }
    .small-font {
        font-size: 0.8rem;
        color: #6c757d;
    }
    .citation {
        font-size: 0.75rem;
        color: #6c757d;
        font-style: italic;
    }
    .topic-pill {
        display: inline-block;
        background-color: #e9f0fd;
        border: 1px solid #1E6FD9;
        color: #1E6FD9;
        border-radius: 20px;
        padding: 0.2rem 0.8rem;
        margin: 0.2rem;
        font-size: 0.8rem;
        cursor: pointer;
    }
    .sidebar-info {
        background-color: #f7f9fd;
        padding: 1rem;
        border-radius: 5px;
        border-left: 3px solid #1E6FD9;
        margin: 1rem 0;
    }
    footer {visibility: hidden;}
    #MainMenu {visibility: hidden;}
    header {visibility: hidden;}
    .stDeployButton {visibility: hidden;}
</style>
""", unsafe_allow_html=True)

# Inicializace session state - uchování konverzace
if 'conversation' not in st.session_state:
    st.session_state.conversation = []

if 'model' not in st.session_state:
    st.session_state.model = None

if 'embeddings' not in st.session_state:
    st.session_state.embeddings = None
    
if 'text_chunks' not in st.session_state:
    st.session_state.text_chunks = None
    
if 'chunk_sources' not in st.session_state:
    st.session_state.chunk_sources = None

# Inicializace sentence-transformers modelu
@st.cache_resource
def get_embedding_model():
    return SentenceTransformer("paraphrase-multilingual-MiniLM-L12-v2")

# Rozšířená znalostní báze - myšlenky Filipa Dřímalky
@st.cache_data
def get_knowledge_base():
    return {
        # Základní informace
        "O_Filipu_Dřímalkovi": """
            Filip Dřímalka je český odborník na digitální transformaci a umělou inteligenci. Je autorem knihy "Budoucnost (ne)práce", 
            kde se zabývá dopady technologií na pracovní trh a budoucnost pracovních pozic. Jako konzultant pomáhá firmám s digitální 
            transformací a implementací AI. Je zakladatelem vzdělávací platformy Digiskills.cz a působí jako mentor pro startupy.
            Vystupuje na konferencích jako TEDx a je častým hostem v podcastech, kde sdílí své myšlenky o budoucnosti práce,
            digitalizaci a dopadu umělé inteligence na společnost.
        """,
        
        "Kniha_Budoucnost_nepráce": """
            Kniha "Budoucnost (ne)práce" se zabývá tím, jak umělá inteligence a automatizace mění pracovní trh. Filip Dřímalka v ní 
            analyzuje, které profese jsou ohroženy automatizací a které naopak získají na významu. Hlavní myšlenkou knihy je, že 
            technologie nenahradí člověka, ale lidé, kteří umí využívat technologie, nahradí ty, kteří to neumí. Dřímalka zdůrazňuje 
            potřebu celoživotního vzdělávání a adaptace na rychle se měnící podmínky. Kniha obsahuje konkrétní příklady z firem, které 
            úspěšně implementovaly AI, a nabízí praktické rady, jak se připravit na změny v pracovním prostředí.
        """,
        
        # Klíčová témata a myšlenky
        "Digitální_transformace_firem": """
            Podle Filipa Dřímalky je digitální transformace firmy komplexní proces, který zahrnuje nejen implementaci technologií, 
            ale především změnu firemní kultury a myšlení lidí. Dřímalka zdůrazňuje, že úspěšná digitální transformace začíná na úrovni 
            vedení, které musí být přesvědčeno o její důležitosti. Doporučuje začít s jasnou strategií a malými experimenty, které přinesou 
            rychlé výsledky a pomohou přesvědčit skeptiky. Klíčové je podle něj zaměřit se na zákaznickou zkušenost a identifikovat oblasti, 
            kde mohou technologie přinést největší hodnotu. Filip Dřímalka varuje před pouhým nakupováním technologií bez strategického plánu 
            a tvrdí, že investice do vzdělávání zaměstnanců je stejně důležitá jako investice do samotných technologií.
        """,
        
        "Budoucnost_pracovního_trhu": """
            Filip Dřímalka předpovídá zásadní změny na pracovním trhu v důsledku nástupu umělé inteligence a automatizace. Podle jeho 
            analýz jsou nejvíce ohroženy profese založené na rutinních a opakujících se činnostech, jako jsou administrativní práce, 
            účetnictví, call centra nebo některé výrobní pozice. Naopak posilovat budou role vyžadující kreativitu, empatii, kritické 
            myšlení a schopnost řešit komplexní problémy. Dřímalka vidí velký potenciál v kombinaci lidských a technologických schopností - 
            tzv. hybridní inteligenci. Zdůrazňuje, že budoucnost patří "augmentovaným" profesionálům, kteří dokáží efektivně využívat AI 
            jako svého asistenta. Přesto varuje, že přechod nebude jednoduchý a společnost musí řešit otázky rekvalifikace a podpory 
            lidí, jejichž práce bude automatizována.
        """,
        
        "AI_a_produktivita_práce": """
            Filip Dřímalka považuje umělou inteligenci za revoluci v produktivitě práce. Na konkrétních příkladech ukazuje, jak generativní 
            AI dokáže zefektivnit práci v mnoha oborech - od marketingu přes vývoj softwaru až po právní služby. Podle jeho výzkumu může 
            správně implementovaná AI zvýšit produktivitu až o 40% u znalostních pracovníků. Klíčem je podle něj nechat AI převzít rutinní 
            a opakující se úkoly, které nevyžadují kreativitu nebo strategické uvažování. Zároveň upozorňuje, že největším přínosem není 
            samotná automatizace, ale uvolnění lidského potenciálu pro hodnotnější činnosti. Dřímalka také zdůrazňuje význam dat - firmy 
            s kvalitními daty a schopností je zpracovávat budou mít výraznou konkurenční výhodu.
        """,
        
        "Celoživotní_vzdělávání": """
            Filip Dřímalka považuje celoživotní vzdělávání za jedinou jistotu v éře umělé inteligence. Kritizuje tradiční vzdělávací 
            systém, který podle něj nepřipravuje lidi na rychle se měnící svět. Místo memorování faktů doporučuje rozvíjet schopnost 
            učit se nové věci, kritické myšlení a adaptabilitu. Podporuje koncept "T-shaped" profesionálů, kteří mají hlubokou expertizu 
            v jedné oblasti, ale zároveň širší přehled v souvisejících oborech. Dřímalka věří, že budoucnost vzdělávání bude personalizovaná 
            a založená na praktických projektech. Doporučuje věnovat minimálně hodinu denně sebevzdělávání a experimentování s novými 
            technologiemi. Mezi konkrétní dovednosti, které považuje za klíčové pro budoucnost, řadí digitální gramotnost, datovou analytiku, 
            kritické myšlení a emoční inteligenci.
        """,
        
        "Implementace_AI_ve_firmách": """
            Při implementaci umělé inteligence ve firmách Filip Dřímalka doporučuje postupovat strategicky a systematicky. Na základě svých 
            zkušeností z konzultací pro firmy různých velikostí navrhuje začít identifikací problémů a oblastí, kde může AI přinést největší 
            hodnotu. Důležité je stanovit měřitelné cíle a konkrétní KPI pro hodnocení úspěšnosti implementace. Dřímalka zdůrazňuje, že 
            implementace AI není jen technologický projekt, ale vyžaduje změnu procesů a často i organizační struktury. Doporučuje začít 
            s menšími pilotními projekty, které přinesou rychlé výsledky a pomohou přesvědčit skeptiky. Za klíčový faktor úspěchu považuje 
            zapojení zaměstnanců a jejich vzdělávání - lidé musí pochopit, že AI není hrozbou, ale nástrojem, který jim pomůže být 
            efektivnější. Dřímalka také upozorňuje na důležitost etických aspektů a transparentnosti při implementaci AI řešení.
        """,
        
        "Hybridní_inteligence": """
            Koncept hybridní inteligence je jedním z klíčových témat, kterým se Filip Dřímalka zabývá. Jde o spojení lidské a umělé 
            inteligence, kde každá přináší své jedinečné schopnosti. Podle Dřímalky umělá inteligence vyniká v analýze velkých objemů dat, 
            identifikaci vzorců a automatizaci rutinních úkolů, zatímco lidé jsou lepší v kreativitě, etickém rozhodování a řešení 
            nejednoznačných situací. Nejúspěšnější budou podle něj ti, kteří dokáží efektivně kombinovat obě formy inteligence - používat 
            AI jako "kognitivního asistenta", který rozšiřuje jejich schopnosti. Na konkrétních příkladech ukazuje, jak může hybridní 
            inteligence fungovat v praxi - např. u lékařů podporovaných AI v diagnostice, právníků využívajících AI pro analýzu smluv nebo 
            designérů spolupracujících s generativními modely. Dřímalka předpovídá, že hybridní inteligence povede k vytvoření zcela nových 
            profesí a způsobů práce.
        """,
        
        "Budoucí_dovednosti": """
            Filip Dřímalka identifikuje několik klíčových dovedností, které budou podle něj nezbytné pro úspěch v éře umělé inteligence. 
            Digitální gramotnost považuje za základní předpoklad, ale zdůrazňuje, že nejde jen o technické znalosti, ale o schopnost 
            strategicky využívat technologie k řešení problémů. Dalšími klíčovými dovednostmi jsou podle něj kritické myšlení a schopnost 
            ověřovat informace, kreativita a inovativní myšlení, komplexní řešení problémů a adaptabilita. Velký důraz klade na tzv. "měkké 
            dovednosti" jako je emoční inteligence, komunikace a spolupráce, které podle něj AI nebude schopna plně nahradit. Dřímalka také 
            vyzdvihuje význam podnikavosti a schopnosti identifikovat příležitosti. Doporučuje rozvíjet tzv. "metadovednosti" - schopnost 
            učit se nové věci, propojovat znalosti z různých oborů a adaptovat se na změny.
        """,
        
        "Etika_a_AI": """
            V oblasti etiky umělé inteligence Filip Dřímalka zdůrazňuje odpovědnost firem a vývojářů za způsob, jakým je AI nasazována. 
            Varuje před nekritickým přijetím algoritmického rozhodování bez lidského dohledu a zdůrazňuje potřebu transparentnosti AI systémů. 
            Upozorňuje na rizika spojená s předsudky v datech, na kterých se AI učí, a doporučuje různorodé týmy při vývoji AI, které mohou 
            tyto problémy odhalit. Dřímalka podporuje přístup "AI centred on humans" - umělá inteligence by měla být navrhována tak, aby 
            sloužila lidem a respektovala lidské hodnoty. Diskutuje také o širších společenských dopadech automatizace a potřebě hledat 
            řešení pro lidi, jejichž práce bude nahrazena. Věří, že etické aspekty AI budou stále důležitějším tématem a firmy, které je 
            budou ignorovat, riskují ztrátu důvěry zákazníků i zaměstnanců.
        """,
        
        "Praktické_využití_generativní_AI": """
            Filip Dřímalka je velkým zastáncem praktického využití generativní umělé inteligence v každodenní práci. Na základě vlastních 
            experimentů s nástroji jako GPT-4 a DALL-E 2 ukazuje konkrétní způsoby, jak mohou tyto technologie zvýšit produktivitu v různých 
            profesích. V oblasti copywritingu a marketingu zdůrazňuje možnost rychlého vytváření variant textů a jejich testování. 
            Pro vývojáře software popisuje, jak AI může pomoci s kódováním, debugováním a dokumentací. V oblasti designu vyzdvihuje možnosti 
            rychlého generování vizuálních konceptů a iterací. Dřímalka také sdílí praktické tipy pro efektivní práci s generativní AI - 
            jak formulovat prompty, jak ověřovat výstupy a jak AI výstupy dále zpracovávat. Zdůrazňuje, že klíčem není nechat AI pracovat 
            samostatně, ale vytvořit efektivní spolupráci, kde člověk zadává kontext, směr a kriticky hodnotí výsledky, zatímco AI pomáhá 
            s generováním obsahu a řešení.
        """,
        
        "Digitální_wellbeing": """
            Filip Dřímalka se ve svých přednáškách a článcích zabývá také tématem digitálního wellbeingu - jak zůstat zdravý a produktivní 
            v digitálním světě. Upozorňuje na rizika digitálního přetížení, neustálého rozptylování a závislosti na technologiích. 
            Na základě výzkumů i vlastních zkušeností doporučuje konkrétní strategie, jak technologie využívat vědomě a záměrně. 
            Mezi jeho doporučení patří pravidelné digitální detoxy, nastavení jasných hranic mezi pracovním a osobním životem, využívání 
            technik hluboké práce (deep work) a vědomé omezování notifikací a rozptýlení. Dřímalka také zdůrazňuje význam fyzického pohybu, 
            kvalitního spánku a osobních vztahů jako protiváhy k digitálnímu světu. Věří, že v budoucnosti bude schopnost vědomě pracovat 
            s technologiemi a chránit svou pozornost ještě důležitější než dnes.
        """,
        
        "Budoucnost_vzdělávání": """
            V oblasti vzdělávání Filip Dřímalka předpovídá zásadní transformaci tradičního modelu. Kritizuje současný vzdělávací systém 
            za to, že nedostatečně připravuje studenty na rychle se měnící svět a na spolupráci s umělou inteligencí. Věří, že budoucnost 
            patří personalizovanému vzdělávání, které se přizpůsobí individuálním potřebám, tempu a stylu učení každého studenta. 
            Klíčovou roli v tom podle něj budou hrát vzdělávací technologie a AI tutoring systémy. Dřímalka prosazuje projektovou výuku 
            založenou na řešení reálných problémů a mezioborovou spolupráci. Zdůrazňuje potřebu rozvíjet kritické myšlení, kreativitu 
            a schopnost učit se nové věci nad memorováním faktů. Věří, že formální vzdělávání se bude více prolínat s celoživotním učením 
            a hranice mezi školou a praxí se budou stírat. Dřímalka také podporuje model mikrocertifikací a uznávání dovedností získaných 
            praxí nebo samostudiem.
        """,
        
        "Transformace_pracovního_prostředí": """
            Filip Dřímalka se zabývá tím, jak se mění pracovní prostředí v digitální éře. Na základě svých konzultací pro firmy různých 
            velikostí identifikuje několik klíčových trendů - flexibilní pracovní modely (včetně hybridní a remote práce), důraz 
            na kolaborační nástroje a platformy, postupný odklon od tradičních hierarchických struktur směrem k agilním a projektově 
            orientovaným týmům. Dřímalka věří, že fyzické kanceláře nezaniknou, ale změní svou funkci - stanou se především místem 
            pro spolupráci, kreativní setkávání a budování vztahů, zatímco individuální práce bude probíhat často na dálku. Zdůrazňuje 
            potřebu nových přístupů k vedení lidí v digitálním prostředí, založených na důvěře, autonomii a zaměření na výsledky 
            místo kontroly času. Předpovídá také růst důležitosti tzv. "liquid workforces" - flexibilních sítí expertů spolupracujících 
            na konkrétních projektech.
        """,
        
        "Startupové_zkušenosti": """
            Filip Dřímalka má bohaté zkušenosti se světem startupů, ať už jako zakladatel vlastních projektů nebo jako mentor a angel investor. 
            Ze svých zkušeností zdůrazňuje několik klíčových lekcí pro úspěšné podnikání v digitální éře. Považuje za zásadní začít s jasným 
            pochopením problému, který startup řeší, a ověřit si poptávku ještě před vytvořením kompletního produktu (princip MVP - minimum 
            viable product). Dřímalka prosazuje agilní přístup k vývoji založený na rychlých iteracích a neustálé zpětné vazbě od zákazníků. 
            Z vlastní zkušenosti zdůrazňuje důležitost budování kvalitního týmu s komplementárními dovednostmi a sdílenou vizí. Varuje před 
            common startup killers jako je špatné cash-flow management, přílišná technická dokonalost na úkor rychlosti uvedení na trh, nebo 
            neschopnost pivotovat na základě zpětné vazby. Věří, že největší příležitosti pro startupy leží v oblastech, kde se protíná 
            technologická inovace s reálnými problémy lidí a firem.
        """,
        
        "Vize_společnosti_5.0": """
            Filip Dřímalka ve svých vystoupeních často představuje vizi tzv. Společnosti 5.0 - konceptu původně navrženého v Japonsku, který 
            popisuje další fázi vývoje po informační společnosti. Jde o společnost, kde jsou fyzický a kybernetický prostor hluboce propojeny 
            a technologie jsou plně integrovány do každodenního života s cílem řešit společenské výzvy. Dřímalka tento koncept dále rozvíjí 
            v kontextu české a evropské reality. Zdůrazňuje, že cílem není technologie samotná, ale využití technologií k vytvoření udržitelné, 
            inkluzivní a prosperující společnosti. Podle jeho vize bude Společnost 5.0 charakterizována personalizovanými službami využívajícími 
            AI a velká data, inteligentními městy a infrastrukturou, novými modely práce a vzdělávání a důrazem na wellbeing a kvalitu života. 
            Dřímalka však upozorňuje i na výzvy spojené s touto transformací - otázky soukromí, bezpečnosti, digitální propasti a potřeby nových 
            regulačních rámců.
        """,
        
        "Podcastové_vystoupení_o_AI": """
            V několika českých podcastech Filip Dřímalka diskutoval o dopadu umělé inteligence na společnost a byznys. Zdůrazňoval, že jsme 
            teprve na začátku AI revoluce a že generativní AI jako GPT-4 a podobné modely znamenají zásadní průlom v tom, jak stroje mohou 
            pracovat s jazykem a generovat obsah. Vysvětloval, že současná generativní AI je skvělá v rozpoznávání vzorců a generování 
            pravděpodobného obsahu, ale nemá skutečné porozumění a nemůže nahradit lidskou kreativitu a úsudek. Dřímalka předpovídal, že 
            během následujících 5-10 let uvidíme masivní adopci AI nástrojů ve většině odvětví a profesí. Diskutoval také o potenciálních 
            rizicích spojených s AI, včetně možnosti dezinformací, manipulace a prohloubení nerovností. Zdůrazňoval potřebu jak technických 
            řešení (např. rozpoznávání AI-generovaného obsahu), tak regulačních a etických rámců. Přes všechny výzvy však Dřímalka vyjadřoval 
            optimismus ohledně budoucnosti, kde lidé a AI spolupracují.
        """,
        
        "TEDx_přednáška_o_budoucnosti_práce": """
            Ve své přednášce na TEDx Filip Dřímalka mluvil o tom, jak umělá inteligence redefinuje samotný koncept práce. Začal historickým 
            přehledem, jak technologie vždy měnily pracovní trh - od průmyslové revoluce přes počítače až po současnou AI revoluci. 
            Na konkrétních příkladech ukázal, jak AI již nyní transformuje různé profese a průmyslová odvětví. Hlavním poselstvím přednášky 
            bylo, že budoucnost práce nespočívá v "souboji" člověka proti stroji, ale v novém modelu spolupráce, který nazývá "hybridní 
            inteligencí". Dřímalka zdůrazňoval, že největší hodnotu budou vytvářet lidé, kteří dokáží kombinovat své jedinečně lidské 
            schopnosti (kreativita, empatie, etické uvažování) s možnostmi umělé inteligence. Přednášku uzavřel výzvou k novému přístupu 
            ke vzdělávání, který by lidi připravoval na tento nový svět práce, a k vytvoření společenských struktur, které zajistí, že 
            benefity AI revoluce budou široce sdíleny.
        """,
        
        "Názor_na_ChatGPT_a_generativní_AI": """
            Filip Dřímalka považuje ChatGPT a další generativní AI nástroje za přelomovou technologii, která zásadně mění způsob, jakým 
            pracujeme s informacemi a vytváříme obsah. Na základě vlastních experimentů a sledování jejich vývoje identifikuje několik 
            klíčových dopadů těchto technologií. Za prvé, generativní AI podle něj demokratizuje přístup ke kreativním nástrojům a umožňuje 
            i netechnickým uživatelům vytvářet kvalitní obsah. Za druhé, tyto nástroje výrazně zvyšují produktivitu v mnoha profesích tím, 
            že automatizují rutinní aspekty práce jako je psaní emailů, vytváření reportů nebo generování kódu. Za třetí, mění požadavky 
            na dovednosti - důležitější než pamatovat si informace je umět formulovat správné otázky a kriticky hodnotit výstupy AI. 
            Dřímalka však upozorňuje i na limity a rizika - problém halucinací (AI generuje přesvědčivě znějící, ale fakticky nesprávné 
            informace), riziko plagiátorství a autorských práv, a možnost vytváření dezinformací. Přesto věří, že přínosy převažují nad 
            riziky a že generativní AI představuje podobně zásadní průlom jako byl internet nebo chytré telefony.
        """,
    }

# Seznam doporučených otázek
suggested_questions = [
    "Jak konkrétně AI mění pracovní trh a jaké profese zaniknou?",
    "Jaké konkrétní dovednosti budou v budoucnu nejvíce ceněné díky AI?",
    "Jak se můžu připravit na změny v pracovním trhu způsobené AI?",
    "Jaké strategie pro celoživotní vzdělávání doporučuje Filip Dřímalka?",
    "Jakým způsobem mohou firmy efektivně implementovat AI do svých procesů?",
    "Jaké jsou největší výzvy při digitalizaci a jak je překonat?",
    "Jak Filip Dřímalka vidí koncept hybridní inteligence?",
    "Co si Filip Dřímalka myslí o ChatGPT a generativní AI?",
    "Jak by podle Filipa Dřímalky mělo vypadat vzdělávání v budoucnosti?",
    "Co je to Společnost 5.0 podle Filipa Dřímalky?",
    "Jaké jsou etické aspekty AI, na které Filip Dřímalka upozorňuje?",
    "Jaké jsou praktické tipy pro využití generativní AI v běžné práci?",
    "Co Filip Dřímalka říkal o AI ve své TEDx přednášce?",
    "Jak se podle Filipa Dřímalky mění pracovní prostředí v digitální éře?"
]

# Funkce pro rozdělení delších textů na menší chunky
def create_text_chunks(knowledge_base, chunk_size=500, overlap=100):
    """Rozdělí texty ze znalostní báze na menší chunky s překryvem."""
    chunks = []
    chunk_sources = []
    
    for key, text in knowledge_base.items():
        # Vyčištění textu - odstranění nadbytečných mezer
        text = re.sub(r'\s+', ' ', text).strip()
        
        # Pokud je text dostatečně krátký, zachováme ho celý
        if len(text) <= chunk_size:
            chunks.append(text)
            chunk_sources.append(key)
        else:
            # Rozdělení na věty
            sentences = re.split(r'(?<=[.!?])\s+', text)
            current_chunk = ""
            
            for sentence in sentences:
                # Pokud by přidání další věty překročilo velikost chunku, uložíme současný chunk
                if len(current_chunk) + len(sentence) > chunk_size and current_chunk:
                    chunks.append(current_chunk)
                    chunk_sources.append(key)
                    # Přetok z minulého chunku pro zachování kontextu
                    current_chunk = current_chunk[-overlap:] if len(current_chunk) > overlap else current_chunk
                
                current_chunk += " " + sentence
            
            # Přidání posledního chunku, pokud nějaký zbývá
            if current_chunk:
                chunks.append(current_chunk)
                chunk_sources.append(key)
    
    return chunks, chunk_sources

# Funkce pro vyhledávání nejrelevantnějších odpovědí
def search_knowledge_base(query, embeddings, text_chunks, chunk_sources, top_k=3, threshold=0.6):
    """Vyhledá nejrelevantnější chunky textu k dotazu."""
    model = get_embedding_model()
    query_embedding = model.encode([query], convert_to_numpy=True)
    
    # Výpočet kosinové podobnosti
    similarities = cosine_similarity(query_embedding, embeddings)[0]
    
    # Seřazení indexů podle podobnosti (sestupně)
    sorted_indices = np.argsort(similarities)[::-1][:top_k]
    
    # Kontrola relevance
    relevant_chunks = []
    relevant_sources = []
    
    for idx in sorted_indices:
        similarity = similarities[idx]
        
        if similarity >= threshold:
            relevant_chunks.append(text_chunks[idx])
            relevant_sources.append(chunk_sources[idx])
    
    if not relevant_chunks:
        return None, None
    
    return relevant_chunks, relevant_sources

# Funkce pro přípravu znalostní báze
def prepare_knowledge_base():
    # Získání znalostní báze
    knowledge_base = get_knowledge_base()
    
    # Vytvoření chunků
    text_chunks, chunk_sources = create_text_chunks(knowledge_base)
    
    # Inicializace modelu
    model = get_embedding_model()
    
    # Konverze znalostní báze na embeddingy
    embeddings = model.encode(text_chunks, convert_to_numpy=True)
    
    return embeddings, text_chunks, chunk_sources

# Funkce pro získání odpovědi od Claude
def get_claude_response(prompt, context=None):
    try:
        # Získáme API klíč z proměnné prostředí nebo ze Streamlit secrets
        api_key = st.secrets["ANTHROPIC_API_KEY"]
        
        # Vytvoříme klienta
        client = anthropic.Anthropic(api_key=api_key)
        
        # Příprava systémové zprávy
        if context:
            system_message = f"""
            Jsi chatbot představující pohled Filipa Dřímalky na témata AI, digitální transformace a budoucnost práce.
            Odpovídej v první osobě, jako by odpovídal přímo Filip Dřímalka - používej jeho styl komunikace, který je profesionální, 
            optimistický a zaměřený na budoucnost. Buď konkrétní, uváděj příklady a praktické rady.
            
            Použij následující informace jako kontext pro svou odpověď:
            
            {context}
            
            Pokud otázka nesouvisí s tématy digitalizace, AI nebo budoucností práce, zdvořile odpověz, 
            že se zaměřuješ především na tato témata a nabídni uživateli, že může položit otázku z těchto oblastí.
            """
        else:
            system_message = """
            Jsi chatbot představující pohled Filipa Dřímalky na témata AI, digitální transformace a budoucnost práce.
            Odpovídej v první osobě, jako by odpovídal přímo Filip Dřímalka - používej jeho styl komunikace, který je profesionální, 
            optimistický a zaměřený na budoucnost.
            
            Na tuto otázku nemáš specifické informace od Filipa Dřímalky. Nabídni obecnou odpověď z pohledu 
            odborníka na digitální transformaci a AI a navrhni uživateli, aby se zeptal na jiné téma spojené 
            s digitální transformací a budoucností práce.
            """
        
        # Volání API
        response = client.messages.create(
            model="claude-3-opus-20240229",
            max_tokens=1000,
            system=system_message,
            messages=[
                {"role": "user", "content": prompt}
            ]
        )
        
        return response.content[0].text
    except Exception as e:
        st.error(f"Chyba při komunikaci s Claude API: {str(e)}")
        return "Omlouvám se, došlo k technické chybě při zpracování vaší otázky. Zkuste to prosím později nebo položte jinou otázku."

# Funkce pro zpracování dotazu
def process_query(query):
    # Vyhledání relevantních informací
    relevant_chunks, sources = search_knowledge_base(
        query, 
        st.session_state.embeddings, 
        st.session_state.text_chunks, 
        st.session_state.chunk_sources
    )
    
    # Získání odpovědi
    if relevant_chunks:
        # Sloučení relevantních informací
        context = "\n\n".join(relevant_chunks)
        sources_text = ", ".join(set(sources))
        
        # Získání odpovědi od Claude
        response = get_claude_response(query, context)
        
        # Přidání citace zdrojů
        source_info = f"\n\nInformace vychází z: {sources_text}" if sources else ""
        
        return response + source_info, sources
    else:
        # Obecná odpověď, pokud nemáme relevantní informace
        response = get_claude_response(query)
        return response, None

# Funkce pro načtení obrázku z URL
@st.cache_data
def load_image_from_url(url):
    try:
        response = requests.get(url)
        img = Image.open(BytesIO(response.content))
        return img
    except Exception as e:
        st.error(f"Chyba při načítání obrázku: {e}")
        return None

# Hlavní UI aplikace
def main():
    # Rozdělení na dva sloupce - sidebar a hlavní obsah
    col1, col2 = st.columns([1, 3])
    
    # Hlavní sekce - levý sloupec pro profil
    with col1:
        st.image("https://filipdrimalka.cz/wp-content/uploads/2023/12/Filip-Drimalka-square.jpg", width=200)
        st.markdown("<h2>Filip Dřímalka</h2>", unsafe_allow_html=True)
        st.markdown("""
        <div class="sidebar-info">
            <p>Expert na digitální transformaci a autor knihy "Budoucnost (ne)práce".</p>
            <p>Věří, že budoucnost patří lidem, kteří dokáží efektivně využívat AI jako svého asistenta.</p>
        </div>
        """, unsafe_allow_html=True)
        
        st.markdown("### Klíčová témata")
        
        # Klíčová témata jako kliknutelná tlačítka
        topics = [
            "Digitální transformace", 
            "Budoucnost práce", 
            "Hybridní inteligence",
            "Celoživotní vzdělávání",
            "Implementace AI",
            "Společnost 5.0"
        ]
        
        for topic in topics:
            st.markdown(f'<div class="topic-pill" onclick="this.style.backgroundColor=\'#1E6FD9\';this.style.color=\'white\'">{topic}</div>', unsafe_allow_html=True)
    
    # Hlavní sekce
    with col2:
        st.markdown('<p class="main-header">AI Průvodce myšlenkami Filipa Dřímalky</p>', unsafe_allow_html=True)
        st.markdown("Zeptejte se na cokoli o digitální transformaci, AI a budoucnosti práce z pohledu Filipa Dřímalky.")
        
        # Výběr z doporučených otázek
        st.markdown('<p class="sub-header">Doporučené otázky:</p>', unsafe_allow_html=True)
        selected_question = st.selectbox("", [""] + suggested_questions)
        
        # Vlastní otázka
        st.markdown('<p class="sub-header">Nebo napište vlastní otázku:</p>', unsafe_allow_html=True)
        user_input = st.text_input("", placeholder="Např.: Jak se připravit na změny způsobené AI?")
        
        # Odeslání dotazu
        query = user_input if user_input else selected_question
        
        col_button1, col_button2 = st.columns([1, 5])
        with col_button1:
            if st.button("Odeslat"):
                if query:
                    with st.spinner('Filip přemýšlí nad odpovědí...'):
                        # Získání odpovědi
                        response, sources = process_query(query)
                        
                        # Přidání do historie konverzace
                        st.session_state.conversation.append({"role": "user", "content": query})
                        st.session_state.conversation.append({"role": "assistant", "content": response, "sources": sources})
                else:
                    st.warning("Prosím, zadejte otázku nebo vyberte z nabídky.")
        
        with col_button2:
            if st.button("Nová konverzace"):
                st.session_state.conversation = []
                st.experimental_rerun()
        
        # Zobrazení historie konverzace
        st.markdown("### Konverzace:")
        
        for message in st.session_state.conversation:
            if message["role"] == "user":
                st.markdown(f'<div class="message-container user-message"><strong>Vy:</strong> {message["content"]}</div>', unsafe_allow_html=True)
            else:
                source_text = ""
                if "sources" in message and message["sources"]:
                    sources = list(set([source.replace("_", " ") for source in message["sources"]]))
                    source_text = f'<div class="citation">Zdroje: {", ".join(sources)}</div>'
                
                st.markdown(
                    f'<div class="message-container assistant-message"><strong>Filip Dřímalka:</strong> {message["content"]}{source_text}</div>', 
                    unsafe_allow_html=True
                )
    
    # Footer
    st.markdown("""
    <div style="text-align:center; margin-top:30px; padding-top:20px; border-top:1px solid #eee;">
        <p class="small-font">Vytvořeno jako demonstrace AI schopností. Tento chatbot představuje pohled Filipa Dřímalky založený na jeho veřejných vystoupeních a publikacích.</p>
    </div>
    """, unsafe_allow_html=True)

# Inicializace znalostní báze při prvním spuštění
if st.session_state.embeddings is None:
    with st.spinner('Načítám znalostní bázi...'):
        st.session_state.embeddings, st.session_state.text_chunks, st.session_state.chunk_sources = prepare_knowledge_base()

# Spuštění aplikace
if __name__ == "__main__":
    main()
            
