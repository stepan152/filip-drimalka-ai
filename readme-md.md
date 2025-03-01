# AI Průvodce myšlenkami Filipa Dřímalky

Tento projekt je chatbot, který představuje myšlenky a názory Filipa Dřímalky na téma digitální transformace, umělé inteligence a budoucnosti práce. Chatbot je postavený na kombinaci vektorového vyhledávání a Anthropic Claude API.

## Jak to funguje

1. **Znalostní báze**: Aplikace obsahuje strukturovanou znalostní bázi s myšlenkami Filipa Dřímalky z jeho knihy, přednášek, podcastů a dalších zdrojů.
2. **Vektorové vyhledávání**: Uživatelský dotaz je transformován do vektorového prostoru a jsou vyhledány nejrelevantnější části znalostní báze.
3. **AI odpověď**: Relevantní informace jsou předány AI modelu Claude, který na jejich základě formuluje odpověď ve stylu Filipa Dřímalky.

## Nasazení aplikace

### 1. Příprava prostředí

Nainstalujte potřebné závislosti:

```bash
pip install -r requirements.txt
```

### 2. Konfigurace API klíče

Pro funkčnost chatbota je potřeba API klíč k Anthropic Claude. Můžete ho nastavit dvěma způsoby:

**Možnost 1: Soubor .streamlit/secrets.toml**
```toml
ANTHROPIC_API_KEY = "váš_api_klíč"
```

**Možnost 2: Při nasazení na Streamlit Cloud** nastav tajné proměnné v sekci "Secrets" v nastavení aplikace.

### 3. Spuštění aplikace lokálně

```bash
streamlit run app.py
```

### 4. Nasazení na Streamlit Cloud

1. Nahrajte kód na GitHub
2. Propojte svůj GitHub účet se Streamlit Cloud
3. Nasaďte aplikaci z repozitáře
4. Nastavte API klíč v sekci "Secrets"

## Rozšíření znalostní báze

Pro rozšíření znalostní báze můžete přidat další informace o Filipu Dřímalkovi do slovníku `knowledge_base` v souboru `app.py`. Struktura je jednoduchá - klíč je název tématu a hodnota je text s informacemi.

## Autor

[Vaše jméno] - [Váš email nebo kontakt]

---

Vytvořeno s použitím:
- [Streamlit](https://streamlit.io/)
- [Anthropic Claude API](https://www.anthropic.com/claude)
- [Sentence Transformers](https://www.sbert.net/)
- [FAISS](https://github.com/facebookresearch/faiss)