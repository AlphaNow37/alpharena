from pixel_now.protocol import ActionTypes
from pixel_now.constants import MAX_ENERGY


class Player:
    __energy = 0

    def __init__(self, i, sender):
        self.i = i
        self.energy = 0
        self.sender = sender

    @property
    def energy(self):
        return self.__energy

    @energy.setter
    def energy(self, value):
        if value > MAX_ENERGY:
            value = MAX_ENERGY
        if int(value) != int(self.__energy):
            self.sender.send(ActionTypes.SET_ENERGY, int(value))
        self.__energy = value
