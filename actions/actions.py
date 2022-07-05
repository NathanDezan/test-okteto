from typing import Any, Text, Dict, List
from rasa_sdk import Action, Tracker, events
from rasa_sdk.executor import CollectingDispatcher
import requests
import json as js
from pymongo import MongoClient

class ActionIP(Action):

    def name(self) -> Text:
        return "action_ip"

    def run(self, dispatcher: CollectingDispatcher, tracker: Tracker, domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        api_adress='http://ip-api.com/json/'
        ip = tracker.get_slot('ip_entity')
        name = tracker.get_slot('name_entity')
        name = name.capitalize()
        mongo_uri = 'mongodb+srv://dezan:adm@cluster0.clupc.mongodb.net/myFirstDatabase?retryWrites=true&w=majority'
        
        ActionIP.consultAPI(ip, name, api_adress, dispatcher, mongo_uri)

        return []

    def mongoConnections(name, ip, input, uri, lat, lon):
        result = {'Nome': name, 'IP': ip, 'Resultado': {'Cidade': input['city'], 'Estado': input['regionName'], 'Pais': input['country'], 'Latitude': lat, 'Longitude': lon}}

        try:
            client = MongoClient(uri)
            db = client["bot"]
            collection = db["searchs"]
            collection.insert_one(result)
            print("Sucesso ao salvar o dado no bd!")
        except:
            print("Erro na função mongoConnections.")

        return []

    def consultAPI(ip, name, uri, dispatcher, mongo_uri):
        try:
            result_data = requests.get(uri + ip).json()
            aux_coord = js.dumps(result_data).split(",")
            lat, lon = ActionIP.getCoord(aux_coord[7], aux_coord[8])
            info = "\tCidade: " + result_data['city'] + "\n\tEstado: " + result_data['regionName'] + "\n\tPais: " + result_data['country'] + "\n\tCEP: " + result_data['zip'] + "\n\tLatitude: " + lat + "\n\tLongitude: " + lon
            dispatcher.utter_message(text=f"{name} segue as informações sobre o endereço IP ({ip}):\n{info}")

            ActionIP.mongoConnections(name, ip, result_data, mongo_uri, lat, lon)
            print(f"Consulta realizada: \n {info}")
        except:
            dispatcher.utter_message(text="Sinto muito, algo não está correto! Verifique o endereço IP informado.")
            print("Erro na classe ActionIP.")

        return []

    def getCoord(nof_latitude, nof_longitude):
        latitude = nof_latitude[8:]
        longitude = nof_longitude[8:]
        
        return latitude, longitude
    
class ResetSlot(Action):

    def name(self):
        return "action_reset_slot"

    def run(self, dispatcher, tracker, domain):
        return [events.SlotSet("ip_entity", None)]