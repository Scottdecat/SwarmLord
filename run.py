# Based on https://github.com/mindme333/AdditionalPylons

import argparse
import asyncio
import logging
import random
import sys

import sc2
from sc2 import Difficulty, Race
from sc2.client import Client
from sc2.player import Bot, Computer
from sc2.sc2process import SC2Process

# Load bot
from bot import MyBot

bot = Bot(Race.Zerg, MyBot())

# Run ladder game
# This lets python-sc2 connect to a LadderManager game: https://github.com/Cryptyc/Sc2LadderServer
# Based on: https://github.com/Dentosal/python-sc2/blob/master/examples/run_external.py
def run_ladder_game(bot):
    # Load command line arguments
    parser = argparse.ArgumentParser()
    parser.add_argument('--GamePort', type=int, nargs="?", help='Game port')
    parser.add_argument('--StartPort', type=int, nargs="?", help='Start port')
    parser.add_argument('--LadderServer', type=str, nargs="?", help='Ladder server')
    parser.add_argument('--ComputerOpponent', type=str, nargs="?", help='Computer opponent')
    parser.add_argument('--ComputerRace', type=str, nargs="?", help='Computer race')
    parser.add_argument('--ComputerDifficulty', type=str, nargs="?", help='Computer difficulty')
    args, unknown = parser.parse_known_args()
    
    if args.LadderServer == None:
        host = "127.0.0.1"
    else:
        host = args.LadderServer

    host_port = args.GamePort
    lan_port = args.StartPort

    # Versus Computer doesn't work yet
    computer_opponent = False
    if args.ComputerOpponent:
        computer_opponent = True
        computer_race = args.ComputerRace
        computer_difficulty = args.ComputerDifficulty

    # Port config
    ports = [lan_port + p for p in range(1,6)]

    portconfig = sc2.portconfig.Portconfig()
    portconfig.shared = ports[0] # Not used
    portconfig.server = [ports[1], ports[2]]
    portconfig.players = [[ports[3], ports[4]]]

    # Join ladder game
    g = join_ladder_game(
        host=host,
        port=host_port,
        players=[bot],
        realtime=False,
        portconfig=portconfig
    )

    # Run it
    result = asyncio.get_event_loop().run_until_complete(g)
    print(result)

# Modified version of sc2.main._join_game to allow custom host and port.
async def join_ladder_game(host, port, players, realtime, portconfig, save_replay_as=None, step_time_limit=None, game_time_limit=None):
    async with SC2Process(host=host, port=port) as server:
        await server.ping()
        client = Client(server._ws)

        try:
            result = await sc2.main._play_game(players[0], client, realtime, portconfig, step_time_limit, game_time_limit)
            if save_replay_as is not None:
                await client.save_replay(save_replay_as)
            await client.leave()
            await client.quit()
        except ConnectionAlreadyClosed:
            logging.error(f"Connection was closed before the game ended")
            return None

        return result

# Start game
if __name__ == '__main__':
    if "--LadderServer" in sys.argv:
        # Ladder game started by LadderManager
        print("Starting ladder game...")
        run_ladder_game(bot)
