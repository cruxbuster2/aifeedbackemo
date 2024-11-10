# pages.py in websocket_test app
import otree
from otree.api import Page

class TestPage(Page):
    def live_feedback(self, data):
        # Simply return a test response to check WebSocket functionality
        return {self.player.id_in_group: {'feedback': 'WebSocket is working!'}}

page_sequence = [TestPage]
