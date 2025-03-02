import streamlit as st
from PIL import Image
import requests
from io import BytesIO

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

# Předem definované otázky a odpovědi
qa_pairs = {
    "Jak konkrétně AI mění pracovní trh a jaké profese zaniknou?": 
        """AI zásadně transformuje pracovní trh. Nejvíce ohroženy jsou profese založené na rutinních a opakujících se činnostech - administrativa, účetnictví, zákaznické linky, některé výrobní role.

AI dokáže tyto opakující se úkoly řešit efektivněji, rychleji a s menší chybovostí. Naopak posílí role vyžadující kreativitu, empatii, kritické myšlení a řešení komplexních problémů.

Budoucnost patří lidem, kteří dokáží efektivně spolupracovat s umělou inteligencí. Klíčové je rozvíjet schopnosti, které AI nemá - kreativní myšlení, mezilidské dovednosti a adaptabilitu na neustálé změny.""",
    
    "Jaké konkrétní dovednosti budou v budoucnu nejvíce ceněné díky AI?":
        """V éře AI budou nejcennější tyto dovednosti:

1. Digitální gramotnost - schopnost strategicky využívat technologie, i když ne nutně programovat
2. Kritické myšlení - ověřování informací a analytický přístup k problémům
3. Kreativita a inovace - oblasti, kde lidé stále převyšují stroje
4. Emoční inteligence - empatie, komunikační dovednosti a spolupráce
5. Adaptabilita - schopnost učit se nové věci a přizpůsobovat se změnám

Lidé excelující v těchto oblastech zůstanou nenahraditelní i v době pokročilé automatizace.""",
    
    "Jak se můžu připravit na změny v pracovním trhu způsobené AI?":
        """Na změny pracovního trhu způsobené AI se můžeš připravit několika způsoby:

Především je klíčové neustálé vzdělávání - věnuj alespoň hodinu denně učení se něčeho nového. Zaměř se na dovednosti, které AI těžko nahradí - kreativita, sociální inteligence, kritické myšlení.

Snaž se pochopit technologie, ne se jich bát. Experimentuj s nástroji jako ChatGPT nebo DALL-E, abys pochopil jejich možnosti i limity.

Buduj si T-shaped profil - hluboká expertiza v jedné oblasti, ale také širší přehled v souvisejících oborech. A nezapomínej na networking - v digitálním světě budou lidské vztahy a kontakty cenné více než kdy dřív.""",
    
    "Jaké strategie pro celoživotní vzdělávání doporučuje Filip Dřímalka?":
        """Pro celoživotní vzdělávání v digitální éře doporučuji:

Praktické učení založené na projektech - nejlépe se učíme, když řešíme skutečné problémy, ne memorováním teorií.
    
Denní rutinu vzdělávání - věnuj každý den alespoň 30-60 minut učení se něčemu novému.

Multidisciplinární přístup - kombinuj znalosti z různých oborů, největší inovace vznikají na jejich průsečíku.

Komunity a peer learning - zapoj se do skupin lidí, kteří sdílejí tvé zájmy a od kterých se můžeš učit.

Experimentuj s technologiemi - praktické vyzkoušení nových nástrojů ti dá mnohem lepší pochopení než jen čtení o nich.

Reflektuj své zkušenosti - pravidelně si dej čas na zamyšlení nad tím, co ses naučil a jak to můžeš aplikovat.""",
    
    "Jakým způsobem mohou firmy efektivně implementovat AI do svých procesů?":
        """Firmy mohou efektivně implementovat AI skrze několik klíčových kroků:

Začněte s jasnou strategií a identifikací problémů, které AI může pomoci vyřešit - ne technologií pro technologii.

Zaměřte se nejprve na menší pilotní projekty s rychlými výsledky, které pomohou přesvědčit skeptiky ve firmě.

Zapojte zaměstnance do celého procesu - AI implementace není jen technologický projekt, ale především změna způsobu práce.

Investujte do vzdělávání lidí souběžně s implementací technologií - lidé musí pochopit, jak s AI efektivně spolupracovat.

Měřte výsledky pomocí jasných KPI a neustále upravujte přístup na základě získaných dat a zpětné vazby.

Nezapomínejte na etické aspekty a transparentnost - bez důvěry zaměstnanců i zákazníků nemůže být implementace AI úspěšná.""",
    
    "Jaké jsou největší výzvy při digitalizaci a jak je překonat?":
        """Největší výzvy při digitalizaci často nejsou technické, ale lidské povahy:

Odpor ke změnám - lidé přirozeně nemají rádi změny. Řešením je jasná komunikace přínosů, zapojení zaměstnanců do procesu a vytvoření early adopters, kteří pomohou ostatním.

Nedostatečné digitální dovednosti - mnoho firem podceňuje investice do vzdělávání. Je důležité vytvořit vzdělávací programy šité na míru různým úrovním digitální gramotnosti.

Roztříštěné systémy a data - firmy často mají mnoho oddělených systémů. Klíčové je vytvořit integrovanou datovou strategii.

Bezpečnostní rizika - s rostoucí digitalizací přichází větší kybernetické hrozby. Investice do bezpečnosti musí růst stejným tempem jako digitalizace.

Nejasná strategie - mnoho firem nakupuje technologie bez jasné vize. Začněte vždy byznysovým problémem, ne technologií.""",
    
    "Jak Filip Dřímalka vidí koncept hybridní inteligence?":
        """Hybridní inteligence představuje nový model spolupráce mezi lidmi a stroji, kde každý přispívá svými jedinečnými schopnostmi.

AI vyniká v analýze velkých objemů dat, identifikaci vzorců a automatizaci rutinních úkolů. Naproti tomu lidé excelují v kreativitě, empatickém rozhodování a řešení nejednoznačných situací.

Nejúspěšnější budou ti, kteří dokáží efektivně kombinovat obě formy inteligence - používat AI jako "kognitivního asistenta", který rozšiřuje jejich možnosti.

V praxi to můžeme vidět u lékařů spolupracujících s AI na diagnostice, právníků využívajících AI pro analýzu smluv nebo designérů pracujících s generativními modely.

Hybridní inteligence není o soupeření člověka se strojem, ale o vytvoření nové formy spolupráce, která překonává omezení obou.""",

    "Co si Filip Dřímalka myslí o ChatGPT a generativní AI?":
        """ChatGPT a další generativní AI nástroje představují skutečný průlom v tom, jak pracujeme s informacemi a vytváříme obsah.

Tyto technologie demokratizují přístup ke kreativním nástrojům - umožňují i netechnickým uživatelům vytvářet kvalitní obsah, psát kód nebo generovat vizuály.

Obzvlášť oceňuji jejich schopnost výrazně zvýšit produktivitu v mnoha profesích. Generativní AI umí automatizovat repetitivní aspekty práce jako psaní emailů, vytváření reportů nebo generování kódu.

Zajímavé je, jak tyto nástroje mění požadované dovednosti - důležitější než memorovat informace je umět formulovat správné otázky a kriticky hodnotit výstupy AI.

Samozřejmě existují i rizika a limity - problém halucinací (nepřesnosti ve faktech), otázky autorských práv a možnost zneužití pro dezinformace. Přesto věřím, že přínosy jednoznačně převažují.""",
    
    "Jak by podle Filipa Dřímalky mělo vypadat vzdělávání v budoucnosti?":
        """Vzdělávání v budoucnosti se musí zásadně proměnit, aby odpovídalo rychle se měnícímu světu:

Personalizace je klíčová - každý student má jedinečné tempo, styl a potřeby učení. Technologie nám umožní přizpůsobit vzdělávání na míru každému jednotlivci.

Projektová výuka založená na řešení reálných problémů by měla nahradit memorování faktů. Studenti se nejlépe učí, když vidí praktické aplikace znalostí.

Mezioborová spolupráce bude zásadní - inovace vznikají na průsečíku různých disciplín. Vzdělávání by mělo bourat umělé bariéry mezi předměty.

Formální vzdělávání se bude více prolínat s celoživotním učením. Hranice mezi školou a praxí se budou stírat.

AI tutoring systémy umožní personalizovanou zpětnou vazbu a podporu každému studentovi.

Učitelé se stanou spíše průvodci učením než pouhými poskytovateli informací.""",
    
    "Co je to Společnost 5.0 podle Filipa Dřímalky?":
        """Společnost 5.0 je koncept původně navržený v Japonsku, který popisuje další fázi vývoje po informační společnosti.

Jde o vizi, kde jsou fyzický a kybernetický prostor hluboce propojeny a technologie jsou plně integrovány do každodenního života s cílem řešit společenské výzvy.

Klíčové je, že cílem není technologie samotná, ale využití technologií k vytvoření udržitelné, inkluzivní a prosperující společnosti.

V praxi to znamená personalizované služby využívající AI a velká data, inteligentní města a infrastrukturu, nové modely práce a vzdělávání a důraz na wellbeing a kvalitu života.

Tato transformace přináší i významné výzvy - otázky soukromí, bezpečnosti, digitální propasti mezi různými skupinami obyvatel a potřeby nových regulačních rámců.""",
    
    "Jaké jsou etické aspekty AI, na které Filip Dřímalka upozorňuje?":
        """Při implementaci AI je nezbytné myslet na několik zásadních etických aspektů:

Transparentnost algoritmů - lidé by měli rozumět, jak AI systémy dospívají k rozhodnutím, která je ovlivňují.

Odpovědnost - musí být jasné, kdo nese odpovědnost za rozhodnutí učiněná na základě AI.

Férovost a předpojatost - AI systémy mohou nevědomě zesilovat existující předsudky, pokud jsou trénovány na zaujatých datech.

Soukromí - sběr a využití osobních dat pro AI musí respektovat práva jednotlivců.

Lidský dohled - kritická rozhodnutí by měla vždy podléhat lidskému přezkoumání.

Společenské dopady automatizace - musíme řešit otázky rekvalifikace a podpory lidí, jejichž práce bude nahrazena.

Etické aspekty AI nejsou jen volitelným doplňkem, ale zásadním faktorem důvěryhodnosti a dlouhodobé udržitelnosti AI systémů.""",
    
    "Jaké jsou praktické tipy pro využití generativní AI v běžné práci?":
        """Pro efektivní využití generativní AI v každodenní práci doporučuji:

Prompty formulujte jako jasné instrukce - buďte konkrétní ohledně formátu, délky a stylu výstupu, který očekáváte.

Rozdělujte složité úkoly na menší části - AI lépe zvládá konkrétní, ohraničené úlohy než komplexní zadání.

Vždy ověřujte faktickou správnost - generativní AI může produkovat přesvědčivě znějící, ale nesprávné informace.

Používejte AI pro první návrhy, které následně upravíte a zdokonalíte - kombinace AI rychlosti a lidské kreativní finalizace je velmi efektivní.

Experimentujte s různými přístupy k zadání - někdy malá změna ve formulaci může přinést výrazně lepší výsledky.

Učte se od AI - sledujte, jak strukturuje odpovědi a řeší problémy, můžete se inspirovat i v její metodologii.""",
    
    "Co Filip Dřímalka říkal o AI ve své TEDx přednášce?":
        """V TEDx přednášce jsem zdůraznil, že AI nepředstavuje náhradu lidí, ale revoluci ve způsobu, jak pracujeme. 

Začal jsem historickým přehledem - technologie vždy měnily pracovní trh, od průmyslové revoluce přes počítače až po současnou AI revoluci.

Na konkrétních příkladech jsem ukázal, jak AI již nyní transformuje různé profese - od zdravotnictví přes právní služby až po kreativní odvětví.

Hlavním poselstvím přednášky bylo, že budoucnost práce nespočívá v soupeření člověka proti stroji, ale v novém modelu spolupráce - hybridní inteligenci.

Největší hodnotu budou vytvářet lidé, kteří dokáží kombinovat své jedinečně lidské schopnosti s možnostmi umělé inteligence.

Přednášku jsem uzavřel výzvou k novému přístupu ke vzdělávání, který by lidi připravoval na tento nový svět práce.""",
    
    "Jak se podle Filipa Dřímalky mění pracovní prostředí v digitální éře?":
        """Pracovní prostředí prochází v digitální éře několika zásadními změnami:

Flexibilní pracovní modely se stávají standardem - hybridní práce, vzdálená spolupráce a asynchronní komunikace mění dynamiku práce.

Tradiční hierarchické struktury ustupují agilním a projektově orientovaným týmům, které se mohou rychleji adaptovat na změny.

Fyzické kanceláře nemizí, ale mění svou funkci - stávají se místem pro spolupráci, kreativní setkávání a budování vztahů, zatímco individuální práce probíhá často na dálku.

Vedení lidí v digitálním prostředí vyžaduje nové přístupy založené na důvěře, autonomii a zaměření na výsledky místo kontroly času.

Roste význam tzv. "liquid workforces" - flexibilních sítí expertů spolupracujících na konkrétních projektech.""",
    
    "Co obsahuje kniha Budoucnost (ne)práce od Filipa Dřímalky?":
        """Kniha Budoucnost (ne)práce se zabývá tím, jak umělá inteligence a automatizace mění pracovní trh a co to znamená pro jednotlivce i organizace.

V knize analyzuji, které profese jsou ohroženy automatizací a které naopak získají na významu. Hlavní myšlenkou je, že technologie nenahradí člověka, ale lidé, kteří umí využívat technologie, nahradí ty, kteří to neumí.

Kniha obsahuje konkrétní příklady firem, které úspěšně implementovaly AI, a ukazuje, jak tyto technologie změnily způsob jejich práce a zvýšily produktivitu.

Značná část knihy je věnována dovednostem budoucnosti - co se potřebujeme naučit, abychom zůstali relevantní v éře umělé inteligence. Zdůrazňuji význam celoživotního vzdělávání a adaptability na měnící se podmínky.

V závěru nabízím praktické strategie, jak se na tyto změny připravit, ať už jste zaměstnanec, manažer nebo podnikatel.""",
    
    "Jak Filip Dřímalka doporučuje začít s digitální transformací ve firmě?":
        """S digitální transformací ve firmě doporučuji začít těmito kroky:

Nejprve vytvořte jasnou vizi a strategii - definujte, čeho chcete digitalizací dosáhnout a jak to souvisí s vašimi obchodními cíli.

Začněte analýzou současného stavu - zmapujte procesy, technologie a digitální dovednosti ve firmě.

Identifikujte oblasti s největším potenciálem pro rychlé výsledky - hledejte projekty s vysokým dopadem a relativně nízkou složitostí implementace.

Sestavte cross-funkční tým s podporou vedení - digitální transformace musí mít zastánce na nejvyšší úrovni.

Implementujte první pilotní projekty - menší úspěchy pomohou získat podporu pro větší změny.

Investujte do vzdělávání zaměstnanců souběžně s implementací technologií.

Měřte výsledky a komunikujte úspěchy - transparentnost podpoří přijetí změn.""",
    
    "Jaké jsou podle Filipa Dřímalky největší mýty o umělé inteligenci?":
        """O umělé inteligenci koluje řada mýtů, které brání jejímu efektivnímu využití:

Mýtus 1: AI nahradí všechny lidské pracovníky - Ve skutečnosti AI spíše transformuje pracovní role a vytváří nové příležitosti.

Mýtus 2: AI je "superinteligence" schopná myslet jako člověk - Současná AI je specializovaná, nemá vědomí ani obecnou inteligenci.

Mýtus 3: Implementace AI vyžaduje obrovské investice - Dnes existuje mnoho dostupných AI nástrojů, které mohou využít i malé firmy.

Mýtus 4: AI je objektivní a nestranná - AI přebírá předsudky ze svých tréninkových dat a potřebuje lidský dohled.

Mýtus 5: AI je relevantní jen pro technologické firmy - AI má potenciál transformovat prakticky každé odvětví.

Mýtus 6: Začít s AI je příliš složité - Mnoho AI nástrojů je dnes navrženo pro snadné použití i netechnickými uživateli."""
}

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
        st.markdown("Zeptejte se na klíčová témata z oblasti digitální transformace, AI a budoucnosti práce.")
        
        # Výběr z doporučených otázek
        st.markdown('<p class="sub-header">Vyberte otázku:</p>', unsafe_allow_html=True)
        selected_question = st.selectbox("", [""] + list(qa_pairs.keys()))
        
        # Odeslání dotazu
        query = selected_question
        
        col_button1, col_button2 = st.columns([1, 5])
        with col_button1:
            if st.button("Odeslat"):
                if query:
                    # Získání odpovědi
                    response = qa_pairs.get(query, "Na tuto otázku nemám odpověď.")
                    
                    # Přidání do historie konverzace
                    st.session_state.conversation.append({"role": "user", "content": query})
                    st.session_state.conversation.append({"role": "assistant", "content": response})
                else:
                    st.warning("Prosím, vyberte otázku.")
        
        with col_button2:
            if st.button("Nová konverzace"):
   "Jaké jsou hlavní predikce Filipa Dřímalky ohledně AI pro rok 2025?":
    """Pro rok 2025 jsem identifikoval několik klíčových predikcí v oblasti umělé inteligence:

AI gramotnost výrazně vzroste - zaměstnanci i zákazníci budou vzdělanější a firmy budou investovat do praktických kurzů a workshopů.

Digitální propast se prohloubí - rozdíly mezi "power users" a běžnými uživateli se zvětší, přičemž power users se stanou hnací silou inovací.

Pragmatická bezpečnost nabude na významu - firmy budou muset strategicky hodnotit, kde má investice do bezpečnosti smysl a kde jde o zbytečné náklady.

Lidský faktor zůstane klíčový - kontrola, validace a interpretace AI výsledků vyžaduje lidskou inteligenci a schopnost adaptace.

AI se stane součástí osobního brandu i firemních značek - reputace bude ovlivněna kvalitou a spolehlivostí používaných AI nástrojů.

Zaměstnavatelé nabízející moderní AI nástroje budou atraktivnější pro talenty - lidé budou vyhledávat role umožňující práci s nejnovějšími technologiemi.

Cena "běžné inteligence" klesne prakticky na nulu - mnohé expertízy budou díky AI dostupné prakticky každému.

Mnoho firem bude plýtvat prostředky na nevyužité AI služby - což povede k tlaku na optimalizaci a efektivnější využití.""",

"Co Filip Dřímalka doporučuje firmám pro úspěšnou adopci AI?":
    """Pro úspěšnou adopci AI ve firmách doporučuji čtyři klíčové kroky:

Začněte sami u sebe - nejlepší způsob, jak porozumět AI, je učit se přímo v praxi. Vyzkoušejte dostupné nástroje, experimentujte s nimi a zjistěte, co mohou přinést vaší práci.

Testujte různé nástroje a modely - nejprve v malém měřítku hledejte inspiraci a experimentujte, než přistoupíte k plošné implementaci.

Investujte do vzdělávání zaměstnanců - bez dostatečných znalostí a dovedností nemohou lidé plně využívat potenciál AI. Praktické workshopy a kurzy jsou klíčové.

Spolupracujte s experty - zapojte AI specialisty a inovátory, kteří mohou přinést nové perspektivy a zkušenosti.

Nejdůležitější je začít a postupně budovat znalosti a zkušenosti, protože AI se vyvíjí tak rychle, že čekání na "dokonalou" strategii znamená promarnit příležitosti.""",

"Co znamená koncept 'digitální propasti' podle Filipa Dřímalky?":
    """Digitální propast je fenomén, který se v éře AI prohlubuje. Jde o rostoucí rozdíly mezi tzv. "power users" a ostatními uživateli digitálních technologií.

Power users jsou lidé, kteří rychle adoptuji nové technologie, experimentují s nimi a dokáží je efektivně využívat pro zvýšení své produktivity a kreativity. Tito lidé se stávají klíčovými hnacími silami inovací ve firmách.

Na druhé straně spektra jsou uživatelé, kteří se potýkají s nedostatkem digitálních dovedností nebo se změnám aktivně brání. Tato skupina může brzdit celkový technologický pokrok organizace.

Tento trend volá po větší podpoře vzdělávání na základní i pokročilé úrovni. Firmy, které dokáží tuto propast překonat a efektivně vzdělávat všechny své zaměstnance, získají významnou konkurenční výhodu.

Je důležité si uvědomit, že digitální propast není jen technologický problém, ale i sociální a organizační výzva vyžadující systematický přístup.""",

"Jak se podle Filipa Dřímalky změní hodnota 'inteligence' v éře AI?":
    """S nástupem pokročilé umělé inteligence dochází k fenoménu, který nazývám "komoditní inteligence". Cena běžné "inteligence" v mnoha oblastech klesá prakticky na nulu, protože je nahrazována umělou inteligencí.

To má několik zásadních důsledků:

1. Expertíza, která dříve vyžadovala roky studia a praxe, je nyní částečně dostupná "na vyžádání" prostřednictvím AI nástrojů.

2. Běžní lidé mohou díky AI porozumět složitým algoritmům, analýzám a informacím, které byly dříve doménou specialistů.

3. Hodnota se přesouvá od samotného vlastnictví informací k schopnosti klást správné otázky, kriticky hodnotit výstupy AI a kreativně kombinovat různé perspektivy.

4. Konkurenční výhoda firem i jednotlivců bude stále více záviset na tom, jak efektivně dokáží využívat AI k řešení komplexních problémů a vytváření nové hodnoty.

Tento trend zásadně mění dynamiku na trhu práce i v byznysu obecně. Úspěšní budou ti, kdo nepřemýšlí o AI jako o náhradě lidí, ale jako o nástroji, který rozšiřuje lidské schopnosti.""",

"Co je podle Filipa Dřímalky 'AI plýtvání' a jak mu předcházet?":
    """AI plýtvání je fenomén, kdy firmy investují do pokročilých AI služeb a nástrojů, ale plně nevyužívají jejich potenciál. Jde o rostoucí problém, který vidím u mnoha organizací:

Firmy často platí za prémiové verze AI nástrojů, ze kterých využívají jen zlomek funkcí.

Nakupují se řešení bez jasné strategie implementace a měření návratnosti investic.

Zaměstnanci nemají dostatečné vzdělání a podporu, aby mohli nástroje efektivně používat.

Jak tomuto plýtvání předcházet:

1. Začněte s auditem aktuálního využití AI nástrojů - zjistěte, co skutečně používáte a s jakým přínosem.

2. Vytvořte jasnou strategii adopce AI s měřitelnými cíli a KPI.

3. Investujte do vzdělávání a podpory zaměstnanců souběžně s implementací technologií.

4. Postupujte iterativně - začněte s menšími projekty, vyhodnocujte výsledky a postupně rozšiřujte úspěšné přístupy.

5. Pravidelně přehodnocujte portfolio AI nástrojů a služeb - nebojte se ukončit spolupráci s těmi, které nepřinášejí očekávanou hodnotu.

S rostoucí nabídkou AI služeb bude optimalizace jejich využití stále důležitějším aspektem efektivního řízení nákladů i inovačního potenciálu firem."""w             st.session_state.conversation = []
                st.experimental_rerun()
"Jaké jsou hlavní predikce Filipa Dřímalky ohledně AI pro rok 2025?":
    """Pro rok 2025 jsem identifikoval několik klíčových predikcí v oblasti umělé inteligence:

AI gramotnost výrazně vzroste - zaměstnanci i zákazníci budou vzdělanější a firmy budou investovat do praktických kurzů a workshopů.

Digitální propast se prohloubí - rozdíly mezi "power users" a běžnými uživateli se zvětší, přičemž power users se stanou hnací silou inovací.

Pragmatická bezpečnost nabude na významu - firmy budou muset strategicky hodnotit, kde má investice do bezpečnosti smysl a kde jde o zbytečné náklady.

Lidský faktor zůstane klíčový - kontrola, validace a interpretace AI výsledků vyžaduje lidskou inteligenci a schopnost adaptace.

AI se stane součástí osobního brandu i firemních značek - reputace bude ovlivněna kvalitou a spolehlivostí používaných AI nástrojů.

Zaměstnavatelé nabízející moderní AI nástroje budou atraktivnější pro talenty - lidé budou vyhledávat role umožňující práci s nejnovějšími technologiemi.

Cena "běžné inteligence" klesne prakticky na nulu - mnohé expertízy budou díky AI dostupné prakticky každému.

Mnoho firem bude plýtvat prostředky na nevyužité AI služby - což povede k tlaku na optimalizaci a efektivnější využití.""",

"Co Filip Dřímalka doporučuje firmám pro úspěšnou adopci AI?":
    """Pro úspěšnou adopci AI ve firmách doporučuji čtyři klíčové kroky:

Začněte sami u sebe - nejlepší způsob, jak porozumět AI, je učit se přímo v praxi. Vyzkoušejte dostupné nástroje, experimentujte s nimi a zjistěte, co mohou přinést vaší práci.

Testujte různé nástroje a modely - nejprve v malém měřítku hledejte inspiraci a experimentujte, než přistoupíte k plošné implementaci.

Investujte do vzdělávání zaměstnanců - bez dostatečných znalostí a dovedností nemohou lidé plně využívat potenciál AI. Praktické workshopy a kurzy jsou klíčové.

Spolupracujte s experty - zapojte AI specialisty a inovátory, kteří mohou přinést nové perspektivy a zkušenosti.

Nejdůležitější je začít a postupně budovat znalosti a zkušenosti, protože AI se vyvíjí tak rychle, že čekání na "dokonalou" strategii znamená promarnit příležitosti.""",

"Co znamená koncept 'digitální propasti' podle Filipa Dřímalky?":
    """Digitální propast je fenomén, který se v éře AI prohlubuje. Jde o rostoucí rozdíly mezi tzv. "power users" a ostatními uživateli digitálních technologií.

Power users jsou lidé, kteří rychle adoptuji nové technologie, experimentují s nimi a dokáží je efektivně využívat pro zvýšení své produktivity a kreativity. Tito lidé se stávají klíčovými hnacími silami inovací ve firmách.

Na druhé straně spektra jsou uživatelé, kteří se potýkají s nedostatkem digitálních dovedností nebo se změnám aktivně brání. Tato skupina může brzdit celkový technologický pokrok organizace.

Tento trend volá po větší podpoře vzdělávání na základní i pokročilé úrovni. Firmy, které dokáží tuto propast překonat a efektivně vzdělávat všechny své zaměstnance, získají významnou konkurenční výhodu.

Je důležité si uvědomit, že digitální propast není jen technologický problém, ale i sociální a organizační výzva vyžadující systematický přístup.""",

"Jak se podle Filipa Dřímalky změní hodnota 'inteligence' v éře AI?":
    """S nástupem pokročilé umělé inteligence dochází k fenoménu, který nazývám "komoditní inteligence". Cena běžné "inteligence" v mnoha oblastech klesá prakticky na nulu, protože je nahrazována umělou inteligencí.

To má několik zásadních důsledků:

1. Expertíza, která dříve vyžadovala roky studia a praxe, je nyní částečně dostupná "na vyžádání" prostřednictvím AI nástrojů.

2. Běžní lidé mohou díky AI porozumět složitým algoritmům, analýzám a informacím, které byly dříve doménou specialistů.

3. Hodnota se přesouvá od samotného vlastnictví informací k schopnosti klást správné otázky, kriticky hodnotit výstupy AI a kreativně kombinovat různé perspektivy.

4. Konkurenční výhoda firem i jednotlivců bude stále více záviset na tom, jak efektivně dokáží využívat AI k řešení komplexních problémů a vytváření nové hodnoty.

Tento trend zásadně mění dynamiku na trhu práce i v byznysu obecně. Úspěšní budou ti, kdo nepřemýšlí o AI jako o náhradě lidí, ale jako o nástroji, který rozšiřuje lidské schopnosti.""",

"Co je podle Filipa Dřímalky 'AI plýtvání' a jak mu předcházet?":
    """AI plýtvání je fenomén, kdy firmy investují do pokročilých AI služeb a nástrojů, ale plně nevyužívají jejich potenciál. Jde o rostoucí problém, který vidím u mnoha organizací:

Firmy často platí za prémiové verze AI nástrojů, ze kterých využívají jen zlomek funkcí.

Nakupují se řešení bez jasné strategie implementace a měření návratnosti investic.

Zaměstnanci nemají dostatečné vzdělání a podporu, aby mohli nástroje efektivně používat.

Jak tomuto plýtvání předcházet:

1. Začněte s auditem aktuálního využití AI nástrojů - zjistěte, co skutečně používáte a s jakým přínosem.

2. Vytvořte jasnou strategii adopce AI s měřitelnými cíli a KPI.

3. Investujte do vzdělávání a podpory zaměstnanců souběžně s implementací technologií.

4. Postupujte iterativně - začněte s menšími projekty, vyhodnocujte výsledky a postupně rozšiřujte úspěšné přístupy.

5. Pravidelně přehodnocujte portfolio AI nástrojů a služeb - nebojte se ukončit spolupráci s těmi, které nepřinášejí očekávanou hodnotu.

S rostoucí nabídkou AI služeb bude optimalizace jejich využití stále důležitějším aspektem efektivního řízení nákladů i inovačního potenciálu firem."""       
        # Zobrazení historie konverzace
        st.markdown("### Konverzace:")
        
        for message in st.session_state.conversation:
            if message["role"] == "user":
                st.markdown(f'<div class="message-container user-message"><strong>Vy:</strong> {message["content"]}</div>', unsafe_allow_html=True)
            else:
                st.markdown(
                    f'<div class="message-container assistant-message"><strong>Filip Dřímalka:</strong> {message["content"]}</div>', 
                    unsafe_allow_html=True
                )
    
    # Footer
    st.markdown("""
    <div style="text-align:center; margin-top:30px; padding-top:20px; border-top:1px solid #eee;">
        <p class="small-font">Vytvořeno jako demonstrace AI schopností. Tento chatbot představuje pohled Filipa Dřímalky založený na jeho veřejných vystoupeních a publikacích.</p>
    </div>
    """, unsafe_allow_html=True)

# Spuštění aplikace
if __name__ == "__main__":
    main()
