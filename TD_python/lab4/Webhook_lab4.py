# import du framework permettant de créer un serveur web
from flask import Flask, request
# les échanges se font en json
import json

# pour les fonctions d'appel à OWM
import requests
owmtoken = "7ee6bfdfa6178b4ee99ad48ff12d0b61"
owmurl="http://api.openweathermap.org/data/2.5/"

# intialisation de l'application
app = Flask(__name__)

# définition de la fonction de réponse sur l'URl <site>/webhook
@app.route('/webhook', methods=['POST'])
def webhook():
    if not request.json:
        print("requete sans json - erreur")
    req = request.get_json(force=True)
    # récupération du nom de l'action
    action = req.get('queryResult').get('action')
    print('action ' + action)
    intention=req.get('queryResult').get('intent').get('displayName')
    # reponse par défaut si l'intention n'est pas reconnue
    reponse = {
        "fulfillmentText": u"Désolé, mais je ne sais pas encore répondre à l'intention: " + intention
    }
    if action == "testWebhook":
        # construction de la réponse
        reponse={
            "fulfillmentText": u"Le webhook est opérationnel"
        }
    if action == "donnerMeteo":
        ville = req.get('queryResult').get("parameters").get("Ville")
        print('ville ' + ville)
        try:
          obs = weather(ville)
          reponse = construireSlackWebhookResponse(ville, obs["description"], obs["temp_max"], obs["temp_min"], determineSmiley(obs["id"]))
          #reponse = {
          #    "fulfillmentText": u"Le temps sur: " + ville + " est de type " + obs["description"]
          #}
        except Exception:
           reponse = {
              "fulfillmentText": u"Désolé, mais le service de météo ne connaît la ville: " + ville
           }
    return json.dumps(reponse)

# récupère la description et le temps sur une ville
def weather(ville):
    url = owmurl + "weather/?q=" + ville + "&lang=fr&APPID=" + owmtoken
    print("appel de l'url :" + url)
    r = requests.get(url)
    resultat = r.json()
    description = resultat['weather'][0]["description"]
    temp_min = resultat['main']['temp_min'] - 273.15
    temp_max = resultat['main']['temp_max'] - 273.15
    id = resultat['weather'][0]['id']
    ret= {"description": description, "temp_min":temp_min, "temp_max":temp_max, "id":id}
    return ret

def determineSmiley(weatherId):
    if weatherId < 600:
        return ":umbrella:"
    if weatherId==803 or weatherId==804:
        return ":cloud:"
    if weatherId == 801 or weatherId==802:
        return ":partly_sunny:"
    return ":sunny:"

	
	#######  onstruire la réponse de structure Slack : construireSlackWebhookResponse




########
# run the app
if __name__ == '__main__':
   print("Webhook démarré")
   app.run()