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
                st.session_state.conversation = []
                st.experimental_rerun()
        
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
    main()import streamlit as st
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

# Otázky a odpovědi
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

S rostoucí nabídkou AI služeb bude optimalizace jejich využití stále důležitějším aspektem efektivního řízení nákladů i inovačního potenciálu firem.""",

    "Jaké jsou podle Filipa Dřímalky hlavní predikce AI pro rok 2025?":
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

Tento trend zásadně mění dynamiku na trhu práce i v byznysu obecně. Úspěšní budou ti, kdo nepřemýšlí o AI jako o náhradě lidí, ale jako o nástroji, který rozšiřuje lidské schopnosti."""
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
        
        # Inicializace session state - uchování konverzace
        if 'conversation' not in st.session_state:
            st.session_state.conversation = []
        
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
                st.session_state.conversation = []
                st.experimental_rerun()
        
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
    main()</h2>", unsafe_allow_html=True)
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
        
        # Inicializace session state - uchování konverzace
        if 'conversation' not in st.session_state:
            st.session_state.conversation = []
        
        # Výběr z doporučených otázek
        st.markdown('<p class="sub-header">Vyberte otázku:</p>', unsafe_allow_html=True)
        selected_question = st.selectbox("", [""] + list(qa_pairs.keys()))
