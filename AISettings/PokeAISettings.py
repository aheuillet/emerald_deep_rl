from asyncio import sleep
import itertools
from pyboy import WindowEvent
from AISettings.AISettingsInterface import AISettingsInterface, Config

# Macros
DMG_REWARD = 10
FAINT_REWARD = 100
ENCOUNTER_REWARD = 1000
GYM_REWARD = 10000

class GameState():
    def __init__(self, pyboy):
        game_wrapper = pyboy.game_wrapper()
        self.money = game_wrapper.money
        self.badges = game_wrapper.badges
        self.current_poke = game_wrapper.current_poke
        self.opponent_poke = game_wrapper.opponent_poke
        self.scene = game_wrapper.scene


class PokeAI(AISettingsInterface):
	def __init__(self):
		self.realMax = [] #[[1,1, 2500], [1,1, 200]]		

	def GetReward(self, prevGameState: GameState, pyboy):
		# timeRespawn = pyboy.get_memory_value(0xFFA6) #Time until respawn from death (set when Mario has fell to the bottom of the screen) 
		# if(timeRespawn > 0): # if we cant move return 0 reward otherwise we could be punished for crossing a level
		# 	return 0

		"Get current game state"
		current_state = self.GetGameState(pyboy)

		reward = 0

		if current_state.scene == "overworld":
			pass
		elif current_state.scene == "wild":
			if prevGameState.scene == "overworld":
				reward += 1
			reward += self.ComputeBattleReward(prevGameState, current_state)
		elif current_state.scene == "trainer":
			if prevGameState.scene == "overworld":
				reward += 10
			reward += self.ComputeBattleReward(prevGameState, current_state)
		elif current_state.scene == "gym":
			if prevGameState.scene == "overworld":
				reward += 100
			reward += self.ComputeBattleReward(prevGameState, current_state)

		return reward
	
	def ComputeBattleReward(self, prevGameState: GameState, currentGameState: GameState):
		poke_hp_diff = currentGameState.current_poke.hp - prevGameState.current_poke.hp
		opponent_hp_diff = currentGameState.opponent_poke.hp - prevGameState.opponent_poke.hp
		return DMG_REWARD*poke_hp_diff + DMG_REWARD*opponent_hp_diff

	def GetActions(self):
		baseActions = [WindowEvent.PRESS_BUTTON_A,
                       WindowEvent.PRESS_BUTTON_B,
                       WindowEvent.PRESS_ARROW_UP,
                       WindowEvent.PRESS_ARROW_DOWN,
                       WindowEvent.PRESS_ARROW_LEFT,
                       WindowEvent.PRESS_ARROW_RIGHT,
                       WindowEvent.PRESS_BUTTON_START
                       ]

		totalActionsWithRepeats = list(itertools.permutations(baseActions, 2))
		withoutRepeats = []

		for combination in totalActionsWithRepeats:
			reversedCombination = combination[::-1]
			if(reversedCombination not in withoutRepeats):
				withoutRepeats.append(combination)

		filteredActions = [[action] for action in baseActions] + withoutRepeats

		return filteredActions

	def PrintGameState(self, pyboy):
		gameState = GameState(pyboy)
		game_wrapper = pyboy.game_wrapper()

		print("'Fake', level_progress: ", game_wrapper.level_progress)
		print("'Real', level_progress: ", gameState.real_x_pos)
		print("_level_progress_max: ", gameState._level_progress_max)
		print("World: ", gameState.world)
		print("Time respawn", pyboy.get_memory_value(0xFFA6))

	def GetGameState(self, pyboy):
		return GameState(pyboy)

	def GetHyperParameters(self) -> Config:
		config = Config()
		config.exploration_rate_decay = 0.999
		return config

	def GetLength(self, pyboy):
		result = sum([x[2] for x in self.realMax])

		pyboy.game_wrapper()._level_progress_max = 0 # reset max level progress because game hasnt implemented it
		self.realMax = []

		return result
