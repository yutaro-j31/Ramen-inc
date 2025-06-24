# handlers/game_handler.py
class GameActionHandler:
    def __init__(self, game_controller):
        self.gc = game_controller

    def process_next_week(self, sender):
        """週を進める処理を呼び出す"""
        self.gc.process_next_week()
