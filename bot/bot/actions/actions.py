"""
actions.py — Azioni personalizzate Rasa per IIS Enzo Siciliano
Compatibile con Flask proxy (app.py) che gestisce la conversione link → pulsanti.
"""

import re
from typing import Any, Text, Dict, List

from rasa_sdk import Action, Tracker
from rasa_sdk.executor import CollectingDispatcher
from rasa_sdk.events import SlotSet


# ---------------------------------------------------------------------------
# Utility
# ---------------------------------------------------------------------------

URL_PATTERN = re.compile(r'(https?://[^\s,\)\]]+)', re.IGNORECASE)


def _has_url(text: str) -> bool:
    return bool(URL_PATTERN.search(text))


# ---------------------------------------------------------------------------
# action_info_scuola
# Chiede all'utente quale tipo di informazione desidera
# ---------------------------------------------------------------------------

class InfoScuola(Action):
    def name(self) -> Text:
        return "action_info_scuola"

    def run(
        self,
        dispatcher: CollectingDispatcher,
        tracker: Tracker,
        domain: Dict[Text, Any],
    ) -> List[Dict[Text, Any]]:

        dispatcher.utter_message(
            text="Quali informazioni desideri avere sulla scuola? "
                 "Puoi chiedermi di indirizzi, contatti, orari, circolari, "
                 "iscrizioni o altro."
        )
        return []


# ---------------------------------------------------------------------------
# action_confirm_info
# Conferma l'entità rilevata e risponde con le info pertinenti
# ---------------------------------------------------------------------------

class ActionConfirmInfo(Action):
    def name(self) -> Text:
        return "action_confirm_info"

    # Mappa entità → risposta testuale + eventuale URL
    INFO_MAP: Dict[str, Dict[str, str]] = {
        "liceo scientifico": {
            "text": "Il percorso del liceo scientifico favorisce l'acquisizione delle conoscenze "
                    "e dei metodi propri della matematica, della fisica e delle scienze naturali.",
            "url": "https://www.iisbisignano.edu.it/indirizzo-di-studio/liceo-scientifico-2/",
            "label": "Scopri il Liceo Scientifico",
        },
        "liceo classico": {
            "text": "Il liceo classico consente di approfondire lo studio della civiltà classica "
                    "e della cultura umanistica.",
            "url": "https://www.iisbisignano.edu.it/indirizzo-di-studio/liceo-classico/",
            "label": "Scopri il Liceo Classico",
        },
        "liceo artistico": {
            "text": "Il percorso del Liceo Artistico è indirizzato allo studio dei fenomeni "
                    "estetici e alla pratica artistica.",
            "url": "https://www.iisbisignano.edu.it/indirizzo-di-studio/liceo-artistico/",
            "label": "Scopri il Liceo Artistico",
        },
        "informatica": {
            "text": "L'indirizzo ITI prepara per il mondo delle comunicazioni e dell'informatica.",
            "url": "https://www.iisbisignano.edu.it/indirizzo-di-studio/informatica-e-telecomunicazioni/",
            "label": "Scopri l'ITI",
        },
        "logistica": {
            "text": "L'indirizzo Trasporti e Logistica permette di approfondire la conduzione "
                    "dei sistemi di trasporto navali, terrestri e aerei.",
            "url": "https://www.iisbisignano.edu.it/indirizzo-di-studio/trasporti-e-logistica/",
            "label": "Scopri Trasporti e Logistica",
        },
        "iis bisignano": {
            "text": "Benvenuto all'IIS Enzo Siciliano di Bisignano!",
            "url": "https://www.iisbisignano.edu.it/",
            "label": "Vai al sito ufficiale",
        },
    }

    def run(
        self,
        dispatcher: CollectingDispatcher,
        tracker: Tracker,
        domain: Dict[Text, Any],
    ) -> List[Dict[Text, Any]]:

        entity_value: str = (
            tracker.get_slot("scuola")
            or tracker.get_slot("istituto")
            or ""
        ).lower().strip()

        info = self.INFO_MAP.get(entity_value)

        if info:
            # Invia testo + URL grezzi — il proxy Flask li separerà in {response, links}
            message = f"{info['text']} {info['url']}"
            dispatcher.utter_message(text=message)
        else:
            dispatcher.utter_message(
                text="Ho capito che vuoi informazioni sulla scuola, "
                     "ma non ho trovato dettagli specifici per la tua richiesta. "
                     "Prova a specificare l'indirizzo o l'argomento di interesse."
            )

        return []


# ---------------------------------------------------------------------------
# extraction_school_entity
# Estrae l'entità "scuola" dal messaggio e la salva in uno slot
# ---------------------------------------------------------------------------

class ExtractionSchoolEntity(Action):
    def name(self) -> Text:
        return "extraction_school_entity"

    KNOWN_SCHOOLS = [
        "iis enzo siciliano",
        "iis bisignano",
        "liceo scientifico",
        "liceo classico",
        "liceo artistico",
        "iti",
        "informatica",
        "logistica",
        "trasporti",
    ]

    def run(
        self,
        dispatcher: CollectingDispatcher,
        tracker: Tracker,
        domain: Dict[Text, Any],
    ) -> List[Dict[Text, Any]]:

        latest_message = tracker.latest_message.get("text", "").lower()

        for school in self.KNOWN_SCHOOLS:
            if school in latest_message:
                return [SlotSet("scuola", school)]

        # Usa l'entità estratta da Rasa NLU se disponibile
        entities = tracker.latest_message.get("entities", [])
        for entity in entities:
            if entity.get("entity") in ("scuola", "istituto"):
                return [SlotSet("scuola", entity.get("value", "").lower())]

        return []
