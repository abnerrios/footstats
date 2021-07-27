import os
from pymongo import MongoClient
from dotenv import load_dotenv
import logging
import fbcollect.fbrefstats as fbs
from progress.bar import ChargingBar
load_dotenv()

logging.basicConfig(filename='footstats.log', filemode='w', level=logging.ERROR)

# define a conexão com o servidor de mongodb definido no arquivo .env

def main():
  mongohost = os.getenv('MONGODB_HOST')
  mongoport = int(os.getenv('MONGODB_PORT'))
  mongo = MongoClient(host=mongohost, port=mongoport)
  db = mongo.fbstats

  competitions = fbs.Competitions().competitions()

  for comp in competitions:
    comp_ref = comp.get('href')
    squads = fbs.Squads(comp_ref)
    print('Coletando dados de {}'.format(comp.get('league_name')))
    
    # coleta estatisticas da equipe a cada rodada
    squads_stats = squads.squads()
    bar = ChargingBar('Inserindo squads no banco de dados: ', max=len(squads_stats))
    for squad in squads_stats:
      db.squads.find_one_and_update({'squad_id':squad.id}, {'$set': {'squad_id': squad.id, 'name': squad.name,'country':comp.get('country').upper()}}, upsert=True)

      for stats in squad.stats:
        db.squad_stats.find_one_and_update({'squad_id':squad.id,'date': stats.get('date'), 'stats_type':stats.get('stats_type')},{'$set': stats},upsert=True)
      
      for player in squad.players:
        db.players.find_one_and_update({'player_id': player.get('player_id')},{'$set': player}, upsert=True)

      bar.next()
    bar.finish()

if __name__=='__main__':
  main()