from flask import Flask, render_template, request, jsonify
import requests
import re

RASA_API_URL = 'http://localhost:5005/webhooks/rest/webhook'
app = Flask(__name__)

# Regex per rilevare URL nel testo
URL_PATTERN = re.compile(r'(https?://[^\s,\)\]]+)', re.IGNORECASE)

# Mappa URL → etichetta leggibile per i pulsanti
LINK_LABELS = {
    "iscrizionionline":                "📝 Iscrizioni Online",
    "circolare":                       "📋 Vai alle Circolari",
    "notizie":                         "📰 Vai alle Notizie",
    "libri-di-testo":                  "📚 Lista Libri di Testo",
    "calendario-esami":                "📅 Calendario Esami ICDL",
    "icdl":                            "💻 Info ICDL",
    "liceo-scientifico":               "🔬 Liceo Scientifico",
    "liceo-classico":                  "📜 Liceo Classico",
    "liceo-artistico":                 "🎨 Liceo Artistico",
    "informatica-e-telecomunicazioni": "💡 ITI",
    "trasporti-e-logistica":           "⚓ Trasporti e Logistica",
    "il-contesto":                     "🏫 Presentazione Istituto",
    "dirigenza":                       "👔 Dirigenza",
    "segreteria":                      "🗂️ Segreteria",
    "ptof":                            "📄 PTOF",
    "pon":                             "🇪🇺 PON",
    "etwinning-erasmus":               "✈️ Erasmus+",
    "orario-provvisorio":              "🕐 Orario Classi",
    "adattamento-calendario":          "📆 Calendario Scolastico",
    "visualizzamaterieesame":          "📋 Materie Esame",
    "esami-di-primo":                  "🎓 Info Maturità",
    "iisbisignano":                    "🌐 Sito Ufficiale",
    "istruzione.it":                   "🏛️ MIM",
}


def get_link_label(url):
    """Restituisce un'etichetta leggibile per l'URL dato."""
    for key, label in LINK_LABELS.items():
        if key in url.lower():
            return label
    return "🔗 Apri link"


def extract_links(text):
    """
    Estrae gli URL dal testo e restituisce:
    - testo pulito (senza URL grezzi)
    - lista di dizionari [{label, url}] da passare al frontend
    """
    found_urls = URL_PATTERN.findall(text)
    links = [{"label": get_link_label(url), "url": url.rstrip('.')} for url in found_urls]

    # Rimuove gli URL dal testo (saranno mostrati come pulsanti)
    clean_text = URL_PATTERN.sub("", text).strip()
    clean_text = re.sub(r'\s{2,}', ' ', clean_text)  # spazi doppi
    clean_text = re.sub(r'\s+\.', '.', clean_text)    # spazi prima del punto

    return clean_text, links


@app.route('/')
def index():
    return render_template('index.html')


@app.route('/webhook', methods=['POST'])
def webhook():
    user_message = request.json['message']
    print("User Message:", user_message)

    rasa_response = requests.post(RASA_API_URL, json={'message': user_message})
    rasa_response_json = rasa_response.json()

    print("Rasa Response:", rasa_response_json)

    bot_response = rasa_response_json[0]['text'] if rasa_response_json else "Scusa non ho capito, fai un'altra domanda"

    # Estrae i link dal testo e li separa in un campo dedicato
    clean_text, links = extract_links(bot_response)

    return jsonify({'response': clean_text, 'links': links})


if __name__ == "__main__":
    app.run(debug=True, port=3000)
